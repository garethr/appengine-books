"Models for the book webservice"

from google.appengine.ext import db

class Book(db.Model):
    "Represents a single book"
    asin = db.StringProperty(required=True)
    title = db.StringProperty(required=True)