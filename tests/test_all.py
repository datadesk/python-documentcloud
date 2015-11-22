#! /usr/bin/env python
# -*- coding: utf-8 -*-
"""
Tests out the DocumentCloud API.

Requires you to set DOCUMENTCLOUD_TEST_USERNAME and DOCUMENTCLOUD_TEST_PASSWORD
as global environment variables.
"""
import os
import sys
import six
import random
import string
import textwrap
import unittest
try:
    import cStringIO as io
except ImportError:
    import io
from copy import copy
from documentcloud import DocumentCloud
from documentcloud.toolbox import DoesNotExistError
from documentcloud.toolbox import DuplicateObjectError
from documentcloud.toolbox import CredentialsFailedError
from documentcloud.toolbox import CredentialsMissingError
from documentcloud import Annotation, Document, Project
from documentcloud import Section, Entity, Mention

#
# Odds and ends
#


def get_random_string(length=6):
    """
    Generate a random string of letters and numbers
    """
    return six.u(''.join(
        random.choice(
            string.ascii_letters + string.digits
        ) for i in range(length)
    ))


PANGRAMS = {
    'en': 'The quick brown fox jumps over the lazy dog.',
    'da': 'Quizdeltagerne spiste jordbær med fløde, mens cirkusklovnen \
Wolther spillede på xylofon.',
    'de': 'Falsches Üben von Xylophonmusik quält jeden größeren Zwerg.',
    'el': 'Γαζέες καὶ μυρτιὲς δὲν θὰ βρῶ πιὰ στὸ χρυσαφὶ ξέφωτο.',
    'es': 'El pingüino Wenceslao hizo kilómetros bajo exhaustiva lluvia y \
frío, añoraba a su querido cachorro.',
    'fr': "Portez ce vieux whisky au juge blond qui fume sur son île \
intérieure, à côté de l'alcôve ovoïde, où les bûches se consument dans \
l'âtre, ce qui lui permet de penser à la cænogenèse de l'être dont il est \
question dans la cause ambiguë entendue à Moÿ, dans un capharnaüm qui, pense-\
t-il, diminue çà et là la qualité de son œuvre.",
    'ga': "D'fhuascail Íosa, Úrmhac na hÓighe Beannaithe, pór Éava \
agus Ádhaimh.",
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
            "3.2": "350987-lbex-docid-131059",
            "3.3": "351029-lbex-docid-149714",
            "3.4": "351291-lbex-docid-037292",
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
            "3.2": 11134,
            "3.3": 11070,
            "3.4": 16842,
        }
        return version2slug[str(version)]

    def setUp(self):
        """
        Initialize a bunch of variables we'll use across tests.
        """
        self.test_id = '74103-report-of-the-calpers-special-review'
        self.public_client = DocumentCloud()
        self.private_client = DocumentCloud(
            os.environ['DOCUMENTCLOUD_TEST_USERNAME'],
            os.environ['DOCUMENTCLOUD_TEST_PASSWORD']
        )
        self.fake_client = DocumentCloud("John Doe", "TK")
        self.version = self.get_version()


class SearchTest(BaseTest):
    """"
    Search related tests.
    """
    def test_search(self):
        # Make a couple requests for documents
        self.test_search = 'Calpers special review'
        self.obj_list = self.public_client.documents.search(self.test_search)
        self.obj = self.obj_list[0]

        # Test out their attributes
        self.assertTrue(isinstance(self.obj_list, list))
        self.assertTrue(isinstance(self.obj, Document))
        self.obj.__str__()
        self.obj.__unicode__()
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
            'file_hash',
        ]
        for attr in attr_list:
            self.assertTrue(hasattr(self.obj, attr))

        # Check on the annotations
        obj = self.obj.annotations[0]
        self.assertTrue(isinstance(obj, Annotation))
        obj.__str__()
        obj.__unicode__()

        # Check on the sections
        obj = self.obj.sections[0]
        self.assertTrue(isinstance(obj, Section))
        obj.__str__()
        obj.__unicode__()

        # Check on the entities
        obj = self.obj.entities[0]
        self.assertTrue(isinstance(obj, Entity))
        obj.__str__()
        obj.__unicode__()

        # Check on the mentions
        obj = self.obj.mentions[0]
        self.assertTrue(isinstance(obj, Mention))
        obj.__str__()
        obj.__unicode__()

        # Verify the kwargs on the search work
        one_page = self.public_client.documents.search(
            self.test_search, page=1, per_page=1
        )
        self.assertEqual(len(one_page), 1)


