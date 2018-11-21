import csv
import os

from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker

engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))

def main():
    db.execute("CREATE TABLE IF NOT EXISTS users (id SERIAL PRIMARY KEY, name VARCHAR NOT NULL, password VARCHAR NOT NULL, email VARCHAR unique)")
    db.execute("CREATE TABLE IF NOT EXISTS books (id SERIAL PRIMARY KEY, isbn VARCHAR UNIQUE, title VARCHAR NOT NULL, author VARCHAR NOT NULL, year VARCHAR NOT NULL)")
    db.execute("CREATE TABLE IF NOT EXISTS reviews (id SERIAL PRIMARY KEY, score INTEGER NOT NULL, text VARCHAR NOT NULL, author_id INTEGER REFERENCES users(id), book_id INTEGER REFERENCES books(id))")

    # Works for now but first line of CSV has to be ignor 
    '''
    f = open("books.csv")
    reader = csv.reader(f)
    next(reader, None)
    for isbn, title, author, year in reader:
        db.execute("INSERT INTO books (isbn, title, author, year) VALUES (:isbn, :title, :author, :year)",
                   {"isbn": isbn, "title": title, "author": author, "year": year})
        print(f"Added table books with isbn # {isbn} called {title} wrote by {author} on the year {year}.")
    '''
    db.commit()
    

if __name__ == "__main__":
    main()
