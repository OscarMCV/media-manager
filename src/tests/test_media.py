import os

import pytest

from media_manager.managers.local import Local_MediaManager
from src.media_manager import MediaManager, MUploadFile, AWS_MediaManager


def upload_path(file: MUploadFile) -> str:
    return f"test_upload_files/{file.filename}"


# ====== s3 tests ======
@pytest.mark.asyncio
async def test_s3_download_file(aws_media_manager: MediaManager):
    file = "test_files/test_download_files/test_file.txt"
    response = await aws_media_manager.download_file(file)
    assert response.read() == b"Hello World!"


def test_s3_sync_download_file(aws_media_manager: MediaManager):
    file = "test_files/test_download_files/test_file.txt"
    response = aws_media_manager.sync_download_file(file)
    assert response.read() == b"Hello World!"


@pytest.mark.asyncio
async def test_s3_signed_url(aws_media_manager: MediaManager):
    file = "test_files/test_signed_url/test_file.txt"
    # Test a file that does not exist
    failed_file = "test_files/test_signed_url/failed_file.txt"
    try:
        await aws_media_manager.signed_url(failed_file, verify=True)
        raise Exception("This should raise an exception")
    except FileNotFoundError:
        # This should raise an exception but can´t use pytest.raises
        pass
    response = await aws_media_manager.signed_url(file, verify=True)
    await aws_media_manager.signed_url(file)
    # Check starts
    assert (
        "https://zaplink-release.s3.amazonaws.com/test_files/test_signed_url/"
        "test_file.txt" in response
    )
    assert "AWSAccessKeyId" in response


@pytest.mark.asyncio
async def test_s3_upload_file(test_pdf_file: MUploadFile):
    media_manager = AWS_MediaManager(
        upload_path=upload_path,
        root_folder="test_files",
    )
    await media_manager.upload_file(test_pdf_file)
    complete_path = os.path.join(
        media_manager.root_folder, upload_path(test_pdf_file)
    )
    await media_manager.delete_file(complete_path)


@pytest.mark.asyncio
async def test_s3_delete_files(
    test_pdf_file: MUploadFile, test_xml_file: MUploadFile
):
    media_manager = AWS_MediaManager(
        upload_path=upload_path,
        root_folder="test_files",
        add_environment_as_prefix=False
    )
    # Upload files with async
    await media_manager.upload_file(test_pdf_file)
    # Upload files with sync
    media_manager.sync_upload_file(test_xml_file)
    file_list = await media_manager.list_files_in_folder(
        prefix=os.path.join(media_manager.root_folder, "test_upload_files")
    )
    assert len(file_list) == 2
    prefix = os.path.join(media_manager.root_folder, "test_upload_files")
    await media_manager.delete_files_in_folder(prefix=prefix)
    file_list = await media_manager.list_files_in_folder(
        prefix=os.path.join(media_manager.root_folder, "test_upload_files")
    )
    assert len(file_list) == 0


@pytest.mark.asyncio
async def test_s3_get_file_location():
    media_manager = AWS_MediaManager(
        upload_path=upload_path,
        root_folder="test_files",
        add_environment_as_prefix=False
    )
    test_file = "test_download_files/test_file.txt"
    complete_path = os.path.join(media_manager.root_folder, test_file)
    response = await media_manager.get_file_location(complete_path)
    assert response


@pytest.mark.asyncio
async def test_s3_list_files_in_folder():
    media_manager = AWS_MediaManager(
        upload_path=upload_path,
        root_folder="test_files",
        add_environment_as_prefix=False
    )
    prefix = "test_files/test_download_files"
    response = await media_manager.list_files_in_folder(prefix)
    assert response
    assert len(response) == 3
    assert any(
        item == "test_files/test_download_files/test_file.txt"
        for item in response
    )


@pytest.mark.asyncio
async def test_sync_s3_list_files_in_folder():
    media_manager = AWS_MediaManager(
        upload_path=upload_path,
        root_folder="test_files",
        add_environment_as_prefix=False
    )
    prefix = "test_files/test_download_files"
    response = media_manager.sync_list_files_in_folder(prefix)
    assert response
    assert len(response) == 3
    assert any(
        item == "test_files/test_download_files/test_file.txt"
        for item in response
    )


# ====== Local tests ======
def upload_local_path(file: MUploadFile) -> str:
    return f"{file.filename}"


@pytest.mark.asyncio
async def test_local_upload_file(
    test_pdf_file: MUploadFile, create_folder_path: str
):
    media_manager = Local_MediaManager(
        upload_path=upload_local_path,
        root_folder=create_folder_path,
        add_environment_as_prefix=False
    )
    await media_manager.upload_file(test_pdf_file)
    complete_path = os.path.join(
        media_manager.root_folder, upload_local_path(test_pdf_file)
    )
    await media_manager.delete_file(complete_path)


@pytest.mark.asyncio
async def test_local_delete_files(
    test_pdf_file: MUploadFile,
    test_xml_file: MUploadFile,
    create_folder_path: str,
):
    media_manager = Local_MediaManager(
        upload_path=upload_local_path,
        root_folder=create_folder_path,
        add_environment_as_prefix=False
    )
    # Upload files with async
    await media_manager.upload_file(test_pdf_file)
    # Upload files with sync
    media_manager.sync_upload_file(test_xml_file)
    await media_manager.delete_files_in_folder(prefix=create_folder_path)


@pytest.mark.asyncio
async def test_local_list_files_in_folder(testing_path: str):
    create_folder_path = os.path.join(
        testing_path,
        "test_xml_full_history",
    )
    media_manager = Local_MediaManager(
        upload_path=upload_local_path,
        root_folder=create_folder_path,
        add_environment_as_prefix=False
    )
    prefix = create_folder_path
    response = await media_manager.list_files_in_folder(prefix)
    assert response
    assert len(response) == 5
    expected_files = [
        "mar_2024.xml",
        "may_2024.xml",
        "abr_2024.xml",
        "jun_2024.xml",
        "feb_2024.xml",
    ]
    expected_files.sort()
    response.sort()
    assert response == expected_files


@pytest.mark.asyncio
async def test_sync_test_local_list_files_in_folder(testing_path: str):
    create_folder_path = os.path.join(
        testing_path,
        "test_xml_full_history",
    )
    media_manager = Local_MediaManager(
        upload_path=upload_local_path,
        root_folder=create_folder_path,
        add_environment_as_prefix=False
    )
    prefix = create_folder_path
    response = media_manager.sync_list_files_in_folder(prefix)
    assert response
    assert len(response) == 5
    expected_files = [
        "mar_2024.xml",
        "may_2024.xml",
        "abr_2024.xml",
        "jun_2024.xml",
        "feb_2024.xml",
    ]
    expected_files.sort()
    response.sort()
    assert response == expected_files
