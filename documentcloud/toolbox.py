"""
A few toys the API will use.
"""
import time
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


def retry(ExceptionToCheck, tries=4, delay=3, backoff=2):
    """
    Retry decorator published by Saltry Crane. 
    
    http://www.saltycrane.com/blog/2009/11/trying-out-retry-decorator-python/
    """
    def deco_retry(f):
        def f_retry(*args, **kwargs):
            mtries, mdelay = tries, delay
            try_one_last_time = True
            while mtries > 1:
                try:
                    return f(*args, **kwargs)
                    try_one_last_time = False
                    break
                except ExceptionToCheck, e:
                    print "Retrying in %s seconds" % str(mdelay)
                    time.sleep(mdelay)
                    mtries -= 1
                    mdelay *= backoff
            if try_one_last_time:
                return f(*args, **kwargs)
            return
        return f_retry # true decorator
    return deco_retry

