========
Projects
========

Methods for drawing down, editing and uploading data about DocumentCloud projects. A project is a group of documents.

.. raw:: html

   <hr>

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

   Create a new project on DocumentCloud. You must be authorized to do this. Returns the object representing the new record you've created.

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> obj = client.projects.upload("New project")
        >>> obj
        <Project: New project>

.. raw:: html

   <hr>

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



