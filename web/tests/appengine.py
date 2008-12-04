#!/usr/bin/env python

import unittest
from google.appengine.api import urlfetch
from google.appengine.api import apiproxy_stub_map
from google.appengine.api import urlfetch_stub
from google.appengine.api.memcache import memcache_stub

class AppEngineTestCase(unittest.TestCase):
    
    def setUp(self):
    	apiproxy_stub_map.apiproxy = apiproxy_stub_map.APIProxyStubMap()
    	apiproxy_stub_map.apiproxy.RegisterStub('urlfetch', urlfetch_stub.URLFetchServiceStub())
    	apiproxy_stub_map.apiproxy.RegisterStub('memcache', memcache_stub.MemcacheServiceStub())

    def test_url_fetch(self):
        response = urlfetch.fetch('http://localhost:8081')
        self.assertEquals(200, response.status_code)

if __name__ == "__main__":
    unittest.main()