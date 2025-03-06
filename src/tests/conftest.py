import os
import shutil
from collections.abc import Generator

from io import BytesIO
import pytest

from media_manager import MUploadFile, AWS_MediaManager


# ========= Media management fixtures =========
@pytest.fixture(scope="session")
def workspace_base_dir() -> str:
    return os.path.dirname(
        os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    )


@pytest.fixture(scope="session")
def testing_path(workspace_base_dir: str) -> str:
    return os.path.join(workspace_base_dir, "src/tests/test_files")


@pytest.fixture(scope="session")
def generic_file() -> MUploadFile:
    file_name = "test"
    file_extension = "txt"
    upload_file = MUploadFile(
        file=b"Hello World!", filename=f"{file_name}.{file_extension}"
    )
    return upload_file


@pytest.fixture(scope="session")
def aws_media_manager() -> AWS_MediaManager:
    return AWS_MediaManager()


@pytest.fixture(scope="function")
def test_pdf_file(testing_path: str) -> Generator[MUploadFile, None, None]:
    # Get the file from the test_files folder
    with open(
        os.path.join(
            testing_path,
            "test_file.pdf",
        ),
        "rb",
    ) as f:
        # Generate bytes from the file
        r = BytesIO(f.read())
        yield MUploadFile(
            file=r,
            filename="test_file.pdf",
        )


@pytest.fixture(scope="function")
def test_xml_file(testing_path: str) -> Generator[MUploadFile, None, None]:
    # Get the file from the test_files folder
    with open(
        os.path.join(
            testing_path,
            "test_file.xml",
        ),
        "rb",
    ) as f:
        # Generate bytes from the file
        r = BytesIO(f.read())
        yield MUploadFile(
            file=r,
            filename="test_file.xml",
        )


@pytest.fixture(scope="session")
def create_folder_path(testing_path: str) -> Generator[str, None, None]:
    path = os.path.join(
        testing_path,
        "test_upload_files",
    )
    if not os.path.exists(path):
        os.makedirs(path)
    yield path
    shutil.rmtree(path)
