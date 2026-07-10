from __future__ import annotations

import logging
from typing import Any, Dict, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

from ...api.deps import get_current_user
from ...db.session import get_db
from ...models.domain import ChatMessage, ChatSession, User
from ...services.ai_chat import stream_chat_response
from ...tasks.test_gen import generate_tests

logger = logging.getLogger(__name__)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter()


# =========================================================
# SCHEMAS
# =========================================================

class ChatRequest(BaseModel):
    repo_id: str
    message: str
    session_id: Optional[str] = None


class TestGenRequest(BaseModel):
    repo_id: str
    pr_number: str


# =========================================================
# STREAM CHAT
# =========================================================

@router.post("/stream")
async def chat_stream(
    request: ChatRequest,
    current_user: User = Depends(get_current_user),
    db: Any = Depends(get_db),
) -> StreamingResponse:
    """
    Stream a chat response back to the client.
    """

    session_id = request.session_id

    if not session_id:
        new_session = ChatSession(
            user_id=current_user.id,
            repo_id=request.repo_id,
        )

        await db.chat_sessions.insert_one(
            new_session.model_dump()
        )
        
        session_id = new_session.id

        logger.info(
            "Created new chat session: %s for user: %s",
            session_id,
            current_user.id,
        )

    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=request.message,
    )

    await db.chat_messages.insert_one(
        user_msg.model_dump()
    )

    logger.debug(
        "Chat request saved to DB, starting stream for session: %s",
        session_id,
    )

    return StreamingResponse(
        stream_chat_response(
            repo_id=request.repo_id,
            message=request.message,
            session_id=session_id,
            db=db,
            user_openai_api_key=current_user.openai_api_key,
        ),
        media_type="text/event-stream",
    )


# =========================================================
# CHAT HISTORY
# =========================================================

@router.get("/history/{repo_id}")
async def get_chat_history(
    repo_id: str,
    db: Any = Depends(get_db),
    current_user: User = Depends(get_current_user),
) -> Dict[str, Any]:
    """
    Retrieve chat history for a specific repository.
    """

    session_dict = await db.chat_sessions.find_one(
        {
            "user_id": current_user.id,
            "repo_id": repo_id
        },
        sort=[("created_at", -1)]
    )

    if not session_dict:
        return {
            "session_id": None,
            "messages": []
        }

    messages_cursor = db.chat_messages.find(
        {
            "session_id": session_dict["id"]
        },
        sort=[("created_at", 1)]
    )
    
    messages = await messages_cursor.to_list(length=1000)

    formatted_messages = [
        {
            "role": msg["role"],
            "content": msg["content"]
        }
        for msg in messages
    ]

    return {
        "session_id": session_dict["id"],
        "messages": formatted_messages,
    }


# =========================================================
# TEST GENERATION
# =========================================================

@router.post("/generate-tests")
async def trigger_test_gen(
    request: TestGenRequest,
    current_user: User = Depends(get_current_user),
) -> Dict[str, str]:
    """
    Trigger a background task to generate tests.
    """

    logger.info(
        "Triggering test generation for repo: %s, PR: %s",
        request.repo_id,
        request.pr_number,
    )

    task = generate_tests.delay(
        request.repo_id,
        request.pr_number,
    )

    return {
        "status": "accepted",
        "task_id": task.id,
    }

