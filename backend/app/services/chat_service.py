import logging
from collections.abc import AsyncGenerator

from app.agents.coordinator import CoordinatorAgent
from app.models.chat_session import ChatSession
from app.models.user import User

logger = logging.getLogger(__name__)


class ChatService:
    def __init__(self):
        self.coordinator = CoordinatorAgent()

    async def stream_response(
        self, message: str, session: ChatSession, user: User
    ) -> AsyncGenerator[tuple[str, str | dict], None]:
        # Build conversation history from session
        messages = []
        if session.messages:
            for msg in session.messages:
                messages.append(msg)

        # Add the new user message
        messages.append({"role": "user", "content": message})

        try:
            # Run the coordinator agent
            response_messages = await self.coordinator.run(messages)

            # Extract text and data from agent response
            for msg in response_messages:
                if msg["role"] == "assistant":
                    for block in msg["content"]:
                        if hasattr(block, "text") and block.text:
                            yield "text", block.text
                        elif hasattr(block, "type") and block.type == "tool_use":
                            # Emit structured data for tool calls
                            yield "data", {
                                "tool": block.name,
                                "input": block.input,
                            }

            # Update session messages with conversation history
            session.messages = messages + response_messages

        except Exception:
            logger.exception("Error in chat stream")
            yield "text", (
                "I'm sorry, I encountered an error processing your request. "
                "Please try again."
            )

        yield "done", ""