class DocumentTest(BaseTest):
    """
    Document object related tests.
    """
    def test_public_actions(self):
        """
        Test all the tricks available without authentication.
        """
        # Pull a document
        self.obj = self.public_client.documents.get(self.test_id)

        # Test its attributions
        self.assertTrue(isinstance(self.obj, Document))
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
            'file_hash',
        ]
        [self.assertTrue(hasattr(obj, attr)) for attr in attr_list]
        obj.__str__()
        obj.__unicode__()

        # Raw PDF
        self.assertTrue(len(obj.pdf) > 0)
        # Turning this test off until @knowtheory gets all the value filled
        # for all the old documents in the database.
        #self.assertEqual(hashlib.sha1(pdf).hexdigest(), obj.file_hash)

        # Text
        self.assertEqual(
            obj.get_page_text_url(1),
            'https://www.documentcloud.org/documents/74103/pages/\
report-of-the-calpers-special-review-p1.txt'
        )
        self.assertEqual(
            obj.get_page_text(1).decode().split("\n")[0],
            "Report of the CalPERS Special Review"
        )

        # Images
        self.assertTrue(len(obj.small_image) > 0)
        self.assertTrue(len(obj.thumbnail_image) > 0)
        self.assertTrue(len(obj.normal_image) > 0)
        self.assertTrue(len(obj.large_image) > 0)

        # Annotations
        ann = obj.annotations[0]
        self.assertTrue(isinstance(ann, Annotation))
        ann.__str__()
        ann.__unicode__()

        # Sections
        sec = obj.sections[0]
        self.assertTrue(isinstance(sec, Section))
        sec.__str__()
        sec.__unicode__()

        # Entities
        ent = obj.entities[0]
        self.assertTrue(isinstance(ent, Entity))
        ent.__str__()
        ent.__unicode__()

    def test_private_actions(self):
        """
        Test all the stuff that requires a login.
        """
        # Get an editable document
        obj_id = self.get_editable_document(self.version)
        obj = self.private_client.documents.get(obj_id)

        # Make sure `data` attribute will only accept a dictionary.
        obj.data = dict(foo='bar')
        self.assertRaises(TypeError, obj.set_data, "string")
        self.assertRaises(TypeError, obj.set_data, 666)
        self.assertRaises(TypeError, obj.set_data, obj)

        # Test whether we can put random noise to all the editable fields.
        title = get_random_string()
        source = get_random_string()
        description = get_random_string()
        data = {get_random_string(): get_random_string()}
        if obj.resources.related_article == 'http://documents.latimes.com':
            related_article = 'http://documentcloud.org'
        else:
            related_article = 'http://documents.latimes.com'
        if obj.resources.published_url == 'http://documents.latimes.com':
            published_url = 'http://documentcloud.org'
        else:
            published_url = 'http://documents.latimes.com'
        obj.title = title
        obj.source = source
        obj.description = description
        obj.data = data
        obj.resources.related_article = related_article
        obj.resources.published_url = published_url

        # Save the changes up to DocumentCloud
        obj.put()

        # Pull the object again and verify the changes stuck
        obj = self.private_client.documents.get(obj_id)
        self.assertEqual(obj.title, title)
        self.assertEqual(obj.source, source)
        self.assertEqual(obj.description, description)
        self.assertEqual(obj.data, data)
        self.assertEqual(obj.resources.related_article, related_article)
        self.assertEqual(obj.resources.published_url, published_url)

        # Test reserved namespaces to make sure they're protected
        black_list = [
            'person', 'organization', 'place', 'term', 'email', 'phone',
            'city', 'state', 'country', 'title', 'description', 'source',
            'account', 'group', 'project', 'projectid', 'document', 'access',
            'filter',
        ]
        for key in black_list:
            self.assertRaises(ValueError, setattr, obj, "data", {key: 'foo'})
        obj.data = dict(boom='bap')

        # Resources
        self.assertEqual(obj.published_url, obj.resources.published_url)
        self.assertEqual(obj.related_article, obj.resources.related_article)

        # And their shortcuts
        obj.published_url = 'http://latimes.com'
        obj.related_article = 'http://palewi.re'
        self.assertEqual(obj.published_url, obj.resources.published_url)
        self.assertEqual(obj.related_article, obj.resources.related_article)

        # Test whether the save method properly aliases `put`.
        title = get_random_string()
        obj.title = title
        obj.save()
        obj = self.private_client.documents.get(obj_id)
        self.assertEqual(obj.title, title)

        # Test whether you can save an attribute with some weird encoding
        before_title = copy(obj.title)
        before_description = copy(obj.description)
        obj.title = random.choice(list(PANGRAMS.keys()))
        obj.description = random.choice(list(PANGRAMS.keys()))
        obj.put()
        obj.title = before_title
        obj.description = before_description
        obj.put()

        # Upload
        title = get_random_string()
        obj = self.private_client.documents.upload(
            os.path.join(os.path.dirname(__file__), "test.pdf"),
            title,
            description='Blah blah',
            related_article='http://www.latimes.com',
            data=dict(like_this='like+that', boom='bap'),
        )
        self.assertTrue(isinstance(obj, Document))
        self.assertEqual(obj.title, title)
        self.assertEqual(obj.description, 'Blah blah')
        self.assertEqual(obj.related_article, 'http://www.latimes.com')
        self.assertEqual(
            obj.data,
            {u'like_this': u'like+that', u'boom': u'bap'}
        )

        # Delete
        obj.delete()
        self.assertRaises(
            DoesNotExistError,
            self.private_client.documents.get,
            obj.id
        )

        # Test upload with bad keyword
        title = '001 - Test upload (%s)' % get_random_string()
        self.assertRaises(
            ValueError,
            self.private_client.documents.upload,
            os.path.join(os.path.dirname(__file__), "test.pdf"),
            title,
            description='Blah blah',
            related_article='http://www.latimes.com',
            # Access is an reserved keyword so this should fail
            data=dict(access='this', boom='bap'),
        )

        # Upload with a file object, not a path
        title = get_random_string()
        obj = self.private_client.documents.upload(
            open(os.path.join(os.path.dirname(__file__), "test.pdf"), "rb"),
            title,
        )
        self.assertTrue(isinstance(obj, Document))
        self.assertEqual(obj.title, title)
        obj.delete()

        # Ensure that documents with non-english characters can be uploaded
        pdf = os.path.join(os.path.dirname(__file__), "español.pdf")
        obj = self.private_client.documents.upload(open(pdf, 'rb'))
        self.assertTrue(isinstance(obj, Document))
        obj.delete()

        # Test virtual file upload and delete
        path = os.path.join(os.path.dirname(__file__), "español.pdf")
        real_file = open(path, 'rb')
        if six.PY3:
            virtual_file = io.BytesIO(real_file.read())
        else:
            virtual_file = io.StringIO(real_file.read())
        obj = self.private_client.documents.upload(
            virtual_file,
            title='Espanola!'
        )
        self.assertTrue(isinstance(obj, Document))
        obj.delete()

        # Test secure upload
        title = get_random_string()
        obj = self.private_client.documents.upload(
            os.path.join(os.path.dirname(__file__), "test.pdf"),
            title,
            secure=True,
        )
        self.assertTrue(isinstance(obj, Document))
        obj.delete()

        # Upload everything in this directory.
        obj_list = self.private_client.documents.upload_directory(
            './',
            source='Los Angeles Times',
            published_url='http://www.latimes.com',
        )
        self.assertEqual(len(obj_list), 2)
        self.assertTrue(isinstance(obj_list[0], Document))
        self.assertEqual(obj_list[0].source, 'Los Angeles Times')
        self.assertEqual(obj_list[0].published_url, 'http://www.latimes.com')
        [i.delete() for i in obj_list]

        # Test URL upload
        url = 'http://ord.legistar.com/Chicago/attachments/e3a0cbcb-044d-4ec3-9848-23c5692b1943.pdf'
        obj = self.private_client.documents.upload(url)
        obj.delete()


