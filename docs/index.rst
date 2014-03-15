:tocdepth: 2

====================
python-documentcloud
====================

A simple Python wrapper for the `DocumentCloud API <http://www.documentcloud.org/api/>`_

* Code repository: `https://github.com/datadesk/python-documentcloud <https://github.com/datadesk/python-documentcloud>`_
* Issues: `https://github.com/datadesk/python-documentcloud/issues <https://github.com/datadesk/python-documentcloud/issues>`_
* Packaging: `[https://pypi.python.org/pypi/python-documentcloud <[https://pypi.python.org/pypi/python-documentcloud>`_
* Testing: `https://travis-ci.org/datadesk/python-documentcloud <https://travis-ci.org/datadesk/python-documentcloud>`_
* Coverage: `https://coveralls.io/r/datadesk/python-documentcloud <https://coveralls.io/r/datadesk/python-documentcloud>`_

Features
========

* Retrieve and edit documents and projects, both public and private, from `documentcloud.org <http://www.documentcloud.org/>`_
* Upload PDFs into your documentcloud.org account and organize them into projects
* Download text, images and entities extracted from your PDFs by DocumentCloud

Getting started
===============

This tutorial will walk you through the process of installing python-documentment and making your first requests.

Installation
------------

Provided that you have `pip <http://pypi.python.org/pypi/pip>`_ installed, you can install the library like so: ::

    $ pip install python-documentcloud

Creating a client
-----------------

Before you can interact with DocumentCloud, you first must import the library and initialize a client to talk with the site on your behalf. ::

    >>> from documentcloud import DocumentCloud
    >>> client = DocumentCloud()

Since we didn't provide any log-in credentials, the client above will only be able to access published documents. If have an account at DocumentCloud and want to use that, you can provide the crendentials to the client. ::

    >>> client = DocumentCloud(USERNAME, PASSWORD)

Searching for documents
-----------------------

You can now you use client to interact with DocumentCloud. A search for documents about `journalist Ruben Salazar <http://en.wikipedia.org/wiki/Rub%C3%A9n_Salazar>`_ would look like this: ::

    >>> obj_list = client.documents.search("Ruben Salazar")
    >>> # Let's grab the first one and look at it
    >>> obj = obj_list[0]
    >>> obj
    <Document: Final OIR Report>

Interacting with a document
---------------------------

Once you have you hands on a document object, you can interact with the metadata stored at documentcloud.org. Here's a sample: ::

    >>> print obj.title
    Final OIR Report
    >>> print obj.id
    71072-oir-final-report
    >>> print obj.contributor_organization
    Los Angeles Times
    >>> print obj.canonical_url
    http://www.documentcloud.org/documents/71072-oir-final-report.html

You can even download the PDF, page images and full text. ::

    >>> obj.large_image_url
    ...
    >>> obj.large_image
    ...
    >>> obj.full_text
    ...
    >>> obj.pdf
    ...

Uploading a document
--------------------

You can upload a PDF document from your local machine to documentcloud.org. Here's how: ::

    >>> from documentcloud import DocumentCloud
    >>> client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD)
    >>> obj = client.documents.upload("/home/ben/pdfs/myfile.pdf")

And you don't have to provide a path, you can also upload a file object. ::

    >>> from documentcloud import DocumentCloud
    >>> client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD)
    >>> pdf_ = open("/home/ben/pdfs/myfile.pdf", "rb")
    >>> obj = client.documents.upload(pdf)

Uploading a directory of documents as a project
-----------------------------------------------

Here's how to upload a directory full of documents and add them all to a new project. Be warned, this will upload any documents in directories inside the path you specify. ::

    >>> # Connect to documentcloud
    >>> from documentcloud import DocumentCloud
    >>> client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD)
    >>> # Create the project
    >>> project, created = client.projects.get_or_create_by_title("Groucho Marx's FBI file")
    >>> # Upload all the pdfs
    >>> obj_list = client.documents.upload_directory('/home/ben/pdfs/groucho_marx/')
    >>> # Add the newly created documents to the project
    >>> project.document_list = obj_list
    >>> # Save the changes to the project
    >>> project.put()

Securely uploading a document
-----------------------------

How to upload a document, but prevent it from being sent to DocumentCloud's third-party services like OpenCalais.

    >>> from documentcloud import DocumentCloud
    >>> client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD)
    >>> obj = client.documents.upload("/home/ben/pdfs/myfile.pdf", secure=True)

Uploading a PDF from a URL
--------------------------

