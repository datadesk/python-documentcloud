===========
Other data
===========

Other types of data provided by the DocumentCloud system.

.. raw:: html

   <hr>

.. _annotations:

Annotations
-----------

Notes left in :doc:`documents </documents>`.

.. attribute:: annotation_obj.access

    The privacy level of the resource within the DocumentCloud system. It will be either ``public`` or ``private``.

.. attribute:: annotation_obj.description

    Space for a lengthy text block that will be published below the highlighted text in the DocumentCloud design.

.. attribute:: annotation_obj.id

    The unique identifer of the document in DocumentCloud's system.

.. attribute:: annotation_obj.location

    The location of where the annotation appears on the document's page. Defined by the :ref:`locations` class.

.. attribute:: annotation_obj.page

    The page where the annotation appears.

.. attribute:: annotation_obj.title

    The name of the annotation, which appears in the table of contents and above the highlighted text when published by DocumentCloud.

.. raw:: html

   <hr>

.. _entities:

Entities
--------

Keywords extracted from :doc:`documents </documents>` with OpenCalais.

.. raw:: html

   <hr>

.. _locations:

Locations
---------

The location where :ref:`annotations` are placed within a document.

.. raw:: html

   <hr>

.. _sections:

Sections
--------

Sections of the :doc:`documents </documents>` earmarked by users.

.. attribute:: section_obj.title

    The name of the section.

.. attribute:: section_obj.page

    The page where the section begins.


