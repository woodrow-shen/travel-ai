import asyncio
import json
from typing import Any

from app.agents.base import BaseAgent
from app.agents.budget_agent import BudgetAgent
from app.agents.itinerary_agent import ItineraryAgent
from app.agents.price_agent import PriceAgent
from app.agents.recommendation_agent import RecommendationAgent
from app.agents.search_agent import SearchAgent

COORDINATOR_TOOLS = [
    {
        "name": "dispatch_search",
        "description": "Dispatch search task to the Search Agent. Use for flight/hotel searches.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string", "description": "Description of what to search for"},
                "params": {"type": "object", "description": "Search parameters"},
            },
            "required": ["task", "params"],
        },
    },
    {
        "name": "dispatch_price",
        "description": "Dispatch price comparison task to the Price Agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string"},
                "params": {"type": "object"},
            },
            "required": ["task", "params"],
        },
    },
    {
        "name": "dispatch_recommend",
        "description": "Dispatch recommendation task to the Recommendation Agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string"},
                "params": {"type": "object"},
            },
            "required": ["task", "params"],
        },
    },
    {
        "name": "dispatch_itinerary",
        "description": "Dispatch itinerary generation task to the Itinerary Agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string"},
                "params": {"type": "object"},
            },
            "required": ["task", "params"],
        },
    },
    {
        "name": "dispatch_budget",
        "description": "Dispatch budget estimation task to the Budget Agent.",
        "input_schema": {
            "type": "object",
            "properties": {
                "task": {"type": "string"},
                "params": {"type": "object"},
            },
            "required": ["task", "params"],
        },
    },
    {
        "name": "dispatch_parallel",
        "description": "Dispatch multiple agent tasks in parallel for faster results.",
        "input_schema": {
            "type": "object",
            "properties": {
                "tasks": {
                    "type": "array",
                    "items": {
                        "type": "object",
                        "properties": {
                            "agent": {
                                "type": "string",
                                "enum": [
                                    "search",
                                    "price",
                                    "recommend",
                                    "itinerary",
                                    "budget",
                                ],
                            },
                            "task": {"type": "string"},
                            "params": {"type": "object"},
                        },
                        "required": ["agent", "task", "params"],
                    },
                },
            },
            "required": ["tasks"],
        },
    },
]


class CoordinatorAgent(BaseAgent):
    def __init__(self):
        super().__init__()
        self._agents = {
            "search": SearchAgent(),
            "price": PriceAgent(),
            "recommend": RecommendationAgent(),
            "itinerary": ItineraryAgent(),
            "budget": BudgetAgent(),
        }

    @property
    def name(self) -> str:
        return "coordinator"

    @property
    def system_prompt(self) -> str:
        return (
            "You are the Travel-AI coordinator. You receive user travel queries "
            "in natural language and orchestrate specialist agents to fulfill "
            "them.\n\n"
            "Available agents:\n"
            "- search: Find flights, hotels, activities\n"
            "- price: Compare prices across sources, analyze price history\n"
            "- recommend: Personalized recommendations based on user preferences\n"
            "- itinerary: Generate day-by-day travel schedules\n"
            "- budget: Estimate costs and find alternatives\n\n"
            "Workflow:\n"
            "1. Parse user intent from their message\n"
            "2. Dispatch to appropriate agent(s) — use dispatch_parallel "
            "when tasks are independent\n"
            "3. Synthesize results into a helpful, conversational response\n\n"
            "Always respond in the same language as the user's query."
        )

    @property
    def tools(self) -> list[dict]:
        return COORDINATOR_TOOLS

    async def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "dispatch_parallel":
            return await self._dispatch_parallel(tool_input["tasks"])

        agent_map = {
            "dispatch_search": "search",
            "dispatch_price": "price",
            "dispatch_recommend": "recommend",
            "dispatch_itinerary": "itinerary",
            "dispatch_budget": "budget",
        }

        agent_name = agent_map.get(tool_name)
        if agent_name is None:
            return {"error": f"Unknown tool: {tool_name}"}

        return await self._dispatch_single(agent_name, tool_input)

    async def _dispatch_single(self, agent_name: str, params: dict) -> dict:
        agent = self._agents[agent_name]
        messages = [{"role": "user", "content": json.dumps(params)}]
        result = await agent.run(messages)
        # Extract text content from the last assistant message
        for msg in reversed(result):
            if msg["role"] == "assistant":
                for block in msg["content"]:
                    if hasattr(block, "text"):
                        return {"agent": agent_name, "result": block.text}
        return {"agent": agent_name, "result": "No response from agent"}

    async def _dispatch_parallel(self, tasks: list[dict]) -> list[dict]:
        coros = [
            self._dispatch_single(task["agent"], {"task": task["task"], "params": task["params"]})
            for task in tasks
        ]
        results = await asyncio.gather(*coros, return_exceptions=True)
        return [
            r if isinstance(r, dict) else {"error": str(r)}
            for r in results
        ]
