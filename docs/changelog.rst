Changelog
---------

1.0.4
~~~~~

* Throw an error when integers or other non-strings are included in Document metadata dictionaries
* Added a number of keyword arguments to documents searches to pull a single page, change page size and request document metadata in result
* Temporarily removed SSL from image and text URLs to workaround bugs underlying dependencies

1.0.3
~~~~~

* Encoding bug fix for metadata associated with documents via API


1.0.2
~~~~~

* URLs to PDFs can now be submitted for upload
* Refactored setup.py and tests to be less complex

1.0.1
~~~~~

* Python 3.4 testing
* 400MB upload limit to match DocumentCloud's API restrictions

1.0.0
~~~~~

* Adopted `semantic versioning <http://semver.org/>`_ without breaking existing packages on PyPI
* Fixed bugs with ``get_page_text``
* Added keyword argument during initialization that allows you to override the ``BASE_URI`` and connect with independent clones of DocumentCloud. Contributed by `Adi Eyal <https://github.com/adieyal>`_.
* Refactored unit tests to run more quickly and require fewer web requests
* Documentation moved from the gh-pages branch to master and refactored to be published via `ReadTheDocs <http://readthedocs.org>`_.

0.2
~~~

* Python 3 support
* PEP8 and PyFlakes compliance
* Coverage reports on testing via coveralls.io


0.16
~~~~

* Continuous integration testing with TravisCI
* Fixed bug with empty strings in Document descriptions
* Raise errors when a user tries to save a data keyword reserved by DocumentCloud
* Allow all-caps file extensions
* Retry requests that fail with an increasing backoff delay
* Fixed a bug in how titles are assigned to a file object
* Added access checks when retrieving txt, pdf, img about a document

0.15
~~~~

* File objects can now be submitted for uploading
* Added more support for unicode data thanks to contributions by `Shane Shifflet <https://twitter.com/#!/shaneshifflett>`_.
* Smarter lazy loading of Document attributes missing from a search

0.14
~~~~

* Added ``data`` attribute on Document for storing dictionaries of arbitrary metadata
* Added ``secure`` option for Document uploads to prevent data from being sent to OpenCalais
* Added ``save`` alias on Document and Project objects that uses the pre-existing ``put`` command
* Fixed to url encoding to makes the system more unicode friendly
* Added all Document upload arguments to ``upload_directory`` method

0.13
~~~~

* ``upload_directory`` method for documents

0.12
~~~~

* ``get_or_create_by_title`` method for projects
* Document and project creation methods now return an object, not the new id.
* Projects can pulled by id or by title


0.11
~~~~

* Document search now returns ``mentions`` of the keyword in the documents
* ``related_url`` and ``published_url`` attributes now more easily accessible
* ``normal`` sized images now available
