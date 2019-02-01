import csv
import os

from flask import Flask, render_template, request
from models import *


# Creates connection to DataBase and Binds to db
app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
db.init_app(app)

def main():

    # Opens the file
    b = open("books.csv")

    # Creates iterator to read the file line by line
    reader = csv.reader(b)

    # Skips first line of CSV file
    next(reader, None)

    # Inserts values in to DataBase on line at a time
    for isbn, title, author, year in reader:
        book = Book(isbn=isbn, title=title, author=author, year=year)
        db.session.add(book)
        print(f"Added book: {title} by {author} published on {year}.")
    db.session.commit()

if __name__ == "__main__":
    with app.app_context():
        main()
