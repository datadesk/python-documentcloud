"""
Python library for interacting with the DocumentCloud API.

DocumentCloud's API can search, upload, edit and organize documents hosted
in its system. Public documents are available without an API key, but 
authorization is required to interact with private documents.

Further documentation:

    https://www.documentcloud.org/help/api

"""
import os
import copy
import base64
import urllib, urllib2
from datetime import datetime
from toolbox import *
from dateutil.parser import parse as dateparser
from MultipartPostHandler import MultipartPostHandler
try:
    import json
except ImportError:
    import simplejson as json


#
# API connection clients
#

class BaseDocumentCloudClient(object):
    """
    Patterns common to all of the different API methods.
    """
    BASE_URI = 'https://www.documentcloud.org/api/'
    
    def __init__(self, username, password):
        self.username = username
        self.password = password
    
    @retry(Exception, tries=4)
    def _make_request(self, url, params=None, opener=None):
        """
        Configure a HTTP request, fire it off and return the response.
        """
        # Create the request object
        args = [i for i in [url, params] if i]
        request = urllib2.Request(*args)
        # If the client has credentials, include them as a header
        if self.username and self.password:
            credentials = '%s:%s' % (self.username, self.password)
            encoded_credentials = base64.encodestring(credentials).replace("\n", "")
            header = 'Basic %s' % encoded_credentials
            request.add_header('Authorization', header)
        # If the request provides a custom opener, like the upload request,
        # which relies on a multipart request, it is applied here.
        if opener:
            opener = urllib2.build_opener(opener)
            request_method = opener.open
        else:
            request_method = urllib2.urlopen
        # Make the request
        try:
           response = request_method(request)
        except urllib2.HTTPError, e:
            if e.code == 404:
                raise DoesNotExistError("The resource you've requested does not exist or is unavailable without the proper credentials.")
            elif e.code == 401:
                raise CredentialsFailedError("The resource you've requested requires proper credentials.")
            else:
                raise e
        # Read the response and return it
        return response.read()
    
    @credentials_required
    def put(self, method, params):
        """
        Post changes back to DocumentCloud
        """
        # Prepare the params, first by adding a custom command to simulate a PUT request
        # even though we are actually POSTing. This is something DocumentCloud expects.
        params['_method'] = 'put'
        # Some special case handling of the document_ids list, if it exists
        if params.get("document_ids", None):
            # Pull the document_ids out of the params
            document_ids = params.get("document_ids")
            del params['document_ids']
            params = urllib.urlencode(params, doseq=True)
            # These need to be specially formatted in the style documentcloud
            # expects arrays. The example they provide is:
            # ?document_ids[]=28-boumediene&document_ids[]=207-academy&document_ids[]=30-insider-trading
            params += "".join(['&document_ids[]=%s' % id for id in document_ids])
        # More special case handler of key/value data tags, if they exist
        elif params.get("data", None):
            # Pull them out of the dict
            data = params.get("data")
            del params['data']
            params = urllib.urlencode(params, doseq=True)
            # Format them in the style documentcloud expects
            # ?data['foo']=bar&data['tit']=tat
            params += "".join(['&data[%s]=%s' % (key, value) for key, value in data.items()])
        else:
            # Otherwise, we can just use the vanilla urllib prep method
            params = urllib.urlencode(params, doseq=True)
        # Make the request
        content = self._make_request(
            self.BASE_URI + method,
            params,
        )
    
    def fetch(self, method, params=None):
        """
        Fetch an url.
        """
        # Encode params if they exist
        if params:
            params = urllib.urlencode(params, doseq=True)
        content = self._make_request(
            self.BASE_URI + method,
            params,
        )
        # Convert its JSON to a Python dictionary and return
        return json.loads(content)


class DocumentCloud(BaseDocumentCloudClient):
    """
    The public interface for the DocumentCloud API
    """
    
    def __init__(self, username=None, password=None):
        super(DocumentCloud, self).__init__(username, password)
        self.documents = DocumentClient(self.username, self.password, self)
        self.projects = ProjectClient(self.username, self.password, self)


class DocumentClient(BaseDocumentCloudClient):
    """
    Methods for collecting documents
    """
    def __init__(self, username, password, connection):
        self.username = username
        self.password = password
        # We want to have the connection around on all Document objects
        # this client creates in case the instance needs to hit the API
        # later. Storing it will preserve the credentials.
        self._connection = connection
    
    def _get_search_page(self, query, page, per_page):
        """
        Retrieve one page of search results from the DocumentCloud API.
        """
        params = {
            'q': query,
            'page': page,
            'per_page': per_page,
            'mentions': 3,
        }
        data = self.fetch('search.json', params)
        return data.get("documents")
    
    def search(self, query):
        """
        Retrieve all objects that make a search query.
        
        Example usage:
        
            >> documentcloud.documents.search('salazar')
        
        Based on code by Chris Amico
        """
        page = 1
        document_list = []
        # Loop through all the search pages and fetch everything
        while True:
            results = self._get_search_page(query, page=page, per_page=1000)
            if results:
                document_list += results
                page += 1
            else:
                break
        obj_list = []
        for doc in document_list:
            doc['_connection'] = self._connection
            obj = Document(doc)
            obj_list.append(obj)
        return obj_list
    
    def get(self, id):
        """
        Retrieve a particular document using it's unique identifier.
        
        Example usage:
        
            >> documentcloud.documents.get('71072-oir-final-report')
        
        """
        data = self.fetch('documents/%s.json' % id).get("document")
        data['_connection'] = self._connection
        return Document(data)
    
    @credentials_required
    def upload(self, pdf, title=None, source=None, description=None,
        related_article=None, published_url=None, access='private',
        project=None, data=None, secure=False):
        """
        Upload a PDF or other image file to DocumentCloud.
        
        You can submit either a pdf opened as a file object or a path to a pdf file.
        
        Example usage:
        
            # From a file path
            >> documentcloud.documents.upload("/home/ben/sample.pdf", "sample title")
        
            # From a file object
            >> pdf = open(path, 'rb')
            >> documentcloud.documents.upload(pdf, "sample title")

        Returns the document that's created as a Document object.
        
        Based on code developed by Mitchell Kotler and refined by Christopher Groskopf.
        """
        # Required parameters
        if hasattr(pdf, 'read'):
            params = {'file': pdf}
        else:
            params = {'file': open(pdf, 'rb')}
        # Optional parameters
        if title:
            params['title'] = title
        else:
            # Set it to the file name
            if hasattr(pdf, 'read'):
                params['title'] = pdf.name.split(os.sep)[-1].split(".")[0]
            else:
                params['title'] = pdf.split(os.sep)[-1].split(".")[0]
        if source: params['source'] = source
        if description: params['description'] = description
        if related_article: params['related_article'] = related_article
        if published_url: params['published_url'] = published_url
        if access: params['access'] = access
        if project: params['project'] = project
        if data:
            for key, value in data.items():
                params['data[%s]' % key] = value
        if secure: params['secure'] = 'true'
        # Make the request
        response = self._make_request(self.BASE_URI + 'upload.json', params, MultipartPostHandler)
        return self.get(json.loads(response)['id'])
    
    @credentials_required
    def upload_directory(self, path, source=None, description=None,
        related_article=None, published_url=None, access='private',
        project=None, data=None, secure=False):
        """
        Uploads all the PDFs in the provided directory.
        
        Example usage:
        
            >> documentcloud.documents.upload_directory("/home/ben/pdfs/")
        
        Returns a list of the documents created during the upload.
        
        Based on code developed by Mitchell Kotler and refined by Christopher Groskopf.
        """
        # Loop through the path and get all the files
        path_list = []
        for (dirpath, dirname, filenames) in os.walk(path):
            path_list.extend([os.path.join(dirpath, i) for i in filenames
                if i.lower().endswith(".pdf")])
        # Upload all the pdfs
        obj_list = []
        for pdf_path in path_list:
            obj = self.upload(pdf_path, source=source, description=description,
                related_article=related_article, published_url=published_url,
                access=access, project=project, data=data, secure=secure)
            obj_list.append(obj)
        # Pass back the list of documents
        return obj_list
    
    @credentials_required
    def delete(self, id):
        """
        Deletes a Document.
        """
        data = self.fetch(
            'documents/%s.json' % id,
            {'_method': 'delete'},
        )


