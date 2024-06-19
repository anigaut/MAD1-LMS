from flask import Flask, request, send_file
from flask_restful import Api, Resource, reqparse
from models import *
import os
import werkzeug
from werkzeug.utils import secure_filename
from datetime import datetime
import json
api = Api()

book_parser = reqparse.RequestParser()
book_parser.add_argument("name")
book_parser.add_argument("author")
book_parser.add_argument("genre")
book_parser.add_argument("description")
book_parser.add_argument("price")
book_parser.add_argument("file", type = werkzeug.datastructures.FileStorage, location = 'files')
book_parser.add_argument("cover_pic", type = werkzeug.datastructures.FileStorage, location = 'files')
class BooksAPI(Resource):
    def get(self): #retrieve all books in the DB
        books = Books.query.all()
        all_books = []
        for book in books:
            book_details = {}
            book_details["id"] = book.id
            book_details["name"] = book.name
            book_details["author"] = book.author
            book_details["genre"] = book.genre
            book_details["description"] = book.description
            book_details["price"] = book.price
            all_books.append(book_details)
        return all_books
    
    def post(self):  # add a book to the DB
        args = book_parser.parse_args()

        filename = secure_filename(args['file'].filename)
        path = "static/books/"
        file_path = os.path.join(path, filename)
        args["file"].save(file_path)

        cover_pic_filename = secure_filename(args['cover_pic'].filename)
        pic_path = "static/covers/"
        cover_pic_path = os.path.join(pic_path, cover_pic_filename)
        args["cover_pic"].save(cover_pic_path)

        new_book = Books(
            name = args["name"],
            author = args["author"],
            genre = args["genre"],
            description = args["description"],
            price=  args["price"],
            file = filename,
            cover_pic = cover_pic_filename
        )

        db.session.add(new_book)
        db.session.commit()
        return {"message": "Book added successfully"}, 201

    def delete(self, book_id):
        book = Books.query.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        db.session.delete(book)
        db.session.commit()
        return {"message": "Book deleted successfully"}, 200
    
    def put(self, book_id):
        args = book_parser.parse_args()
        book = Books.query.get(book_id)
        if not book:
            return {"message": "Book not found"}, 404
        
        book.name = args["name"]
        book.author = args["author"]
        book.genre = args["genre"]
        book.description = args["description"]
        book.price = args["price"]

        db.session.commit()
        return {"message": "Book Details Edited successfully"}, 200


genre_parser = reqparse.RequestParser()
genre_parser.add_argument("name")
genre_parser.add_argument("description")
class GenresAPI(Resource):
    def get(self, genre_name): #retrieve all books from a particular genre in the DB
        genre = Genres.query.filter_by(name = genre_name).first()
        if not genre:
            return {"message": "Genre not found"}, 404
        books = genre.books
        genre_books = []
        for book in books:
            book_details = {}
            book_details["id"] = book.id
            book_details["name"] = book.name
            book_details["author"] = book.author
            book_details["genre"] = book.genre
            book_details["description"] = book.description
            book_details["price"] = book.price
            genre_books.append(book_details)
        return genre_books
    
    def post(self):
        args = genre_parser.parse_args()
        genre = Genres.query.filter_by(name = args["name"]).first()
        if genre:
            return {"message": "Genre already exists"}, 400
        
        new_genre = Genres(
            name = args["name"],
            description = args["description"],
            date_added = datetime.now()
        )
        db.session.add(new_genre)
        db.session.commit()
        return {"message": "Genre added successfully"}, 201
    
    def put(self, genre_name):
        args = genre_parser.parse_args()
        genre = Genres.query.filter_by(name = genre_name).first()
        if not genre:
            return {"message": "Genre not found"}, 404
        genre.name = args["name"]
        genre.description = args["description"]
        db.session.commit()
        return {"message": "Genre updated successfully"}, 200
    
    def delete(self, genre_name):
        genre = Genres.query.filter_by(name = genre_name).first()
        if not genre:
            return {"message": "Genre not found"}, 404
        db.session.delete(genre)
        db.session.commit()
        return {"message": "Genre deleted successfully"}, 200
        
api.add_resource(BooksAPI, '/api/books', '/api/books/<book_id>')
api.add_resource(GenresAPI,'/api/genres', '/api/genres/<genre_name>')
