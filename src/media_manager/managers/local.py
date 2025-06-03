from media_manager.base.base import MediaManager
from media_manager.base.datastructures import MUploadFile
from io import BytesIO
import os


class Local_MediaManager(MediaManager):
    # Backend specific Methods
    def _backend_upload(
        self,
        file: MUploadFile,
        complete_path: str,
        *args,
        **kwargs,
    ):
        with open(complete_path, "wb") as f:
            f.write(file.file.read())

    def _backend_delete(self, complete_path: str) -> str:
        # Verify if the file exists
        if not os.path.exists(complete_path):
            raise FileNotFoundError(f"File {complete_path} not found")
        os.remove(complete_path)
        return complete_path

    def _backend_get_file_location(self, complete_path: str) -> str:
        return complete_path

    def _backend_delete_files_in_folder(self, prefix: str) -> list[str]:
        files = self._backend_list_files_in_folder(prefix)
        files_to_delete = [{"Key": file} for file in files]
        for file in files:
            os.remove(os.path.join(prefix, file))
        return files_to_delete

    def _backend_list_files_in_folder(self, prefix: str) -> list[str]:
        files = os.listdir(prefix)
        return files

    def _backend_download_file(self, file) -> BytesIO:
        read_file = BytesIO()
        with open(file, "rb") as f:
            read_file = BytesIO(f.read())
            read_file.seek(0)
        return read_file