How to read a PDF document from a URL on the World Wide Web and upload it to DocumentCloud without saving it to your local hard drive.

    >>> from documentcloud import DocumentCloud
    >>> import urllib, cStringIO
    >>> # Download the URL with urllib
    >>> url = "http://myhost.org/interesting-doc.pdf"
    >>> data = urllib.urlopen(url).read()
    >>> # Stuff it in a file object with cStringIO
    >>> file_obj = cStringIO.StringIO(data)
    >>> # Upload that to DocumentCloud
    >>> client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD)
    >>> obj = client.documents.upload(file_obj)

Documents
=========

Methods for drawing down, editing and uploading data about documents.

Retrieval
---------

.. function:: client.documents.get(id)

   Return the document with the provided DocumentCloud identifer. ::

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> client.documents.get('71072-oir-final-report')
        <Document: Final OIR Report>


.. function:: client.documents.search(keyword)

   Return a list of documents that match the provided keyword. ::

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud()
        >>> obj_list = client.documents.search('Ruben Salazar')
        >>> obj_list[0]
        <Document: Final OIR Report>

Editing
-------

.. method:: document_obj.put()

   Save changes to a document back to DocumentCloud. You must be authorized to make these changes. Only the ``title``, ``source``, ``description``, ``related_article``, ``published_url``, ``access`` and ``data`` attributes may be edited. ::

        >>> # Grab a document
        >>> obj = client.documents.get('71072-oir-final-report')
        >>> print obj.title
        Draft OIR Report
        >>> # Change its title
        >>> obj.title = "Brand new title"
        >>> print obj.title
        Brand New Title
        >>> # Save those changes
        >>> obj.put()

.. method:: document_obj.delete()

   Delete a document from DocumentCloud. You must be authorized to make these changes. ::

        >>> obj = client.documents.get('71072-oir-final-report')
        >>> obj.delete()

.. method:: document_obj.save()

    An alias for ``put`` that saves changes back to DocumentCloud.

Uploading
---------

.. function:: client.documents.upload(pdf, title=None, source=None, description=None, related_article=None, published_url=None, access='private', project=None, data=None, secure=False)

   Upload a PDF to DocumentCloud. You must be authorized to do this. Returns the object representing the new record you've created. You can submit either a file path or a file object.

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> new_id = client.documents.upload("/home/ben/test.pdf", "Test PDF")
        >>> # Now fetch it
        >>> client.documents.get(new_id)
        <Document: Test PDF>

.. function:: client.documents.upload_directory(pdf, source=None, description=None, related_article=None, published_url=None, access='private', project=None, data=None, secure=False)

   Searches through the provided path and attempts to upload all the PDFs it can find. Metadata provided to the other keyword arguments will be recorded for all uploads. Returns a list of document objects that are created. Be warned, this will upload any documents in directories inside the path you specify.

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD)
        >>> obj_list = client.documents.upload_directory('/home/ben/pdfs/groucho_marx/')

Metadata
--------

.. attribute:: document_obj.access

    The privacy level of the resource within the DocumentCloud system. It will be either ``public``, ``private`` or ``organization``, the last of which means the is only visible to members of the contributors organization. Can be edited and saved with a put command.

.. attribute:: document_obj.annotations

    A list of the annotations users have left on the document. The data are modeled by their own Python class, defined in the :ref:`annotations` section.

        >>> obj = client.documents.get('83251-fbi-file-on-christopher-biggie-smalls-wallace')
        >>> obj.annotations
        [<Annotation>, <Annotation>, <Annotation>, <Annotation>, <Annotation>]

.. attribute:: document_obj.canonical_url

    The URL where the document is hosted at documentcloud.org.

.. attribute:: document_obj.contributor

    The user who originally uploaded the document.

.. attribute:: document_obj.contributor_organization

    The organizational affiliation of the user who originally uploaded the document.

.. attribute:: document_obj.created_at

    The date and time that the document was created, in Python's datetime format.

.. attribute:: document_obj.data

    A dictionary containing supplementary data linked to the document. This can any old thing. It's useful if you'd like to store additional metadata. Can be edited and saved with a put command.

    Some keywords are reserved by DocumentCloud and you'll get an error if you try to submit them here. They are: person, organization, place, term, email, phone, city, state, country, title, description, source, account, group, project, projectid, document, access, filter.

        >>> obj = client.documents.get('83251-fbi-file-on-christopher-biggie-smalls-wallace')
        >>> obj.data
        {'category': 'hip-hop', 'byline': 'Ben Welsh', 'pub_date': datetime.date(2011, 3, 1)}

