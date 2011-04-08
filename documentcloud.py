"""
Python library for interacting with the DocumentCloud API.

DocumentCloud's API can search, upload, edit and organize documents hosted
in its system. Public documents are available without an API key, but 
authorization is required to interact with private documents.

Further documentation:

    https://www.documentcloud.org/help/api

"""
import urllib, urllib2
from datetime import datetime
from dateutil.parser import parse as dateparser
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
    def __init__(self, d):
        self.__dict__ = d
        self.resources = Resource(d.get("resources"))
        self.created_at = dateparser(d.get("created_at"))
        self.updated_at = dateparser(d.get("updated_at"))
    
    #
    # Lazy loaded attributes
    #
    
    def get_contributor(self):
        """
        Fetch the contributor field if it does not exist.
        """
        try:
            return self.__dict__[u'contributor']
        except KeyError:
            obj = documentcloud.documents.get(id=self.id)
            self.__dict__[u'contributor'] = obj.contributor
            return obj.contributor
    contributor = property(get_contributor)
    
    def get_contributor_organization(self):
        """
        Fetch the contributor_organization field if it does not exist.
        """
        try:
            return self.__dict__[u'contributor_organization']
        except KeyError:
            obj = documentcloud.documents.get(id=self.id)
            self.__dict__[u'contributor_organization'] = obj.contributor_organization
            return obj.contributor_organization
    contributor_organization = property(get_contributor_organization)
    
    def get_annotations(self):
        """
        Fetch the annotations field if it does not exist.
        """
        try:
            obj_list = self.__dict__[u'annotations']
            return [Annotation(i) for i in obj_list]
        except KeyError:
            obj = documentcloud.documents.get(id=self.id)
            obj_list = [Annotation(i) for i in obj.__dict__['annotations']]
            self.__dict__[u'annotations'] = obj_list
            return obj_list
    annotations = property(get_annotations)
    
    def get_sections(self):
        """
        Fetch the sections field if it does not exist.
        """
        try:
            obj_list = self.__dict__[u'sections']
            return [Section(i) for i in obj_list]
        except KeyError:
            obj = documentcloud.documents.get(id=self.id)
            obj_list = [Section(i) for i in obj.__dict__['sections']]
            self.__dict__[u'sections'] = obj_list
            return obj_list
    sections = property(get_sections)
    
    #
    # Text
    #
    
    def get_full_text_url(self):
        """
        Returns the URL that contains the full text of the document.
        """
        return self.resources.text
    full_text_url = property(get_full_text_url)
    
    def get_full_text(self):
        """
        Downloads and returns the full text of the document.
        """
        req = urllib2.Request(self.full_text_url)
        response = urllib2.urlopen(req)
        return response.read()
    full_text = property(get_full_text)
    
    def get_page_text_url(self, page):
        """
        Returns the URL for the full text of a particular page in the document.
        """
        template = self.resources.page.get('text')
        url = template.replace("{page}", str(page))
        return url
    
    def get_page_text(self, page):
        """
        Downloads and returns the full text of a particular page in the document.
        """
        url = self.get_page_text_url(page)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return response.read()
    
    #
    # Images
    #
    
    def get_pdf_url(self):
        """
        Returns the URL that contains the full PDF of the document.
        """
        return self.resources.pdf
    pdf_url = property(get_pdf_url)
    
    def get_pdf(self):
        """
        Downloads and returns the full PDF of the document.
        """
        req = urllib2.Request(self.pdf_url)
        response = urllib2.urlopen(req)
        return response.read()
    pdf = property(get_pdf)
    
    def get_small_image_url(self, page=1):
        """
        Returns the URL for the small sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        template = self.resources.page.get('image')
        url = template.replace("{page}", str(page)).replace("{size}", "small")
        return url
    small_image_url = property(get_small_image_url)
    
    def get_thumbnail_image_url(self, page=1):
        """
        Returns the URL for the thumbnail sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        template = self.resources.page.get('image')
        url = template.replace("{page}", str(page)).replace("{size}", "thumbnail")
        return url
    thumbnail_image_url = property(get_thumbnail_image_url)
    
    def get_large_image_url(self, page=1):
        """
        Returns the URL for the large sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        template = self.resources.page.get('image')
        url = template.replace("{page}", str(page)).replace("{size}", "large")
        return url
    large_image_url = property(get_large_image_url)
    
    def get_small_image_url_list(self):
        """
        Returns a list of the URLs for the small sized image of every page.
        """
        return [self.get_small_image_url(i) for i in range(1, self.pages +1)]
    small_image_url_list = property(get_small_image_url_list)
    
    def get_thumbnail_image_url_list(self):
        """
        Returns a list of the URLs for the thumbnail sized image of every page.
        """
        return [self.get_thumbnail_image_url(i) for i in range(1, self.pages +1)]
    thumbnail_image_url_list = property(get_thumbnail_image_url_list)
    
    def get_large_image_url_list(self):
        """
        Returns a list of the URLs for the large sized image of every page.
        """
        return [self.get_large_image_url(i) for i in range(1, self.pages +1)]
    large_image_url_list = property(get_large_image_url_list)
    
    def get_small_image(self, page=1):
        """
        Downloads and returns the small sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        url = self.get_small_image_url(page=page)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return response.read()
    small_image = property(get_small_image)
    
    def get_thumbnail_image(self, page=1):
        """
        Downloads and returns the thumbnail sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        url = self.get_thumbnail_image_url(page=page)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return response.read()
    thumbnail_image = property(get_thumbnail_image)
    
    def get_large_image(self, page=1):
        """
        Downloads and returns the large sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        url = self.get_large_image_url(page=page)
        req = urllib2.Request(url)
        response = urllib2.urlopen(req)
        return response.read()
    large_image = property(get_large_image)


