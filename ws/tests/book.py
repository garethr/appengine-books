#!/usr/bin/env python

import os
import unittest
from webtest import TestApp, AppError

from google.appengine.api import urlfetch, mail_stub, apiproxy_stub_map, urlfetch_stub, user_service_stub, datastore_file_stub
from google.appengine.api.memcache import memcache_stub

from main import application
from models import Book

class BookTest(unittest.TestCase):
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

    def test_book_creation(self):
        self.assertEquals(0, Book.all().count())
        book = Book(
           title = "test",
           asin = "1"
        )    
        book.put()  
        self.assertEquals(1, Book.all().count())
        book = Book(
           title = "test2",
           asin = "2"
        )    
        book.put()  
        self.assertEquals(2, Book.all().count())

    def test_book_deletion(self):
        self.assertEquals(0, Book.all().count())
        book = Book(
           title = "test",
           asin = "1"
        )    
        book.put()  
        self.assertEquals(1, Book.all().count())
        book.delete()
        self.assertEquals(0, Book.all().count())

    def book_with_no_content_returns_404(self):  
        self.assertEquals(0, Book.all().count())
        response = self.app.get('/books/1', expect_errors=True)        
        self.assertEquals("404 Not Found", response.status)

    def test_book_with_content_returns_200(self):  
        self.assertEquals(0, Book.all().count())
        book = Book(
            title = "test",
            asin = "1"
        )    
        book.put()
        path = "/books/%s" % book.asin
        response = self.app.get(path, expect_errors=True)        
        self.assertEquals("200 OK", response.status)

    def test_response_from_book_is_json(self):
        self.assertEquals(0, Book.all().count())
        book = Book(
            title = "test",
            asin = "1"
        )    
        book.put()  
        self.assertEquals(1, Book.all().count())
        response = self.app.get('/books/%s' % book.asin, expect_errors=True)
        try:
            response.json
        except AttributeError:
            assert(False)

    def test_response_contents_from_book(self):
        self.assertEquals(0, Book.all().count())
        book = Book(
            title = "test",
            asin = "1"
        )    
        book.put()  
        self.assertEquals(1, Book.all().count())
        response = self.app.get('/books/%s' % book.asin, expect_errors=True)
        response.mustcontain('"asin": "1"')
        response.mustcontain('"title": "test"')

    def test_response_contents_json_from_book(self):
        self.assertEquals(0, Book.all().count())
        book = Book(
            title = "test",
            asin = "1"
        )    
        book.put()  
        self.assertEquals(1, Book.all().count())
        response = self.app.get('/books/%s' % book.asin, expect_errors=True)
        try:
            json = response.json
        except AttributeError:
            assert(False)
        self.assertEqual(json['asin'], "1")
        self.assertEqual(json['title'], "test")

    def test_book_views_return_correct_mime_type(self):
        self.assertEquals(0, Book.all().count())
        book = Book(
            title = "test",
            asin = "1"
        )    
        book.put()  
        self.assertEquals(1, Book.all().count())
        response = self.app.get('/books/%s' % book.asin, expect_errors=True)
        self.assertEquals(response.content_type, "application/json")
        
    def test_book_deletion_via_service(self):
        self.assertEquals(0, Book.all().count())
        book = Book(
           title = "test",
           asin = "1"
        )    
        book.put()  
        self.assertEquals(1, Book.all().count())
        response = self.app.delete('/books/%s' % book.asin, expect_errors=True)
        self.assertEquals(0, Book.all().count())
        
    def test_book_addition_via_service_put(self):
        json = """{
            "asin": "1", 
            "title": "test"
        }"""
        self.assertEquals(0, Book.all().count())
        response = self.app.put('/books/1', params=json, expect_errors=True)
        self.assertEquals(1, Book.all().count())
        response = self.app.get('/books/1', expect_errors=True)
        self.assertEquals("200 OK", response.status)
        
    def test_book_update_via_service_put(self):
        self.assertEquals(0, Book.all().count())
        book = Book(
           title = "test",
           asin = "1"
        )    
        book.put()  
        self.assertEquals(1, Book.all().count())
        json = """{
            "asin": "1", 
            "title": "test update"
        }"""
        response = self.app.put('/books/1', params=json, expect_errors=True)
        self.assertEquals(1, Book.all().count())
        response = self.app.get('/books/1', expect_errors=True)
        self.assertEquals("200 OK", response.status)
        try:
            json = response.json
        except AttributeError:
            assert(False)
        self.assertEqual(json['asin'], "1")
        self.assertEqual(json['title'], "test update")
        
    def test_book_addition_via_service_post(self):
        json = """{
            "asin": "1", 
            "title": "test"
        }"""
        self.assertEquals(0, Book.all().count())
        response = self.app.post('/books', params=json, expect_errors=True)
        self.assertEquals(1, Book.all().count())
        response = self.app.get('/books/1', expect_errors=True)
        self.assertEquals("200 OK", response.status)
        
if __name__ == "__main__":
    unittest.main()