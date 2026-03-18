import logging
import math
from typing import Any

from app.agents.base import BaseAgent
from app.agents.tools.itinerary_tools import ITINERARY_TOOLS

logger = logging.getLogger(__name__)


class ItineraryAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "itinerary"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a travel itinerary specialist. Your job is to create detailed "
            "day-by-day travel itineraries including activities, restaurants, transportation, "
            "and timing. Optimize routes to minimize travel time between locations."
            + self.locale_instruction
        )

    @property
    def tools(self) -> list[dict]:
        return ITINERARY_TOOLS

    async def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "create_itinerary":
            return await self._create_itinerary(tool_input)
        elif tool_name == "optimize_route":
            return await self._optimize_route(tool_input)
        return {"error": f"Unknown tool: {tool_name}"}

    async def _create_itinerary(self, params: dict) -> dict:
        destination = params["destination"]
        start_date = params["start_date"]
        end_date = params["end_date"]
        interests = params.get("interests", [])
        budget_level = params.get("budget_level", "mid")

        # Calculate number of days
        from datetime import date

        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        total_days = (end - start).days + 1

        # Generate a skeleton itinerary
        # In production, the Claude API call (via BaseAgent.run) would generate this
        days = []
        for i in range(total_days):
            current = start.isoformat()
            day = {
                "day": i + 1,
                "date": current,
                "activities": [
                    {
                        "time": "09:00",
                        "type": "activity",
                        "name": f"Explore {destination} - Day {i + 1} morning",
                        "duration_minutes": 120,
                    },
                    {
                        "time": "12:00",
                        "type": "meal",
                        "name": "Lunch",
                        "duration_minutes": 60,
                    },
                    {
                        "time": "14:00",
                        "type": "activity",
                        "name": f"Explore {destination} - Day {i + 1} afternoon",
                        "duration_minutes": 180,
                    },
                    {
                        "time": "18:00",
                        "type": "meal",
                        "name": "Dinner",
                        "duration_minutes": 90,
                    },
                ],
            }
            days.append(day)
            start = start.__class__.fromisoformat(
                (
                    start.__class__.fromisoformat(current)
                    + __import__("datetime").timedelta(days=1)
                ).isoformat()
            )

        return {
            "destination": destination,
            "total_days": total_days,
            "budget_level": budget_level,
            "interests": interests,
            "days": days,
        }

    async def _optimize_route(self, params: dict) -> dict:
        locations = params.get("locations", [])
        if len(locations) <= 2:
            return {"optimized_order": locations, "saved_minutes": 0}

        # Simple nearest-neighbor TSP approximation
        remaining = list(range(len(locations)))
        order = [remaining.pop(0)]

        while remaining:
            last = order[-1]
            nearest = min(
                remaining,
                key=lambda i: self._distance(locations[last], locations[i]),
            )
            order.append(nearest)
            remaining.remove(nearest)

        optimized = [locations[i] for i in order]

        # Estimate savings (rough approximation)
        original_dist = sum(
            self._distance(locations[i], locations[i + 1])
            for i in range(len(locations) - 1)
        )
        optimized_dist = sum(
            self._distance(optimized[i], optimized[i + 1])
            for i in range(len(optimized) - 1)
        )

        # Convert distance savings to approximate minutes (assuming 30 km/h avg)
        saved_km = max(0, original_dist - optimized_dist)
        saved_minutes = int(saved_km / 30 * 60)

        return {"optimized_order": optimized, "saved_minutes": saved_minutes}

    def _distance(self, loc1: dict, loc2: dict) -> float:
        lat1 = loc1.get("lat", 0)
        lng1 = loc1.get("lng", 0)
        lat2 = loc2.get("lat", 0)
        lng2 = loc2.get("lng", 0)
        # Haversine approximation (in km)
        dlat = math.radians(lat2 - lat1)
        dlng = math.radians(lng2 - lng1)
        a = math.sin(dlat / 2) ** 2 + math.cos(math.radians(lat1)) * math.cos(
            math.radians(lat2)
        ) * math.sin(dlng / 2) ** 2
        return 6371 * 2 * math.asin(math.sqrt(a))
