import json
from abc import ABC, abstractmethod
from typing import Any

import anthropic

from app.config import settings


class BaseAgent(ABC):
    def __init__(self):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL

    @property
    @abstractmethod
    def name(self) -> str:
        ...

    @property
    @abstractmethod
    def system_prompt(self) -> str:
        ...

    @property
    @abstractmethod
    def tools(self) -> list[dict]:
        ...

    @abstractmethod
    async def execute_tool(self, tool_name: str, tool_input: dict) -> Any:
        ...

    async def run(self, messages: list[dict], max_turns: int = 10) -> list[dict]:
        response_messages = []

        for _ in range(max_turns):
            response = await self.client.messages.create(
                model=self.model,
                max_tokens=4096,
                system=self.system_prompt,
                tools=self.tools,
                messages=messages,
            )

            assistant_message = {"role": "assistant", "content": response.content}
            messages.append(assistant_message)
            response_messages.append(assistant_message)

            if response.stop_reason == "end_turn":
                break

            if response.stop_reason == "tool_use":
                tool_results = []
                for block in response.content:
                    if block.type == "tool_use":
                        result = await self.execute_tool(block.name, block.input)
                        tool_results.append(
                            {
                                "type": "tool_result",
                                "tool_use_id": block.id,
                                "content": (
                                    json.dumps(result)
                                    if not isinstance(result, str)
                                    else result
                                ),
                            }
                        )

                user_message = {"role": "user", "content": tool_results}
                messages.append(user_message)
                response_messages.append(user_message)

        return response_messages

    async def run_streaming(self, messages: list[dict]):
        async with self.client.messages.stream(
            model=self.model,
            max_tokens=4096,
            system=self.system_prompt,
            tools=self.tools,
            messages=messages,
        ) as stream:
            async for event in stream:
                yield event
