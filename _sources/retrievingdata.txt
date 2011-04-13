===============
Retrieving data
===============

Methods for drawing down data about documents and projects.

.. raw:: html

   <hr>

Documents
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

Projects
--------

.. function:: client.projects.get(id)

   Return the project with the provided DocumentCloud identifer.  ::

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> obj = client.projects.get('1339')
        >>> obj
        <Project: Ruben Salazar>
        >>> obj.document_list[0]
        <Document: Final OIR Report>

.. function:: client.projects.all()

   Return all projects for the authorized DocumentCloud account  ::

        >>> from documentcloud import DocumentCloud
        >>> client = DocumentCloud(USERNAME, PASSWORD)
        >>> obj_list = client.projects.all()
        >>> obj_list[0]
        <Project: Ruben Salazar>

Other sections explain how to :doc:`edit</editingdata>` and :doc:`upload</uploadingdata>` data.


