import pydantic


class BroadcasterPublish(pydantic.BaseModel):
    message: str
    pass
