class HashError(Exception):
    pass


class ModDBDownloadError(Exception):
    pass


class InsufficientSpaceError(RuntimeError):
    """Raised when there is not enough disk space for extraction."""
    pass