class ProjectClient(BaseDocumentCloudClient):
    """
    Methods for collecting projects
    """
    def __init__(self, username, password, connection):
        self.username = username
        self.password = password
        # We want to have the connection around on all Document objects
        # this client creates in case the instance needs to hit the API
        # later. Storing it will preserve the credentials.
        self._connection = connection
    
    @credentials_required
    def all(self):
        """
        Retrieve all your projects. Requires authentication.
        
        Example usage:
        
            >> documentcloud.projects.all()
        
        """
        project_list = self.fetch('projects.json').get("projects")
        obj_list = []
        for proj in project_list:
            proj['_connection'] = self._connection
            proj = Project(proj)
            obj_list.append(proj)
        return obj_list
    
    def get(self, id=None, title=None):
        """
        Retrieve a particular project using its unique identifier or it's title.
        
        But not both.
        
        Example usage:
        
            >> documentcloud.projects.get('arizona-shootings')
        
        """
        # Make sure the kwargs are kosher
        if id and title:
            raise ValueError("You can only retrieve a Project by id or title, not by both")
        elif not id and not title:
            raise ValueError("You must provide an id or a title to make a request.")
        # Pull the hits
        if id:
            hit_list = [i for i in self.all() if str(i.id) == str(id)]
        elif title:
            hit_list = [i for i in self.all() if i.title.lower().strip() == title.lower().strip()]
        # Throw an error if there's more than one hit.
        if len(hit_list) > 1:
            raise DuplicateObjectError("There is more than one project that matches your request.")
        # Try to pull the first hit
        try:
            return hit_list[0]
        except IndexError:
            # If it's not there, you know to throw this error.
            raise DoesNotExistError("The resource you've requested does not exist or is unavailable without the proper credentials.")
    
    def get_by_id(self, id):
        """
         A reader-friendly shortcut to retrieve projects based on their ID. 
        """
        return self.get(id=id)
    
    def get_by_title(self, title):
        """
        A reader-friendly shortcut to retrieve projects based on their title. 
        """
        return self.get(title=title)
    
    @credentials_required
    def create(self, title, description=None, document_ids=None):
        """
        Creates a new project.
        
        Returns its unique identifer in documentcloud
        
        Example usage:
        
            >> documentcloud.projects.create("The Ruben Salazar Files")
        
        """
        params = {
            'title': title,
        }
        if description: params['description'] = description
        params = urllib.urlencode(params, doseq=True)
        if document_ids:
            # These need to be specially formatted in the style documentcloud
            # expects arrays. The example they provide is:
            # ?document_ids[]=28-boumediene&document_ids[]=207-academy&document_ids[]=30-insider-trading
            params += "".join(['&document_ids[]=%s' % id for id in document_ids])
        response = self._make_request(self.BASE_URI + "projects.json", params)
        new_id = json.loads(response)['project']['id']
        # If it doesn't exist, that suggests the project already exists
        if not new_id:
            raise DuplicateObjectError("The Project title you tried to create already exists")
        # Fetch the actual project object from the API and return that.
        return self.get(new_id)
    
    @credentials_required
    def get_or_create_by_title(self, title):
        """
        Fetch a title, if it exists. Create it if it doesn't.
        
        Returns a tuple with the object first, and then a boolean that indicates
        whether or not the object was created fresh. True means it's brand new.
        """
        try:
            obj = self.get_by_title(title)
            created = False
        except DoesNotExistError:
            obj = self.create(title=title)
            created = True
        return obj, created
    
    @credentials_required
    def delete(self, id):
        """
        Deletes a Project.
        """
        data = self.fetch(
            'projects/%s.json' % id,
            {'_method': 'delete'},
        )


