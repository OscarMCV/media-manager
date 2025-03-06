from .managers.aws import AWS_MediaManager
from .managers.local import Local_MediaManager
from .base.base import MediaManager
from .base.datastructures import MUploadFile
import os
from functools import lru_cache


__all__ = ["AWS_MediaManager", "Local_MediaManager", "MediaManager", "MUploadFile"]


@lru_cache
def get_system_media_manager() -> MediaManager:
    if os.getenv("MEDIA_MANAGER", "local") == "AWS":
        return AWS_MediaManager()
    else:
        return Local_MediaManager()
