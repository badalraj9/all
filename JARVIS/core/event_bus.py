import asyncio
import fnmatch
from typing import Dict, List, Callable, Awaitable, Any, Optional
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from loguru import logger

from JARVIS.core.config import settings

class EventPriority(Enum):
    HIGH = 0
    NORMAL = 1
    LOW = 2

@dataclass
class Event:
    name: str
    data: Dict[str, Any]
    source: str
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
    priority: EventPriority = EventPriority.NORMAL

@dataclass
class Subscription:
    pattern: str
    callback: Callable[[Event], Awaitable[None]]
    priority: EventPriority

class EventBus:
    def __init__(self):
        self._subscribers: List[Subscription] = []
        self._history: List[Event] = []
        self._lock = asyncio.Lock()

    def subscribe(self, pattern: str, callback: Callable[[Event], Awaitable[None]], priority: EventPriority = EventPriority.NORMAL):
        """Subscribe to events matching the pattern (e.g., 'system.*', 'file.open')."""
        sub = Subscription(pattern=pattern, callback=callback, priority=priority)
        self._subscribers.append(sub)
        # Sort by priority (HIGH < NORMAL < LOW in enum value)
        self._subscribers.sort(key=lambda s: s.priority.value)
        logger.debug(f"Subscribed to {pattern} with priority {priority.name}")

    async def emit(self, name: str, data: Dict[str, Any], source: str, priority: EventPriority = EventPriority.NORMAL):
        """Emit an event to all matching subscribers."""
        event = Event(name=name, data=data, source=source, priority=priority)

        # Add to history
        async with self._lock:
            self._history.append(event)
            if len(self._history) > settings.MAX_EVENT_HISTORY:
                self._history.pop(0)

        logger.debug(f"Event emitted: {name} from {source}")

        # Notify subscribers
        tasks = []
        for sub in self._subscribers:
            if fnmatch.fnmatch(name, sub.pattern):
                tasks.append(self._safe_execute(sub, event))

        if tasks:
            await asyncio.gather(*tasks)

    async def _safe_execute(self, sub: Subscription, event: Event):
        try:
            await sub.callback(event)
        except Exception as e:
            logger.error(f"Error in handler for event {event.name}: {e}")

    def get_history(self) -> List[Event]:
        return list(self._history)

    def clear_history(self):
        self._history.clear()

    async def wait_for_event(self, pattern: str, timeout: float = 5.0) -> Optional[Event]:
        """Wait for an event matching the pattern."""
        future = asyncio.get_event_loop().create_future()

        async def _wrapper(event: Event):
            if not future.done():
                future.set_result(event)

        self.subscribe(pattern, _wrapper)

        try:
            return await asyncio.wait_for(future, timeout)
        except asyncio.TimeoutError:
            return None

# Singleton instance
event_bus = EventBus()
