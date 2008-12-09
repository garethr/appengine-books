#!/usr/bin/env python

import os
import unittest
from webtest import TestApp, AppError

from google.appengine.api import urlfetch, mail_stub, apiproxy_stub_map, urlfetch_stub, user_service_stub, datastore_file_stub
from google.appengine.api.memcache import memcache_stub

from main import application
import settings 

class BooksTest(unittest.TestCase):
    def setUp(self):
                
        self.app = TestApp(application())
    	apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    	apiproxy_stub_map.apiproxy.RegisterStub('mail', mail_stub.MailServiceStub())
    	apiproxy_stub_map.apiproxy.RegisterStub('user', user_service_stub.UserServiceStub())
    	apiproxy_stub_map.apiproxy.RegisterStub('urlfetch', urlfetch_stub.URLFetchServiceStub())
    	apiproxy_stub_map.apiproxy.RegisterStub('memcache', memcache_stub.MemcacheServiceStub())        
        stub = datastore_file_stub.DatastoreFileStub('temp', '/dev/null', '/dev/null')
        apiproxy_stub_map.apiproxy.RegisterStub('datastore_v3', stub)
        
        os.environ['APPLICATION_ID'] = "temp"

    def test_json_returns_200(self):  
        response = self.app.get('/books.json', expect_errors=True)        
        self.assertEquals("200 OK", response.status)

    def test_json_view_is_json(self):
        response = self.app.get('/books.json', expect_errors=True)
        try:
            response.json # simplejons
        except AttributeError:
            assert(False)
                
    def test_json_views_return_correct_mime_type(self):
        response = self.app.get('/books.json', expect_errors=True)
        self.assertEquals(response.content_type, "application/json")
                
if __name__ == "__main__":
    unittest.main()