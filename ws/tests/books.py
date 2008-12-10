#!/usr/bin/env python

import os
import unittest
from webtest import TestApp, AppError

from google.appengine.api import urlfetch, mail_stub, apiproxy_stub_map, urlfetch_stub, user_service_stub, datastore_file_stub
from google.appengine.api.memcache import memcache_stub

from main import application
from models import Book
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

    def test_index_returns_404(self):     
        response = self.app.get('/', expect_errors=True)
        self.assertEquals("404 Not Found", response.status)

    def test_books_with_no_content_returns_404(self):  
        self.assertEquals(0, Book.all().count())
        response = self.app.get('/books', expect_errors=True)        
        self.assertEquals("404 Not Found", response.status)

    def test_books_with_content_returns_200(self):  
        self.assertEquals(0, Book.all().count())
        book = Book(
            title = "test",
            asin = "1"
        )    
        book.put()   
        response = self.app.get('/books', expect_errors=True)        
        self.assertEquals("200 OK", response.status)
    
    def test_response_from_books_is_json(self):
        self.assertEquals(0, Book.all().count())
        book = Book(
            title = "test",
            asin = "1"
        )    
        book.put()  
        self.assertEquals(1, Book.all().count())
        response = self.app.get('/books/', expect_errors=True)
        try:
            response.json # simplejons
        except AttributeError:
            assert(False)
    
    def test_response_contents_from_books(self):
        self.assertEquals(0, Book.all().count())
        book = Book(
            title = "test",
            asin = "1"
        )    
        book.put()  
        self.assertEquals(1, Book.all().count())
        response = self.app.get('/books/', expect_errors=True)
        response.mustcontain('"asin": "1"')
        response.mustcontain('"title": "test"')

    def test_response_contents_json_from_books(self):
        self.assertEquals(0, Book.all().count())
        book = Book(
            title = "test",
            asin = "1"
        )    
        book.put()  
        self.assertEquals(1, Book.all().count())
        response = self.app.get('/books/', expect_errors=True)
        try:
            json = response.json # simplejons
        except AttributeError:
            assert(False)
        self.assertEqual(len(json), 1)
        self.assertEqual(json[0]['asin'], "1")
        self.assertEqual(json[0]['title'], "test")
            
    def test_books_views_return_correct_mime_type(self):
        self.assertEquals(0, Book.all().count())
        book = Book(
            title = "test",
            asin = "1"
        )    
        book.put()  
        self.assertEquals(1, Book.all().count())
        response = self.app.get('/books/', expect_errors=True)
        self.assertEquals(response.content_type, "application/json")
                
if __name__ == "__main__":
    unittest.main()