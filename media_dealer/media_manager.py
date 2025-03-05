import os
from collections.abc import Callable
from io import BytesIO

import boto3
from botocore.exceptions import ClientError
from fastapi import UploadFile

from app.core.config import settings
from app.utilities.exceptions import ItemNotFoundException


class MediaFetcher:
    def __init__(self):
        self._client = boto3.client(
            "s3",
            region_name=settings.AWS_REGION_NAME,
            aws_access_key_id=settings.AWS_ACCESS_KEY,
            aws_secret_access_key=settings.AWS_SECRET_KEY,
        )

    async def download_file(self, file: str) -> BytesIO:
        response = BytesIO()
        self._client.download_fileobj(
            Bucket=settings.AWS_S3_BUCKET_NAME, Key=file, Fileobj=response
        )
        response.seek(0)
        return response

    def sync_download_file(self, file: str) -> BytesIO:
        response = BytesIO()
        self._client.download_fileobj(
            Bucket=settings.AWS_S3_BUCKET_NAME, Key=file, Fileobj=response
        )
        response.seek(0)
        return response

    async def signed_url(self, file: str, verify: bool = False) -> str:
        if verify:
            try:
                self._client.head_object(
                    Bucket=settings.AWS_S3_BUCKET_NAME, Key=file
                )
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    raise ItemNotFoundException(item_id=file, item_name="File")
                else:
                    raise
        params = {"Bucket": settings.AWS_S3_BUCKET_NAME, "Key": file}
        url = self._client.generate_presigned_url(
            "get_object", Params=params, ExpiresIn=3600
        )
        return url


