#!/usr/bin/env python

"""
This application provides a simple RESTful webservice for interacting with 
a list of books. No admin interface or front end is provided as they are 
part of other applications. Currently the service talks JSON.
"""

# TODO: Authentication
# TODO: Tests

import wsgiref.handlers
import simplejson
import logging

from google.appengine.api import memcache
from google.appengine.ext import webapp
from google.appengine.api import mail

import settings
from models import Book

# set to False for production
_DEBUG = True

def _email_new_book(book):
    "Send an email about a new book being added to the list"

    # instatiate the object
    message = mail.EmailMessage(sender="gareth.rushgrove@gmail.com",
                                subject="New Book Added")

    # ser the to and body fields
    message.to = "Gareth Rushgrove <gareth.rushgrove@gmail.com>"
    message.body = """
    Someone just added %s (%s) to the book list.
    """ % (book.title, book.asin)

    # send the message
    logging.debug("Sent email about %s (%s)" % (book.title, book.asin))
    message.send()

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
            # if we have no books then return not found
            if not books_for_output:
                return self.error(404)
            # convert the datastructure to json
            json = simplejson.dumps(books_for_output, sort_keys=False, indent=4)
            # store the json in the cache for a specified time
            memcache.add("ws_books", json, settings.CACHE_TIME)

        # serve the response with the correct content type
        self.response.headers['Content-Type'] = 'application/json'        
        # write the json to the response
        logging.info('Request for book list')
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
        logging.info('Add new book request')
        try:
            # save the object to the datastore
            book.put()
            # send an email about the new book
            _email_new_book(book)
        except:
            logging.error("Error occured creating new book via POST")
            self.error(500)

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
        logging.info("Request for %s (%s)" % (book.title, book.asin))
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
        logging.info("Update request for %s (%s)" % (title, asin))
        # save the object to the datastore
        try:
            # save the object to the datastore
            book.put()
            # send an email about the new book
            _email_new_book(book)            
            # we'e updated so we need to clear the cache
            memcache.delete("ws_books")
        except:
            logging.error("Error occured creating/updating \
                book %s (%s) via PUT") % (title, asin)
            self.error(500)
    
    def delete(self, asin):
        "Delete the book from the datastore"
        try:
            # retrieve the book based on its ASIN value
            book = Book.all().filter('asin =', asin)[0]
        except IndexError:
            # if we don't find a book then throw a Not Found error
            return self.error(404)

        logging.info("Update request for %s (%s)" % (book.title, asin))
        try:
            # delete the book
            book.delete()
            # we'e updated so we need to clear the cache
            memcache.delete("ws_books")
        except:
            logging.error("Error occured deleting %s (%s)"
                % (book.title, asin))
            self.error(500)

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