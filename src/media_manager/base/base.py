from media_manager.base.datastructures import MUploadFile
from typing_extensions import TypedDict
from collections.abc import Callable
import os


class DeletedFile(TypedDict):
    key: str

class Base:
    def __init__(
        self,
        upload_path: Callable,
        root_folder: str = "",
        add_environment_as_prefix: bool = True,
    ):
        self.upload_path = upload_path
        self.root_folder = root_folder
        self.add_environment_as_prefix = add_environment_as_prefix
        self.environment = os.getenv("ENVIRONMENT", "local")

    def get_complete_path(self, file: MUploadFile, **kwargs) -> str:
        complete_file_name = self.upload_path(file, **kwargs)
        if self.add_environment_as_prefix:
            complete_path = os.path.join(
                self.environment, self.root_folder, complete_file_name
            )
        else:
            complete_path = f"{self.root_folder}/{complete_file_name}"
        return complete_path

    # Backend specific Methods
    def __backend_upload(self, file: MUploadFile, complete_path: str) -> str:
        raise NotImplementedError
    
    def __backend_delete(self, complete_path: str) -> str:
        raise NotImplementedError

    def __backend_get_file_location(self, complete_path: str) -> str:
        raise NotImplementedError
    
    def __backend_delete_files_in_folder(self, prefix: str) -> list[str]:
        raise NotImplementedError

    def __backend_list_files_in_folder(self, prefix: str) -> list[str]:
        raise NotImplementedError

    # ===== Abstract Methods sync methods =====
    def sync_upload_file(self, file: MUploadFile, **kwargs) -> str:
        complete_path = self.get_complete_path(file, **kwargs)
        self.__backend_upload(file, complete_path)
        return complete_path
    
    def sync_delete_file(self, complete_path: str) -> str:
        delete_response = self.__backend_delete(complete_path)
        return delete_response

    def sync_get_file_location(self, complete_path: str) -> str:
        location = self.__backend_get_file_location(complete_path)
        return location
    
    def sync_delete_files_in_folder(self, prefix: str) -> list[DeletedFile]:
        deleted_files = self.__backend_delete_files_in_folder(prefix)
        return [
            {"key": file} for file in deleted_files
        ]
    
    def sync_list_files_in_folder(self, prefix: str) -> list[str]:
        return self.__backend_list_files_in_folder(prefix)

    # ===== Abstract Methods async methods =====
    async def upload_file(self, file: MUploadFile, **kwargs) -> str:
        complete_path = self.get_complete_path(file, **kwargs)
        self.__backend_upload(file, complete_path)
        return complete_path

    async def delete_file(self, complete_path: str) -> str:
        delete_response = self.__backend_delete(complete_path)
        return delete_response
    
    async def get_file_location(self, complete_path: str) -> str:
        location = self.__backend_get_file_location(complete_path)
        return location

    async def delete_files_in_folder(self, prefix: str) -> list[DeletedFile]:
        deleted_files = self.__backend_delete_files_in_folder(prefix)
        return [
            {"key": file} for file in deleted_files
        ]
    
    async def list_files_in_folder(self, prefix: str) -> list[str]:
        return self.__backend_list_files_in_folder(prefix)