.. attribute:: document_obj.description

    A summary of the document. Can be edited and saved with a put command.

.. attribute:: document_obj.entities

    A list of the entities extracted from the document by `OpenCalais <http://www.opencalais.com/>`_. The data are modeled by their own Python class, defined in the :ref:`entities` section.

        >>> obj = client.documents.get('83251-fbi-file-on-christopher-biggie-smalls-wallace')
        >>> obj.entities
        [<Entity: Angeles>, <Entity: FD>, <Entity: OO>, <Entity: Los Angeles>, ...

.. attribute:: document_obj.full_text

    Returns the full text of the document, as extracted from the original PDF by DocumentCloud. Results may vary, but this will give you what they got. Currently, DocumentCloud only makes this available for public documents.

        >>> obj = client.documents.get('71072-oir-final-report')
        >>> obj.full_text
        "Review of the Los Angeles County Sheriff's\nDepartment's Investigation into the\nHomicide of Ruben Salazar\nA Special Report by the\nLos Angeles County Office of Independent Review\n ...

.. attribute:: document_obj.full_text_url

    Returns the URL that contains the full text of the document, as extracted from the original PDF by DocumentCloud. 

.. attribute:: document_obj.id

    The unique identifer of the document in DocumentCloud's system. Typically this is a string that begins with a number, like ``83251-fbi-file-on-christopher-biggie-s.malls-wallace``

.. attribute:: document_obj.large_image

    Returns the binary data for the "large" sized image of the document's first page. If you would like the data for some other page, pass the page number into ``document_obj.get_large_image(page)``. Currently, DocumentCloud only makes this available for public documents.

.. attribute:: document_obj.large_image_url

    Returns a URL containing the "large" sized image of the document's first page. If you would like the URL for some other page, pass the page number into ``document_obj.get_large_image_url(page)``.

.. attribute:: document_obj.large_image_url_list

    Returns a list of URLs for the "large" sized image of every page in the document.

.. attribute:: document_obj.mentions

    When the document has been retrieved via a search, this returns a list of places the search keywords appear in the text. The data are modeled by their own Python class, defined in the :ref:`mentions` section.

        >>> obj_list = client.documents.search('Christopher Wallace')
        >>> obj = obj_list[0]
        >>> obj.mentions
        [<Mention: Page 2>, <Mention: Page 3> ....

.. attribute:: document_obj.normal_image

    Returns the binary data for the "normal" sized image of the document's first page. If you would like the data for some other page, pass the page number into ``document_obj.get_normal_image(page)``. Currently, DocumentCloud only makes this available for public documents.

.. attribute:: document_obj.normal_image_url

    Returns a URL containing the "normal" sized image of the document's first page. If you would like the URL for some other page, pass the page number into ``document_obj.get_normal_image_url(page)``.

.. attribute:: document_obj.normal_image_url_list

    Returns a list of URLs for the "normal" sized image of every page in the document.

.. attribute:: document_obj.pages

    The number of pages in the document.

.. attribute:: document_obj.pdf

    Returns the binary data for document's original PDF file. Currently, DocumentCloud only makes this available for public documents.

.. attribute:: document_obj.pdf_url

    Returns a URL containing the binary data for document's original PDF file.

.. attribute:: document_obj.published_url

    Returns an URL outside of documentcloud.org where this document has been published.

.. attribute:: document_obj.related_article

    Returns an URL for a news story related to this document.

.. attribute:: document_obj.sections

    A list of the sections earmarked in the text by a user. The data are modeled by their own Python class, defined in the :ref:`sections` section.

        >>> obj = client.documents.get('74103-report-of-the-calpers-special-review')
        >>> obj.sections
        [<Section: Letter to Avraham Shemesh and Richard Resller of SIM Group>, <Section: Letter to Ralph Whitworth, founder of Relational Investors>, ...

.. attribute:: document_obj.small_image

    Returns the binary data for the "small" sized image of the document's first page. If you would like the data for some other page, pass the page number into ``document_obj.get_small_image(page)``. Currently, DocumentCloud only makes this available for public documents.

.. attribute:: document_obj.small_image_url

    Returns a URL containing the "small" sized image of the document's first page. If you would like the URL for some other page, pass the page number into ``document_obj.get_small_image_url(page)``.

.. attribute:: document_obj.small_image_url_list

    Returns a list of URLs for the "small" sized image of every page in the document.

.. attribute:: document_obj.source

    The original source of the document. Can be edited and saved with a put command.

.. attribute:: document_obj.thumbnail_image

    Returns the binary data for the "thumbnail" sized image of the document's first page. If you would like the data for some other page, pass the page number into ``document_obj.get_thumbnail_image(page)``. Currently, DocumentCloud only makes this available for public documents.

.. attribute:: document_obj.thumbnail_image_url

    Returns a URL containing the "thumbnail" sized image of the document's first page. If you would like the URL for some other page, pass the page number into ``document_obj.get_small_thumbnail_url(page)``.

.. attribute:: document_obj.thumbnail_image_url_list

    Returns a list of URLs for the "small" sized image of every page in the document.

.. attribute:: document_obj.title

    The name of the document. Can be edited and saved with a put command.

.. attribute:: document_obj.updated_at

    The date and time that the document was last updated, in Python's datetime format.

Projects
========

Methods for drawing down, editing and uploading data about DocumentCloud projects. A project is a group of documents.

Retrieval
---------

.. function:: client.projects.get(id=None, title=None)

   Return the project with the provided DocumentCloud identifer. You can retrieve projects using either the `id` or `title`. ::

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> # Fetch using the id
        >>> obj = client.projects.get(id='816')
        >>> obj
        <Project: The Ruben Salazar Files>
        >>> # Fetch using the title
        >>> obj = client.projects.get(title='The Ruben Salazar Files')
        >>> obj
        <Project: The Ruben Salazar Files>

.. function:: client.projects.get_by_id(id)

   Return the project with the provided id. Operates the same as `client.projects.get`.

.. function:: client.projects.get_by_title(title)

   Return the project with the provided title. Operates the same as `client.projects.get`.

.. function:: client.projects.all()

   Return all projects for the authorized DocumentCloud account  ::

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> obj_list = client.projects.all()
        >>> obj_list[0]
        <Project: Ruben Salazar>

Editing
-------

.. method:: project_obj.put()

   Save changes to a project back to DocumentCloud. You must be authorized to make these changes. Only the `title`, `source`, `document_list` attributes may be edited. ::

        >>> obj = client.projects.get('816')
        >>> obj.title = "Brand new title"
        >>> obj.put()

.. method:: project_obj.delete()

   Delete a project from DocumentCloud. You must be authorized to make these changes. ::

        >>> obj = client.projects.get('816')
        >>> obj.delete()

.. method:: project_obj.save()

    An alias for ``put`` that saves changes back to DocumentCloud.

Creation
--------

.. method:: client.projects.create(title=None,description=None, document_ids=None)

   Create a new project on DocumentCloud. You must be authorized to do this. Returns the object representing the new record you've created.

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> obj = client.projects.create("New project")
        >>> obj
        <Project: New project>

.. method:: client.projects.get_or_create_by_title(title=None)

   Fetch the project with provided name, or create it if it does not exist. You must be authorized to do this. Returns a tuple. An object representing the record comes first. A boolean that reports whether or not the objects was created fresh comes second. It is true when the record was created, false when it was found on the site already.

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> # The first time it will be created and added to documentcloud.org
        >>> obj, created = client.projects.get_or_create_by_title("New project")
        >>> obj, created
        <Project: New project>, True
        >>> # The second time it will be fetched from documentcloud.org
        >>> obj, created = client.projects.get_or_create_by_title("New project")
        >>> obj, created
        <Project: New project>, False

Metadata
--------

.. attribute:: project_obj.description

    A summary of the project. Can be edited and saved with a put command.

.. attribute:: project_obj.document_ids

    A list that contains the unique identifier of the documents assigned to this project. Cannot be edited. Edit the document_list instead.

        >>> obj = client.projects.get('816')
        >>> obj.document_ids
        [u'19419-times-columnist-ruben-salazar-killed-by-bullet', u'19420-usps-american-journalists-stamp', u'19280-fbi-file-on-el-paso-investigations', u'19281-letter-from-the-lapd-chief', ...

.. attribute:: project_obj.document_list

    A list that documents assigned to this project. Can be expanded by appending new documents to the list or cleared by reassigning it as an empty list and then issuing the put command.

        >>> obj = client.projects.get('816')
        >>> obj.document_list
        [<Document: Times Columnist Ruben Salazar Slain by Tear-gas Missile>, <Document: Salazar's Legacy Lives On>, <Document: Cub Reporter Catches Attention of El Paso FBI>, ...

..  method:: project_obj.get_document(id)

        Retrieves a particular document from the project using the provided DocumentCloud identifer.

.. attribute:: project_obj.id

    The unique identifer of the project in DocumentCloud's system. Typically this is a number.

.. attribute:: project_obj.title

    The name of the project. Can be edited and saved with a put command.

Other data
===========

Other types of data provided by the DocumentCloud system.

.. _annotations:

Annotations
-----------

Notes left in documents.

.. attribute:: annotation_obj.access

    The privacy level of the resource within the DocumentCloud system. It will be either ``public`` or ``private``.

.. attribute:: annotation_obj.description

    Space for a lengthy text block that will be published below the highlighted text in the DocumentCloud design.

.. attribute:: annotation_obj.id

    The unique identifer of the document in DocumentCloud's system.

.. attribute:: annotation_obj.location

    The location of where the annotation appears on the document's page. Defined by the :ref:`locations` class.

.. attribute:: annotation_obj.page

    The page where the annotation appears.

.. attribute:: annotation_obj.title

    The name of the annotation, which appears in the table of contents and above the highlighted text when published by DocumentCloud.

.. _entities:

Entities
--------

Keywords extracted from documents with OpenCalais.

.. attribute:: location_obj.revelance

    The weighting associated with this connection by OpenCalais. Higher numbers are supposed to be more relevant.

.. attribute:: location_obj.type

    The category of entity the value belongs to.

.. attribute:: location_obj.value

    The name of the entity extracted from the document (i.e. "Los Angeles" or "Museum of Modern Art")

.. _locations:

Locations
---------

The location where :ref:`annotations` are placed within a document.

.. attribute:: location_obj.bottom

    The value of the bottom edge of an annotation.

.. attribute:: location_obj.left

    The value of the left edge of an annotation.

.. attribute:: location_obj.right

    The value of the right edge of an annotation.

.. attribute:: location_obj.top

    The value of the top edge of an annotation.

.. _mentions:

Mentions
--------

Mentions of a search keyword found in one of the documents.

.. attribute:: mention_obj.page

    The page where the mention occurs.

.. attribute:: mention_obj.text

    The text surrounding the mention of the keyword.

.. _sections:

Sections
--------

Sections of the documents earmarked by users.

.. attribute:: section_obj.title

    The name of the section.

.. attribute:: section_obj.page

    The page where the section begins.

Changelog
=========

0.16
----

- Continuous integration testing with TravisCI
- Fixed bug with empty strings in Document descriptions
- Raise errors when a user tries to save a data keyword reserved by DocumentCloud
- Allow all-caps file extensions
- Retry requests that fail with an increasing backoff delay
- Fixed a bug in how titles are assigned to a file object
- Added access checks when retrieving txt, pdf, img about a document

0.15
----

* File objects can now be submitted for uploading
* Added more support for unicode data thanks to contributions by `Shane Shifflet <https://twitter.com/#!/shaneshifflett>`_.
* Smarter lazy loading of Document attributes missing from a search

0.14
----
* Added ``data`` attribute on Document for storing dictionaries of arbitrary metadata
* Added ``secure`` option for Document uploads to prevent data from being sent to OpenCalais
* Added ``save`` alias on Document and Project objects that uses the pre-existing ``put`` command
* Fixed to url encoding to makes the system more unicode friendly
* Added all Document upload arguments to ``upload_directory`` method

0.13
----

* ``upload_directory`` method for documents

0.12
----

* ``get_or_create_by_title`` method for projects
* Document and project creation methods now return an object, not the new id.
* Projects can pulled by id or by title


0.11
----

* Document search now returns ``mentions`` of the keyword in the documents
* ``related_url`` and ``published_url`` attributes now more easily accessible
* ``normal`` sized images now available

Credits
=======

This project would not be possible without the generous work of people like:

* `The DocumentCloud team <https://www.documentcloud.org/about>`_ and particularly `Jeremy Ashkenas <https://github.com/jashkenas>`_.
* `Chris Amico <https://github.com/eyeseast>`_, `Christopher Groskopf <https://github.com/onyxfish/>`_ and `Mitchell Kotler <http://www.muckrock.com/blog/using-the-documentcloud-api/>`_, who broke ground with great code that I've shamelessly lifted and adapted for this module.
* Fixes from friendly people like `Joe Germuska <https://github.com/JoeGermuska>`_ and `Shane Shifflet <https://twitter.com/#!/shaneshifflett>`.
