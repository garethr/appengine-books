#!/usr/bin/env python

import os
import unittest
from webtest import TestApp, AppError

from google.appengine.api import urlfetch, mail_stub, apiproxy_stub_map, urlfetch_stub, user_service_stub, datastore_file_stub
from google.appengine.api.memcache import memcache_stub
from google.appengine.api.urlfetch import DownloadError, InvalidURLError

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

    def test_webservice_is_up(self):  
        try:
            urlfetch.fetch(settings.WEB_SERVICE_URL)
        except DownloadError, InvalidURLError:
            assert(False)
        
    def test_index_returns_200(self):  
        response = self.app.get('/', expect_errors=True)        
        self.assertEquals("200 OK", response.status)
    
    def test_html_tag_present(self):
        response = self.app.get('/', expect_errors=True)        
        response.mustcontain("<html>")
            
    def test_web_view_return_correct_mime_type(self):
        response = self.app.get('/', expect_errors=True)
        self.assertEquals(response.content_type, "text/html")
                
    def test_web_view_return_correct_mime_type(self):
        response = self.app.get('/', expect_errors=True)
        self.assertEquals(response.content_type, "text/html")
                       
if __name__ == "__main__":
    unittest.main()