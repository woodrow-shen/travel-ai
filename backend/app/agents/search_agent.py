import asyncio
import logging
from datetime import datetime
from typing import Any

from app.agents.base import BaseAgent
from app.agents.tools.flight_tools import FLIGHT_TOOLS
from app.agents.tools.hotel_tools import HOTEL_TOOLS
from app.clients.amadeus_client import AmadeusClient
from app.clients.google_flights_client import GoogleFlightsClient
from app.clients.kiwi_client import KiwiClient
from app.clients.normalizer import (
    deduplicate_flights,
    normalize_amadeus_flight,
    normalize_google_flights_flight,
    normalize_kiwi_flight,
    normalize_skyscanner_flight,
)
from app.clients.skyscanner_client import SkyscannerClient
from app.lib.currency import get_exchange_rates

logger = logging.getLogger(__name__)

GATEWAY_HUBS = {
    "JP": {"hubs": ["NRT", "HND", "KIX", "NGO"], "name": "Japan"},
    "KR": {"hubs": ["ICN", "GMP"], "name": "South Korea"},
    "TH": {"hubs": ["BKK", "DMK"], "name": "Thailand"},
    "ID": {"hubs": ["CGK"], "name": "Indonesia"},
}

AIRPORT_COUNTRY = {
    "FKS": "JP", "CTS": "JP", "SDJ": "JP", "OKA": "JP", "KMQ": "JP",
    "HIJ": "JP", "FUK": "JP", "KOJ": "JP", "NGS": "JP", "OIT": "JP",
    "MYJ": "JP", "TAK": "JP", "KMI": "JP", "AOJ": "JP", "AXT": "JP",
    "PUS": "KR", "CJU": "KR", "TAE": "KR",
    "CNX": "TH", "HKT": "TH", "USM": "TH", "KBV": "TH",
    "DPS": "ID", "JOG": "ID", "SUB": "ID",
}

FOREIGNER_DISCOUNTS = {
    "JP": {
        "NH": {"name": "Experience JAPAN Fare", "price": 5500, "currency": "JPY"},
        "JL": {"name": "Japan Explorer Pass", "price": 5500, "currency": "JPY"},
    },
}


class SearchAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.amadeus = AmadeusClient()
        self.skyscanner = SkyscannerClient()
        self.kiwi = KiwiClient()
        self.google_flights = GoogleFlightsClient()

    @property
    def name(self) -> str:
        return "search"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a travel search specialist. Your job is to search for flights and hotels "
            "based on user requirements. Use the available tools to find options. "
            "When searching for destinations without direct international "
            "flights, use multi-segment search: find gateway hubs, search "
            "international + domestic segments, and combine them. For Japan "
            "domestic flights, always check for foreigner discount fares "
            "(ANA Experience JAPAN Fare ~\u00a55,500, "
            "JAL Japan Explorer Pass ~\u00a55,500)."
        )

    @property
    def tools(self) -> list[dict]:
        return FLIGHT_TOOLS + HOTEL_TOOLS

    async def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "search_flights":
            return await self._search_flights(tool_input)
        elif tool_name == "search_hotels":
            return await self._search_hotels(tool_input)
        elif tool_name == "search_domestic_flights":
            return await self._search_domestic_flights(tool_input)
        elif tool_name == "resolve_gateway_hubs":
            return await self._resolve_gateway_hubs(tool_input)
        elif tool_name == "combine_segments":
            return await self._combine_segments(tool_input)
        return {"error": f"Unknown tool: {tool_name}"}

    async def _search_flights(self, params: dict) -> dict:
        origin = params["origin"]
        destination = params["destination"]
        departure_date = params["date_from"]
        return_date = params.get("date_to")
        passengers = params.get("passengers", 1)
        cabin_class = params.get("cabin_class")
        max_stops = params.get("max_stops")

        # Multi-source parallel search
        results = await asyncio.gather(
            self.amadeus.search_flights(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=passengers,
                cabin_class=cabin_class,
                max_stops=max_stops,
            ),
            self.skyscanner.search_flights(
                origin_sky_id=origin,
                destination_sky_id=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=passengers,
            ),
            self.kiwi.search_flights(
                origin_sky_id=origin,
                destination_sky_id=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=passengers,
            ),
            self.google_flights.search_flights(
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                adults=passengers,
            ),
            get_exchange_rates("EUR"),
            return_exceptions=True,
        )
        amadeus_raw, skyscanner_raw, kiwi_raw, google_flights_raw, rates_raw = results
        exchange_rates = (
            rates_raw if isinstance(rates_raw, dict) else {}
        )

        # Normalize all sources
        normalized: list[dict] = []
        sources_used: list[str] = []

        if isinstance(amadeus_raw, list) and amadeus_raw:
            sources_used.append("amadeus")
            for offer in amadeus_raw:
                try:
                    normalized.append(
                        normalize_amadeus_flight(
                            offer, exchange_rates=exchange_rates
                        )
                    )
                except Exception:
                    logger.debug("Normalize Amadeus failed", exc_info=True)
        elif isinstance(amadeus_raw, BaseException):
            logger.warning("Amadeus search failed: %s", amadeus_raw)

        if isinstance(skyscanner_raw, list) and skyscanner_raw:
            sources_used.append("skyscanner")
            for itin in skyscanner_raw:
                try:
                    normalized.append(
                        normalize_skyscanner_flight(
                            itin, origin=origin, destination=destination
                        )
                    )
                except Exception:
                    logger.debug("Normalize Skyscanner failed", exc_info=True)
        elif isinstance(skyscanner_raw, BaseException):
            logger.warning("Skyscanner search failed: %s", skyscanner_raw)

        if isinstance(kiwi_raw, list) and kiwi_raw:
            sources_used.append("kiwi")
            for itin in kiwi_raw:
                try:
                    normalized.append(normalize_kiwi_flight(itin))
                except Exception:
                    logger.debug("Normalize Kiwi failed", exc_info=True)
        elif isinstance(kiwi_raw, BaseException):
            logger.warning("Kiwi search failed: %s", kiwi_raw)

        if isinstance(google_flights_raw, list) and google_flights_raw:
            sources_used.append("google_flights")
            for itin in google_flights_raw:
                try:
                    normalized.append(normalize_google_flights_flight(itin))
                except Exception:
                    logger.debug("Normalize Google Flights failed", exc_info=True)
        elif isinstance(google_flights_raw, BaseException):
            logger.warning("Google Flights search failed: %s", google_flights_raw)

        deduped = deduplicate_flights(normalized)
        deduped.sort(key=lambda f: f.get("price", float("inf")))

        return {
            "flights": deduped,
            "total": len(deduped),
            "sources": sources_used,
        }

    async def _search_hotels(self, params: dict) -> dict:
        # Hotel API integration placeholder
        return {"hotels": [], "total": 0, "source": "booking"}

    async def _search_domestic_flights(self, params: dict) -> dict:
        country = params["country"]
        origin = params["origin"]
        destination = params["destination"]
        date = params["date"]

        # Use Amadeus for domestic flight search
        results = await self.amadeus.search_flights(
            origin=origin,
            destination=destination,
            departure_date=date,
            max_results=10,
        )

        # Check for foreigner discount availability
        discounts = FOREIGNER_DISCOUNTS.get(country, {})
        flights = []
        for offer in results:
            segments = offer.get("itineraries", [{}])[0].get("segments", [{}])
            airline = segments[0].get("carrierCode", "") if segments else ""
            flight_data = {
                "source": "amadeus",
                "data": offer,
                "airline": airline,
            }
            if airline in discounts:
                flight_data["foreigner_discount"] = discounts[airline]
            flights.append(flight_data)

        return {
            "flights": flights,
            "total": len(flights),
            "foreigner_discounts_available": bool(discounts),
            "available_discounts": discounts,
        }

    async def _resolve_gateway_hubs(self, params: dict) -> dict:
        destination = params["destination"]
        country = AIRPORT_COUNTRY.get(destination)
        if country and country in GATEWAY_HUBS:
            hub_info = GATEWAY_HUBS[country]
            return {
                "destination": destination,
                "country": country,
                "country_name": hub_info["name"],
                "gateway_hubs": hub_info["hubs"],
                "needs_multi_segment": True,
            }
        return {"destination": destination, "needs_multi_segment": False}

    async def _combine_segments(self, params: dict) -> dict:
        international = params.get("international_flights", [])
        domestic = params.get("domestic_flights", [])
        min_layover = params.get("min_layover_minutes", 120)
        max_layover = params.get("max_layover_minutes", 360)

        combinations = []
        for intl in international:
            for dom in domestic:
                # Calculate layover time
                intl_arrival = intl.get("arrival")
                dom_departure = dom.get("departure")

                if intl_arrival and dom_departure:
                    try:
                        arr_time = datetime.fromisoformat(intl_arrival)
                        dep_time = datetime.fromisoformat(dom_departure)
                        layover_mins = (dep_time - arr_time).total_seconds() / 60

                        if min_layover <= layover_mins <= max_layover:
                            intl_price = intl.get("price", 0)
                            dom_price = dom.get("price", 0)
                            combinations.append({
                                "international": intl,
                                "domestic": dom,
                                "layover_minutes": int(layover_mins),
                                "total_price": intl_price + dom_price,
                                "same_airport": intl.get("destination") == dom.get("origin"),
                            })
                    except (ValueError, TypeError):
                        continue

        # Sort: same airport first, then by total price
        combinations.sort(key=lambda c: (not c["same_airport"], c["total_price"]))

        return {"combinations": combinations, "total": len(combinations)}
