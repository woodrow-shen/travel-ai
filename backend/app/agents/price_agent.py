import logging
from typing import Any

from app.agents.base import BaseAgent
from app.agents.tools.price_tools import PRICE_TOOLS
from app.clients.amadeus_client import AmadeusClient

logger = logging.getLogger(__name__)


class PriceAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self.amadeus = AmadeusClient()

    @property
    def name(self) -> str:
        return "price"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a price comparison specialist. Your job is to compare prices across "
            "multiple sources for flights and hotels, and analyze price trends using "
            "historical data. Identify the best deals and present clear comparisons."
        )

    @property
    def tools(self) -> list[dict]:
        return PRICE_TOOLS

    async def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "compare_prices":
            return await self._compare_prices(tool_input)
        elif tool_name == "get_price_history":
            return await self._get_price_history(tool_input)
        return {"error": f"Unknown tool: {tool_name}"}

    async def _compare_prices(self, params: dict) -> dict:
        item_type = params["item_type"]
        search_params = params["search_params"]

        if item_type == "flight":
            origin = search_params.get("origin", "")
            destination = search_params.get("destination", "")
            date = search_params.get("date", "")

            amadeus_raw = await self.amadeus.search_flights(
                origin=origin, destination=destination, departure_date=date
            )

            sources = []
            if isinstance(amadeus_raw, list) and amadeus_raw:
                sources.append({
                    "name": "amadeus",
                    "results_count": len(amadeus_raw),
                    "cheapest": self._extract_cheapest_amadeus(amadeus_raw),
                })

            return {
                "comparisons": sources,
                "sources_checked": [s["name"] for s in sources],
                "best_source": sources[0]["name"] if sources else None,
            }

        return {"comparisons": [], "sources_checked": []}

    async def _get_price_history(self, params: dict) -> dict:
        # Would query price_history table in a real implementation
        return {
            "origin": params["origin"],
            "destination": params["destination"],
            "days_back": params.get("days_back", 90),
            "history": [],
            "average": 0,
            "min": 0,
            "max": 0,
            "trend": "insufficient_data",
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
