"""
Python library for interacting with the DocumentCloud API.

DocumentCloud's API can search, upload, edit and organize documents hosted
in its system. Public documents are available without an API key, but
authorization is required to interact with private documents.

Further documentation:

    http://python-documentcloud.readthedocs.org
    https://www.documentcloud.org/help/api

"""
from __future__ import absolute_import
import os
import re
import sys
import six
import json
import copy
import base64
from .toolbox import retry
from .toolbox import DoesNotExistError
from .toolbox import DuplicateObjectError
from .toolbox import credentials_required
from .toolbox import CredentialsFailedError
from dateutil.parser import parse as dateparser
from .MultipartPostHandler import MultipartPostHandler, PostHandler
if six.PY3:
    import urllib.parse
    import urllib.error
    import urllib.request
else:
    from six.moves import urllib


#
# API connection clients
#

class BaseDocumentCloudClient(object):
    """
    Patterns common to all of the different API methods.
    """
    BASE_URI = 'https://www.documentcloud.org/api/'

    def __init__(self, username, password, base_uri=None):
        self.BASE_URI = base_uri or BaseDocumentCloudClient.BASE_URI
        self.username = username
        self.password = password

    @retry(Exception, tries=3)
    def _make_request(self, url, params=None, opener=None):
        """
        Configure a HTTP request, fire it off and return the response.
        """
        # Create the request object
        args = [i for i in [url, params] if i]
        request = urllib.request.Request(*args)
        # If the client has credentials, include them as a header
        if self.username and self.password:
            credentials = '%s:%s' % (self.username, self.password)
            encoded_credentials = base64.encodestring(
                credentials.encode("utf-8")
            ).decode("utf-8").replace("\n", "")
            header = 'Basic %s' % encoded_credentials
            request.add_header('Authorization', header)
        # If the request provides a custom opener, like the upload request,
        # which relies on a multipart request, it is applied here.
        if opener:
            opener = urllib.request.build_opener(opener)
            request_method = opener.open
        else:
            request_method = urllib.request.urlopen
        # Make the request
        try:
            response = request_method(request)
        except Exception:
            e = sys.exc_info()[1]
            if getattr(e, 'code', None) == 404:
                raise DoesNotExistError("The resource you've requested does \
not exist or is unavailable without the proper credentials.")
            elif getattr(e, 'code', None) == 401:
                raise CredentialsFailedError("The resource you've requested \
requires proper credentials.")
            else:
                raise e
        # Read the response and return it
        return response.read()

    @credentials_required
    def put(self, method, params):
        """
        Post changes back to DocumentCloud
        """
        # Prepare the params, first by adding a custom command to
        # simulate a PUT request even though we are actually POSTing.
        # This is something DocumentCloud expects.
        params['_method'] = 'put'
        # Some special case handling of the document_ids list, if it exists
        if params.get("document_ids", None):
            # Pull the document_ids out of the params
            document_ids = params.get("document_ids")
            del params['document_ids']
            params = urllib.parse.urlencode(params, doseq=True)
            # These need to be specially formatted in the style documentcloud
            # expects arrays. The example they provide is:
            # ?document_ids[]=28-boumediene&document_ids[]=\
            # 207-academy&document_ids[]=30-insider-trading
            params += "".join([
                '&document_ids[]=%s' % id for id in document_ids
            ])
        # More special case handler of key/value data tags, if they exist
        elif params.get("data", None):
            # Pull them out of the dict
            data = params.get("data")
            del params['data']
            params = urllib.parse.urlencode(params, doseq=True)
            # Format them in the style documentcloud expects
            # ?data['foo']=bar&data['tit']=tat
            params += "".join([
                '&data[%s]=%s' % (
                    urllib.parse.quote_plus(key.encode("utf-8")),
                    urllib.parse.quote_plus(value.encode("utf-8"))
                ) for key, value in
                data.items()
            ])
        else:
            # Otherwise, we can just use the vanilla urllib prep method
            params = urllib.parse.urlencode(params, doseq=True)

        # Make the request
        self._make_request(
            self.BASE_URI + method,
            params.encode("utf-8"),
        )

    def fetch(self, method, params=None):
        """
        Fetch an url.
        """
        # Encode params if they exist
        if params:
            params = urllib.parse.urlencode(params, doseq=True).encode("utf-8")
        content = self._make_request(
            self.BASE_URI + method,
            params,
        )
        # Convert its JSON to a Python dictionary and return
        return json.loads(content.decode("utf-8"))


