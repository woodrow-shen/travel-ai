import asyncio
import json
import logging
import uuid
from datetime import UTC, datetime
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
from app.schemas.search import (
    AdventureDestination,
    AdventureSearchRequest,
    AdventureSearchResponse,
    DirectFlightRecommendation,
    DirectSearchRequest,
    DirectSearchResponse,
    FlightResult,
    FlightSearchRequest,
    FlightSegment,
    HotelSearchRequest,
    HotelSearchResponse,
    PriceInfo,
    SearchResponse,
    normalized_dict_to_flight_result,
)

logger = logging.getLogger(__name__)

_CACHE_TTL = 1800  # 30 minutes


class SearchService:
    def __init__(self):
        self.amadeus = AmadeusClient()
        self.skyscanner = SkyscannerClient()
        self.kiwi = KiwiClient()

    async def search_flights(
        self, request: FlightSearchRequest, user: User
    ) -> SearchResponse:
        origin = request.origin.upper()
        destination = request.destination.upper()
        departure_date = str(request.date_from)
        return_date = str(request.date_to) if request.date_to else None
        currency = request.currency or "TWD"

        # Parallel multi-source search
        amadeus_task = self.amadeus.search_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=request.passengers,
            cabin_class=request.cabin_class,
            max_stops=request.max_stops,
        )
        skyscanner_task = self.skyscanner.search_flights(
            origin_sky_id=origin,
            destination_sky_id=destination,
            departure_date=departure_date,
            return_date=return_date,
            adults=request.passengers,
        )
        kiwi_task = self.kiwi.search_flights(
            origin_sky_id=origin,
            destination_sky_id=destination,
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

        # Log exchange rate fetch failure
        if isinstance(rates_raw, BaseException):
            logger.warning("Exchange rate fetch failed: %s", rates_raw)

        # Normalize all results into common dict format
        normalized: list[dict] = []

        if isinstance(amadeus_raw, list):
            for offer in amadeus_raw:
                try:
                    normalized.append(
                        normalize_amadeus_flight(
                            offer, currency=currency, exchange_rates=exchange_rates
                        )
                    )
                except Exception:
                    logger.debug("Failed to normalize Amadeus offer", exc_info=True)
        elif isinstance(amadeus_raw, BaseException):
            logger.warning("Amadeus search failed: %s", amadeus_raw)

        if isinstance(skyscanner_raw, list):
            for itin in skyscanner_raw:
                try:
                    normalized.append(
                        normalize_skyscanner_flight(
                            itin,
                            currency=currency,
                            origin=request.origin,
                            destination=request.destination,
                        )
                    )
                except Exception:
                    logger.debug("Failed to normalize Skyscanner offer", exc_info=True)
        elif isinstance(skyscanner_raw, BaseException):
            logger.warning("Skyscanner search failed: %s", skyscanner_raw)

        if isinstance(kiwi_raw, list):
            for itin in kiwi_raw:
                try:
                    normalized.append(normalize_kiwi_flight(itin, currency=currency))
                except Exception:
                    logger.debug("Failed to normalize Kiwi offer", exc_info=True)
        elif isinstance(kiwi_raw, BaseException):
            logger.warning("Kiwi search failed: %s", kiwi_raw)

        # Deduplicate and convert to FlightResult
        deduped = deduplicate_flights(normalized)
        now_iso = datetime.now(tz=UTC).isoformat()
        results = [normalized_dict_to_flight_result(d) for d in deduped]

        # Sort by price
        results.sort(key=lambda f: f.price)

        # Cache each flight in Redis for compare
        await self._cache_flights(results, normalized, now_iso)

        search_id = uuid.uuid4().hex[:16]
        return SearchResponse(
            search_id=search_id,
            type="flight",
            flights=results,
            total_results=len(results),
            search_params={
                "origin": origin,
                "destination": destination,
                "date_from": str(request.date_from),
                "date_to": str(request.date_to) if request.date_to else None,
                "passengers": request.passengers,
            },
            created_at=now_iso,
        )

    async def search_hotels(
        self, request: HotelSearchRequest, user: User
    ) -> HotelSearchResponse:
        return HotelSearchResponse(results=[], total=0)

    async def search_direct(
        self, request: DirectSearchRequest, user: User
    ) -> DirectSearchResponse:
        currency = "TWD"

        direct_results = await asyncio.gather(
            self.amadeus.search_flights(
                origin=request.origin.upper(),
                destination=request.destination.upper(),
                departure_date=str(request.date_from),
                return_date=str(request.date_to),
                adults=request.passengers,
                cabin_class=request.cabin_class,
                max_stops=0,
                max_results=50,
            ),
            get_exchange_rates("EUR"),
        )
        amadeus_results: list[dict] = direct_results[0]
        exchange_rates: dict[str, float] = direct_results[1]

        flights: list[FlightResult] = []
        for offer in amadeus_results:
            try:
                d = normalize_amadeus_flight(
                    offer, currency=currency, exchange_rates=exchange_rates
                )
                if d.get("stops", 0) == 0:
                    flights.append(normalized_dict_to_flight_result(d))
            except Exception:
                logger.debug("Failed to normalize Amadeus direct flight", exc_info=True)

        # Score and rank direct flights
        recommendations: list[DirectFlightRecommendation] = []
        for flight in flights:
            score = self._score_direct_flight(flight, user)
            recommendations.append(
                DirectFlightRecommendation(
                    rank=0,
                    score=score,
                    flight=flight,
                    reasons=self._get_score_reasons(flight, user),
                    price=PriceInfo(amount=flight.price, currency=flight.currency),
                )
            )

        recommendations.sort(key=lambda r: r.score, reverse=True)
        for i, rec in enumerate(recommendations):
            rec.rank = i + 1

        return DirectSearchResponse(
            recommendations=recommendations[:10],
            total_direct_flights=len(recommendations),
        )

    async def search_adventure(
        self, request: AdventureSearchRequest, user: User
    ) -> AdventureSearchResponse:
        amadeus_results = await self.amadeus.search_inspiration(
            origin=request.origin.upper(),
            departure_date=str(request.date_from),
        )

        seen_airports: set[str] = set()
        adventures: list[AdventureDestination] = []

        for offer in amadeus_results:
            airport = offer.get("destination", "")
            if airport in seen_airports:
                continue
            seen_airports.add(airport)

            price_data = offer.get("price", {})
            price_amount = float(price_data.get("total", 0))
            currency = price_data.get("currency", "TWD")
            if price_amount <= 0:
                continue

            price = PriceInfo(amount=price_amount, currency=currency)

            # Build a stub FlightResult for adventure destinations
            stub_segment = FlightSegment(
                airline="",
                flight_number="",
                departure_airport=request.origin,
                arrival_airport=airport,
                departure_time="",
                arrival_time="",
                duration_minutes=0,
            )
            best_flight = FlightResult(
                id=uuid.uuid4().hex[:12],
                provider="amadeus",
                price=price_amount,
                currency=currency,
                outbound_segments=[stub_segment],
                total_duration_minutes=0,
                stops=0,
            )

            adventures.append(
                AdventureDestination(
                    rank=0,
                    destination={
                        "city": offer.get("destination", ""),
                        "airport": airport,
                        "country": "",
                    },
                    best_flight=best_flight,
                    price=price,
                    tags=self._get_adventure_tags_from_price(price),
                )
            )

        adventures.sort(key=lambda a: a.price.amount)
        for i, adv in enumerate(adventures[:10]):
            adv.rank = i + 1

        coverage = f"Searched {len(seen_airports)}+ destinations"
        return AdventureSearchResponse(
            adventures=adventures[:10],
            search_coverage=coverage,
            origin=request.origin,
        )

    async def _cache_flights(
        self,
        results: list[FlightResult],
        normalized: list[dict],
        fetched_at: str,
    ) -> None:
        """Cache flight data in Redis for compare lookups. Gracefully skip on failure."""
        try:
            from app.db.redis import redis_client

            # Build a mapping of flight_id -> list of normalized dicts (all sources)
            id_to_dicts: dict[str, list[dict]] = {}
            for d in normalized:
                from app.schemas.search import _stable_flight_id

                fid = _stable_flight_id(d.get("flight_number", ""), d.get("departure_time", ""))
                id_to_dicts.setdefault(fid, []).append(d)

            pipe = redis_client.pipeline()
            for flight in results:
                cache_data = {
                    "flight": flight.model_dump(mode="json"),
                    "sources": id_to_dicts.get(flight.id, []),
                    "fetched_at": fetched_at,
                }
                pipe.setex(f"flight:{flight.id}", _CACHE_TTL, json.dumps(cache_data))
            await pipe.execute()
        except Exception:
            logger.debug("Redis cache write failed, skipping", exc_info=True)

    def _score_direct_flight(self, flight: FlightResult, user: User) -> int:
        score = 50

        # Parse hour from first segment departure_time (ISO 8601 string)
        dep_time = ""
        if flight.outbound_segments:
            dep_time = flight.outbound_segments[0].departure_time
        hour = self._parse_hour(dep_time)

        if hour is not None:
            if 8 <= hour <= 14:
                score += 20
            elif 14 < hour <= 20:
                score += 10

        if flight.total_duration_minutes:
            if flight.total_duration_minutes < 180:
                score += 15
            elif flight.total_duration_minutes < 300:
                score += 10

        if flight.price > 0:
            if flight.price < 10000:
                score += 10
            elif flight.price < 20000:
                score += 5

        return min(score, 100)

    def _get_score_reasons(self, flight: FlightResult, user: User) -> list[str]:
        reasons = []
        dep_time = ""
        if flight.outbound_segments:
            dep_time = flight.outbound_segments[0].departure_time
        hour = self._parse_hour(dep_time)

        if hour is not None:
            if 8 <= hour <= 14:
                reasons.append("Morning departure")
            elif 14 < hour <= 20:
                reasons.append("Afternoon departure")

        if flight.total_duration_minutes and flight.total_duration_minutes < 180:
            reasons.append("Short flight time")

        if flight.stops == 0:
            reasons.append("Direct flight")

        return reasons

    @staticmethod
    def _parse_hour(iso_str: str) -> int | None:
        """Extract hour from ISO 8601 datetime string."""
        if not iso_str or "T" not in iso_str:
            return None
        try:
            time_part = iso_str.split("T")[1]
            return int(time_part[:2])
        except (IndexError, ValueError):
            return None

    def _get_adventure_tags_from_price(self, price: PriceInfo) -> list[str]:
        tags = []
        if price.amount < 5000:
            tags.append("Budget")
        return tags
