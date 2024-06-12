"""Custom exceptions for the MPFlash package."""


class MPFlashError(Exception):
    """Base class for exceptions in this module."""

    def __init__(self, message: str):
        self.message = message
        super().__init__(message)
