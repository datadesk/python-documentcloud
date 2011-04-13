============
Editing data
============

Methods for saving things you do in Python back to documentcloud.org

.. raw:: html

   <hr>

Documents
---------

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

Projects
---------

.. method:: project_obj.put()

   Save changes to a project back to DocumentCloud. You must be authorized to make these changes. Only the `title`, `source`, `document_list` attributes may be edited. ::

        >>> obj = client.projects.get('1339')
        >>> obj.title = "Brand new title"
        >>> obj.put()

.. method:: project_obj.delete()

   Delete a project from DocumentCloud. You must be authorized to make these changes. ::

        >>> obj = client.projects.get('1339')
        >>> obj.delete()


