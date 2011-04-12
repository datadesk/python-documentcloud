#! /usr/bin/env python
"""
Tests out the DocumentCloud API.

Most requests require authentication, which I'm not sure how deal with properly
in this circumstance. For the time being, I'm importing latimes.com credentials
and fiddling around with junk files I've placed in there. Obviously, that means
this test suite will only work on my computer, which seems like a problem.

If you know how I ought to sort this sort of thing out, please let me know.
"""
import os
import random
import string
import textwrap
import unittest
from documentcloud import DocumentCloud
from documentcloud import CredentialsMissingError, DuplicateObjectError
from documentcloud import CredentialsFailedError, DoesNotExistError
from documentcloud import Annotation, Document, Project, Section, Entity
from private_settings import DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD

#
# Odds and ends
#

def get_random_string(length=6):
    """
    Generate a random string of letters and numbers
    """
    return ''.join(random.choice(string.letters + string.digits) for i in xrange(length))

#
# Tests
#

class BaseTest(unittest.TestCase):
    
    def setUp(self):
        self.test_search = 'Calpers special review'
        self.test_id = '74103-report-of-the-calpers-special-review'
        self.public_client = DocumentCloud()
        self.private_client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD)
        self.fake_client = DocumentCloud("John Doe", "TK")


class DocumentSearchTest(BaseTest):
    
    def test_search(self):
        """
        Test a search.
        """
        obj_list = self.public_client.documents.search(self.test_search)
        self.assertEqual(type(obj_list), type([]))
        self.assertEqual(type(obj_list[0]), Document)
    
#    def test_multipage_search(self):
#        """
#        Test a search that will return more than a single page of results.
#        """
#        obj_list = documentcloud.documents.search("johnson")
#        self.assertTrue(len(obj_list) > 1000)
    
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
        ]
        [self.assertTrue(hasattr(obj, attr)) for attr in attr_list]
    
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
    
    def test_get_put(self):
        """
        Test whether we can put random noise to all the editable fields.
        """
        # Pull the object we'll deface
        obj = self.private_client.documents.get("15144-mitchrpt")
        # Create random strings we will save to the editable attributes
        title = 'The Mitchell Report (%s)' % get_random_string()
        source = 'DLA Piper (%s)' % get_random_string()
        description = get_random_string()
        if obj.resources.related_article == 'http://documents.latimes.com':
            related_article = 'http://documentcloud.org'
        else:
            related_article = 'http://documents.latimes.com'
        if obj.resources.published_url == 'http://documents.latimes.com':
            published_url = 'http://documentcloud.org'
        else:
            published_url = 'http://documents.latimes.com'
        # Set the random strings our local object's attributes
        obj.title = title
        obj.source = source
        obj.description = description
        obj.resources.related_article = related_article
        obj.resources.published_url = published_url
        # Save the changes up to DocumentCloud
        obj.put()
        # Pull the object again and verify the changes stuck
        obj = self.private_client.documents.get("15144-mitchrpt")
        self.assertEqual(obj.title, title)
        self.assertEqual(obj.source, source)
        self.assertEqual(obj.description, description)
        self.assertEqual(obj.resources.related_article, related_article)
        self.assertEqual(obj.resources.published_url, published_url)
    
    def test_upload(self):
        title = 'Test upload (%s)' % get_random_string()
        new_id = self.private_client.documents.upload(
            os.path.join(os.path.dirname(__file__), "test.pdf"),
            title,
        )
        obj = self.private_client.documents.get(new_id)
        self.assertEqual(type(obj), Document)


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
        Test a `get` request for a particular project
        """
        obj = self.private_client.projects.get('934')
        self.assertEqual(type(obj), Project)
    
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
        obj = self.private_client.projects.get("703")
        # Create random strings we will save to the editable attributes
        title = 'The Klee Report (%s)' % get_random_string()
        description = textwrap.dedent("""
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
        obj = self.private_client.projects.get("703")
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
        obj = self.private_client.projects.get("703")
        self.assertEqual(len(obj.document_list), len(proj_ids))
    
    def test_document_list_type_restrictions(self):
        """
        Make sure document_lists will only accept Document objects
        """
        obj = self.private_client.projects.get("703")
        self.assertRaises(TypeError, obj.document_list.append, "The letter C")
    
    def test_create(self):
        """
        Test whether you can create a new project.
        """
        new_id = self.private_client.projects.create("This is only a test (%s)" % get_random_string())
        proj = self.private_client.projects.get(new_id)
        self.assertEqual(type(proj), Project)


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
