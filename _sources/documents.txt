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

   Save changes to a document back to DocumentCloud. You must be authorized to make these changes. Only the `title`, `source`, `description`, `related_article`, `published_url` and `access` attributes may be edited. ::

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


