#!/usr/bin/env python

# TODO: error handling
# TODO: authentication
# TODO: styles
# TODO: tests
# TODO: comments
# TODO: pylint

import os
import wsgiref.handlers
import simplejson

from google.appengine.api.urlfetch import fetch
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api.urlfetch import DELETE, PUT

import settings

# set to False for production
_DEBUG = True

class BooksHandler(webapp.RequestHandler):
    def get(self):
        # get the JSON from the webservice
        response = fetch(settings.WEB_SERVICE_URL)
        json = response.content        
        # convert the JSON to Python objects
        books = simplejson.loads(json)
        # seed the context with the list of books
        context = {
            "books": books
        }
        # calculate the template path
        path = os.path.join(os.path.dirname(__file__), 'templates',
            'index.html')
        # render the template with the provided context
        self.response.out.write(template.render(path, context))        
        
class AddBookHandler(webapp.RequestHandler):
    "Manage adding new books to the web service"
    def get(self):
        "Render a simple add form"
        context = {}
        # calculate the template path
        path = os.path.join(os.path.dirname(__file__), 'templates',
            'add.html')
        # render the template with the provided context
        self.response.out.write(template.render(path, context))

    def post(self):
        ""
        title = self.request.get("title")
        asin = self.request.get("asin")
        book = {
            "title": title,
            "asin": asin
        }
        # create the JSON object
        json = simplejson.dumps(book, sort_keys=False)
        url = "%s%s" % (settings.WEB_SERVICE_URL, asin)        
        response = fetch(url, method=PUT, payload=json)
        self.redirect("/")
        
class DeleteBookHandler(webapp.RequestHandler):
    def post(self):
        asin = self.request.get("asin")
        url = "%s%s" % (settings.WEB_SERVICE_URL, asin)
        response = fetch(url, method=DELETE)
        self.redirect("/")

def application():
    "Separate application method for ease of testing"
    # register URL handlers
    return webapp.WSGIApplication([
        ('/', BooksHandler),
        ('/add/?$', AddBookHandler),
        ('/delete/?$', DeleteBookHandler),
    ], debug=False)

def main():
    "Run the application"
    wsgiref.handlers.CGIHandler().run(application())

if __name__ == '__main__':
    # if not imported then run the main() function
    main()