#
# API objects
#

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


class Annotation(BaseAPIObject):
    """
    An annotation earmarked inside of a Document.
    """
    def __init__(self, d):
        self.__dict__ = d
    
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


class Document(BaseAPIObject):
    """
    A document returned by the API.
    """
    def __init__(self, d):
        self.__dict__ = d
        self.resources = Resource(d.get("resources"))
        self.mentions = [Mention(i) for i in d.get("mentions", [])] or None
        self.created_at = dateparser(d.get("created_at"))
        self.updated_at = dateparser(d.get("updated_at"))
    
    #
    # Updates and such
    #
    
    def put(self):
        """
        Save changes made to the object to DocumentCloud.
        
        According to DocumentCloud's docs, edits are allowed for the following
        fields:
        
            * title
            * source
            * description
            * related_article
            * access
            * published_url
            * data key/value pairs
        
        Returns nothing.
        """
        params = dict(
            title=self.title,
            source=self.source,
            description=self.description,
            related_article=self.resources.related_article,
            published_url=self.resources.published_url,
            access=self.access,
            data=self.data,
        )
        self._connection.put('documents/%s.json' % self.id, params)
    
    def save(self):
        """
        An alias to `'put` that post changes back to DocumentCloud
        """
        self.put()

    def delete(self):
        """
        Deletes this object from documentcloud.org.
        """
        self._connection.documents.delete(self.id)
    
    #
    # Lazy loaded attributes
    #
    
    def _lazy_load(self):
        """
        Fetch metadata if it was overlooked during the object's creation.
        
        This can happen when you retrieve documents via search, because
        the JSON response does not include complete meta data for all 
        results. 
        """
        obj = self._connection.documents.get(id=self.id)
        self.__dict__['contributor'] = obj.contributor
        self.__dict__['contributor_organization'] = obj.contributor_organization
        self.__dict__['data'] = obj.data
        self.__dict__['annotations'] = obj.__dict__['annotations']
        self.__dict__['sections'] = obj.__dict__['sections']
    
    def get_contributor(self):
        """
        Fetch the contributor field if it does not exist.
        """
        try:
            return self.__dict__['contributor']
        except KeyError:
            self._lazy_load()
            return self.__dict__['contributor']
    contributor = property(get_contributor)
    
    def get_contributor_organization(self):
        """
        Fetch the contributor_organization field if it does not exist.
        """
        try:
            return self.__dict__['contributor_organization']
        except KeyError:
            self._lazy_load()
            return self.__dict__['contributor_organization']
    contributor_organization = property(get_contributor_organization)
    
    def set_data(self, data):
        """
        Update the data attribute, making sure it's a dictionary.
        """
        if type(data) != type({}):
            raise TypeError("This attribute must be a dictionary.")
        self.__dict__['data'] = data
    
    def get_data(self):
        """
        Fetch the data field if it does not exist.
        """
        try:
            return self.__dict__['data']
        except KeyError:
            self._lazy_load()
            return self.__dict__['data']
    data = property(get_data, set_data)
    
    def get_annotations(self):
        """
        Fetch the annotations field if it does not exist.
        """
        try:
            obj_list = self.__dict__['annotations']
            return [Annotation(i) for i in obj_list]
        except KeyError:
            self._lazy_load()
            obj_list = self.__dict__['annotations']
            return [Annotation(i) for i in obj_list]
    annotations = property(get_annotations)
    
    def get_sections(self):
        """
        Fetch the sections field if it does not exist.
        """
        try:
            obj_list = self.__dict__['sections']
            return [Section(i) for i in obj_list]
        except KeyError:
            self._lazy_load()
            obj_list = self.__dict__['sections']
            return [Section(i) for i in obj_list]
    sections = property(get_sections)
    
    def get_entities(self):
        """
        Fetch the entities extracted from this document by OpenCalais.
        """
        try:
            return self.__dict__['entities']
        except KeyError:
            entities = self._connection.fetch(
                    "documents/%s/entities.json" % self.id
                ).get("entities")
            obj_list = []
            for type, entity_list in entities.items():
                for entity in entity_list:
                    entity['type'] = type
                    obj = Entity(entity)
                    obj_list.append(obj)
            self.__dict__['entities'] = obj_list
            return self.__dict__['entities']
    entities = property(get_entities)
    
    #
    # Text
    #
    
    def _get_url(self, url):
        if self.access == 'public':
            req = urllib2.Request(url)
            try:
                return urllib2.urlopen(req).read()
            except urllib2.HTTPError:
                raise NotImplementedError(
                    "Currently, DocumentCloud only allows you to access this resource on public documents."
                )
        else:
            raise NotImplementedError(
                "Currently, DocumentCloud only allows you to access this resource on public documents."
            )
    
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
        return self._get_url(self.full_text_url)
    full_text = property(get_full_text)
    
    def get_page_text_url(self, page):
        """
        Returns the URL for the full text of a particular page in the document.
        """
        template = self.resources.page.get('text')
        url = template.replace("{page}", str(page))
        return self._get_url(url)
    
    def get_page_text(self, page):
        """
        Downloads and returns the full text of a particular page in the document.
        """
        url = self.get_page_text_url(page)
        return self._get_url(url)
    
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
        return self._get_url(self.pdf_url)
    pdf = property(get_pdf)
    
    def get_small_image_url(self, page=1):
        """
        Returns the URL for the small sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        template = self.resources.page.get('image')
        return template.replace("{page}", str(page)).replace("{size}", "small")
    small_image_url = property(get_small_image_url)
    
    def get_thumbnail_image_url(self, page=1):
        """
        Returns the URL for the thumbnail sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        template = self.resources.page.get('image')
        return template.replace("{page}", str(page)).replace("{size}", "thumbnail")
    thumbnail_image_url = property(get_thumbnail_image_url)
    
    def get_normal_image_url(self, page=1):
        """
        Returns the URL for the "normal" sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        template = self.resources.page.get('image')
        return template.replace("{page}", str(page)).replace("{size}", "normal")
    normal_image_url = property(get_normal_image_url)

    def get_large_image_url(self, page=1):
        """
        Returns the URL for the large sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        template = self.resources.page.get('image')
        return template.replace("{page}", str(page)).replace("{size}", "large")
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
    
    def get_normal_image_url_list(self):
        """
        Returns a list of the URLs for the normal sized image of every page.
        """
        return [self.get_normal_image_url(i) for i in range(1, self.pages +1)]
    normal_image_url_list = property(get_normal_image_url_list)
    
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
        return self._get_url(url)
    small_image = property(get_small_image)
    
    def get_thumbnail_image(self, page=1):
        """
        Downloads and returns the thumbnail sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        url = self.get_thumbnail_image_url(page=page)
        return self._get_url(url)
    thumbnail_image = property(get_thumbnail_image)
    
    def get_normal_image(self, page=1):
        """
        Downloads and returns the normal sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        url = self.get_normal_image_url(page=page)
        return self._get_url(url)
    normal_image = property(get_normal_image)
    
    def get_large_image(self, page=1):
        """
        Downloads and returns the large sized image of a single page.
        
        The page kwarg specifies which page to return. One is the default.
        """
        url = self.get_large_image_url(page=page)
        return self._get_url(url)
    large_image = property(get_large_image)
    
    #
    # Etc.
    #
    
    def set_related_article(self, string):
        """
        Updates the related article back in the resources object so your changes
        can be property reflected in any future "puts."
        """
        self.resources.related_article = string
    
    def get_related_article(self):
        """
        Returns a related article, if one has been provided.
        """
        return self.resources.related_article
    related_article = property(get_related_article, set_related_article)
    
    def set_published_url(self, string):
        """
        Updates the published url back in the resources object so your changes
        can be property reflected in any future "puts."
        """
        self.resources.published_url = string

    def get_published_url(self):
        """
        Returns the url where the record is published, if one has been provided.
        """
        return self.resources.published_url
    published_url = property(get_published_url, set_published_url)


