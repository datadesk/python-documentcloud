"""
Python library for interacting with the DocumentCloud API.

DocumentCloud's API can search, upload, edit and organize documents hosted
in its system. Public documents are available without an API key, but 
authorization is required to interact with private documents.

Further documentation:

    https://www.documentcloud.org/help/api

"""
import urllib, urllib2
import datetime
try:
    import json
except ImportError:
    import simplejson as json


class BaseAPIObject(object):
    """
    An abstract version of the objects returned by the API.
    """

    def __init__(self, d):
        self.__dict__ = d
    
    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.__str__())
    
    def __str__(self):
        return self.__unicode__().encode("utf-8")
    
    def __unicode__(self):
        return unicode(self.title)


class Document(BaseAPIObject):
    """
    A document returned by the API.
    """
    pass


class Project(BaseAPIObject):
    """
    A project returned by the API.
    """
    pass


class documentcloud(object):
    """
    The main public method for interacting with the API.
    """
    
    BASE_URL = u'https://www.documentcloud.org/api/'
    # For storing calls we've already made.
    # URLs will be keys, responses will be values
    _cache = {}

    # 
    # Public methods
    #

    class documents(object):
        """
        Methods for collecting Documents.
        """
        
        @staticmethod
        def search(query, page=1, per_page=10):
            """
            Retrieve all objects that make a search query.
            
            Example usage:
            
                >> documentcloud.documents.search('salazar')
                
            """
            url = documentcloud.BASE_URL + u'search.json'
            params = {
                'q': query,
                'page': page,
                'per_page': per_page,
            }
            params = urllib.urlencode(params)
            req = urllib2.Request(url, params)
            response = urllib2.urlopen(req)
            data = response.read()
            data = json.loads(data)
            return [Document(d) for d in data.get('documents')]


if __name__ == '__main__':
    document_list = documentcloud.documents.search('salazar')
    print document_list







