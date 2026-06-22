from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
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
    db: Session = Depends(get_db)
):
    # Ensure session exists
    session_id = request.session_id
    if not session_id:
        new_session = ChatSession(user_id=current_user.id, repo_id=request.repo_id)
        db.add(new_session)
        db.commit()
        db.refresh(new_session)
        session_id = new_session.id
        
    # Save user message
    user_msg = ChatMessage(session_id=session_id, role="user", content=request.message)
    db.add(user_msg)
    db.commit()
    
    return StreamingResponse(
        stream_chat_response(request.repo_id, request.message, session_id, db, current_user.openai_api_key),
        media_type="text/event-stream"
    )

@router.get("/history/{repo_id}")
def get_chat_history(
    repo_id: str, 
    db: Session = Depends(get_db), 
    current_user: User = Depends(get_current_user)
):
    session = db.query(ChatSession).filter(
        ChatSession.user_id == current_user.id,
        ChatSession.repo_id == repo_id
    ).order_by(ChatSession.created_at.desc()).first()
    
    if not session:
        return {"session_id": None, "messages": []}
        
    messages = db.query(ChatMessage).filter(ChatMessage.session_id == session.id).order_by(ChatMessage.created_at.asc()).all()
    return [{"role": msg.role, "content": msg.content} for msg in messages]

@router.post("/generate-tests")
async def trigger_test_gen(request: TestGenRequest, current_user: User = Depends(get_current_user)):
    # Enqueue background task
    task = generate_tests.delay(request.repo_id, request.pr_number)
    return {"status": "accepted", "task_id": task.id}
