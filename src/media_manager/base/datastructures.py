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
    ) -> None:
        self.filename = filename
        self.file = file

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}(filename={self.filename!r}"