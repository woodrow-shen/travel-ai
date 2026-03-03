from typing import Any

import pytest

from app.agents.base import BaseAgent


class ConcreteAgent(BaseAgent):
    @property
    def name(self) -> str:
        return "test"

    @property
    def system_prompt(self) -> str:
        return "You are a test agent."

    @property
    def tools(self) -> list[dict]:
        return [
            {
                "name": "test_tool",
                "description": "A test tool",
                "input_schema": {
                    "type": "object",
                    "properties": {"input": {"type": "string"}},
                    "required": ["input"],
                },
            }
        ]

    async def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        if tool_name == "test_tool":
            return {"result": f"processed: {tool_input['input']}"}
        return {"error": "unknown tool"}


def test_base_agent_is_abstract():
    with pytest.raises(TypeError):
        BaseAgent()


def test_concrete_agent_instantiation():
    agent = ConcreteAgent()
    assert agent.name == "test"
    assert agent.system_prompt == "You are a test agent."
    assert len(agent.tools) == 1
    assert agent.tools[0]["name"] == "test_tool"


async def test_execute_tool():
    agent = ConcreteAgent()
    result = await agent.execute_tool("test_tool", {"input": "hello"})
    assert result == {"result": "processed: hello"}


async def test_execute_unknown_tool():
    agent = ConcreteAgent()
    result = await agent.execute_tool("unknown", {})
    assert result == {"error": "unknown tool"}
