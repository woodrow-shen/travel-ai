import logging
import uuid
from typing import Any

from sqlalchemy import select

from app.agents.base import BaseAgent
from app.agents.tools.recommendation_tools import RECOMMENDATION_TOOLS
from app.db.session import async_session_factory
from app.models.user import UserPreference

logger = logging.getLogger(__name__)

# Simplified airline ratings (Skytrax-inspired, 1-5 scale)
AIRLINE_RATINGS = {
    "SQ": 5.0, "NH": 4.8, "CX": 4.7, "JL": 4.7, "BR": 4.5,
    "TG": 4.2, "CI": 4.0, "JX": 4.3, "KE": 4.3, "OZ": 4.2,
    "GA": 3.8, "VJ": 3.2, "MM": 3.0, "TR": 3.3,
}

# Widebody aircraft patterns (more comfortable on long flights)
WIDEBODY_PATTERNS = ["787", "777", "A350", "A380", "A330", "767", "747"]


class RecommendationAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "recommendation"

    @property
    def system_prompt(self) -> str:
        return (
            "You are a travel recommendation specialist. Your job is to provide personalized "
            "recommendations based on user preferences, reviews, and quality scores. "
            "For direct flight mode, score flights based on: airline rating, departure time "
            "reasonableness, flight duration, aircraft comfort, and price (as secondary factor)."
            + self.locale_instruction
        )

    @property
    def tools(self) -> list[dict]:
        return RECOMMENDATION_TOOLS

    async def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "get_user_preferences":
            return await self._get_user_preferences(tool_input)
        elif tool_name == "analyze_reviews":
            return await self._analyze_reviews(tool_input)
        return {"error": f"Unknown tool: {tool_name}"}

    async def _get_user_preferences(self, params: dict) -> dict:
        user_id_str = params.get("user_id")
        if not user_id_str:
            return {
                "user_id": None,
                "preferences": {},
                "note": "No user_id provided",
            }

        try:
            user_uuid = uuid.UUID(user_id_str)
        except (ValueError, TypeError):
            return {
                "user_id": user_id_str,
                "preferences": {},
                "note": "Invalid user_id format",
            }

        async with async_session_factory() as db:
            stmt = select(UserPreference).where(UserPreference.user_id == user_uuid)
            result = await db.execute(stmt)
            pref = result.scalar_one_or_none()

        if not pref:
            return {
                "user_id": user_id_str,
                "preferences": {},
                "note": "No preferences set",
            }

        return {
            "user_id": user_id_str,
            "preferences": {
                "preferred_airlines": pref.preferred_airlines or [],
                "excluded_airlines": pref.excluded_airlines or [],
                "preferred_alliances": pref.preferred_alliances or [],
                "cabin_classes": pref.cabin_classes or [],
                "max_stops": pref.max_stops,
                "home_airports": pref.home_airports or [],
            },
        }

    async def _analyze_reviews(self, params: dict) -> dict:
        item_type = params["item_type"]
        item_id = params["item_id"]

        if item_type == "airline":
            rating = AIRLINE_RATINGS.get(item_id, 3.5)
            highlights = []

            if rating >= 4.5:
                highlights.append("Top-rated airline")
            if rating >= 4.0:
                highlights.append("Excellent service")
            if item_id in ("NH", "JL", "SQ", "CX"):
                highlights.append("Award-winning")

            return {
                "item_type": "airline",
                "item_id": item_id,
                "score": rating,
                "max_score": 5.0,
                "review_count": 0,  # Would come from real review data
                "highlights": highlights,
            }

        elif item_type == "hotel":
            return {
                "item_type": "hotel",
                "item_id": item_id,
                "score": 0,
                "max_score": 5.0,
                "review_count": 0,
                "highlights": [],
            }

        return {"error": f"Unknown item type: {item_type}"}
