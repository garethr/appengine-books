#!/usr/bin/env python

"""
This site generates an admin interface to a RESTful webservice.
"""

# TODO: error handling
# TODO: styles
# TODO: tests
# TODO: flash message

import os
import wsgiref.handlers
import simplejson

from google.appengine.api.urlfetch import fetch
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api.urlfetch import DELETE, PUT
from google.appengine.api import users

import settings

# set to False for production
_DEBUG = True

class BooksHandler(webapp.RequestHandler):
    "Page handlers"
    def get(self):
        "Build the admin interface"
        # get the JSON from the webservice
        response = fetch(settings.WEB_SERVICE_URL)
        json = response.content        
        # convert the JSON to Python objects
        books = simplejson.loads(json)
        
        #message = self.response.get_cookie("flash")
        #self.response.delete_cookie("flash")

        # get the current user
        user = users.get_current_user()
        logout = users.create_logout_url("/")
        
        # seed the context with the list of books
        context = {
            "books": books,
            "user": user,
            "logout": logout
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
        # get the current user
        user = users.get_current_user()
        logout = users.create_logout_url("/")
        # seed the context with the user details
        context = {
            "user": user,
            "logout": logout
        }
        # calculate the template path
        path = os.path.join(os.path.dirname(__file__), 'templates',
            'add.html')
        # render the template with the provided context
        self.response.out.write(template.render(path, context))

    def post(self):
        "Add the book to the webservice"
        # get the posted data
        title = self.request.get("title")
        asin = self.request.get("asin")
        # create the JSON object
        book = {
            "title": title,
            "asin": asin
        }
        json = simplejson.dumps(book, sort_keys=False)
        # work out the url for the book
        url = "%s%s" % (settings.WEB_SERVICE_URL, asin)        
        # send a PUT request to add or update the book record
        fetch(url, method=PUT, payload=json)
        # redirect back to the home page
        # self.response.set_cookie("flash", "Success")
        
        self.redirect("/")
        
class DeleteBookHandler(webapp.RequestHandler):
    "Handlers for deleting records"
    def post(self):
        "Delete a book from the webservice datastore"
        # get the asin from the request
        asin = self.request.get("asin")
        # work out the webservice url
        url = "%s%s" % (settings.WEB_SERVICE_URL, asin)
        # send a DELETE request for that record
        fetch(url, method=DELETE)
        # reirect back to the home page
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