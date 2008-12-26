#!/usr/bin/env python

"""
This site generates an admin interface to a RESTful webservice.
"""

# TODO: Styles
# TODO: Tests

import os
import wsgiref.handlers
import simplejson
import logging

import gmemsess

from google.appengine.api.urlfetch import fetch, DownloadError
from google.appengine.ext.webapp import template
from google.appengine.ext import webapp
from google.appengine.api.urlfetch import DELETE, PUT
from google.appengine.api import users

import settings

# set to False for production
_DEBUG = settings.DEBUG

class BooksHandler(webapp.RequestHandler):
    "Page handlers"
    def get(self):
        "Build the admin interface"        
        try:
            # get the JSON from the webservice
            response = fetch(settings.WEB_SERVICE_URL)
        except DownloadError:
            self.error(500)
        json = response.content
        # convert the JSON to Python objects
        try:
            books = simplejson.loads(json)
        except ValueError:
            books = []
        # initialise the session
        sess = gmemsess.Session(self)  
        # get the flash message if any
        message = sess.get("flash", "")

        # get the current user
        user = users.get_current_user()
        logout = users.create_logout_url("/")
        
        # seed the context with the list of books
        context = {
            "books": books,
            "user": user,
            "logout": logout,
            "version": os.environ['CURRENT_VERSION_ID'],
            "flash": message
        }
        # calculate the template path
        path = os.path.join(os.path.dirname(__file__), 'templates',
            'index.html')
            
        # always clear the flash message
        sess["flash"] = ""
        # save the sessions
        sess.save()
            
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
            "logout": logout,
            "version": os.environ['CURRENT_VERSION_ID'],
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
        ident = self.request.get("ident")
        url = self.request.get("url")
        # create the JSON object
        book = {
            "title": title,
            "ident": ident,
            "url": url,
            "message": ""
        }
        json = simplejson.dumps(book, sort_keys=False)
        # work out the url for the book
        url = "%s%s" % (settings.WEB_SERVICE_URL, ident)       
        logging.info("Request to add %s (%s)" % (title, ident))
        try:
            # send a PUT request to add or update the book record
            fetch(url, method=PUT, payload=json)
        except DownloadError:
            self.error(500)
        # redirect back to the home page

        # grab the session data
        sess = gmemsess.Session(self)
        # set the flash message
        sess["flash"] = "Added book %s (%s)" % (title, ident)
        # save the session data
        sess.save()

        # redirect back to the home page
        self.redirect("/")
        
class DeleteBookHandler(webapp.RequestHandler):
    "Handlers for deleting records"
    def post(self):
        "Delete a book from the webservice datastore"
        # get the ident from the request
        ident = self.request.get("ident")
        # work out the webservice url
        url = "%s%s" % (settings.WEB_SERVICE_URL, ident)
        logging.info("Request to delete book with ident %s" % ident)
        try:
            # send a DELETE request for that record
            fetch(url, method=DELETE)
        except DownloadError:
            self.error(500)        
            
        # grab the session data
        sess = gmemsess.Session(self)
        # set the flash message
        sess["flash"] = "Deleted book with ident %s" % ident
        # save the session data
        sess.save()
                
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