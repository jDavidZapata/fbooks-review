
#from flask.ext.login import login_user , logout_user , current_user , login_required

from flask import Flask, flash, redirect, render_template, request, session, abort, redirect, url_for, g
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

app = Flask(__name__)


# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
# Session(app)
app.secret_key = b'_3#y2L"F4Q8z\n\xec]/'

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))


@app.route("/", methods=["GET", "POST"])
def index():

    error = None

    book = None

    books = db.execute(
        'SELECT * FROM books ORDER BY random() LIMIT 9').fetchall()

    db.close()

    """Check to see if User is in session."""

    user_id = session.get('user_id')

    if (not 'user_id' in session):
        g.user = None

        return render_template("index.html", books=books, error=error, book=book)
    else:
        g.user = db.execute(
            'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }
        ).fetchone()
        db.close()

        return render_template("index.html", books=books, error=error, book=book)


@app.route('/register', methods=('GET', 'POST'))
def register():
    """Register a new user.
        Check if the user is in session.
        Validates that the name and email are not already taken. 
        Redirect to index page.
        #Hashes the password for security.
    """
    error = None

    success = None

    user_id = session.get('user_id')

    if ('user_id' in session):

        g.user = db.execute(
            'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }
        ).fetchone()

        db.close()

        # change to redirect to current page
        return render_template("index.html")

    if request.method == 'POST':

        name = request.form['name']
        password = request.form['password']
        email = request.form['email']

        error = None

        if not name:
            error = 'Name is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email required.'

        user = db.execute("SELECT * FROM users WHERE email IN (:email)",
                          {"email": email}).fetchone()

        if user is not None:
            error = 'User with email {0} is already registered.'.format(email)


        if error is None:
            """If the name is available, store it in the database and go to the login page"""

            db.execute("INSERT INTO users (name, password, email) VALUES (:name, :password, :email)",
                       {"name": name, "password": password, "email": email})
            db.commit()

            
            user = db.execute("SELECT * FROM users WHERE email IN (:email)", {
                              "email": email}).fetchone()
            

            """Store the user id in a new session and return to the index"""

            session.clear()
            session['user_id'] = user['id']
            g.user = user 
            
            '''
            g.user = db.execute(
                'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }
            ).fetchone()
            '''

            db.close()

            success = 'Thank You For Signing Up.'

            # Change to redirect to curent page
            return redirect(url_for('index'))

    return render_template('auth/register.html', book=book, error=error, success=success)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered user by adding the user id to the session."""

    error = None

    success = None

    user_id = session.get('user_id')
    if ('user_id' in session):
        g.user = db.execute(
            'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }
        ).fetchone()
        db.close()

        # change to redirect to current page
        return render_template("index.html", error=error)

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        error = None
        user = db.execute("SELECT * FROM users WHERE email IN (:email) AND password IN (:password)",
                          {"email": email, "password": password}).fetchone()

        if user is None:
            error = 'Incorrect Email or Password.'

        if error is None:

            """Store the user id in a new session and return to the index."""
            session.clear()
            session['user_id'] = user['id']
            g.user = db.execute(
                'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }
            ).fetchone()
            db.close()

            success = 'Your Now Signed In.'

            return redirect(url_for('index'))

    return render_template('auth/login.html', book=book, error=error, success=success)


@app.route('/logout')
def logout():

    success = None

    """Clear the current session, including the stored user id."""
    session.clear()
    g.user = None

    success = 'Your Now Loged Out.'

    return redirect(url_for('index', success=success))


@app.route('/search', methods=['GET', 'POST'])
def search():

    error = None

    book = None

    books = None

    user_id = session.get('user_id')

    """Check to see if User is in session."""

    if (not 'user_id' in session):
        g.user = None

    else:
        g.user = db.execute(
            'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }
        ).fetchone()

        db.close()

    if request.method == 'POST':

        if request.form.get('b_title', None):
            b_title = request.form['b_title']
            books = db.execute(
                "SELECT * FROM books WHERE title ILIKE ('%' || :title || '%')", {"title": b_title, }).fetchall()
            db.close()
            if books is None:
                error = "No Such Title"
            return render_template("search.html", books=books, error=error, book=book)

        elif request.form.get('b_author', None):
            b_author = request.form['b_author']
            books = db.execute(
                "SELECT * FROM books WHERE author ILIKE ('%' || :author || '%')", {"author": b_author, }).fetchall()
            db.close()
            if books is None:
                error = "No Such Author"
            return render_template("search.html", books=books, error=error, book=book)

        elif request.form.get('b_isbn', None):
            b_isbn = request.form['b_isbn']
            books = db.execute(
                "SELECT * FROM books WHERE isbn ILIKE ('%' || :isbn || '%')", {"isbn": b_isbn, }).fetchall()
            db.close()
            if books is None:
                error = "No Such isbn #"
            return render_template("search.html", books=books, error=error, book=book)

        else:
            books = db.execute(
                'SELECT * FROM books ORDER BY random() LIMIT 9').fetchall()
            db.close()

            return render_template("search.html", books=books, error=error)

    # book = db.execute('SELECT * FROM books WHERE title = :title', {"title": b_title,}).fetchone()
    books = db.execute(
        'SELECT * FROM books ORDER BY random() LIMIT 9').fetchall()

    return render_template("search.html", books=books, error=error, book=book)


@app.route('/book/<string:b_title>')
def book(b_title):

    error = None

    user_id = session.get('user_id')

    """Check to see if User is in session."""

    if (not 'user_id' in session):
        g.user = None

        #book = db.execute('SELECT * FROM books WHERE title = :title', {"title": b_title,}).fetchone()
        book = db.execute('SELECT title, author, isbn, year, round(avg(rating), 1), count(rating) from books left join reviews on isbn = rbook_isbn where title IN (:title) group by title, author, isbn, year', {
                          "title": b_title, }).fetchone()

        return render_template("bookpage.html", book=book, error=error)

    else:
        g.user = db.execute(
            'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }
        ).fetchone()

        db.close()

        # book = db.execute('SELECT * FROM books WHERE title = :title', {"title": b_title,}).fetchone()
        book = db.execute('SELECT title, author, isbn, year, round(avg(rating), 1), count(rating) from books left join reviews on isbn = rbook_isbn where title IN (:title) group by title, author, isbn, year', {
                          "title": b_title, }).fetchone()

        session['b_title'] = b_title

        return render_template("bookpage.html", book=book, error=error)


@app.route('/create', methods=['GET', 'POST'])
def create():

    error = None

    success = None

    book = None

    """Check to see if User is in session."""

    if (not 'user_id' in session):
        g.user = None

        return render_template("bookpage.html", error=error, book=book)

    else:

        user_id = session.get('user_id')

        b_title = session.get('b_title')

        # book = db.execute('SELECT * FROM books WHERE title = :title', {"title": b_title,}).fetchone()
        book = db.execute('SELECT title, author, isbn, year, round(avg(rating), 1), count(rating) from books left join reviews on isbn = rbook_isbn where title IN (:title) group by title, author, isbn, year', {
                          "title": b_title, }).fetchone()

        g.user = db.execute(
            'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }).fetchone()

        db.close()

        if request.method == 'POST':

            rating = request.form['radio']
            review_text = request.form['reviewtext']
            review_user_id = user_id
            rbook_isbn = book.isbn

            error = None

            # check to see if user id is in the review for that book

            if error is None:

                user_review = db.execute("SELECT * FROM reviews WHERE review_user_id IN (:review_user_id) AND rbook_isbn IN (:rbook_isbn)", {
                                         "review_user_id": review_user_id, "rbook_isbn": rbook_isbn}).fetchone()

                if user_review is not None:

                    error = 'You have already Reviewed this Book.'

                else:

                    db.execute("INSERT INTO reviews (rating, review_text, review_user_id, rbook_isbn) VALUES (:rating, :review_text, :review_user_id, :rbook_isbn)",
                               {"rating": rating, "review_text": review_text, "review_user_id": review_user_id, "rbook_isbn": rbook_isbn})
                    db.commit()

                    success = 'Great Review!!!'

                    book = db.execute('SELECT title, author, isbn, year, round(avg(rating), 1), count(rating) from books left join reviews on isbn = rbook_isbn where title IN (:title) group by title, author, isbn, year', {
                                      "title": b_title, }).fetchone()

                    return render_template("bookpage.html", error=error, book=book, success=success)

        return render_template("bookpage.html", error=error, book=book)


@app.route('/api/<isbn>', methods=['GET', 'POST'])
def api(isbn):
    if request.method == 'GET':

        '''
        make jason response

        {
        "title": "Memory",
        "author": "Doug Lloyd",
        "year": 2015,
        "isbn": "1632168146",
        "review_count": 28,
        "average_score": 5.0
        }
        '''


if __name__ == "__main__":
    app.secret_key = os.urandom(13)
    app.run()
