from __future__ import annotations

import asyncio
import json
import logging
from typing import Any, AsyncGenerator, Dict, List, Optional

logger = logging.getLogger(__name__)


# =========================================================
# EVENT MANAGER
# =========================================================

class EventManager:
    """
    Manages in-memory pub-sub for Server-Sent Events (SSE) and background tasks.
    """

    def __init__(self) -> None:
        self.subscribers: List[asyncio.Queue[str]] = []
        self._loop: Optional[asyncio.AbstractEventLoop] = None

    def set_loop(self, loop: asyncio.AbstractEventLoop) -> None:
        """
        Set the asyncio event loop for thread-safe publishing.
        """
        self._loop = loop

    def publish_sync(self, event_type: str, data: Dict[str, Any]) -> None:
        """
        Publish an event to all connected SSE clients (thread-safe).
        """
        message = json.dumps({"type": event_type, "data": data})
        
        if self._loop and self._loop.is_running():
            for queue in self.subscribers:
                self._loop.call_soon_threadsafe(queue.put_nowait, message)
        else:
            logger.warning(
                "Event manager loop not set or not running, dropping event of type '%s'.",
                event_type,
            )

    async def subscribe(self) -> AsyncGenerator[str, None]:
        """
        Subscribe to events via an asyncio Queue. Yields messages to SSE stream.
        """
        queue: asyncio.Queue[str] = asyncio.Queue()
        self.subscribers.append(queue)
        
        try:
            while True:
                message = await queue.get()
                yield message
        finally:
            if queue in self.subscribers:
                self.subscribers.remove(queue)


# Singleton instance
event_manager = EventManager()

