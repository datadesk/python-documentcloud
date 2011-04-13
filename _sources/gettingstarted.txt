===============
Getting started
===============

This tutorial will walk you through the process of installing python-documentment and making your first requests.

.. raw:: html

   <hr>

Installation
------------

Provided that you have `pip <http://pypi.python.org/pypi/pip>`_ installed, you can install the library like so: ::

    $ pip install python-documentcloud

.. raw:: html

   <hr>

Creating a client
-----------------

Before you can interact with DocumentCloud, you first must import the library and initialize a client to talk with the site on your behalf. ::

    >>> from documentcloud import DocumentCloud
    >>> client = DocumentCloud()

Since we didn't provide any log-in credentials, the client above will only be able to access published documents. If have an account at DocumentCloud and want to use that, you can provide the crendentials to the client. ::

    >>> client = DocumentCloud(USERNAME, PASSWORD)

.. raw:: html

   <hr>

Searching for documents
-----------------------

You can now you use client to interact with DocumentCloud. A search for documents about `journalist Ruben Salazar <http://en.wikipedia.org/wiki/Rub%C3%A9n_Salazar>`_ would look like this: ::

    >>> obj_list = client.documents.search("Ruben Salazar")
    >>> # Let's grab the first one and look at it
    >>> obj = obj_list[0]
    >>> obj
    <Document: Final OIR Report>

.. raw:: html

   <hr>

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

Move ahead to the sections on :doc:`retrieving </retrievingdata>`, :doc:`editing </editingdata>` and :doc:`uploading </uploadingdata>` data for more detail on what's possible.


