class Project(BaseAPIObject):
    """
    A project returned by the API.
    """
    pass


class Section(BaseAPIObject):
    """
    A section earmarked inside of a Document
    """
    pass


class Annotation(BaseAPIObject):
    """
    An annotation earmarked inside of a Document.
    """
    def __repr__(self):
        return '<%s>' % self.__class__.__name__
    
    def __str__(self):
        return self.__unicode__().encode("utf-8")
    
    def __unicode__(self):
        return u''
    
    def get_location(self):
        """
        Return the location as a good
        """
        image_string =  self.__dict__['location']['image']
        image_ints = map(int, image_string.split(","))
        return Location(*image_ints)
    location = property(get_location)


class Location(object):
    """
    The location of a 
    """
    def __repr__(self):
        return '<%s>' % self.__class__.__name__
    
    def __str__(self):
        return self.__unicode__().encode("utf-8")
    
    def __unicode__(self):
        return u''
    
    def __init__(self, top, right, bottom, left):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left


class Resource(BaseAPIObject):
    """
    The resources associated with a Document. Hyperlinks and such.
    """
    def __repr__(self):
        return '<%ss>' % self.__class__.__name__
    
    def __str__(self):
        return self.__unicode__().encode("utf-8")
    
    def __unicode__(self):
        return u''


class documentcloud(object):
    """
    The main public method for interacting with the API.
    """
    
    BASE_URL = u'https://www.documentcloud.org/api/'
    # For storing calls we've already made.
    # URLs will be keys, responses will be values
    _cache = {}

    #
    # Private methods
    #
    
    @staticmethod
    def _get_search_page(query, page, per_page):
        """
        Retrieve one page of search results from the DocumentCloud API.
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
        return json.loads(data).get("documents")

    # 
    # Public methods
    #

    class documents(object):
        """
        Methods for collecting Documents.
        """
        
        @staticmethod
        def search(query):
            """
            Retrieve all objects that make a search query.
            
            Example usage:
            
                >> documentcloud.documents.search('salazar')
            
            """
            page = 1
            document_list = []
            while True:
                results = documentcloud._get_search_page(query, page=page, per_page=1000)
                if results:
                    document_list += results
                    page += 1
                else:
                    break
            return [Document(d) for d in document_list]
        
        @staticmethod
        def get(id):
            """
            Retrieve a particular document using it's unique identifier.
            
            Example usage:
            
                >> documentcloud.documents.get(u'71072-oir-final-report')
            
            """
            url = documentcloud.BASE_URL + 'documents/%s.json' % id
            req = urllib2.Request(url)
            response = urllib2.urlopen(req)
            data = response.read()
            return Document(json.loads(data).get("document"))


if __name__ == '__main__':
    from pprint import pprint
    #document_list = documentcloud.documents.search('Calpers special review')
    #obj = document_list[0]
    #pprint(obj.contributor)
    #pprint(obj.__dict__)
    #pprint(obj.annotations)
    #pprint(obj.resources.__dict__)
    #print obj.get_page_text(1)
    obj = documentcloud.documents.get(u'74103-report-of-the-calpers-special-review')
    pprint(obj.sections)
    #pprint(obj)





