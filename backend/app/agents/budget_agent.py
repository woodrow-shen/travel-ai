import logging
from typing import Any

from app.agents.base import BaseAgent
from app.agents.tools.budget_tools import BUDGET_TOOLS

logger = logging.getLogger(__name__)

# Daily cost estimates by destination and budget level (TWD)
DAILY_COSTS = {
    "default": {"budget": 2000, "mid": 5000, "luxury": 15000},
    "JP": {"budget": 3000, "mid": 7000, "luxury": 20000},
    "KR": {"budget": 2500, "mid": 5500, "luxury": 15000},
    "TH": {"budget": 1500, "mid": 3500, "luxury": 12000},
    "ID": {"budget": 1200, "mid": 3000, "luxury": 10000},
    "US": {"budget": 4000, "mid": 8000, "luxury": 25000},
    "EU": {"budget": 3500, "mid": 7500, "luxury": 22000},
}


class BudgetAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "budget"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a travel budget specialist. Your job is to estimate trip costs "
            "and find budget-friendly alternatives. Consider flights, hotels, activities, "
            "food, transportation, and other daily expenses."
            + self.locale_instruction
        )

    @property
    def tools(self) -> list[dict]:
        return BUDGET_TOOLS

    async def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "estimate_costs":
            return await self._estimate_costs(tool_input)
        elif tool_name == "find_alternatives":
            return await self._find_alternatives(tool_input)
        return {"error": f"Unknown tool: {tool_name}"}

    async def _estimate_costs(self, params: dict) -> dict:
        destination = params["destination"]
        days = params["days"]
        travelers = params.get("travelers", 1)
        budget_level = params.get("budget_level", "mid")

        # Determine country code from destination (simplified lookup)
        country = destination[:2].upper() if len(destination) == 2 else "default"
        daily = DAILY_COSTS.get(country, DAILY_COSTS["default"])
        daily_cost = daily.get(budget_level, daily["mid"])

        accommodation = daily_cost * 0.4 * days * travelers
        food = daily_cost * 0.25 * days * travelers
        transport = daily_cost * 0.15 * days * travelers
        activities = daily_cost * 0.15 * days * travelers
        misc = daily_cost * 0.05 * days * travelers
        total = accommodation + food + transport + activities + misc

        return {
            "destination": destination,
            "days": days,
            "travelers": travelers,
            "budget_level": budget_level,
            "currency": "TWD",
            "total": round(total),
            "breakdown": {
                "accommodation": round(accommodation),
                "food": round(food),
                "local_transport": round(transport),
                "activities": round(activities),
                "miscellaneous": round(misc),
            },
            "note": "Estimate excludes international flights. Actual costs may vary.",
        }

    async def _find_alternatives(self, params: dict) -> dict:
        item_type = params["item_type"]
        current = params["current_option"]
        suggestions = []

        if item_type == "flight":
            suggestions = [
                {"tip": "Try flexible dates (±3 days) for lower fares"},
                {"tip": "Consider nearby airports as alternatives"},
                {"tip": "Check budget airlines for the same route"},
                {"tip": "Book 6-8 weeks in advance for best prices"},
            ]
        elif item_type == "hotel":
            suggestions = [
                {"tip": "Consider hostels or guesthouses for budget stays"},
                {"tip": "Look for apartments on longer stays (better daily rate)"},
                {"tip": "Stay slightly outside city center for lower prices"},
                {"tip": "Check for last-minute deals"},
            ]
        elif item_type == "activity":
            suggestions = [
                {"tip": "Look for free walking tours"},
                {"tip": "Check for city passes that bundle activities"},
                {"tip": "Visit museums on free admission days"},
            ]

        return {
            "item_type": item_type,
            "current_option": current,
            "alternatives": [],  # Would be populated from actual search
            "suggestions": suggestions,
            "savings": 0,
        }
