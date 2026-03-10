import asyncio
import json
import logging
from typing import Any

from app.clients.amadeus_client import AmadeusClient
from app.clients.kiwi_client import KiwiClient
from app.clients.normalizer import (
    deduplicate_flights,
    normalize_amadeus_flight,
    normalize_kiwi_flight,
    normalize_skyscanner_flight,
)
from app.clients.skyscanner_client import SkyscannerClient
from app.lib.currency import get_exchange_rates
from app.models.user import User
from app.schemas.compare import (
    CompareResult,
    FlightCompareRequest,
    FlightCompareResponse,
    HotelCompareRequest,
    HotelCompareResponse,
    PricePoint,
    UnifiedCompareRequest,
)
from app.schemas.search import normalized_dict_to_flight_result

logger = logging.getLogger(__name__)


class PriceService:
    def __init__(self):
        self.amadeus = AmadeusClient()
        self.skyscanner = SkyscannerClient()
        self.kiwi = KiwiClient()

    async def unified_compare(
        self, request: UnifiedCompareRequest, user: User
    ) -> list[CompareResult]:
        """Compare items by reading cached data from Redis."""
        results: list[CompareResult] = []

        try:
            from app.db.redis import redis_client

            for item_id in request.item_ids:
                cache_key = f"{request.item_type}:{item_id}"
                raw = await redis_client.get(cache_key)
                if not raw:
                    continue

                data = json.loads(raw)
                sources: list[dict] = data.get("sources", [])
                flight_data: dict = data.get("flight", {})
                fetched_at: str = data.get("fetched_at", "")

                # Build label from cached flight data
                out_segs = flight_data.get("outbound_segments", [])
                ret_segs = flight_data.get("return_segments") or []
                first_out = out_segs[0] if out_segs else {}
                last_out = out_segs[-1] if out_segs else {}

                out_stops = flight_data.get("stops", max(len(out_segs) - 1, 0))
                out_suffix = "s" if out_stops > 1 else ""
                out_stop_label = "direct" if out_stops == 0 else f"{out_stops} stop{out_suffix}"

                label = (
                    f"{first_out.get('airline', '')} "
                    f"{first_out.get('departure_airport', '')} → "
                    f"{last_out.get('arrival_airport', '')} ({out_stop_label})"
                ).strip()

                if ret_segs:
                    first_ret = ret_segs[0]
                    last_ret = ret_segs[-1]
                    ret_stops = max(len(ret_segs) - 1, 0)
                    ret_suffix = "s" if ret_stops > 1 else ""
                    ret_stop_label = "direct" if ret_stops == 0 else f"{ret_stops} stop{ret_suffix}"
                    label += (
                        f" / {first_ret.get('airline', '')} "
                        f"{first_ret.get('departure_airport', '')} → "
                        f"{last_ret.get('arrival_airport', '')} ({ret_stop_label})"
                    ).rstrip()

                # Build price points from all source dicts
                prices: list[PricePoint] = []
                for src in sources:
                    prices.append(
                        PricePoint(
                            provider=src.get("source", ""),
                            price=float(src.get("price", 0)),
                            currency=src.get("currency", "TWD"),
                            url=src.get("booking_url") or None,
                            fetched_at=fetched_at,
                        )
                    )

                if not prices:
                    continue

                price_values = [p.price for p in prices]
                results.append(
                    CompareResult(
                        item_id=item_id,
                        item_type=request.item_type,
                        label=label,
                        prices=prices,
                        lowest_price=min(price_values),
                        highest_price=max(price_values),
                        average_price=sum(price_values) / len(price_values),
                    )
                )
        except Exception:
            logger.warning("unified_compare Redis read failed", exc_info=True)

        return results

    async def compare_flights(
        self, request: FlightCompareRequest, user: User
    ) -> FlightCompareResponse:
        departure_date = str(request.date_from)
        return_date = str(request.date_to) if request.date_to else None

        # Multi-source parallel search
        amadeus_task = self.amadeus.search_flights(
            origin=request.origin,
            destination=request.destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=request.passengers,
            cabin_class=request.cabin_class,
        )
        skyscanner_task = self.skyscanner.search_flights(
            origin_sky_id=request.origin,
            destination_sky_id=request.destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=request.passengers,
        )
        kiwi_task = self.kiwi.search_flights(
            origin_sky_id=request.origin,
            destination_sky_id=request.destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=request.passengers,
        )

        rates_task = get_exchange_rates("EUR")

        gather_results = await asyncio.gather(
            amadeus_task, skyscanner_task, kiwi_task, rates_task,
            return_exceptions=True,
        )
        amadeus_raw: Any = gather_results[0]
        skyscanner_raw: Any = gather_results[1]
        kiwi_raw: Any = gather_results[2]
        rates_raw = gather_results[3]
        exchange_rates: dict[str, float] = rates_raw if isinstance(rates_raw, dict) else {}

        if isinstance(rates_raw, BaseException):
            logger.warning("Exchange rate fetch failed: %s", rates_raw)

        currency = "TWD"

        normalized: list[dict] = []
        sources: list[str] = []

        if isinstance(amadeus_raw, list) and amadeus_raw:
            sources.append("amadeus")
            for offer in amadeus_raw:
                try:
                    normalized.append(
                        normalize_amadeus_flight(
                            offer, currency=currency, exchange_rates=exchange_rates
                        )
                    )
                except Exception:
                    logger.debug("Failed to normalize Amadeus compare offer", exc_info=True)

        if isinstance(skyscanner_raw, list) and skyscanner_raw:
            sources.append("skyscanner")
            for itin in skyscanner_raw:
                try:
                    normalized.append(
                        normalize_skyscanner_flight(
                            itin,
                            origin=request.origin,
                            destination=request.destination,
                        )
                    )
                except Exception:
                    logger.debug("Failed to normalize Skyscanner compare offer", exc_info=True)

        if isinstance(kiwi_raw, list) and kiwi_raw:
            sources.append("kiwi")
            for itin in kiwi_raw:
                try:
                    normalized.append(normalize_kiwi_flight(itin))
                except Exception:
                    logger.debug("Failed to normalize Kiwi compare offer", exc_info=True)

        deduped = deduplicate_flights(normalized)
        results = [normalized_dict_to_flight_result(d) for d in deduped]

        # Sort by price
        results.sort(key=lambda f: f.price)

        cheapest = results[0] if results else None
        fastest = min(
            (f for f in results if f.total_duration_minutes),
            key=lambda f: f.total_duration_minutes,
            default=None,
        )

        return FlightCompareResponse(
            results=results,
            sources=sources,
            cheapest=cheapest,
            fastest=fastest,
        )

    async def compare_hotels(
        self, request: HotelCompareRequest, user: User
    ) -> HotelCompareResponse:
        return HotelCompareResponse(results=[], sources=[])
