from media_manager.base.base import MediaManager
import os
import boto3
from botocore.client import ClientCreator
from functools import cached_property
from botocore.exceptions import ClientError
from io import BytesIO
from media_manager.base.datastructures import MUploadFile
from collections.abc import Callable


class AWS_MediaManager(MediaManager):
    def __init__(
        self,
        upload_path: Callable | None = None,
        root_folder="",
        add_environment_as_prefix=True,
        bucket: str | None = None,
        aws_access_key_id: str | None = None,
        aws_secret_access_key: str | None = None,
        aws_region_name: str | None = None,
    ):
        if bucket is None:
            bucket = os.getenv("AWS_S3_BUCKET_NAME", None)
        if aws_access_key_id is None:
            aws_access_key_id = os.getenv("AWS_ACCESS_KEY", None)
        if aws_secret_access_key is None:
            aws_secret_access_key = os.getenv("AWS_SECRET_KEY", None)
        if aws_region_name is None:
            aws_region_name = os.getenv("AWS_REGION_NAME", None)
        # Validate all required environment variables are set
        if any(
            i is None
            for i in [
                bucket,
                aws_access_key_id,
                aws_secret_access_key,
                aws_region_name,
            ]
        ):
            raise ValueError(
                "AWS_S3_BUCKET_NAME, AWS_ACCESS_KEY, AWS_SECRET_KEY, and"
                " AWS_REGION_NAME environment variables must be set"
            )
        # Set attributes
        self.bucket_name = bucket
        self.aws_access_key_id = aws_access_key_id
        self.aws_secret_access_key = aws_secret_access_key
        self.aws_region_name = aws_region_name
        self._s3_client = None
        # Set bucket
        self.bucket = boto3.resource(
            "s3",
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key,
            region_name=aws_region_name,
        ).Bucket(self.bucket_name)
        super().__init__(upload_path, root_folder, add_environment_as_prefix)

    @cached_property
    def client(self) -> ClientCreator:
        return boto3.client(
            "s3",
            region_name=self.aws_region_name,
            aws_access_key_id=self.aws_access_key_id,
            aws_secret_access_key=self.aws_secret_access_key,
        )

    @cached_property
    def s3_client(self) -> ClientCreator:
        if not self._s3_client:
            self._s3_client = boto3.client(
                "s3",
                region_name=self.aws_region_name,
                aws_access_key_id=self.aws_access_key_id,
                aws_secret_access_key=self.aws_secret_access_key,
            )
        return self._s3_client

    # Backend specific Methods
    def _backend_upload(self, file: MUploadFile, complete_path, *args, **kwargs):
        ExtraArgs = kwargs.get("ExtraArgs", {})
        self.bucket.upload_fileobj(file.file, Key=complete_path, ExtraArgs=ExtraArgs)

    def _backend_delete(self, complete_path: str) -> str:
        response = self.bucket.delete_objects(
            Delete={"Objects": [{"Key": complete_path}], "Quiet": True}
        )
        return response

    def _backend_get_file_location(self, complete_path: str) -> str:
        return f"https://{self.bucket_name}.s3.{self.aws_region_name}.amazonaws.com/{complete_path}"

    def _backend_delete_files_in_folder(self, prefix: str) -> list[str]:
        files_in_folder = self._backend_list_files_in_folder(prefix)
        files_to_delete = [{"Key": file} for file in files_in_folder]
        s3_client = self.s3_client
        if files_to_delete:
            s3_client.delete_objects(
                Bucket=self.bucket_name, Delete={"Objects": files_to_delete}
            )
        return files_to_delete

    def _backend_list_files_in_folder(self, prefix: str) -> list[str]:
        s3_client = self.s3_client
        response = s3_client.list_objects_v2(Bucket=self.bucket_name, Prefix=prefix)
        files_in_folder = response.get("Contents", [])
        files = [file["Key"] for file in files_in_folder]  # type: ignore
        # Exclude the specified folder from the list
        return [file for file in files if file != f"{prefix}/"]

    def _backend_download_file(self, file: str) -> BytesIO:
        response = BytesIO()
        self.client.download_fileobj(
            Bucket=self.bucket_name, Key=file, Fileobj=response
        )
        response.seek(0)
        return response

    async def signed_url(self, file: str, verify: bool = False) -> str:
        if verify:
            try:
                self.client.head_object(Bucket=self.bucket_name, Key=file)
            except ClientError as e:
                if e.response["Error"]["Code"] == "404":
                    raise FileNotFoundError
                else:
                    raise
        params = {"Bucket": self.bucket_name, "Key": file}
        url = self.client.generate_presigned_url(
            "get_object", Params=params, ExpiresIn=3600
        )
        return url
