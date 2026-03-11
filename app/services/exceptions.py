"""Custom application exceptions."""


class UserNotFoundError(Exception):
    """Raised when a requested user does not exist."""


class EmailAlreadyRegisteredError(Exception):
    """Raised when an email address is already in use."""


class UsernameAlreadyTakenError(Exception):
    """Raised when a username is already in use."""


class InvalidCredentialsError(Exception):
    """Raised when login credentials do not match any user."""


class PostNotFoundError(Exception):
    """Raised when a requested post does not exist."""


class UnauthorizedPostAccessError(Exception):
    """Raised when a user tries to modify a post they do not own."""
