from flask_restx import Namespace, Resource, fields
from flask import jsonify

# Sample data
books = [
    {"id": 1, "title": "Book 1", "author": "Author 1"},
    {"id": 2, "title": "Book 2", "author": "Author 2"}
]

book_ns = Namespace('books', description='Books operations')

@book_ns.route('/')
class BooksOperations(Resource):
    def get(self):
        result = jsonify(books)
        return result, 200