class DocumentSet(list):
    """
    A custom class for project lists associated with projects.
    
    Allows some tweaks, like preventing duplicate documents
    from getting into the list and ensuring that only Document
    objects are appended.
    """
    def append(self, obj):
        # Verify that the user is trying to add a Document object
        if not isinstance(obj, Document):
            raise TypeError("Only Document objects can be added to the document_list")
        # Check if the object is already in the list
        if obj.id in [i.id for i in list(self.__iter__())]:
            raise DuplicateObjectError("This object already exists in the document_list")
        # If it's all true, append it.
        super(DocumentSet, self).append(copy.copy(obj))


class Entity(BaseAPIObject):
    """
    Keywords and such extracted from the document by OpenCalais.
    """
    def __unicode__(self):
        return unicode(self.value)


class Location(object):
    """
    The location of an Annotation.
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


class Mention(BaseAPIObject):
    """
    A mention of a search found in the document.
    """
    def __unicode__(self):
        return unicode("Page %s" % (self.page))


class Project(BaseAPIObject):
    """
    A project returned by the API.
    """
    def __setattr__(self, attr, value):
        """
        An override that allows for a custom method setting 'document_list'
        """
        # Allow document_list to be zeroed out with [] or None
        if attr == 'document_list':
            if value == None:
                self.__dict__['document_list'] = DocumentSet([])
            elif isinstance(value, list):
                self.__dict__['document_list'] = DocumentSet(value)
            else:
                raise TypeError
        else:
            object.__setattr__(self, attr, value)
    
    #
    # Updates and such
    #
    
    def put(self):
        """
        Save changes made to the object to documentcloud.org
        
        According to DocumentCloud's docs, edits are allowed for the following
        fields:
        
            * title
            * description
            * document_ids
        
        Returns nothing.
        """
        params = dict(
            title=self.title,
            description=self.description,
            document_ids=[str(i.id) for i in self.document_list]
        )
        self._connection.put('projects/%s.json' % self.id, params)
    
    def save(self):
        """
        An alias to `'put` that post changes back to DocumentCloud
        """
        self.put()
    
    def delete(self):
        """
        Deletes this object from documentcloud.org.
        """
        self._connection.projects.delete(self.id)
    
    #
    # Documents
    #
    
    def get_document_list(self):
        """
        Retrieves all documents included in this project.
        """
        try:
            return self.__dict__['document_list']
        except KeyError:
            obj_list = DocumentSet([self._connection.documents.get(i) for i in self.document_ids])
            self.__dict__['document_list'] = obj_list
            return obj_list
    document_list = property(get_document_list)
    
    def get_document(self, id):
        """
        Retrieves a particular document from this project.
        """
        obj_list = self.document_list
        matches = [i for i in obj_list if str(i.id) == str(id)]
        if not matches:
            raise DoesNotExistError("The resource you've requested does not exist or is unavailable without the proper credentials.")
        return matches[0]


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
    
    def __getattr__(self, name):
        # When these attrs don't exist in the DocumentCloud db,
        # they aren't included in the JSON. But we need to them
        # to come out as empty strings if someone tries to call
        # them here in Python.
        if name in ['related_article', 'published_url']:
            return ''
        else:
            raise AttributeError


class Section(BaseAPIObject):
    """
    A section earmarked inside of a Document
    """
    pass


