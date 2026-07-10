from __future__ import annotations

import json
import logging
from typing import AsyncGenerator, Optional

from openai import OpenAI

from ..core.config import settings
from ..models.domain import ChatMessage
from .rag import search_repository

logger = logging.getLogger(__name__)

# =========================================================
# CONFIG
# =========================================================

MODEL_NAME = getattr(
    settings,
    "OPENAI_MODEL",
    "gpt-4.1",
)

TOP_K = 5


# =========================================================
# CREATE CLIENT
# =========================================================

def create_client(
    user_openai_api_key: Optional[str] = None,
) -> Optional[OpenAI]:

    api_key = (
        user_openai_api_key
        or settings.OPENAI_API_KEY
    )

    if not api_key:

        logger.warning(
            "OpenAI API Key not configured."
        )

        return None

    return OpenAI(api_key=api_key)


# =========================================================
# SYSTEM PROMPT
# =========================================================

SYSTEM_PROMPT = """
You are BugMind AI Copilot.

You are an expert:

- Software Engineer
- Security Engineer
- Debugger
- Code Reviewer

Rules:

Always answer using repository context.

Never hallucinate.

If context is missing,
say so clearly.

Always explain code.

Always give clean code examples.

Always use Markdown.
"""

# =========================================================
# BUILD CONTEXT
# =========================================================

def build_context(
    repo_id: str,
    question: str,
) -> str:
    """
    Retrieve relevant repository context.
    """

    contexts = search_repository(
        repo_id=repo_id,
        query=question,
        n_results=TOP_K,
    )

    if not contexts:
        return "No relevant repository context found."

    return "\n\n".join(contexts)


# =========================================================
# STREAM CHAT RESPONSE
# =========================================================

async def stream_chat_response(
    repo_id: str,
    message: str,
    session_id: str,
    db,
    user_openai_api_key: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Stream AI response using Server-Sent Events.
    """

    client = create_client(
        user_openai_api_key
    )

    context = build_context(
        repo_id,
        message,
    )

    full_response = ""

    if client is None:

        mock = (
            "OpenAI API key not configured.\n\n"
            f"Retrieved Context:\n\n{context[:300]}"
        )

        yield f"data: {json.dumps({'content': mock})}\n\n"

        yield "data: [DONE]\n\n"

        full_response = mock

    else:

        prompt = f"""
Repository Context

{context}

-------------------------------------

User Question

{message}
"""

        try:

            stream = client.chat.completions.create(

                model=MODEL_NAME,

                messages=[
                    {
                        "role": "system",
                        "content": SYSTEM_PROMPT,
                    },
                    {
                        "role": "user",
                        "content": prompt,
                    },
                ],

                temperature=0.2,

                stream=True,
            )

            for chunk in stream:

                delta = chunk.choices[0].delta.content

                if not delta:
                    continue

                full_response += delta

                yield (
                    f"data: "
                    f"{json.dumps({'content': delta})}"
                    "\n\n"
                )

            yield "data: [DONE]\n\n"

        except Exception as ex:

            logger.exception(
                "Streaming failed."
            )

            error = str(ex)

            yield (
                f"data: "
                f"{json.dumps({'error': error})}"
                "\n\n"
            )

            yield "data: [DONE]\n\n"

            full_response = error

# =========================================================
# SAVE CHAT HISTORY
# =========================================================

async def save_chat_history(
    db,
    session_id: str,
    role: str,
    content: str,
) -> None:
    """
    Save chat message to MongoDB.
    """

    try:

        message = ChatMessage(
            session_id=session_id,
            role=role,
            content=content,
        )

        await db.chat_messages.insert_one(
            message.model_dump()
        )

    except Exception:

        logger.exception(
            "Failed to save chat history."
        )


# =========================================================
# CHAT COMPLETION WRAPPER
# =========================================================

async def chat(
    repo_id: str,
    message: str,
    session_id: str,
    db,
    user_openai_api_key: Optional[str] = None,
) -> AsyncGenerator[str, None]:
    """
    Wrapper around stream_chat_response.
    Automatically stores the conversation.
    """

    await save_chat_history(
        db=db,
        session_id=session_id,
        role="user",
        content=message,
    )

    full_response = ""

    async for event in stream_chat_response(
        repo_id=repo_id,
        message=message,
        session_id=session_id,
        db=db,
        user_openai_api_key=user_openai_api_key,
    ):

        if event.startswith("data: "):

            payload = event[6:].strip()

            if payload != "[DONE]":

                try:

                    parsed = json.loads(payload)

                    if "content" in parsed:

                        full_response += parsed["content"]

                except Exception:
                    pass

        yield event

    if full_response:

        await save_chat_history(
            db=db,
            session_id=session_id,
            role="assistant",
            content=full_response,
        )


# =========================================================
# SIMPLE NON-STREAM CHAT
# =========================================================

async def chat_once(
    repo_id: str,
    message: str,
    session_id: str,
    db,
    user_openai_api_key: Optional[str] = None,
) -> str:
    """
    Returns the complete AI response as a string.
    """

    response = ""

    async for event in chat(
        repo_id=repo_id,
        message=message,
        session_id=session_id,
        db=db,
        user_openai_api_key=user_openai_api_key,
    ):

        if not event.startswith("data: "):
            continue

        payload = event[6:].strip()

        if payload == "[DONE]":
            continue

        try:

            parsed = json.loads(payload)

            response += parsed.get(
                "content",
                "",
            )

        except Exception:
            pass

    return response


# =========================================================
# EXPORTS
# =========================================================

__all__ = [
    "chat",
    "chat_once",
    "stream_chat_response",
]