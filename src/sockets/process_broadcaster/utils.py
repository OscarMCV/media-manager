from asyncio import (
    AbstractEventLoop,
    get_running_loop,
)
from asyncio import (
    get_event_loop as asyncio_get_event_loop,
)


def get_event_loop() -> AbstractEventLoop:
    # Validate if the event loop is already running
    if asyncio_get_event_loop().is_running():
        return get_running_loop()
    # Create a new event loop
    return asyncio_get_event_loop()
