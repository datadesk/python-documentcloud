========
Projects
========

Methods for drawing down, editing and uploading data about DocumentCloud projects. A project is a group of documents.

.. raw:: html

   <hr>

Retrieval
---------

.. function:: client.projects.get(id)

   Return the project with the provided DocumentCloud identifer.  ::

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> obj = client.projects.get('816')
        >>> obj
        <Project: The Ruben Salazar Files>
        >>> obj.document_list[0]
        <Document: Times Columnist Ruben Salazar Slain by Tear-gas Missile>

.. function:: client.projects.all()

   Return all projects for the authorized DocumentCloud account  ::

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> obj_list = client.projects.all()
        >>> obj_list[0]
        <Project: Ruben Salazar>

.. raw:: html

   <hr>

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

.. raw:: html

   <hr>

Creation
--------

.. method:: client.projects.create(title=None,description=None, document_ids=None)

   Create a new project on DocumentCloud. You must be authorized to do this. Returns the DocumentCloud identifer of the new record you've created.

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> new_id = client.projects.upload("New project")
        >>> # Now fetch it
        >>> client.projects.get(new_id)
        <Project: New project>


