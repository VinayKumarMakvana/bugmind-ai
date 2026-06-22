import asyncio
import json
from fastapi import APIRouter, Request
from sse_starlette.sse import EventSourceResponse
import redis.asyncio as aioredis
from ...core.config import settings

router = APIRouter()

# Redis connection for Pub/Sub
redis_url = settings.REDIS_URL if hasattr(settings, 'REDIS_URL') else "redis://localhost:6379/0"

@router.get("/events")
async def sse_endpoint(request: Request):
    """
    Subscribe to real-time events via Server-Sent Events (SSE).
    """
    async def event_generator():
        # Connect to Redis
        r = aioredis.from_url(redis_url, decode_responses=True)
        pubsub = r.pubsub()
        await pubsub.subscribe("bugmind_events")

        try:
            # Send initial connection message
            yield {
                "event": "connected",
                "data": json.dumps({"message": "Subscribed to real-time events"})
            }

            while True:
                # If client disconnects, stop
                if await request.is_disconnected():
                    break

                # Poll for new messages from Redis
                message = await pubsub.get_message(ignore_subscribe_messages=True, timeout=1.0)
                if message:
                    yield {
                        "event": "update",
                        "data": message["data"]
                    }
        except asyncio.CancelledError:
            pass
        finally:
            await pubsub.unsubscribe("bugmind_events")
            await pubsub.close()
            await r.aclose()

    return EventSourceResponse(event_generator())
