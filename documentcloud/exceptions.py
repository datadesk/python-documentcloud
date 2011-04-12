"""
Custom exceptions the API will use.
"""
class CredentialsMissingError(Exception):
    """
    Raised if an API call is attempted without the required login credentials
    """
    pass


class CredentialsFailedError(Exception):
    """
    Raised if an API call fails because the login credentials are no good.
    """
    pass


class DoesNotExistError(Exception):
    """
    Raised when the user asks the API for something it cannot find.
    """
    pass

class DuplicateObjectError(Exception):
    """
    Raised when the user tries to add a duplicate to a distinct list.
    """
    pass