class DocumentCloud(BaseDocumentCloudClient):
    """
    The public interface for the DocumentCloud API
    """
    def __init__(self, username=None, password=None, base_uri=None):
        super(DocumentCloud, self).__init__(username, password, base_uri)
        self.documents = DocumentClient(
            self.username,
            self.password, self, base_uri
        )
        self.projects = ProjectClient(
            self.username,
            self.password,
            self,
            base_uri
        )


class DocumentClient(BaseDocumentCloudClient):
    """
    Methods for collecting documents
    """
    def __init__(self, username, password, connection, base_uri=None):
        super(DocumentClient, self).__init__(username, password, base_uri)
        # We want to have the connection around on all Document objects
        # this client creates in case the instance needs to hit the API
        # later. Storing it will preserve the credentials.
        self._connection = connection

    def is_url(self, value):
        """
        Test if a pdf being submitted is a valid URL
        """
        regex = re.compile(
                r'^(?:http|ftp)s?://'  # http:// or https://
                r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+(?:[A-Z]{2,6}\.?|[A-Z0-9-]{2,}\.?)|'  # domain...
                r'localhost|'  # localhost...
                r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # ...or ip
                r'(?::\d+)?'  # optional port
                r'(?:/?|[/?]\S+)$', re.IGNORECASE)
        return re.match(regex, value) is not None

    def _get_search_page(
        self,
        query,
        page,
        per_page=1000,
        mentions=3,
        data=False,
    ):
        """
        Retrieve one page of search results from the DocumentCloud API.
        """
        if mentions > 10:
            raise ValueError("You cannot search for more than 10 mentions")
        params = {
            'q': query,
            'page': page,
            'per_page': per_page,
            'mentions': mentions,
        }
        if data:
            params['data'] = 'true'
        response = self.fetch('search.json', params)
        return response.get("documents")

    def search(self, query, page=None, per_page=1000, mentions=3, data=False):
        """
        Retrieve all objects that make a search query.

        Will loop through all pages that match unless you provide
        the number of pages you'd like to restrict the search to.

        Example usage:

            >> documentcloud.documents.search('salazar')
        """
        # If the user provides a page, search it and stop there
        if page:
            document_list = self._get_search_page(
                query,
                page=page,
                per_page=per_page,
                mentions=mentions,
                data=data,
            )
        # If the user doesn't provide a page keep looping until you have
        # everything
        else:
            page = 1
            document_list = []
            # Loop through all the search pages and fetch everything
            while True:
                results = self._get_search_page(
                    query,
                    page=page,
                    per_page=per_page,
                    mentions=mentions,
                    data=data,
                )
                if results:
                    document_list += results
                    page += 1
                else:
                    break
        # Convert the JSON objects from the API into Python objects
        obj_list = []
        for doc in document_list:
            doc['_connection'] = self._connection
            obj = Document(doc)
            obj_list.append(obj)
        # Pass it back out
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
    def upload(
        self, pdf, title=None, source=None, description=None,
        related_article=None, published_url=None, access='private',
        project=None, data=None, secure=False, force_ocr=False
    ):
        """
        Upload a PDF or other image file to DocumentCloud.

        You can submit either a pdf opened as a file object or a path
        to a pdf file.

        Example usage:

            # From a file path
            >> documentcloud.documents.upload(
            >>  "/home/ben/sample.pdf",
            >>  "sample title"
            >>)

            # From a file object
            >> pdf = open(path, 'rb')
            >> documentcloud.documents.upload(pdf, "sample title")

        Returns the document that's created as a Document object.

        Based on code developed by Mitchell Kotler and
        refined by Christopher Groskopf.
        """
        # Required pdf parameter
        if hasattr(pdf, 'read'):
            try:
                size = os.fstat(pdf.fileno()).st_size
            except Exception:
                size = 0
            params = {'file': pdf}
            opener = MultipartPostHandler
        elif self.is_url(pdf):
            size = 0
            params = {'file': pdf}
            opener = PostHandler  # URL uploads don't need MultiPart
        else:
            size = os.path.getsize(pdf)
            params = {'file': open(pdf, 'rb')}
            opener = MultipartPostHandler
        # Enforce file size limit of the DocumentCloud API
        if size >= 399999999:
            raise ValueError("The pdf you have submitted is over the \
DocumentCloud API's 400MB file size limit. Split it into smaller pieces \
and try again.")
        # Optional parameters
        if title:
            params['title'] = title
        else:
            # Set it to the file name
            if hasattr(pdf, 'read'):
                params['title'] = pdf.name.split(os.sep)[-1].split(".")[0]
            else:
                params['title'] = pdf.split(os.sep)[-1].split(".")[0]
        if source:
            params['source'] = source
        if description:
            params['description'] = description
        if related_article:
            params['related_article'] = related_article
        if published_url:
            params['published_url'] = published_url
        if access:
            params['access'] = access
        if project:
            params['project'] = project
        if data:
            for key, value in list(data.items()):
                is_valid_data_keyword(key)
                params['data[%s]' % key] = value
        if secure:
            params['secure'] = 'true'
        if force_ocr:
            params['force_ocr'] = 'true'
        # Make the request
        response = self._make_request(
            self.BASE_URI + 'upload.json',
            params,
            opener=opener
        )
        # Pull the id from the response
        response_id = json.loads(response.decode("utf-8"))['id'].split("-")[0]
        # Get the document and return it
        return self.get(response_id)

    @credentials_required
    def upload_directory(
        self, path, source=None, description=None,
        related_article=None, published_url=None, access='private',
        project=None, data=None, secure=False, force_ocr=False
    ):
        """
        Uploads all the PDFs in the provided directory.

        Example usage:

            >> documentcloud.documents.upload_directory("/home/ben/pdfs/")

        Returns a list of the documents created during the upload.

        Based on code developed by Mitchell Kotler and refined
        by Christopher Groskopf.
        """
        # Loop through the path and get all the files
        path_list = []
        for (dirpath, dirname, filenames) in os.walk(path):
            path_list.extend([
                os.path.join(dirpath, i) for i in filenames
                if i.lower().endswith(".pdf")
            ])
        # Upload all the pdfs
        obj_list = []
        for pdf_path in path_list:
            obj = self.upload(
                pdf_path, source=source, description=description,
                related_article=related_article, published_url=published_url,
                access=access, project=project, data=data, secure=secure,
                force_ocr=force_ocr
            )
            obj_list.append(obj)
        # Pass back the list of documents
        return obj_list

    @credentials_required
    def delete(self, id):
        """
        Deletes a Document.
        """
        self.fetch(
            'documents/%s.json' % id.split("-")[0],
            {'_method': 'delete'},
        )


