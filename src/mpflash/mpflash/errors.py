"""Custom exceptions for the MPFlash package."""


class MPFlashError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)

EXIT_OK = 0
EXIT_ERROR = -1
EXIT_CANCELLED = -2
EXIT_DOWNLOAD_FAILED = -3