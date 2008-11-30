from google.appengine.ext import db

class Book(db.Model):
    asin = db.StringProperty(required=True)
    title = db.StringProperty(required=True)