#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests out the DocumentCloud API.

Requires you to set DOCUMENTCLOUD_TEST_USERNAME and DOCUMENTCLOUD_TEST_PASSWORD
as global environment variables.
"""
import os
import sys
import random
import string
import textwrap
import unittest
import StringIO
from copy import copy
from documentcloud import DocumentCloud
from documentcloud import CredentialsMissingError, DuplicateObjectError
from documentcloud import CredentialsFailedError, DoesNotExistError
from documentcloud import Annotation, Document, Project, Section, Entity, Mention

#
# Odds and ends
#

def get_random_string(length=6):
    """
    Generate a random string of letters and numbers
    """
    return unicode(''.join(random.choice(string.letters + string.digits) for i in xrange(length)))

PANGRAMS = {
    'en': 'The quick brown fox jumps over the lazy dog.',
    'da': 'Quizdeltagerne spiste jordbær med fløde, mens cirkusklovnen Wolther spillede på xylofon.',
    'de': 'Falsches Üben von Xylophonmusik quält jeden größeren Zwerg.',
    'el': 'Γαζέες καὶ μυρτιὲς δὲν θὰ βρῶ πιὰ στὸ χρυσαφὶ ξέφωτο.',
    'es': 'El pingüino Wenceslao hizo kilómetros bajo exhaustiva lluvia y frío, añoraba a su querido cachorro.',
    'fr': "Portez ce vieux whisky au juge blond qui fume sur son île intérieure, à côté de l'alcôve ovoïde, où les bûches se consument dans l'âtre, ce qui lui permet de penser à la cænogenèse de l'être dont il est question dans la cause ambiguë entendue à Moÿ, dans un capharnaüm qui, pense-t-il, diminue çà et là la qualité de son œuvre.",
    'ga': "D'fhuascail Íosa, Úrmhac na hÓighe Beannaithe, pór Éava agus Ádhaimh.",
    'hu': 'Árvíztűrő tükörfúrógép.',
    'is': 'Kæmi ný öxi hér ykist þjófum nú bæði víl og ádrepa.',
    'jp': """'いろはにほへとちりぬるを
      わかよたれそつねならむ
      うゐのおくやまけふこえて
      あさきゆめみしゑひもせす""",
    'iw': '? דג סקרן שט בים מאוכזב ולפתע מצא לו חברה איך הקליטה.',
    'pl': 'Pchnąć w tę łódź jeża lub ośm skrzyń fig.',
    'ru': 'чащах юга жил бы цитрус? Да, но фальшивый экземпляр!'
}

#
# Tests
#

class BaseTest(unittest.TestCase):
    """
    A base class for all of our tests.
    """
    def get_version(self):
        """
        Figure out which version of Python we're testing with.
        """
        return float("%s.%s" % sys.version_info[0:2])

    def get_editable_document(self, version):
        """
        Return the slug of the Document set aside for testing
        this version of Python against. 

        We have to set aside a different document for each version
        because Travis CI tests run concurrently and we don't want
        different tests stepping on each other.
        """
        version2slug = {
            "2.5": "351008-lbex-docid-3383445",
            "2.6": "15144-mitchrpt",
            "2.7": "351151-lbex-docid-130036",
        }
        return version2slug[str(version)]

    def get_editable_project(self, version):
        """
        Return the id of the Project set aside for testing
        this version of Python against. 

        We have to set aside a different project for each version
        because Travis CI tests run concurrently and we don't want
        different tests stepping on each other.
        """
        version2slug = {
            "2.5": 11051,
            "2.6": 11048,
            "2.7": 11047,
        }
        return version2slug[str(version)]

    def setUp(self):
        """
        Initialize a bunch of variables we'll use across tests.
        """
        self.test_search = 'Calpers special review'
        self.test_id = '74103-report-of-the-calpers-special-review'
        self.public_client = DocumentCloud()
        self.private_client = DocumentCloud(
            os.environ['DOCUMENTCLOUD_TEST_USERNAME'], 
            os.environ['DOCUMENTCLOUD_TEST_PASSWORD']
        )
        self.fake_client = DocumentCloud("John Doe", "TK")
        self.version = self.get_version()
        self.editable_document = self.get_editable_document(self.version)
        self.editable_project = self.get_editable_project(self.version)


class DocumentTest(BaseTest):
    """"
    Document object related tests.
    """
    def test_search(self):
        """
        Test a search.
        """
        obj_list = self.public_client.documents.search(self.test_search)
        self.assertEqual(type(obj_list), type([]))
        self.assertEqual(type(obj_list[0]), Document)

    def test_search_attrs(self):
        """
        Verify that all the Document attributes exist.
        """
        obj = self.public_client.documents.search(self.test_search)[0]
        attr_list = [
            'access',
            'annotations',
            'canonical_url',
            'contributor',
            'contributor_organization',
            'created_at',
            'description',
            'id',
            'pages',
            'resources',
            'sections',
            'source',
            'title',
            'updated_at',
            'data',
        ]
        for attr in attr_list:
            self.assertTrue(hasattr(obj, attr))

    def test_search_annotations(self):
        """
        Test whether annotations exist.
        """
        obj = self.public_client.documents.search(self.test_search)[0]
        self.assertEqual(type(obj.annotations[0]), Annotation)

    def test_search_sections(self):
        """
        Test whether sections exist.
        """
        obj = self.public_client.documents.get(self.test_id)
        self.assertEqual(type(obj.sections[0]), Section)

    def test_search_entities(self):
        """
        Test whether entities exist.
        """
        obj = self.public_client.documents.get(self.test_id)
        self.assertEqual(type(obj.entities[0]), Entity)

    def test_get(self):
        """
        Test a get request for a particular document.
        """
        obj = self.public_client.documents.get(self.test_id)
        self.assertEqual(type(obj), Document)

    def test_get_attrs(self):
        """
        Verify that all the Document attributes exist.
        """
        obj = self.public_client.documents.get(self.test_id)
        attr_list = [
            'access',
            'annotations',
            'canonical_url',
            'contributor',
            'contributor_organization',
            'created_at',
            'description',
            'id',
            'pages',
            'resources',
            'sections',
            'source',
            'title',
            'updated_at',
            'data',
        ]
        [self.assertTrue(hasattr(obj, attr)) for attr in attr_list]

    def test_get_pdf(self):
        """
        Test if you can pull the PDF
        """
        obj = self.public_client.documents.get(self.test_id)
        self.assertTrue(len(obj.pdf) > 0, True)

#    def test_get_full_text(self):
#        """
#        Test if you can pull the full text
#        """
#        obj = self.public_client.documents.get(self.test_id)
#        try:
#            self.assertTrue(len(obj.full_text) > 0, True)
#        except:
#            self.assertRaises(obj.full_text, NotImplementedError)

    def test_get_images(self):
        """
        Test if you can pull the images
        """
        obj = self.public_client.documents.get(self.test_id)
        self.assertTrue(len(obj.small_image) > 0, True)
        self.assertTrue(len(obj.thumbnail_image) > 0, True)
        self.assertTrue(len(obj.normal_image) > 0, True)
        self.assertTrue(len(obj.large_image) > 0, True)

    def test_get_annotations(self):
        """
        Test whether annotations exist.
        """
        obj = self.public_client.documents.get(self.test_id)
        self.assertEqual(type(obj.annotations[0]), Annotation)

    def test_get_sections(self):
        """
        Test whether sections exist.
        """
        obj = self.public_client.documents.get(self.test_id)
        self.assertEqual(type(obj.sections[0]), Section)

    def test_get_entities(self):
        """
        Test whether entities exist.
        """
        obj = self.public_client.documents.get(self.test_id)
        self.assertEqual(type(obj.entities[0]), Entity)

    def test_get_mentions(self):
        """
        Test whether mentions exist.
        """
        obj = self.public_client.documents.search(self.test_search)[0]
        self.assertEqual(type(obj.mentions[0]), Mention)

    def test_set_data_type_restrictions(self):
        """
        Make sure `data` attribute will only accept a dictionary.
        """
        obj = self.private_client.documents.get(self.test_id)
        obj.data = dict(foo='bar')
        self.assertRaises(TypeError, obj.set_data, "string")
        self.assertRaises(TypeError, obj.set_data, 666)
        self.assertRaises(TypeError, obj.set_data, obj)

    def test_get_put(self):
        """
        Test whether we can put random noise to all the editable fields.
        """
        # Pull the object we'll deface
        obj = self.private_client.documents.get(self.editable_document)
        # Create random strings we will save to the editable attributes
        title = get_random_string()
        source = get_random_string()
        description = get_random_string()
        data = {get_random_string(): get_random_string()}
        if obj.resources.related_article == u'http://documents.latimes.com':
            related_article = u'http://documentcloud.org'
        else:
            related_article = u'http://documents.latimes.com'
        if obj.resources.published_url == u'http://documents.latimes.com':
            published_url = u'http://documentcloud.org'
        else:
            published_url = u'http://documents.latimes.com'
        # Set the random strings our local object's attributes
        obj.title = title
        obj.source = source
        obj.description = description
        obj.data = data
        obj.resources.related_article = related_article
        obj.resources.published_url = published_url
        # Save the changes up to DocumentCloud
        obj.put()
        # Pull the object again and verify the changes stuck
        obj = self.private_client.documents.get(self.editable_document)
        self.assertEqual(obj.title, title)
        self.assertEqual(obj.source, source)
        self.assertEqual(obj.description, description)
        self.assertEqual(obj.data, data)
        self.assertEqual(obj.resources.related_article, related_article)
        self.assertEqual(obj.resources.published_url, published_url)

    def test_reserved_data_namespace(self):
        """
        Make sure the wrapper doesn't let you try to save
        reserved data namespaces.
        """
        # Pull the object we'll deface
        obj = self.private_client.documents.get((self.editable_document)
        black_list = [
            'person', 'organization', 'place', 'term', 'email', 'phone',
            'city', 'state', 'country', 'title', 'description', 'source',
            'account', 'group', 'project', 'projectid', 'document', 'access',
            'filter',
        ]
        for key in black_list:
            self.assertRaises(ValueError, setattr, obj, "data", {key: 'foo'})
        obj.data = dict(boom='bap')

    def test_save(self):
        """
        Test whether the save method properly aliases `put`.
        """
        # Pull the object we'll deface
        obj = self.private_client.documents.get(self.editable_document)
        # Create random strings we will save to the editable attributes
        title = get_random_string()
        obj.title = title
        # Save the changes up to DocumentCloud with the alias
        obj.save()
        # Pull the object again and verify the changes stuck
        obj = self.private_client.documents.get(self.editable_document)
        self.assertEqual(obj.title, title)

    def test_put_with_weird_encoding(self):
        """
        Test whether you can save an attribute with some weird encoding
        in the title.
        """
        # Pull the object we'll deface
        obj = self.private_client.documents.get(self.editable_document)
        before_title = copy(obj.title)
        before_description = copy(obj.description)
        # Add something weird to the title and save it
        after_title = copy(PANGRAMS['iw'])
        after_description = copy(PANGRAMS['jp'])
        obj.title =  after_title
        obj.description = after_description
        obj.put()
        self.assertEqual(obj.title, after_title)
        self.assertEqual(obj.description, after_description)
        # Switch it back
        obj.title = before_title
        obj.description = before_description
        obj.put()
        self.assertEqual(obj.title, before_title)
        self.assertEqual(obj.description, before_description)

    def test_upload_and_delete(self):
        """
        Makes sure you can create and delete a document.
        """
        # Create it
        title = get_random_string()
        obj = self.private_client.documents.upload(
            os.path.join(os.path.dirname(__file__), "test.pdf"),
            title,
            description='Blah blah',
            related_article='http://www.latimes.com',
            data=dict(like='this', boom='bap'),
        )
        self.assertEqual(type(obj), Document)
        self.assertEqual(obj.description, 'Blah blah')
        self.assertEqual(obj.related_article, 'http://www.latimes.com')
        self.assertEqual(obj.data, {'like': 'this', 'boom': 'bap'})
        # Delete it
        obj.delete()
        self.assertRaises(DoesNotExistError, self.private_client.documents.get, obj.id)

    def test_upload_with_bad_data_keyword(self):
        """
        Test to make sure an error is thrown if someone tries to upload 
        a document with a reserved keyword in the 'data' attribute.
        """
        title = '001 - Test upload (%s)' % get_random_string()
        self.assertRaises(ValueError, self.private_client.documents.upload,
            os.path.join(os.path.dirname(__file__), "test.pdf"),
            title,
            description='Blah blah',
            related_article='http://www.latimes.com',
            # Access is an reserved keyword
            data=dict(access='this', boom='bap'),
        )

    def test_file_obj_upload_and_delete(self):
        """
        Test that uploading works when you provide a file object instead of a 
        path.
        """
        # Create it
        title = get_random_string()
        obj = self.private_client.documents.upload(
            open(os.path.join(os.path.dirname(__file__), "test.pdf"), "rb"),
            title,
        )
        self.assertEqual(type(obj), Document)
        self.assertEqual(obj.title, title)
        # Delete it
        obj.delete()
        self.assertRaises(DoesNotExistError, self.private_client.documents.get, obj.id)

    def test_unicode_upload_and_delete(self):
        """
        Ensure that documents with non-english characters can be uploaded
        """
        pdf = os.path.join(os.path.dirname(__file__), "español.pdf")
        obj = self.private_client.documents.upload(open(pdf, 'rb'))
        self.assertEqual(type(obj), Document)
        # Delete it
        obj.delete()
        self.assertRaises(DoesNotExistError, self.private_client.documents.get, obj.id)

    def test_virtual_file_upload_and_delete(self):
        """
        Proxy test case for files stored in memory, for instance, django-storages
        these tests are difficult to create as the class used to represent a file
        object is determined at runtime by the DEFAULT_FILE_STORAGE var (django)
        anyway, the main point is to show the MultipartPostHandler can handle unicode
        """
        path = os.path.join(os.path.dirname(__file__), "español.pdf")
        real_file = open(path, 'rb')
        virtual_file = StringIO.StringIO(real_file.read())
        obj = self.private_client.documents.upload(virtual_file, title='Espanola!')
        self.assertEqual(type(obj), Document)
        # Delete it
        obj.delete()
        self.assertRaises(DoesNotExistError, self.private_client.documents.get, obj.id)

    def test_secure_upload_and_delete(self):
        """
        Make sure you can create and delete a document using the secure
        parameter that hides your data from OpenCalais.
        
        Currently I don't know a way to test whether the parameter is properly
        applied. It seems to work in the UI, but, as far as I know, the API
        doesn't return an indicator that I have figured out how to test.
        """
        # Create it
        title = get_random_string()
        obj = self.private_client.documents.upload(
            os.path.join(os.path.dirname(__file__), "test.pdf"),
            title,
            secure=True,
        )
        self.assertEqual(type(obj), Document)
        # Delete it
        obj.delete()
        self.assertRaises(DoesNotExistError, self.private_client.documents.get, obj.id)

    def test_upload_directory(self):
        """
        Makes sure you can upload all the pdfs in a directory.
        """
        # Upload everything in this directory.
        obj_list = self.private_client.documents.upload_directory('./',
            source='Los Angeles Times',
            published_url='http://www.latimes.com',
        )
        # Which should only be one document
        self.assertEqual(len(obj_list), 2)
        self.assertEqual(type(obj_list[0]), Document)
        self.assertEqual(obj_list[0].source, 'Los Angeles Times')
        self.assertEqual(obj_list[0].published_url, 'http://www.latimes.com')
        # And which we should be able to delete
        [i.delete() for i in obj_list]
        [self.assertRaises(DoesNotExistError, self.private_client.documents.get, obj.id)
            for obj in obj_list]

    def test_resources(self):
        """
        Makes sure the canonical url is a top-level attribute on the Document.
        """
        obj = self.public_client.documents.get(self.test_id)
        # Test that they come out the same
        self.assertEqual(obj.published_url, obj.resources.published_url)
        self.assertEqual(obj.related_article, obj.resources.related_article)
        # Then test that they setattr the same
        obj.published_url = 'http://latimes.com'
        obj.related_article = 'http://palewire.com'
        self.assertEqual(obj.published_url, obj.resources.published_url)
        self.assertEqual(obj.related_article, obj.resources.related_article)


class ProjectTest(BaseTest):

    def test_all(self):
        """
        Test an `all` request for a list of all projects belong to an 
        authorized user.
        """
        obj_list = self.private_client.projects.all()
        self.assertEqual(type(obj_list), type([]))
        self.assertEqual(type(obj_list[0]), Project)

    def test_get(self):
        """
        Test a `get` methods for a particular project
        """
        obj = self.private_client.projects.get('934')
        self.assertEqual(type(obj), Project)
        obj2 = self.private_client.projects.get_by_id('934')
        self.assertEqual(obj.id, obj2.id)
        obj3 = self.private_client.projects.get_by_title(obj2.title)
        self.assertEqual(obj2.id, obj3.id)

    def test_document_list(self):
        """
        Verify that a project can pull back all if its associated documents.
        """
        obj = self.private_client.projects.get('934')
        doc_list = obj.document_list
        self.assertEqual(type(doc_list[0]), Document)

    def test_get_document(self):
        """
        Verify that a project can pull a particular document by id
        """
        obj = self.private_client.projects.get('934')
        doc = obj.get_document(u'25798-pr-01092011-loughner')
        self.assertEqual(type(doc), Document)

    def test_put(self):
        """
        Test whether we can put random noise to all the editable fields.
        """
        # Pull the object we'll deface
        obj = self.private_client.projects.get(self.editable_project)
        # Create random strings we will save to the editable attributes
        title = u'The Klee Report (%s)' % get_random_string()
        description = textwrap.dedent(u"""
        An independent probe into Sam Zell\'s purchase of Tribune Company by 
        investigator Kenneth Klee. Released at the end of July 2010. (%s)
        """)
        description = description % get_random_string()
        # Set the random strings our local object's attributes
        # and zero out the document list.
        obj.title = title
        obj.description = description
        obj.document_list = []
        # Save the changes up to DocumentCloud
        obj.put()
        # Pull the object again and verify the changes stuck
        obj = self.private_client.projects.get(self.editable_project)
        self.assertEqual(obj.title, title)
        self.assertEqual(obj.description, description)
        self.assertEqual(len(obj.document_list), 0)
        # Now add all the documents back in
        proj_ids = [
            u'12667-the-klee-report-volume-2',
            u'12666-the-klee-report-volume-1'
        ]
        for id in proj_ids:
            doc = self.private_client.documents.get(id)
            obj.document_list.append(doc)
        obj.put()
        obj = self.private_client.projects.get(self.editable_project)
        self.assertEqual(len(obj.document_list), len(proj_ids))

    def test_save(self):
        """
        Test whether the save method properly aliases `put`.
        """
        # Pull the object we'll deface
        obj = self.private_client.projects.get(self.editable_project)
        # Create random strings we will save to the editable attributes
        title = get_random_string()
        # Save the changes up to DocumentCloud with the alias
        obj.title = title
        obj.save()
        # Pull the object again and verify the changes stuck
        obj = self.private_client.projects.get(self.editable_project)
        self.assertEqual(obj.title, title)

    def test_document_list_type_restrictions(self):
        """
        Make sure document_lists will only accept Document objects
        """
        obj = self.private_client.projects.get(self.editable_project)
        self.assertRaises(TypeError, obj.document_list.append, "The letter C")

    def test_create_and_delete(self):
        """
        Test whether you can create a new project.
        """
        # Create it
        title = get_random_string()
        doc = self.private_client.documents.get(self.editable_document)
        proj = self.private_client.projects.create(
            title,
            description='Blah blah',
            document_ids=[doc.id]
        )
        self.assertEqual(type(proj), Project)
        self.assertEqual(proj.title, title)
        self.assertEqual(proj.description, 'Blah blah')
        self.assertEqual(proj.document_list[0].id, doc.id)
        # Delete it
        proj.delete()
        self.assertRaises(DoesNotExistError, self.private_client.projects.get, proj.id)

    def test_get_or_create(self):
        """
        Test whether get_or_create methods are working.
        """
        # Create it
        title = get_random_string()
        proj, c = self.private_client.projects.get_or_create_by_title(title)
        self.assertEqual(type(proj), Project)
        self.assertEqual(c, True)
        # Get it
        proj, c = self.private_client.projects.get_or_create_by_title(title)
        self.assertEqual(type(proj), Project)
        self.assertEqual(c, False)
        # Delete it
        proj.delete()
        self.assertRaises(DoesNotExistError, self.private_client.projects.get, proj.id)


class ErrorTest(BaseTest):

    def test_missing_credentials(self):
        """
        Make sure CredentialsMissingError works.
        """
        self.assertRaises(CredentialsMissingError, self.public_client.projects.all)

    def test_failed_credentials(self):
        """
        Make sure CredentialsFailedError works.
        """
        self.assertRaises(CredentialsFailedError, self.public_client.fetch, "projects.json")

    def test_does_not_exist(self):
        """
        Make sure DoesNotExistError works.
        """
        self.assertRaises(DoesNotExistError, self.public_client.documents.get, 'TK')

    def test_duplicate_object(self):
        """
        Make sure DuplicateObjectError works.
        """
        obj = self.private_client.projects.get("703")
        doc = self.private_client.documents.get(u'12666-the-klee-report-volume-1')
        self.assertRaises(DuplicateObjectError, obj.document_list.append, doc)


if __name__ == '__main__':
    unittest.main()
