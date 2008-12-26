"Models for the book webservice"

from google.appengine.ext import db

class Book(db.Model):
    "Represents a single book"
    ident = db.StringProperty(required=True)
    title = db.StringProperty(required=True)
    url = db.StringProperty(required=True)