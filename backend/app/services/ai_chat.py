import json
from openai import OpenAI
from ..core.config import settings
from .rag import retrieve_context
from ..models.domain import ChatMessage

async def stream_chat_response(repo_id: str, message: str, session_id: str, db, user_openai_api_key: str = None):
    """Yields streaming chunks of AI response using Server-Sent Events, and persists history."""
    
    api_key = user_openai_api_key or settings.OPENAI_API_KEY
    client = OpenAI(api_key=api_key) if api_key else None
    
    context = retrieve_context(repo_id, message, n_results=3)
    context_text = "\n\n".join(context) if context else "No relevant code context found."
    
    full_ai_response = ""
    
    if not client:
        full_ai_response = f"[Mock Mode] OPENAI_API_KEY is not set. I retrieved the following context: {context_text[:100]}... How else can I help you?"
        yield f"data: {json.dumps({'content': '[Mock Mode] OPENAI_API_KEY is not set. '})}\n\n"
        yield f"data: {json.dumps({'content': f'I retrieved the following context: {context_text[:100]}... '})}\n\n"
        yield f"data: {json.dumps({'content': 'How else can I help you?'})}\n\n"
        yield "data: [DONE]\n\n"
    else:
        system_prompt = (
            "You are BugMind AI Copilot, an elite programming assistant. "
            "Use the provided codebase context to answer the user's question with precise, "
            "actionable advice, and always format your code examples beautifully."
        )
        prompt = f"Codebase Context:\n{context_text}\n\nUser Question:\n{message}"
        
        try:
            response = client.chat.completions.create(
                model="gpt-4o",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                stream=True
            )
            
            for chunk in response:
                if chunk.choices and chunk.choices[0].delta.content:
                    content_piece = chunk.choices[0].delta.content
                    full_ai_response += content_piece
                    yield f"data: {json.dumps({'content': content_piece})}\n\n"
                    
            yield "data: [DONE]\n\n"
        except Exception as e:
            yield f"data: {json.dumps({'error': str(e)})}\n\n"
            yield "data: [DONE]\n\n"
            full_ai_response += f"[Error: {str(e)}]"

    ai_msg = ChatMessage(session_id=session_id, role="ai", content=full_ai_response)
    await db.chat_messages.insert_one(ai_msg.model_dump())
