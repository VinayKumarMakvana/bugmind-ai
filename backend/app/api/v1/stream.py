from __future__ import annotations

import asyncio
import json
import logging
from typing import AsyncGenerator, Dict, Any

from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse

from ...core.events import event_manager

logger = logging.getLogger(__name__)


# =========================================================
# ROUTER
# =========================================================

router = APIRouter()


# =========================================================
# SSE ENDPOINT
# =========================================================

@router.get("/events")
async def sse_endpoint(request: Request) -> EventSourceResponse:
    """
    Subscribe to real-time events via Server-Sent Events (SSE).
    """

    async def event_generator() -> AsyncGenerator[Dict[str, Any], None]:
        try:
            # Send initial connection message
            yield {
                "event": "connected",
                "data": json.dumps({"message": "Subscribed to real-time events"}),
            }

            subscriber = event_manager.subscribe()
            logger.info("New SSE client connected.")

            while True:
                # If client disconnects, stop
                if await request.is_disconnected():
                    logger.info("SSE client disconnected normally.")
                    break
                
                # Wait for the next message from the subscriber queue, with a timeout
                # to occasionally check if the client is still connected.
                try:
                    message = await asyncio.wait_for(
                        anext(subscriber),
                        timeout=1.0,
                    )
                    
                    yield {
                        "event": "update",
                        "data": message,
                    }
                except asyncio.TimeoutError:
                    continue
                except StopAsyncIteration:
                    break

        except asyncio.CancelledError:
            logger.info("SSE client connection cancelled.")
            pass
        except Exception as e:
            logger.exception("Unexpected error in SSE generator")

    return EventSourceResponse(event_generator())

