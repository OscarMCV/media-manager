import typing


class MUploadFile:
    """
    An uploaded file included as part of the request data.
    """

    def __init__(
        self,
        file: typing.BinaryIO,
        *,
        filename: str | None = None,
        content_type: str | None = None,
    ) -> None:
        self.filename = filename
        self.file = file
        self.content_type = content_type

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(filename={self.filename!r})"
