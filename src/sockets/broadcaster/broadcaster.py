from broadcaster import Broadcast

from .schemas import BroadcasterPublish


class BroadCaster(Broadcast):
    def __init__(
        self, redis_host: str, redis_port: int, redis_database: int = 3
    ) -> None:
        super().__init__(f"redis:/{redis_host}:{redis_port}/{redis_database}")
        self.connected = False
        return

    @property
    def connected(self) -> bool:
        try:
            return self._connected
        except AttributeError:
            return False

    @connected.setter
    def connected(self, value: bool) -> None:
        self._connected = value

    async def connect(self) -> None:
        await super().connect()
        self.connected = True
        return

    async def publish(self, channel: str, message: BroadcasterPublish):
        # This validation is useful to ensure that the message can be
        # serialized but there is not such a defined schema to send
        if issubclass(type(message), BroadcasterPublish):
            valid_message = message.model_dump_json()
        else:
            raise TypeError("message must be an instance of BroadcasterPublish")
        return await super().publish(channel, valid_message)
