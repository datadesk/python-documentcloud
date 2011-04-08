#! /usr/bin/env python
import unittest
from documentcloud import documentcloud


class BaseTest(unittest.TestCase):
    
    def setUp(self):
        self.test_search = 'Ruben Salazar'
        self.test_id = '71072-oir-final-report'


class SearchTest(BaseTest):

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
        self.assertEqual(len(obj_list) > 1000, True)

if __name__ == '__main__':
    unittest.main()
