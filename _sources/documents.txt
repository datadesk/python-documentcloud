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

Attributes
----------

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

    A list of the entities extracted from the document by `OpenCalais <http://www.opencalais.com/>`_. The data are modeled by their own Python class, defined int the :ref:`entities` section.

        >>> obj = client.documents.get('83251-fbi-file-on-christopher-biggie-smalls-wallace')
        >>> obj.entities
        [<Entity: Angeles>, <Entity: FD>, <Entity: OO>, <Entity: Los Angeles>, ...

.. attribute:: document_obj.full_text

    Returns the full text of the document, as extracted from the original PDF by DocumentCloud. Results may vary, but this will give you what they got.

        >>> obj = client.documents.get('71072-oir-final-report')
        >>> obj.full_text[:250]
        "Review of the Los Angeles County Sheriff's\nDepartment's Investigation into the\nHomicide of Ruben Salazar\nA Special Report by the\nLos Angeles County Office of Independent Review\n ...

.. attribute:: document_obj.title

    The name of the Document. Can be edited and saved with a put command.




