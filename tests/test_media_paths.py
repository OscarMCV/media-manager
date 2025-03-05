import uuid

from fastapi import UploadFile

from app.utilities.media.media_manager import MediaManager
from app.utilities.media.media_paths.rpus import (
    get_rpu_documents_media_manager,
    upload_rpu_only_document,
)


def test_upload_rpu_only_document(generic_file: UploadFile):
    file_name = "test"
    file_extension = "txt"
    rpu_id = uuid.uuid4().hex
    file_path = upload_rpu_only_document(file=generic_file, rpu_id=rpu_id)
    assert file_path == f"{rpu_id}/{file_name}.{file_extension}"


def test_get_rpu_documents_media_manager():
    media_manager = get_rpu_documents_media_manager()
    assert isinstance(media_manager, MediaManager)
    assert media_manager.root_folder == "documents/rpus"
