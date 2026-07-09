from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import List
from ...services.ai_chat import stream_chat_response
from ...tasks.test_gen import generate_tests
from ..deps import get_current_user
from ...models.domain import User, ChatSession, ChatMessage
from ...db.session import get_db

router = APIRouter()

class ChatRequest(BaseModel):
    repo_id: str
    message: str
    session_id: str = None

class TestGenRequest(BaseModel):
    repo_id: str
    pr_number: str

@router.post("/stream")
async def chat_stream(
    request: ChatRequest, 
    current_user: User = Depends(get_current_user),
    db = Depends(get_db)
):
    session_id = request.session_id
    if not session_id:
        new_session = ChatSession(user_id=current_user.id, repo_id=request.repo_id)
        await db.chat_sessions.insert_one(new_session.model_dump())
        session_id = new_session.id
        
    user_msg = ChatMessage(session_id=session_id, role="user", content=request.message)
    await db.chat_messages.insert_one(user_msg.model_dump())
    
    return StreamingResponse(
        stream_chat_response(request.repo_id, request.message, session_id, db, current_user.openai_api_key),
        media_type="text/event-stream"
    )

@router.get("/history/{repo_id}")
async def get_chat_history(
    repo_id: str, 
    db = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    session_dict = await db.chat_sessions.find_one(
        {"user_id": current_user.id, "repo_id": repo_id},
        sort=[("created_at", -1)]
    )
    
    if not session_dict:
        return {"session_id": None, "messages": []}
        
    messages_cursor = db.chat_messages.find({"session_id": session_dict["id"]}, sort=[("created_at", 1)])
    messages = await messages_cursor.to_list(length=1000)
    
    return {"session_id": session_dict["id"], "messages": [{"role": msg["role"], "content": msg["content"]} for msg in messages]}

@router.post("/generate-tests")
async def trigger_test_gen(request: TestGenRequest, current_user: User = Depends(get_current_user)):
    task = generate_tests.delay(request.repo_id, request.pr_number)
    return {"status": "accepted", "task_id": task.id}
