import asyncio
import json
import logging

logger = logging.getLogger(__name__)

class EventManager:
    def __init__(self):
        self.subscribers = []
        self._loop = None

    def set_loop(self, loop):
        self._loop = loop

    def publish_sync(self, event_type: str, data: dict):
        message = json.dumps({"type": event_type, "data": data})
        if self._loop and self._loop.is_running():
            for queue in self.subscribers:
                self._loop.call_soon_threadsafe(queue.put_nowait, message)
        else:
            logger.warning("Event manager loop not set or not running, dropping event.")

    async def subscribe(self):
        queue = asyncio.Queue()
        self.subscribers.append(queue)
        try:
            while True:
                message = await queue.get()
                yield message
        finally:
            self.subscribers.remove(queue)

event_manager = EventManager()
