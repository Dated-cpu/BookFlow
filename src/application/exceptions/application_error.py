class ApplicationError(Exception):
    """Base error for application layer."""


class AuthenticationError(ApplicationError):
    """Authentication failure (invalid credentials, expired token, etc.)."""