class ProjectClient(BaseDocumentCloudClient):
    """
    Methods for collecting projects
    """
    def __init__(self, username, password, connection, base_uri=None):
        super(ProjectClient, self).__init__(username, password, base_uri)
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
        Retrieve a particular project using its unique identifier or
        it's title.

        But not both.

        Example usage:

            >> documentcloud.projects.get('arizona-shootings')
        """
        # Make sure the kwargs are kosher
        if id and title:
            raise ValueError("You can only retrieve a Project by id or \
                title, not by both")
        elif not id and not title:
            raise ValueError("You must provide an id or a title to \
                make a request.")
        # Pull the hits
        if id:
            hit_list = [i for i in self.all() if str(i.id) == str(id)]
        elif title:
            hit_list = [
                i for i in self.all() if
                i.title.lower().strip() == title.lower().strip()
            ]
        # Throw an error if there's more than one hit.
        if len(hit_list) > 1:
            raise DuplicateObjectError("There is more than one project that \
                matches your request.")
        # Try to pull the first hit
        try:
            return hit_list[0]
        except IndexError:
            # If it's not there, you know to throw this error.
            raise DoesNotExistError("The resource you've requested does not \
                exist or is unavailable without the proper credentials.")

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
        if description:
            params['description'] = description
        params = urllib.parse.urlencode(params, doseq=True)
        if document_ids:
            # These need to be specially formatted in the style documentcloud
            # expects arrays. The example they provide is:
            # ?document_ids[]=28-boumediene&document_ids[]=207-academy\
            # &document_ids[]=30-insider-trading
            params += "".join([
                '&document_ids[]=%s' % id for id in document_ids
            ])
        response = self._make_request(
            self.BASE_URI + "projects.json",
            params.encode("utf-8")
        )
        new_id = json.loads(response.decode("utf-8"))['project']['id']
        # If it doesn't exist, that suggests the project already exists
        if not new_id:
            raise DuplicateObjectError("The Project title you tried to create \
                already exists")
        # Fetch the actual project object from the API and return that.
        return self.get(new_id)

    @credentials_required
    def get_or_create_by_title(self, title):
        """
        Fetch a title, if it exists. Create it if it doesn't.

        Returns a tuple with the object first, and then a boolean that
        indicates whether or not the object was created fresh. True means it's
        brand new.
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
        self.fetch(
            'projects/%s.json' % id,
            {'_method': 'delete'},
        )

