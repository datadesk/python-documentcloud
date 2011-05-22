=========
Changelog
=========

0.14
----
* Added ``data`` attribute on Document for storing dictionaries of arbitrary metadata
* Added ``secure`` option for Document uploads to prevent data from being sent to OpenCalais
* Added ``save`` alias on Document and Project objects that uses the pre-existing ``put`` command
* Fixed to url encoding to makes the system more unicode friendly
* Added all Document upload arguments to ``upload_directory`` method

0.13
----

* ``upload_directory`` method for documents

0.12
----

* ``get_or_create_by_title`` method for projects
* Document and project creation methods now return an object, not the new id.
* Projects can pulled by id or by title


0.11
----

* Document search now returns ``mentions`` of the keyword in the documents
* ``related_url`` and ``published_url`` attributes now more easily accessible
* ``normal`` sized images now available
