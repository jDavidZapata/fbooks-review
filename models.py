import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    password = db.Column(db.String, nullable=False)
    email = db.Column(db.String, nullable=False, unique=True)
    my_books = db.relationship("Mybook", backref="user", lazy=True)

    def __repr__(self):
        return '<User %r>' % self.name

    def add_book(self, isbn, title, author, year):
        b = Book(isbn=isbn, title=title, author=author, year=year)
        db.session.add(b)
        db.session.commit()

    def add_my_book(self, user_id, book_isbn):
        mb = Mybook(user_id=self.id, isbn=isbn)
        db.session.add(mb)
        db.session.commit()


class Book(db.Model):
    __tablename__ = "books"
    id = db.Column(db.Integer, primary_key=True)
    isbn = db.Column(db.String, nullable=False, unique=True)
    title = db.Column(db.String, nullable=False)
    author = db.Column(db.String, nullable=False)
    year = db.Column(db.Integer, nullable=False)
    reviews = db.relationship("Review", backref="book", lazy=True)

    def __repr__(self):
        return '<Book title: %r>' % self.title


    def add_review(self, review_text, rating, rbook_isbn, review_user_id):
        r = Review(review_text=review_text, rating=rating, rbook_isbn=self.isbn, review_user_id=review_user_id)
        db.session.add(r)
        db.session.commit()


class Review(db.Model):
    __tablename__ = "reviews"
    id = db.Column(db.Integer, primary_key=True)
    review_text = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    rbook_isbn = db.Column(db.String, db.ForeignKey("books.isbn"), nullable=False)
    review_user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    reviewers = db.relationship("User", backref="review", lazy=True)


    def __repr__(self):
        return '<Review isbn # %r>' % self.rbook_isbn

class Mybook(db.Model):
    __tablename__ = "my_books"
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)
    isbn = db.Column(db.String, db.ForeignKey("books.isbn"), nullable=False)