#
# API objects
#


@six.python_2_unicode_compatible
class BaseAPIObject(object):
    """
    An abstract version of the objects returned by the API.
    """
    def __init__(self, d):
        self.__dict__ = d

    def __repr__(self):
        return '<%s: %s>' % (self.__class__.__name__, self.__str__())

    def __str__(self):
        return six.text_type(self.title)


class Annotation(BaseAPIObject):
    """
    An annotation earmarked inside of a Document.
    """
    def __init__(self, d):
        self.__dict__ = d

    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def __str__(self):
        return six.text_type('')

    def get_location(self):
        """
        Return the location as a good
        """
        image_string = self.__dict__['location']['image']
        image_ints = list(map(int, image_string.split(",")))
        return Location(*image_ints)
    location = property(get_location)


class DocumentDataDict(dict):
    """
    The key/value store DocumentCloud allows with each Document.

    Functions the same as a standard Python dictionary, with two exception:
    key names protected by DocumentCloud are restricted and only strings
    are allowed.

    If you try to set an integer or other type as a key or value it will
    throw a TypeError.
    """
    def __init__(self, *args, **kwargs):
        for d in args:
            for key, value in d.items():
                self.validate_key(key)
                self.validate_value(value)
        dict.__init__(self, *args, **kwargs)

    def __setitem__(self, key, value):
        self.validate_key(key)
        self.validate_value(value)
        dict.__setitem__(self, key, value)

    def validate_key(self, key):
        is_valid_data_keyword(key)
        if not isinstance(key, six.string_types):
            raise TypeError("data attribute keys must be strings")

    def validate_value(self, value):
        if not isinstance(value, six.string_types):
            raise TypeError("data attribute values must be strings")


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
            title=self.title or '',
            source=self.source or '',
            description=self.description or '',
            related_article=self.resources.related_article or '',
            published_url=self.resources.published_url or '',
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
        self.__dict__['contributor_organization'] = \
            obj.contributor_organization
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
        # Make sure a dict got passed it
        if not isinstance(data, type({})):
            raise TypeError("This attribute must be a dictionary.")
        # Set the attribute
        self.__dict__['data'] = DocumentDataDict(data)

    def get_data(self):
        """
        Fetch the data field if it does not exist.
        """
        try:
            return DocumentDataDict(self.__dict__['data'])
        except KeyError:
            self._lazy_load()
            return DocumentDataDict(self.__dict__['data'])
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
            for type, entity_list in list(entities.items()):
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
            req = urllib.request.Request(
                url,
                headers={'User-Agent': "python-documentcloud"}
            )
            return urllib.request.urlopen(req).read()
        else:
            raise NotImplementedError(
                "Currently, DocumentCloud only allows you to access this \
resource on public documents."
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
        return url

    def get_page_text(self, page):
        """
        Downloads and returns the full text of a particular page
        in the document.
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
        return template.replace(
            "{page}",
            str(page)
        ).replace("{size}", "small")
    small_image_url = property(get_small_image_url)

    def get_thumbnail_image_url(self, page=1):
        """
        Returns the URL for the thumbnail sized image of a single page.

        The page kwarg specifies which page to return. One is the default.
        """
        template = self.resources.page.get('image')
        return template.replace(
            "{page}",
            str(page)
        ).replace("{size}", "thumbnail")
    thumbnail_image_url = property(get_thumbnail_image_url)

    def get_normal_image_url(self, page=1):
        """
        Returns the URL for the "normal" sized image of a single page.

        The page kwarg specifies which page to return. One is the default.
        """
        template = self.resources.page.get('image')
        return template.replace(
            "{page}",
            str(page)
        ).replace("{size}", "normal")
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
        return [self.get_small_image_url(i) for i in range(1, self.pages + 1)]
    small_image_url_list = property(get_small_image_url_list)

    def get_thumbnail_image_url_list(self):
        """
        Returns a list of the URLs for the thumbnail sized image of every page.
        """
        return [
            self.get_thumbnail_image_url(i) for i in range(1, self.pages + 1)
        ]
    thumbnail_image_url_list = property(get_thumbnail_image_url_list)

    def get_normal_image_url_list(self):
        """
        Returns a list of the URLs for the normal sized image of every page.
        """
        return [self.get_normal_image_url(i) for i in range(1, self.pages + 1)]
    normal_image_url_list = property(get_normal_image_url_list)

    def get_large_image_url_list(self):
        """
        Returns a list of the URLs for the large sized image of every page.
        """
        return [self.get_large_image_url(i) for i in range(1, self.pages + 1)]
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
        Updates the related article back in the resources object so your
        changes can be property reflected in any future "puts."
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
        Returns the url where the record is published if one has been provided.
        """
        return self.resources.published_url
    published_url = property(get_published_url, set_published_url)


class DocumentSet(list):
    """
    A custom class for document lists associated with projects.

    Allows some tweaks, like preventing duplicate documents
    from getting into the list and ensuring that only Document
    objects are appended.
    """
    def append(self, obj):
        # Verify that the user is trying to add a Document object
        if not isinstance(obj, Document):
            raise TypeError("Only Document objects can be added to the \
document_list")
        # Check if the object is already in the list
        if obj.id in [i.id for i in list(self.__iter__())]:
            raise DuplicateObjectError("This object already exists in \
the document_list")
        # If it's all true, append it.
        super(DocumentSet, self).append(copy.copy(obj))


class Entity(BaseAPIObject):
    """
    Keywords and such extracted from the document by OpenCalais.
    """
    @property
    def title(self):
        return self.value

    def __str__(self):
        return six.text_type(self.value)


@six.python_2_unicode_compatible
class Location(object):
    """
    The location of an Annotation.
    """
    def __repr__(self):
        return '<%s>' % self.__class__.__name__

    def __str__(self):
        return six.text_type('')

    def __init__(self, top, right, bottom, left):
        self.top = top
        self.right = right
        self.bottom = bottom
        self.left = left


class Mention(BaseAPIObject):
    """
    A mention of a search found in the document.
    """
    @property
    def title(self):
        return self.page

    def __str__(self):
        return six.text_type("Page %s" % (self.page))


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
            if value is None:
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
            title=self.title or '',
            description=self.description or '',
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
            obj_list = DocumentSet([
                self._connection.documents.get(i) for i in self.document_ids
            ])
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
            raise DoesNotExistError("The resource you've requested does not \
exist or is unavailable without the proper credentials.")
        return matches[0]


class Resource(BaseAPIObject):
    """
    The resources associated with a Document. Hyperlinks and such.
    """
    def __repr__(self):
        return '<%ss>' % self.__class__.__name__

    def __str__(self):
        return six.text_type('')

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


RESERVED_KEYWORDS = [
    'person', 'organization', 'place', 'term', 'email', 'phone',
    'city', 'state', 'country', 'title', 'description', 'source',
    'account', 'group', 'project', 'projectid', 'document', 'access',
    'filter',
]


def is_valid_data_keyword(keyword):
    """
    Accepts a keyword submitted to the Document's "data" attribute and verifies
    that is is safe and not one of the reserved words DocumentCloud does not
    allow.

    Returns True is keyword is safe. Raises ValueError if it is not.

    See: https://github.com/documentcloud/documentcloud/blob/master/config/\
initializers/entity_map.rb#L22
    And: https://github.com/datadesk/python-documentcloud/issues/81
    """
    if keyword in RESERVED_KEYWORDS:
        raise ValueError("The key %s is reserved by DocumentCloud. \
You can't use it in 'data'" % keyword)
    else:
        return True
