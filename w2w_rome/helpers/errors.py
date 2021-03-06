class BaseRomeException(Exception):
    pass


class ConnectionPortsError(BaseRomeException):
    pass


class ConnectedToDifferentPortsError(BaseRomeException):
    """Sub ports of the logical port connected to different logical ports."""


class NotSupportedError(BaseRomeException):
    """This function doesn't supported."""


class GotErrorInThreads(BaseRomeException):
    """Got some error when executing func in a thread."""
