from media_manager.base.datastructures import MUploadFile
from typing_extensions import TypedDict
from io import BytesIO
from collections.abc import Callable
import os


class DeletedFile(TypedDict):
    key: str


class MediaManager:
    def __init__(
        self,
        upload_path: Callable | None = None,
        root_folder: str = "",
        add_environment_as_prefix: bool = True,
    ):
        self.upload_path = upload_path
        self.root_folder = root_folder
        self.add_environment_as_prefix = add_environment_as_prefix
        self.environment = os.getenv("ENVIRONMENT", "local")

    def get_complete_path(self, file: MUploadFile, *args, **kwargs) -> str:
        if self.upload_path is None:
            raise ValueError("upload_path is required for this operation")
        complete_file_name = self.upload_path(file, **kwargs)
        if self.add_environment_as_prefix:
            complete_path = os.path.join(
                self.environment, self.root_folder, complete_file_name
            )
        else:
            complete_path = f"{self.root_folder}/{complete_file_name}"
        return complete_path

    # Backend specific Methods
    def _backend_upload(
        self, file: MUploadFile, complete_path: str, *args, **kwargs
    ) -> str:
        raise NotImplementedError

    def _backend_delete(self, complete_path: str, *args, **kwargs) -> str:
        raise NotImplementedError

    def _backend_get_file_location(self, complete_path: str, *args, **kwargs) -> str:
        raise NotImplementedError

    def _backend_delete_files_in_folder(
        self, prefix: str, *args, **kwargs
    ) -> list[str]:
        raise NotImplementedError

    def _backend_list_files_in_folder(self, prefix: str, *args, **kwargs) -> list[str]:
        raise NotImplementedError

    def _backend_download_file(self, file: str) -> BytesIO:
        raise NotImplementedError

    # ===== Abstract Methods sync methods =====
    def sync_upload_file(self, file: MUploadFile, *args, **kwargs) -> str:
        complete_path = self.get_complete_path(file, *args, **kwargs)
        self._backend_upload(file, complete_path, *args, **kwargs)
        return complete_path

    def sync_delete_file(self, complete_path: str, *args, **kwargs) -> str:
        delete_response = self._backend_delete(complete_path, *args, **kwargs)
        return delete_response

    def sync_get_file_location(self, complete_path: str, *args, **kwargs) -> str:
        location = self._backend_get_file_location(complete_path, *args, **kwargs)
        return location

    def sync_delete_files_in_folder(
        self, prefix: str, *args, **kwargs
    ) -> list[DeletedFile]:
        deleted_files = self._backend_delete_files_in_folder(prefix, *args, **kwargs)
        return [{"key": file} for file in deleted_files]

    def sync_list_files_in_folder(self, prefix: str, *args, **kwargs) -> list[str]:
        return self._backend_list_files_in_folder(prefix, *args, **kwargs)

    def sync_download_file(self, file: str, *args, **kwargs) -> BytesIO:
        return self._backend_download_file(file, *args, **kwargs)

    def sync_signed_url(self, file: str, verify: bool, *args, **kwargs) -> str:
        raise NotImplementedError

    # ===== Abstract Methods async methods =====
    async def upload_file(self, file: MUploadFile, *args, **kwargs) -> str:
        complete_path = self.get_complete_path(file, *args, **kwargs)
        self._backend_upload(file, complete_path, *args, **kwargs)
        return complete_path

    async def delete_file(self, complete_path: str, *args, **kwargs) -> str:
        delete_response = self._backend_delete(complete_path, *args, **kwargs)
        return delete_response

    async def get_file_location(self, complete_path: str, *args, **kwargs) -> str:
        location = self._backend_get_file_location(complete_path, *args, **kwargs)
        return location

    async def delete_files_in_folder(
        self, prefix: str, *args, **kwargs
    ) -> list[DeletedFile]:
        deleted_files = self._backend_delete_files_in_folder(prefix, *args, **kwargs)
        return [{"key": file} for file in deleted_files]

    async def list_files_in_folder(self, prefix: str, *args, **kwargs) -> list[str]:
        return self._backend_list_files_in_folder(prefix, *args, **kwargs)

    async def download_file(self, file: str, *args, **kwargs) -> BytesIO:
        return self._backend_download_file(file, *args, **kwargs)

    async def signed_url(self, file: str, verify: bool, *args, **kwargs) -> str:
        raise NotImplementedError
