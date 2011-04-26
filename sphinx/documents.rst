=========
Documents
=========

Methods for drawing down, editing and uploading data about documents.

.. raw:: html

   <hr>

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

.. raw:: html

   <hr>

Editing
-------

.. method:: document_obj.put()

   Save changes to a document back to DocumentCloud. You must be authorized to make these changes. Only the ``title``, ``source``, ``description``, ``related_article``, ``published_url`` and ``access`` attributes may be edited. ::

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

.. raw:: html

   <hr>

Uploading
---------

.. method:: client.documents.upload(path, title=None, source=None, description=None, related_article=None, published_url=None, access='private', project=None)

   Upload a PDF to DocumentCloud. You must be authorized to do this. Returns the DocumentCloud identifer of the new record you've created.

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> new_id = client.documents.upload("/home/ben/test.pdf", "Test PDF")
        >>> # Now fetch it
        >>> client.documents.get(new_id)
        <Document: Test PDF>

.. raw:: html

   <hr>

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

.. attribute:: document_obj.description

    A summary of the document. Can be edited and saved with a put command.

.. attribute:: document_obj.entities

    A list of the entities extracted from the document by `OpenCalais <http://www.opencalais.com/>`_. The data are modeled by their own Python class, defined in the :ref:`entities` section.

        >>> obj = client.documents.get('83251-fbi-file-on-christopher-biggie-smalls-wallace')
        >>> obj.entities
        [<Entity: Angeles>, <Entity: FD>, <Entity: OO>, <Entity: Los Angeles>, ...

.. attribute:: document_obj.full_text

    Returns the full text of the document, as extracted from the original PDF by DocumentCloud. Results may vary, but this will give you what they got.

        >>> obj = client.documents.get('71072-oir-final-report')
        >>> obj.full_text
        "Review of the Los Angeles County Sheriff's\nDepartment's Investigation into the\nHomicide of Ruben Salazar\nA Special Report by the\nLos Angeles County Office of Independent Review\n ...

.. attribute:: document_obj.full_text_url

    Returns the URL that contains the full text of the document, as extracted from the original PDF by DocumentCloud. 

.. attribute:: document_obj.id

    The unique identifer of the document in DocumentCloud's system. Typically this is a string that begins with a number, like ``83251-fbi-file-on-christopher-biggie-s.malls-wallace``

.. attribute:: document_obj.large_image

    Returns the binary data for the "large" sized image of the document's first page. If you would like the data for some other page, pass the page number into ``document_obj.get_large_image(page)``.

.. attribute:: document_obj.large_image_url

    Returns a URL containing the "large" sized image of the document's first page. If you would like the URL for some other page, pass the page number into ``document_obj.get_large_image_url(page)``.

.. attribute:: document_obj.large_image_url_list

    Returns a list of URLs for the "large" sized image of every page in the document.

.. attribute:: document_obj.normal_image

    Returns the binary data for the "normal" sized image of the document's first page. If you would like the data for some other page, pass the page number into ``document_obj.get_normal_image(page)``.

.. attribute:: document_obj.normal_image_url

    Returns a URL containing the "normal" sized image of the document's first page. If you would like the URL for some other page, pass the page number into ``document_obj.get_normal_image_url(page)``.

.. attribute:: document_obj.normal_image_url_list

    Returns a list of URLs for the "normal" sized image of every page in the document.

.. attribute:: document_obj.pages

    The number of pages in the document.

.. attribute:: document_obj.pdf

    Returns the binary data for document's original PDF file.

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

    Returns the binary data for the "small" sized image of the document's first page. If you would like the data for some other page, pass the page number into ``document_obj.get_small_image(page)``.

.. attribute:: document_obj.small_image_url

    Returns a URL containing the "small" sized image of the document's first page. If you would like the URL for some other page, pass the page number into ``document_obj.get_small_image_url(page)``.

.. attribute:: document_obj.small_image_url_list

    Returns a list of URLs for the "small" sized image of every page in the document.

.. attribute:: document_obj.source

    The original source of the document. Can be edited and saved with a put command.

.. attribute:: document_obj.thumbnail_image

    Returns the binary data for the "thumbnail" sized image of the document's first page. If you would like the data for some other page, pass the page number into ``document_obj.get_thumbnail_image(page)``.

.. attribute:: document_obj.thumbnail_image_url

    Returns a URL containing the "thumbnail" sized image of the document's first page. If you would like the URL for some other page, pass the page number into ``document_obj.get_small_thumbnail_url(page)``.

.. attribute:: document_obj.thumbnail_image_url_list

    Returns a list of URLs for the "small" sized image of every page in the document.

.. attribute:: document_obj.title

    The name of the document. Can be edited and saved with a put command.

.. attribute:: document_obj.updated_at

    The date and time that the document was last updated, in Python's datetime format.

