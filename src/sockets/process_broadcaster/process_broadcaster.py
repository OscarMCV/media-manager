from asyncio import AbstractEventLoop
from collections.abc import Callable

from sockets.broadcaster.broadcaster import BroadCaster
from sockets.broadcaster.schemas import BroadcasterPublish


class ProcessBroadcaster:
    def __init__(
        self,
        broadcast_messages: bool = True,
        redis_host: str = "localhost",
        redis_port: int = 6379,
        redis_database: int = 3,
    ) -> None:
        self._broadcaster = None
        self._channel = None
        # Parameters assignment
        self.broadcast_messages = broadcast_messages
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_database = redis_database
        return

    @property
    def broadcast_messages(self) -> bool:
        return self._broadcast_messages

    @broadcast_messages.setter
    def broadcast_messages(self, value: bool):
        self._broadcast_messages = value

    @property
    def broadcast_channel(self) -> str:
        if self._channel is None:
            raise Exception("Must set broadcast channel before broadcast")
        return self._channel

    @broadcast_channel.setter
    def broadcast_channel(self, value: str):
        self._channel = value

    @property
    def loop(self) -> AbstractEventLoop:
        if self._loop is None:
            raise Exception(
                "Must set event loop before broadcast to websocket"
            )
        return self._loop

    @loop.setter
    def loop(self, current_event_loop: AbstractEventLoop):
        self._loop = current_event_loop

    @property
    def broadcaster(self) -> BroadCaster:
        if self._broadcaster is not None:
            return self._broadcaster
        self._broadcaster = BroadCaster(
            redis_host=self.redis_host,
            redis_port=self.redis_port,
            redis_database=self.redis_database,
        )
        return self._broadcaster

    async def disconnect(self):
        if self.broadcaster.connected:
            await self.broadcaster.disconnect()
            self.broadcaster.connected = False
        return

    def sync_disconnect(self):
        self.loop.run_until_complete(self.disconnect())
        return

    async def broadcast(
        self, message: BroadcasterPublish, cache: Callable | None = None
    ) -> BroadcasterPublish:
        if self.broadcast_messages:
            if not self.broadcaster.connected:
                await self.broadcaster.connect()
            await self.broadcaster.publish(
                channel=self.broadcast_channel, message=message
            )
            if cache:
                cache(self, message)
        return message

    def sync_broadcast(
        self, message: BroadcasterPublish, cache: Callable | None = None
    ) -> BroadcasterPublish:
        """Synchronous version of broadcast."""
        if self.broadcast_messages:
            return self.loop.run_until_complete(
                self.broadcast(message=message, cache=cache)
            )

    def calculate_progress(
        self,
        current_element: int = 1,
        total_elements: int = 1,
        base_percentage: int = 0,
        top_percentage: int = 100,
    ) -> int:
        """
        Calculate the progress percentage based on the current element and
        total elements.
        """
        if top_percentage > 100:
            # The current process cant be more than 100%
            top_percentage = 100
        current_percentage = (
            (current_element / max(total_elements, 1))
            * (top_percentage - base_percentage)
        ) + base_percentage
        return int(min(current_percentage, 100))
