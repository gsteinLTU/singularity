import asyncio
import pygame

class CustomTimer:
    _tasks = {}  # Shared class-level dictionary to track tasks

    @classmethod
    async def _start_timer(cls, event_type, interval_ms):
        """Internal coroutine to post events periodically."""
        while event_type in cls._tasks:
            pygame.event.post(pygame.event.Event(event_type))
            await asyncio.sleep(interval_ms / 1000.0)  # Convert ms to seconds

    @classmethod
    def set_timer(cls, event_type, interval_ms):
        """Start or update a timer for a specific event type."""
        cls.cancel_timer(event_type)  # Cancel existing timer if it exists
        if interval_ms > 0:
            cls._tasks[event_type] = asyncio.create_task(cls._start_timer(event_type, interval_ms))

    @classmethod
    def cancel_timer(cls, event_type):
        """Cancel the timer for a specific event type."""
        if event_type in cls._tasks:
            cls._tasks[event_type].cancel()
            del cls._tasks[event_type]

    @classmethod
    def cancel_all_timers(cls):
        """Cancel all active timers."""
        for task in list(cls._tasks.keys()):
            cls.cancel_timer(task)
