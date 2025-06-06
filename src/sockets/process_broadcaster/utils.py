from functools import wraps
from typing import Callable
import os
from asyncio import (
    AbstractEventLoop,
    get_event_loop as asyncio_get_event_loop,
    get_running_loop,
)
from .process_broadcaster import ProcessBroadcaster


def get_event_loop() -> AbstractEventLoop:
    # Validate if the event loop is already running
    if asyncio_get_event_loop().is_running():
        return get_running_loop()
    # Create a new event loop
    return asyncio_get_event_loop()


def broadcaster_handler_context_manager(func) -> Callable:
    @wraps(func)
    def wrapper(*args, **kwargs):
        # Remove the broadcaster from the kwargs
        kwargs.pop("process_broadcaster", None)
        broadcast_messages = bool(os.environ.get("BROADCAST_MESSAGES"))
        process_broadcaster = ProcessBroadcaster(
            broadcast_messages=broadcast_messages
        )
        process_broadcaster.loop = get_event_loop()
        try:
            kwargs["process_broadcaster"] = process_broadcaster
            return func(*args, **kwargs)
        finally:
            try:
                process_broadcaster.sync_disconnect()
            except Exception:
                # If the broadcaster is not connected, it will raise an error
                pass

    return wrapper
