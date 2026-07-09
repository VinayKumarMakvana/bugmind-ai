import asyncio
import json
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
from ...core.events import event_manager

router = APIRouter()

@router.get("/events")
async def sse_endpoint(request: Request):
    """
    Subscribe to real-time events via Server-Sent Events (SSE).
    """
    async def event_generator():
        try:
            # Send initial connection message
            yield {
                "event": "connected",
                "data": json.dumps({"message": "Subscribed to real-time events"})
            }

            subscriber = event_manager.subscribe()
            while True:
                # If client disconnects, stop
                if await request.is_disconnected():
                    break
                
                # Wait for the next message from the subscriber queue, with a timeout
                # to occasionally check if the client is still connected.
                try:
                    message = await asyncio.wait_for(anext(subscriber), timeout=1.0)
                    yield {
                        "event": "update",
                        "data": message
                    }
                except asyncio.TimeoutError:
                    continue
        except asyncio.CancelledError:
            pass

    return EventSourceResponse(event_generator())
