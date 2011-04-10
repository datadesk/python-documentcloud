#! /usr/bin/env python
import unittest
from documentcloud import DocumentCloud
from documentcloud import Annotation, Document, Project, Section
from private_settings import DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD


class BaseTest(unittest.TestCase):
    
    def setUp(self):
        self.test_search = 'Calpers special review'
        self.test_id = '74103-report-of-the-calpers-special-review'
        self.public_client = DocumentCloud()
        self.private_client = DocumentCloud(DOCUMENTCLOUD_USERNAME, DOCUMENTCLOUD_PASSWORD)


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
    
    def test_attrs(self):
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

    def annotations(self):
        """
        Test whether annotations exist.
        """
        obj = self.public_client.documents.search(self.test_search)[0]
        self.assertEqual(type(obj.annotations[0]), Annotation)
    
    def sections(self):
        """
        Test whether sections exist.
        """
        obj = self.public_client.documents.get(self.test_id)
        self.assertEqual(type(obj.sections[0]), Section)


class DocumentGetTest(BaseTest):
    
    def test_get(self):
        """
        Test a get request for a particular document.
        """
        obj = self.public_client.documents.get(self.test_id)
        self.assertEqual(type(obj), Document)
    
    def test_attrs(self):
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
    
    def annotations(self):
        """
        Test whether annotations exist.
        """
        obj = self.public_client.documents.get(self.test_id)
        self.assertEqual(type(obj.annotations[0]), Annotation)
    
    def sections(self):
        """
        Test whether sections exist.
        """
        obj = self.public_client.documents.get(self.test_id)
        self.assertEqual(type(obj.sections[0]), Section)


class ProjectTest(BaseTest):
    
    def get_all(self):
        """
        Test an all request for a list of all projects belong to an 
        authorized user.
        """
        obj_list = self.private_client.projects.all()
        self.assertEqual(type(obj_list), type([]))
        self.assertEqual(type(obj_list[0]), Project)


if __name__ == '__main__':
    unittest.main()
