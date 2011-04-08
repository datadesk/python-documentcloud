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
        obj_list = documentcloud.documents.search('ruben salazar')
        self.assertEqual(type(obj_list), type([]))


if __name__ == '__main__':
    unittest.main()
