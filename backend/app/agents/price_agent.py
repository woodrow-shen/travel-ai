import asyncio
import logging
from statistics import mean
from typing import Any

from sqlalchemy import select

from app.agents.base import BaseAgent
from app.agents.tools.price_tools import PRICE_TOOLS
from app.clients.amadeus_client import AmadeusClient
from app.clients.google_flights_client import GoogleFlightsClient
from app.clients.kiwi_client import KiwiClient
from app.clients.normalizer import (
    deduplicate_flights,
    deduplicate_hotels,
    normalize_amadeus_flight,
    normalize_google_flights_flight,
    normalize_kiwi_flight,
    normalize_kiwi_hotel,
    normalize_skyscanner_flight,
    normalize_skyscanner_hotel,
)
from app.clients.skyscanner_client import SkyscannerClient
from app.db.session import async_session_factory
from app.lib.currency import get_exchange_rates
from app.models.price_history import PriceHistory

logger = logging.getLogger(__name__)


class PriceAgent(BaseAgent):
    def __init__(self, locale: str = "zh-TW"):
        super().__init__(locale=locale)
        self.amadeus = AmadeusClient()
        self.skyscanner = SkyscannerClient()
        self.kiwi = KiwiClient()
        self.google_flights = GoogleFlightsClient()

    @property
    def name(self) -> str:
        return "price"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a price comparison specialist. Your job is to compare prices across "
            "multiple sources for flights and hotels, and analyze price trends using "
            "historical data. Identify the best deals and present clear comparisons."
            + self.locale_instruction
        )

    @property
    def tools(self) -> list[dict]:
        return PRICE_TOOLS

    async def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "compare_prices":
            return await self._compare_prices(tool_input)
        elif tool_name == "get_price_history":
            return await self._get_price_history(tool_input)
        elif tool_name == "get_price_graph":
            return await self._get_price_graph(tool_input)
        return {"error": f"Unknown tool: {tool_name}"}

    async def _compare_prices(self, params: dict) -> dict:
        item_type = params["item_type"]
        search_params = params["search_params"]

        if item_type == "hotel":
            return await self._compare_hotel_prices(search_params)

        if item_type != "flight":
            return {"comparisons": [], "sources_checked": []}

        origin = search_params.get("origin", "")
        destination = search_params.get("destination", "")
        date = search_params.get("date", "")

        # Multi-source parallel search
        results = await asyncio.gather(
            self.amadeus.search_flights(
                origin=origin,
                destination=destination,
                departure_date=date,
            ),
            self.skyscanner.search_flights(
                origin_sky_id=origin,
                destination_sky_id=destination,
                departure_date=date,
            ),
            self.kiwi.search_flights(
                origin_sky_id=origin,
                destination_sky_id=destination,
                departure_date=date,
            ),
            self.google_flights.search_flights(
                origin=origin,
                destination=destination,
                departure_date=date,
            ),
            get_exchange_rates("EUR"),
            return_exceptions=True,
        )
        amadeus_raw, skyscanner_raw, kiwi_raw, google_flights_raw, rates_raw = results
        exchange_rates = (
            rates_raw if isinstance(rates_raw, dict) else {}
        )

        sources = []
        normalized: list[dict] = []

        if isinstance(amadeus_raw, list) and amadeus_raw:
            for offer in amadeus_raw:
                try:
                    normalized.append(
                        normalize_amadeus_flight(
                            offer, exchange_rates=exchange_rates
                        )
                    )
                except Exception:
                    pass
            sources.append({
                "name": "amadeus",
                "results_count": len(amadeus_raw),
            })

        if isinstance(skyscanner_raw, list) and skyscanner_raw:
            for itin in skyscanner_raw:
                try:
                    normalized.append(
                        normalize_skyscanner_flight(
                            itin,
                            origin=origin,
                            destination=destination,
                        )
                    )
                except Exception:
                    pass
            sources.append({
                "name": "skyscanner",
                "results_count": len(skyscanner_raw),
            })

        if isinstance(kiwi_raw, list) and kiwi_raw:
            for itin in kiwi_raw:
                try:
                    normalized.append(normalize_kiwi_flight(itin))
                except Exception:
                    pass
            sources.append({
                "name": "kiwi",
                "results_count": len(kiwi_raw),
            })

        if isinstance(google_flights_raw, list) and google_flights_raw:
            for itin in google_flights_raw:
                try:
                    normalized.append(normalize_google_flights_flight(itin))
                except Exception:
                    pass
            sources.append({
                "name": "google_flights",
                "results_count": len(google_flights_raw),
            })

        deduped = deduplicate_flights(normalized)
        deduped.sort(key=lambda f: f.get("price", float("inf")))

        cheapest = deduped[0] if deduped else None
        best_source = cheapest.get("source") if cheapest else None

        return {
            "comparisons": deduped,
            "sources_checked": [s["name"] for s in sources],
            "best_source": best_source,
            "cheapest_price": cheapest.get("price") if cheapest else None,
            "total_options": len(deduped),
        }

    async def _get_price_history(self, params: dict) -> dict:
        origin = params["origin"]
        destination = params["destination"]
        days_back = params.get("days_back", 90)

        async with async_session_factory() as db:
            stmt = (
                select(
                    PriceHistory.price_amount,
                    PriceHistory.price_currency,
                    PriceHistory.created_at,
                )
                .where(
                    PriceHistory.origin == origin,
                    PriceHistory.destination == destination,
                )
                .order_by(PriceHistory.created_at.desc())
                .limit(days_back)
            )
            result = await db.execute(stmt)
            rows = result.all()

        if not rows:
            return {
                "origin": origin,
                "destination": destination,
                "days_back": days_back,
                "history": [],
                "average": 0,
                "min": 0,
                "max": 0,
                "trend": "insufficient_data",
            }

        prices = [row[0] for row in rows]
        currency = rows[0][1]
        history = [
            {"price": row[0], "currency": row[1], "date": row[2].isoformat()}
            for row in rows
        ]

        avg = mean(prices)
        # Simple trend: compare first half average vs second half average
        mid = len(prices) // 2
        if mid > 0:
            recent_avg = mean(prices[:mid])
            older_avg = mean(prices[mid:])
            if recent_avg < older_avg * 0.95:
                trend = "decreasing"
            elif recent_avg > older_avg * 1.05:
                trend = "increasing"
            else:
                trend = "stable"
        else:
            trend = "insufficient_data"

        return {
            "origin": origin,
            "destination": destination,
            "days_back": days_back,
            "currency": currency,
            "history": history,
            "average": round(avg, 2),
            "min": round(min(prices), 2),
            "max": round(max(prices), 2),
            "trend": trend,
        }

    async def _get_price_graph(self, params: dict) -> dict:
        """Get daily lowest prices from Google Flights price graph."""
        origin = params["origin"]
        destination = params["destination"]
        departure_range = params["departure_range"]
        return_date = params.get("return_date")
        currency = params.get("currency", "TWD")

        try:
            points = await self.google_flights.get_price_graph(
                origin=origin,
                destination=destination,
                departure_range=departure_range,
                return_date=return_date,
                currency=currency,
            )
        except Exception:
            logger.exception("Google Flights price graph failed for %s->%s", origin, destination)
            return {"error": "Failed to fetch price graph", "points": []}

        if not points:
            return {
                "origin": origin,
                "destination": destination,
                "points": [],
                "message": "No price data available for this route/range.",
            }

        prices = [p["price"] for p in points]
        cheapest = min(points, key=lambda p: p["price"])

        return {
            "origin": origin,
            "destination": destination,
            "currency": currency,
            "points": points,
            "total_days": len(points),
            "cheapest_date": cheapest["departureDate"],
            "cheapest_price": cheapest["price"],
            "average_price": round(mean(prices), 2),
            "min_price": min(prices),
            "max_price": max(prices),
        }

    async def _compare_hotel_prices(self, search_params: dict) -> dict:
        """Compare hotel prices across Skyscanner and Kiwi."""
        location = search_params.get("location", "")
        checkin = search_params.get("check_in", "")
        checkout = search_params.get("check_out", "")
        guests = search_params.get("guests", 1)
        currency = "TWD"

        # Resolve locations
        sky_ac = self.skyscanner.hotel_autocomplete(location)
        kiwi_ac = self.kiwi.stays_autocomplete(location)
        ac_results = await asyncio.gather(sky_ac, kiwi_ac, return_exceptions=True)

        sky_entity_id = ""
        if isinstance(ac_results[0], list) and ac_results[0]:
            sky_entity_id = str(ac_results[0][0].get("entityId", ""))

        kiwi_dest_id = ""
        kiwi_dest_type = "city"
        if isinstance(ac_results[1], list) and ac_results[1]:
            kiwi_dest_id = str(ac_results[1][0].get("dest_id", ""))
            kiwi_dest_type = ac_results[1][0].get("dest_type", "city")

        tasks: list = []
        labels: list[str] = []
        if sky_entity_id:
            tasks.append(self.skyscanner.search_hotels(
                entity_id=sky_entity_id, checkin=checkin,
                checkout=checkout, adults=guests, currency=currency,
            ))
            labels.append("skyscanner")
        if kiwi_dest_id:
            tasks.append(self.kiwi.search_hotels(
                dest_id=kiwi_dest_id, dest_type=kiwi_dest_type,
                checkin=checkin, checkout=checkout,
                adults=guests, currency=currency,
            ))
            labels.append("kiwi")

        if not tasks:
            return {"comparisons": [], "sources_checked": []}

        results = await asyncio.gather(*tasks, return_exceptions=True)

        normalized: list[dict] = []
        for idx, raw in enumerate(results):
            label = labels[idx]
            if isinstance(raw, BaseException) or not isinstance(raw, list):
                continue
            for hotel in raw:
                try:
                    if label == "skyscanner":
                        normalized.append(normalize_skyscanner_hotel(
                            hotel, currency=currency,
                            checkin=checkin, checkout=checkout,
                        ))
                    else:
                        normalized.append(normalize_kiwi_hotel(
                            hotel, currency=currency,
                            checkin=checkin, checkout=checkout,
                        ))
                except Exception:
                    continue

        deduped = deduplicate_hotels(normalized)
        return {
            "comparisons": deduped,
            "sources_checked": labels,
            "total": len(deduped),
        }

    def _extract_cheapest_amadeus(self, offers: list[dict]) -> float:
        prices = []
        for offer in offers:
            try:
                price = float(offer.get("price", {}).get("grandTotal", 0))
                if price > 0:
                    prices.append(price)
            except (ValueError, TypeError):
                continue
        return min(prices) if prices else float("inf")
