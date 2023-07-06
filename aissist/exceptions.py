class AIssistError(Exception):
    """Base class for all exceptions raised by AIssist"""


class InvalidParameterError(AIssistError):
    """Raised when an invalid parameter is passed to a function"""
