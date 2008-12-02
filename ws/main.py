#!/usr/bin/env python

"""
This application provides a simple RESTful webservice for interacting with 
a list of books. No admin interface or front end is provided as they are 
part of other applications. Currently the service talks JSON.
"""

# TODO: More exception handling
# TODO: Sending correct status codes
# TODO: All views should return something
# TODO: Authentication
# TODO: Write tests
# TODO: Adding logging

import wsgiref.handlers
import simplejson

from google.appengine.api import memcache
from google.appengine.ext import webapp

import settings
from models import Book

# set to False for production
_DEBUG = True

class BooksHandler(webapp.RequestHandler):
    """
    Exposes methods that act on the full list of books
    in the datastore.
    """

    def get(self):
        "Returns a list of books"
        # first check if we have the list of books in the cache
        json = memcache.get("ws_books")
        # if not then we need to create it
        if json is None:
            # get all books
            books = Book.all()
            books_for_output = []
                
            for book in books:
                # for each book create a data structure representation
                books_for_output.append({
                    "title": book.title,
                    "asin": book.asin,
                    "key": str(book.key())
                })
            # convert the datastructure to json
            json = simplejson.dumps(books_for_output, sort_keys=False, indent=4)
            # store the json in the cache for a specified time
            memcache.add("ws_books", json, settings.CACHE_TIME)

        # serve the response with the correct content type
        self.response.headers['Content-Type'] = 'application/json'        
        # write the json to the response
        self.response.out.write(json)

    def post(self):
        "Creates a new book record from a json representation"
        # get the request body
        json = self.request.body
        # convert the JSON to a Python object
        representation = simplejson.loads(json)
        # create a datastore object from the JSON
        book = Book(
            title = representation['title'],
            asin = representation['asin']
        )
        # save the object to the datastore
        book.put()
        
class BookHandler(webapp.RequestHandler):
    "Exposes methods for acting on a single book record"

    def get(self, asin):
        "Show the JSON representation of the book"
        try:
            # retrieve the book based on its ASIN value
            book = Book.all().filter('asin =', asin)[0]
        except IndexError:
            # if we don't find a book then throw a Not Found error
            return self.error(404)
        
        # create the datastructure we will convert to JSON
        book_for_output = {
            "title": book.title,
            "asin": book.asin,
            "key": str(book.key())
        }
        # create the JSON object
        json = simplejson.dumps(book_for_output, sort_keys=False, indent=4)

        # serve the response with the correct content type
        self.response.headers['Content-Type'] = 'application/json'        
        # write the json to the response
        self.response.out.write(json)

    def put(self, asin):
        "Update an existing book or create a new one"

        # get the JSON from the request
        json = self.request.body
        # convert the JSON to a Python object 
        representation = simplejson.loads(json)
        # set the properties
        title = representation['title']
        asin = representation['asin']

        try:
            # retrieve the book based on its ASIN value
            book = Book.all().filter('asin =', asin)[0]
            book.title = title
            book.asin = asin
        except IndexError:
            # if we don't find a book then create one
            book = Book(
                title = title,
                asin = asin
            )
        # we'e updated so we need to clear the cache
        memcache.delete("ws_books")
        # save the object to the datastore
        book.put()    
    
    def delete(self, asin):
        "Delete the book from the datastore"
        try:
            # retrieve the book based on its ASIN value
            book = Book.all().filter('asin =', asin)[0]
        except IndexError:
            # if we don't find a book then throw a Not Found error
            return self.error(404)

        # delete the book
        book.delete()
        # clear the cache
        memcache.delete("ws_books")

def application():
    "Separate application method for ease of testing"
    # register URL handlers
    return webapp.WSGIApplication([
        ('/books/([A-Za-z0-9]+)/?$', BookHandler),
        ('/books/?$', BooksHandler)
    ], debug=False)

def main():
    "Run the application"
    wsgiref.handlers.CGIHandler().run(application())

if __name__ == '__main__':
    # if not imported then run the main() function
    main()