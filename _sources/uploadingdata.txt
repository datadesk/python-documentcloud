==============
Uploading data
==============

Methods for posting new data up to documentcloud.org

.. raw:: html

   <hr>

Documents
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

Projects
--------

.. method:: client.projects.create(title=None,description=None, document_ids=None)

   Create a new project on DocumentCloud. You must be authorized to do this. Returns the DocumentCloud identifer of the new record you've created.

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> new_id = client.projects.upload("New project")
        >>> # Now fetch it
        >>> client.projects.get(new_id)
        <Project: New project>



