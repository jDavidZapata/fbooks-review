import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

# Creates connection to DataBase and Binds to db
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name VARCHAR NOT NULL, password VARCHAR NOT NULL, email VARCHAR unique)")
    db.execute("CREATE TABLE IF NOT EXISTS books (id SERIAL PRIMARY KEY, isbn VARCHAR NOT NULL, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year INTEGER NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS reviews (id SERIAL PRIMARY KEY, rating INTEGER NOT NULL, review_text VARCHAR NOT NULL, review_user_id INTEGER REFERENCES users(id), rbook_isbn VARCHAR REFERENCES books(isbn))")

    # Opens the file   
    f = open("books.csv")

    # Creates iterator to read the file line by line
    reader = csv.reader(f)

    # Skips first line of CSV file
    next(reader, None)

    # Inserts values in to DataBase on line at a time
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added table books with isbn # {isbn} called {title} writen by {author} on the year {year}.")
   
    db.commit()
    

if __name__ == "__main__":
    main()
