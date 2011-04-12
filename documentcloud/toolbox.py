"""
A few toys the API will use.
"""
from functools import wraps

#
# Exceptions
#

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

#
# Decorators
#

def credentials_required(method_func):
    """
    Decorator for methods that checks that the client has credentials.
    
    Throws a CredentialsMissingError when they are absent.
    """
    def _checkcredentials(self, *args, **kwargs):
        if self.username and self.password:
            return method_func(self, *args, **kwargs)
        else:
            raise CredentialsMissingError("This is a private method. You must provide a username and password when you initialize the DocumentCloud client to attempt this type of request.")
    
    return wraps(method_func)(_checkcredentials)

