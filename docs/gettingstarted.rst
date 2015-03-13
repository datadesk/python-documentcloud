Getting started
===============

This tutorial will walk you through the process of installing python-documentcloud and making your first requests.

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
    >>> pdf = open("/home/ben/pdfs/myfile.pdf", "rb")
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
