#!/usr/bin/env python

"""
Client for uploading books from a CSV file. Is run as follows:

bulkload_client.py 
    --filename ws/books.csv
    --kind Book 
    --url http://localhost:8080/load 
    --cookie='dev_appserver_login="test@example.com:True"'
"""

from google.appengine.ext import bulkload
from google.appengine.api import datastore_types
from google.appengine.ext import search

class BookLoader(bulkload.Loader):
    "Book bulkloader"
    def __init__(self):
        "Set the expected data structure for the CSV file"
        bulkload.Loader.__init__(self, 'Book', 
            [('title', str), ('asin', str),])

    def HandleEntity(self, entity):
        "Make the entities searchable"
        ent = search.SearchableEntity(entity)
        return ent

if __name__ == '__main__':
    # make the script importable
    bulkload.main(BookLoader())