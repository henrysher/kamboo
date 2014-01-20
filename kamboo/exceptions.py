class KambooException(Exception):
    """
    A base exception class for all Kamboo-related exceptions.
    """
    pass


class ValidationError(KambooException):
    pass


class TimeOutException(KambooException):
    pass


class TooManyRecordsException(KambooException):
    """
    Exception raised when a search of records returns more
    records than requested.
    """
    pass