class ProjectTest(BaseTest):
    """
    Project object related tests.
    """
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
        Test ability to get a project and look at it.
        """
        # Make sure all the different pull commands return the same thing
        obj = self.private_client.projects.get('934')
        self.assertTrue(isinstance(obj, Project))

        obj2 = self.private_client.projects.get_by_id('934')
        self.assertEqual(obj.id, obj2.id)

        obj3 = self.private_client.projects.get_by_title(obj2.title)
        self.assertEqual(obj2.id, obj3.id)

        # Test other attributes
        obj.__str__()
        obj.__unicode__()

        # Document list
        doc_list = obj.document_list
        self.assertTrue(isinstance(doc_list[0], Document))

        # Pull a document
        doc = obj.get_document('25798-pr-01092011-loughner')
        self.assertTrue(isinstance(doc, Document))

    def test_put(self):
        """
        Test whether we can put random noise to all the editable fields.
        """
        # Pull the project
        self.editable_project = self.get_editable_project(self.version)
        obj = self.private_client.projects.get(self.editable_project)

        # Create random strings we will save to the editable attributes
        title = 'The Klee Report (%s)' % get_random_string()
        description = textwrap.dedent("""
        An independent probe into Sam Zell's purchase of Tribune Company by
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
            '12667-the-klee-report-volume-2',
            '12666-the-klee-report-volume-1'
        ]
        for id in proj_ids:
            doc = self.private_client.documents.get(id)
            obj.document_list.append(doc)
        obj.put()
        obj = self.private_client.projects.get(self.editable_project)
        self.assertEqual(len(obj.document_list), len(proj_ids))

        # Verify that the save alias to put works
        title = get_random_string()
        obj.title = title
        obj.save()
        obj = self.private_client.projects.get(self.editable_project)
        self.assertEqual(obj.title, title)

        # Make sure document_lists will only accept Document objects
        obj = self.private_client.projects.get(self.editable_project)
        self.assertRaises(TypeError, obj.document_list.append, "The letter C")

    def test_create_and_delete(self):
        """
        Test whether you can create a new project.
        """
        # Create it
        title = get_random_string()
        doc_id = self.get_editable_document(self.version)
        doc = self.private_client.documents.get(doc_id)
        proj = self.private_client.projects.create(
            title,
            description='Blah blah',
            document_ids=[doc.id]
        )
        self.assertTrue(isinstance(proj, Project))
        self.assertEqual(proj.title, title)
        self.assertEqual(proj.description, 'Blah blah')
        self.assertEqual(proj.document_list[0].id, doc.id)

        # Delete it
        proj.delete()
        self.assertRaises(
            DoesNotExistError,
            self.private_client.projects.get,
            proj.id
        )

    def test_get_or_create(self):
        """
        Test whether get_or_create methods are working.
        """
        # Create it
        title = get_random_string()
        proj, c = self.private_client.projects.get_or_create_by_title(title)
        self.assertTrue(isinstance(proj, Project))
        self.assertTrue(c)
        # Get it
        proj, c = self.private_client.projects.get_or_create_by_title(title)
        self.assertTrue(isinstance(proj, Project))
        self.assertFalse(c)
        # Delete it
        proj.delete()


class ErrorTest(BaseTest):
    """
    Test a lot of the errors.
    """
    def test_missing_credentials(self):
        """
        Make sure CredentialsMissingError works.
        """
        self.assertRaises(
            CredentialsMissingError,
            self.public_client.projects.all
        )

    def test_failed_credentials(self):
        """
        Make sure CredentialsFailedError works.
        """
        self.assertRaises(
            CredentialsFailedError,
            self.public_client.fetch,
            "projects.json"
        )

    def test_does_not_exist(self):
        """
        Make sure DoesNotExistError works.
        """
        self.assertRaises(
            DoesNotExistError,
            self.public_client.documents.get,
            'TK'
        )

    def test_duplicate_object(self):
        """
        Make sure DuplicateObjectError works.
        """
        obj = self.private_client.projects.get("703")
        doc = self.private_client.documents.get(
            '12666-the-klee-report-volume-1'
        )
        self.assertRaises(DuplicateObjectError, obj.document_list.append, doc)


if __name__ == '__main__':
    unittest.main()
