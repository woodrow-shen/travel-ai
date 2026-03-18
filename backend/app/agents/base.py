import json
from abc import ABC, abstractmethod
from typing import Any

import anthropic

from app.config import settings


class BaseAgent(ABC):
    def __init__(self, locale: str = "zh-TW"):
        self.client = anthropic.AsyncAnthropic(api_key=settings.ANTHROPIC_API_KEY)
        self.model = settings.ANTHROPIC_MODEL
        self.locale = locale

    LOCALE_INSTRUCTIONS: dict[str, str] = {
        "en": (
            "\n\nRespond in English."
            " Use TWD for prices unless the user specifies otherwise."
        ),
        "ja": (
            "\n\n日本語で回答してください。"
            "価格は特に指定がない限りTWDを使用してください。"
        ),
        "ko": (
            "\n\n한국어로 답변해 주세요."
            " 가격은 사용자가 별도로 지정하지 않는 한 TWD를 사용해 주세요."
        ),
        "es": (
            "\n\nResponde en español. Usa TWD para los precios"
            " a menos que el usuario indique lo contrario."
        ),
        "fr": (
            "\n\nRépondez en français. Utilisez TWD pour les"
            " prix sauf indication contraire de l'utilisateur."
        ),
        "de": (
            "\n\nAntworten Sie auf Deutsch. Verwenden Sie TWD"
            " für Preise, es sei denn, der Benutzer gibt"
            " etwas anderes an."
        ),
        "th": (
            "\n\nกรุณาตอบเป็นภาษาไทย"
            " ใช้สกุลเงิน TWD สำหรับราคา"
            " เว้นแต่ผู้ใช้จะระบุเป็นอย่างอื่น"
        ),
        "vi": (
            "\n\nVui lòng trả lời bằng tiếng Việt."
            " Sử dụng TWD cho giá cả"
            " trừ khi người dùng chỉ định khác."
        ),
        "zh-CN": (
            "\n\n请用简体中文回复。"
            "价格请使用新台币（TWD），除非用户另有指定。"
        ),
        "pt-BR": (
            "\n\nResponda em português brasileiro."
            " Use TWD para preços, a menos que o usuário"
            " especifique o contrário."
        ),
        "it": (
            "\n\nRispondi in italiano. Usa TWD per i prezzi"
            " a meno che l'utente non specifichi diversamente."
        ),
    }

    @property
    def locale_instruction(self) -> str:
        return self.LOCALE_INSTRUCTIONS.get(
            self.locale,
            "\n\n請用繁體中文回覆。價格請使用新台幣（TWD），除非使用者另有指定。",
        )

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