class MediaManager:
    S3 = "s3"
    LOCAL = "local"

    def __init__(
        self,
        method: str,
        upload_path: Callable,
        root_folder: str = "",
        bucket: str | None = None,
        add_environment_as_prefix: bool = True,
    ) -> None:
        self.add_environment_as_prefix = add_environment_as_prefix
        self._s3_client = None
        self.method = method
        self.upload_path = upload_path
        self.root_folder = root_folder
        self.__selected_method_upload = {
            "s3": self.s3_upload,
            "local": self.local_upload,
        }[method]
        self.__selected_method_list_files_in_folder = {
            "s3": self.s3_list_files_in_folder,
            "local": self.local_list_files_in_folder,
        }[method]
        self.__selected_method_delete = {
            "s3": self.s3_delete_file,
            "local": self.local_delete_file,
        }[method]
        self.__selected_method_get_file_location = {
            "s3": self.s3_get_file_location,
            "local": self.local_get_file_location,
        }[method]
        self.__selected_method_delete_files_in_folder = {
            "s3": self.s3_delete_files_in_folder,
            "local": self.local_delete_files_in_folder,
        }[method]
        if method == self.S3:
            self.bucket_name = bucket or settings.AWS_S3_BUCKET_NAME
            self.bucket = boto3.resource(
                "s3",
                aws_access_key_id=settings.AWS_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SECRET_KEY,
                region_name=settings.AWS_REGION_NAME,
            ).Bucket(self.bucket_name)

    # ===== S3 Methods =====
    def _get_s3_client(self):
        if not self._s3_client:
            self._s3_client = boto3.client(
                "s3",
                region_name=settings.AWS_REGION_NAME,
                aws_access_key_id=settings.AWS_ACCESS_KEY,
                aws_secret_access_key=settings.AWS_SECRET_KEY,
            )
        return self._s3_client

    def s3_upload(self, file: UploadFile, name: str) -> None:
        self.bucket.upload_fileobj(file.file, Key=name)

    def s3_delete_file(self, file: str) -> dict:
        response = self.bucket.delete_objects(
            Delete={"Objects": [{"Key": file}], "Quiet": True}
        )
        return response

    async def s3_get_file_location(self, file: str) -> str:
        return f"https://{self.bucket_name}.s3.{settings.AWS_REGION_NAME}.amazonaws.com/{file}"

    def s3_list_files_in_folder(self, prefix: str) -> list[dict]:
        s3_client = self._get_s3_client()
        response = s3_client.list_objects_v2(
            Bucket=self.bucket_name, Prefix=prefix
        )
        files_in_folder = response.get("Contents", [])
        return files_in_folder

    def s3_delete_files_in_folder(self, prefix: str) -> list[dict]:
        files_in_folder = self.s3_list_files_in_folder(prefix)
        files_to_delete = [{"Key": file["Key"]} for file in files_in_folder]
        s3_client = self._get_s3_client()
        if files_to_delete:
            s3_client.delete_objects(
                Bucket=self.bucket_name, Delete={"Objects": files_to_delete}
            )
        return files_to_delete

    # ===== Local Methods =====
    def local_upload(self, file: UploadFile, name: str) -> None:
        with open(name, "wb") as f:
            f.write(file.file.read())

    def local_delete_file(self, file: str) -> dict:
        # Verify if the file exists
        if not os.path.exists(file):
            raise ItemNotFoundException(item_id=file, item_name="File")
        os.remove(file)
        return {"Key": file}

    async def local_get_file_location(self, file: str) -> str:
        return file

    def local_list_files_in_folder(self, prefix: str) -> list[str]:
        files = os.listdir(prefix)
        return files

    def local_delete_files_in_folder(self, prefix: str) -> list[dict]:
        files = self.local_list_files_in_folder(prefix)
        files_to_delete = [{"Key": file} for file in files]
        for file in files:
            os.remove(os.path.join(prefix, file))
        return files_to_delete

    # ===== General Methods =====
    async def upload_file(self, file: UploadFile, **kwargs) -> str:
        """
        Uploads a file to the selected method.
        """
        name = self.upload_path(file, **kwargs)
        if self.add_environment_as_prefix:
            complete_path = os.path.join(
                settings.ENVIRONMENT, self.root_folder, name
            )
        else:
            complete_path = os.path.join(self.root_folder, name)
        self.__selected_method_upload(file, complete_path)
        return complete_path

    def sync_upload_file(self, file: UploadFile, **kwargs) -> str:
        """
        Uploads a file to the selected method.
        """
        name = self.upload_path(file, **kwargs)
        if self.add_environment_as_prefix:
            complete_path = os.path.join(
                settings.ENVIRONMENT, self.root_folder, name
            )
        else:
            complete_path = os.path.join(self.root_folder, name)
        self.__selected_method_upload(file, complete_path)
        return complete_path

    async def delete_file(self, file: str):
        response = self.__selected_method_delete(file)
        return response

    def sync_delete_file(self, file: str):
        response = self.__selected_method_delete(file)
        return response

    async def get_file_location(self, file: str) -> str:
        return await self.__selected_method_get_file_location(file)

    async def delete_files_in_folder(self, prefix: str) -> list[dict]:
        files_to_delete = self.__selected_method_delete_files_in_folder(prefix)
        return files_to_delete

    async def list_files_in_folder(self, prefix: str):
        """
        Lists all files in the specified folder within the S3 bucket.

        Must provide the prefix from the root folder.

        Example of directory structure in S3:
        ```
        - root_folder/
            - folder1/
                - file1.txt
                - file2.txt
            - folder2/
                - file3.txt
        ```

        Example of a valid response for prefix 'root_folder/folder1/':
        ```
        ['file1.txt', 'file2.txt']
        ```

        Example of a valid empty response due to a wrong prefix 'root_folder/nonexistent_folder/':
        ```
        []
        ```

        :param prefix: The prefix (path) from the root folder in the S3 bucket.
        :type prefix: str
        :return: A list of filenames in the specified folder.
        :rtype: list[str]
        """
        response = self.__selected_method_list_files_in_folder(prefix)
        if self.method == self.LOCAL:
            return response
        files = [file["Key"] for file in response]  # type: ignore
        # Exclude the specified folder from the list
        return [file for file in files if file != f"{prefix}/"]

    def sync_list_files_in_folder(self, prefix: str):
        """
        Lists all files in the specified folder within the S3 bucket.
        This is a sync implementation of the list_files_in_folder method.
        """
        response = self.__selected_method_list_files_in_folder(prefix)
        if self.method == self.LOCAL:
            return response
        files = [file["Key"] for file in response]  # type: ignore
        # Exclude the specified folder from the list
        return [file for file in files if file != f"{prefix}/"]
