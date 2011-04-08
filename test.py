#! /usr/bin/env python
import unittest
from documentcloud import Document
from documentcloud import documentcloud


class BaseTest(unittest.TestCase):
    
    def setUp(self):
        self.test_search = 'Ruben Salazar'
        self.test_id = '71072-oir-final-report'


class DocumentSearchTest(BaseTest):

    def test_search(self):
        """
        Test a search.
        """
        obj_list = documentcloud.documents.search(self.test_search)
        self.assertEqual(type(obj_list), type([]))
    
    def test_multipage_search(self):
        """
        Test a search that will return more than a single page of results.
        """
        obj_list = documentcloud.documents.search("johnson")
        self.assertTrue(len(obj_list) > 1000)


class DocumentGetTest(BaseTest):

    def test_get(self):
        """
        Test a get request for a particular document.
        """
        obj = documentcloud.documents.get(self.test_id)
        self.assertEqual(type(obj), Document)


if __name__ == '__main__':
    unittest.main()
