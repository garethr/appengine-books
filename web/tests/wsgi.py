#!/usr/bin/env python

import unittest
from webtest import TestApp
from main import application

class WSGITest(unittest.TestCase):
    def setUp(self):
        self.app = TestApp(application())
    
    def test_index(self):        
        response = self.app.get('/')
        assert '<html>' in str(response)
        
if __name__ == "__main__":
    unittest.main()