import json

from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.dependencies import get_current_user
from app.models.chat_session import ChatSession
from app.models.user import User
from app.schemas.chat import ChatRequest
from app.services.chat_service import ChatService

router = APIRouter()


@router.post("")
async def chat(
    body: ChatRequest,
    user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if body.session_id:
        result = await db.execute(
            select(ChatSession).where(
                ChatSession.id == body.session_id, ChatSession.user_id == user.id
            )
        )
        session = result.scalar_one_or_none()
    else:
        session = ChatSession(user_id=user.id, title=body.message[:100], messages=[])
        db.add(session)
        await db.flush()

    service = ChatService()

    async def event_stream():
        async for event_type, data in service.stream_response(body.message, session, user):
            if event_type == "text":
                yield f"event: text\ndata: {json.dumps({'content': data})}\n\n"
            elif event_type == "data":
                yield f"event: data\ndata: {json.dumps(data)}\n\n"
            elif event_type == "done":
                yield f"event: done\ndata: {json.dumps({'session_id': str(session.id)})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )
