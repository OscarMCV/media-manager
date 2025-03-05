import os
import shutil
from collections.abc import Generator
from io import BytesIO

import pytest
from fastapi import UploadFile


# ========= Media management fixtures =========
@pytest.fixture(scope="function")
def test_pdf_file(
    testing_path: str, test_pdf_file_path: str
) -> Generator[UploadFile, None, None]:
    # Get the file from the test_files folder
    with open(
        os.path.join(
            testing_path,
            test_pdf_file_path,
        ),
        "rb",
    ) as f:
        # Generate bytes from the file
        r = BytesIO(f.read())
        yield UploadFile(
            file=r,
            filename="test_file.pdf",
        )


@pytest.fixture(scope="function")
def test_xml_file_path(testing_path: str) -> Generator[str, None, None]:
    path = os.path.join(
        testing_path,
        "testing_files/test_file.xml",
    )
    yield path


@pytest.fixture(scope="function")
def test_xml_file(
    testing_path: str, test_xml_file_path: str
) -> Generator[UploadFile, None, None]:
    # Get the file from the test_files folder
    with open(
        os.path.join(
            testing_path,
            test_xml_file_path,
        ),
        "rb",
    ) as f:
        # Generate bytes from the file
        r = BytesIO(f.read())
        yield UploadFile(
            file=r,
            filename="test_file.xml",
        )


@pytest.fixture(scope="session")
def create_folder_path(testing_path: str) -> Generator[str, None, None]:
    path = os.path.join(
        testing_path,
        "testing_files/test_upload_files",
    )
    if not os.path.exists(path):
        os.makedirs(path)
    yield path
    shutil.rmtree(path)


@pytest.fixture(scope="session")
def generic_file() -> UploadFile:
    file_name = "test"
    file_extension = "txt"
    upload_file = UploadFile(
        file=b"Hello World!", filename=f"{file_name}.{file_extension}"
    )
    return upload_file
