from flask import Flask, flash, redirect, render_template, request, session, abort, redirect, url_for, g, jsonify
import requests, json
from models import *
from sqlalchemy import func, desc, and_, inspect

## from flask.ext.login import login_user , logout_user , current_user , login_required

app = Flask(__name__)

# Check for environment variable
if not os.getenv("DATABASE_URL"):
    raise RuntimeError("DATABASE_URL is not set")

# Set up database
app.config["SQLALCHEMY_DATABASE_URI"] = os.getenv("DATABASE_URL")
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
db.init_app(app)



# Configure session to use filesystem
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"

app.secret_key = b'_3#y2L"F4Q8z\n\xec]/'

print(app.config)

@app.route("/", methods=["GET", "POST"])
def index():

    error = None
    book = None

    """ Get 9 random books. """
    books = Book.query.order_by(func.random()).limit(9).all()
    
    """Check to see if User is in session."""
    user_id = session.get('user_id')
    user_name = session.get('user_name')

    if (not 'user_id' in session):
        
        return render_template("index.html", books=books, error=error)
    
    else:
        
        g.user_id = user_id
        g.user_name = user_name

        return render_template("index.html", books=books, error=error)


@app.route('/register', methods=('GET', 'POST'))
def register():
    """ Register a new user. """
        
    error = None
    success = None

    books = Book.query.order_by(func.random()).limit(9).all()

    """ Check if the user is in session. """
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    
    if ('user_id' in session):
        g.user_id = user_id
        g.user_name = user_name
        
        return redirect(url_for('index'))

    if request.method == 'POST':

        name = request.form['name']
        password = request.form['password']
        email = request.form['email']

        if not name:
            error = 'Name is required.'
        elif not password:
            error = 'Password is required.'
        elif not email:
            error = 'Email is required.'

        """ Make sure email is not already register. """
        user = User.query.filter_by(email=email).first()

        if user is not None:
            error = 'User with email {0} is already registered.'.format(email)

        if error is None:
            """If the email is available, store it in the database and go to the login page. """

            user = User(name=name, password=password, email=email)
            db.session.add(user)
            db.session.commit()

            """Store the user id in a new session and return to the index"""

            session.clear()
            
            session['user_id'] = user.id
            session['user_name'] = user.name

            g.user_id = user.id
            g.user_name = user.name
            
            success = 'Thank You, For Signing Up.'
            
            return render_template('index.html', success=success, books=books)

    return render_template('auth/register.html', error=error, books=books)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """ Log in a registered user by adding the user id to the session. """

    error = None
    success = None

    books = Book.query.order_by(func.random()).limit(9).all()
    
    """ If the users id is in the session, then user already loged in. """
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    
    if ('user_id' in session):
        g.user_id = user_id
        g.user_name = user_name
        
        return redirect(url_for('index'))

    if request.method == 'POST':
        """ Get values from form. """

        email = request.form['email']
        password = request.form['password']

        """ Get user from database. """
        user = User.query.filter(and_(User.email == email, User.password == (password))).first() 

        if user is None:
            error = 'Incorrect Email or Password.'

        if error is None:
            """ Store the user id in a new session and return to the index."""

            session.clear()
            session['user_id'] = user.id
            session['user_name'] = user.name
            
            g.user_id = user.id
            g.user_name = user.name

            success = 'Your Now Signed In.'

            return render_template('index.html', success=success, error=error, books=books)

    return render_template('auth/login.html', books=books, error=error)


@app.route('/logout')
def logout():
    """ Long out user. """

    success = None

    """Clear the current session."""
    session.clear()
    
    success = 'Your Now Loged Out.'

    return redirect(url_for('index'))
    


@app.route('/search', methods=['GET', 'POST'])
def search():
    """ Search for books. """

    error = None
    books = None

    """Check to see if User is in session."""
    user_id = session.get('user_id')
    user_name = session.get('user_name')
    
    if ('user_id' in session):
                        
        g.user_id = user_id
        g.user_name = user_name

    if request.method == 'POST':

        """ Get books with title. """
        if request.form.get('b_title', None):

            b_title = request.form['b_title']
            title = '%{}%'.format(b_title)
            books = Book.query.filter(Book.title.ilike(title)).order_by(Book.title.asc()).all()
            
            if not books:
                error = 'No Such Title'
            return render_template("search.html", books=books, error=error, book=book)

            """ Get book with author. """
        elif request.form.get('b_author', None):
            b_author = request.form['b_author']
            author = '%{}%'.format(b_author)
            books = Book.query.filter(Book.author.ilike(author)).order_by(Book.title.asc()).all()
            
            if not books:
                error = 'No Such Author'
            return render_template("search.html", books=books, error=error, book=book)

            """ Get books with isbn #. """
        elif request.form.get('b_isbn', None):
            b_isbn = request.form['b_isbn']
            isbn = '%{}%'.format(b_isbn)
            books = Book.query.filter(Book.isbn.ilike(isbn)).order_by(Book.title.asc()).all()
            
            if not books:
                error = 'No Such isbn #'
            return render_template("search.html", books=books, error=error, book=book)

            """ Else get 9 random books. """
        else:
            error = 'Random Books'
            
            books = Book.query.order_by(func.random()).limit(9).all()
            
            return render_template("search.html", books=books, error=error)
    
    books = Book.query.order_by(func.random()).limit(9).all()
    
    return render_template("search.html", books=books, error=error)


@app.route('/book/<string:b_title>', methods=['GET', 'POST'])
def book(b_title):
    """ Results for book. """

    error = None    

    """ Get book from database. """
    
    book = db.session.query(Book.title, Book.author, Book.isbn, Book.year, func.round(func.avg(Review.rating), 2).label('round'), func.count(Review.rating).label('count')).outerjoin(Review, Book.isbn == Review.rbook_isbn).filter(Book.title == (b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).all()

    print('book:{}'.format(book))
       
    """Check to see if User is in session."""

    user_id = session.get('user_id')
    user_name = session.get('user_name')
   
    if (not 'user_id' in session):
        
        if not book:
            # If there is no book.
            error = 'No Such Book.'
       
        return render_template("bookpage.html", book=book, error=error)

    else:
        g.user_id = user_id
        g.user_name = user_name
        
        if not book:
            # If there is no book.
            error = 'No Such Book.'

            return render_template("bookpage.html", book=book, error=error)
       
        book = [r._asdict() for r in book]

        print('book:{}'.format(book))

        b_isbn = book[0]['isbn']
        b_author = book[0]['author']
        b_year = book[0]['year']
        b_count = book[0]['count']
        b_rating = book[0]['round']

        reviews = Review.query.filter(Review.rbook_isbn == b_isbn).all()
        
        print('reviews:{}'.format(reviews))

        """ Api request. """
    
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.getenv("API_KEY"), "isbns": b_isbn})
        
        if res.status_code != 200:
            raise Exception("ERROR: API request unsuccessful.")
       
        data = res.json()

        print(data)

        """ Take values out of data from Api request. """
        goodr_review_count = data['books'][0]['work_ratings_count']

        goodr_review_rating = data['books'][0]['average_rating']

        """ Put values from data into book. """     

        book[0]['goodr_review_count'] = goodr_review_count
        book[0]['goodr_review_rating'] = goodr_review_rating

        session['b_title'] = b_title
  
        return render_template("bookpage.html", book=book, error=error, reviews=reviews)


@app.route('/create', methods=['GET', 'POST'])
def create():
    """ Create review. """

    error = None
    success = None
    
    """Check to see if User is in session."""

    if (not 'user_id' in session):
        
        return redirect(url_for('search'))
       
    else:

        user_id = session.get('user_id')
        user_name = session.get('user_name')
        
        b_title = session.get('b_title')
        
        g.user_id = user_id
        g.user_name = user_name
                
        book = db.session.query(Book.title, Book.author, Book.isbn, Book.year, func.round(func.avg(Review.rating), 2).label('round'), func.count(Review.rating).label('count')).outerjoin(Review, Book.isbn == Review.rbook_isbn).filter(Book.title == (b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).all()

        if not book:
            error = 'Pick A Book'
            books = Book.query.order_by(func.random()).limit(9).all()

            return render_template("search.html", error=error, books=books)

        if request.method == 'POST':
            """ Get values from form. """

            rating = request.form['radio']
            review_text = request.form['reviewtext']
            review_user_id = user_id            
            rbook_isbn = book[0].isbn

            """ Check for user id in the reviews for that book. """

            if error is None:

                user_review = Review.query.filter(and_(Review.review_user_id == (review_user_id), Review.rbook_isbn == (rbook_isbn))).first()
               
                if user_review is not None:

                    error = 'You have already Reviewed this Book.'

                else:
                    """ If not reviewed by user, add review. """

                    # book.add_review(review_text, rating, rbook_isbn, review_user_id)

                    review = Review(review_text=review_text, rating=rating, rbook_isbn=rbook_isbn, review_user_id=review_user_id)
                    db.session.add(review)
                    db.session.commit()

                    success = 'Great Review!!!'
                    
                    book = db.session.query(Book.title, Book.author, Book.isbn, Book.year, func.round(func.avg(Review.rating), 2).label('round'), func.count(Review.rating).label('count')).outerjoin(Review, Book.isbn == Review.rbook_isbn).filter(Book.title == (b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).all()

                    reviews = Review.query.filter(Review.rbook_isbn == rbook_isbn).all()

                    return render_template("bookpage.html", error=error, book=book, reviews=reviews, success=success)

        return render_template("bookpage.html", error=error, book=book)


@app.route('/api/book/<isbn>', methods=['GET', 'POST'])
def book_api(isbn):
    """ Api route. """
    
    if request.method == 'GET':
        """Return details about a single book."""
        
        # Make sure book exists.
        book = db.session.query(Book.title, Book.author, Book.isbn, Book.year, func.round(func.avg(Review.rating), 2).label('round'), func.count(Review.rating).label('count')).outerjoin(Review, Book.isbn == Review.rbook_isbn).filter(Book.isbn == (isbn)).group_by(Book.title, Book.author, Book.isbn, Book.year).all()

        if not book:
            return jsonify({"error": "Invalid isbn"}), 404

        # Get all info values.
        print('That')
        print(book)
        return jsonify({
            "title": book[0].title,
            "author": book[0].author,
            "year": book[0].year,
            "isbn": book[0].isbn,
            "review_count": book[0].count,
            "average_score": str(book[0].round),
        })


@app.route('/my_books', methods=['GET', 'POST'])
def my_books():
    """ Route for my books. """

    error = None
    success = None
    
    """Check to see if User is in session."""

    if (not 'user_id' in session):
               
        return redirect(url_for('index'))

    else:

        user_id = session.get('user_id')

        user_name= session.get('user_name')
                
        b_title = session.get('b_title')

        g.user_id = user_id

        g.user_name = user_name

        """  display a list of my books.  
            also add link button 'to add a book' to my books.
            add link to bookspage. """

        return render_template("my_books.html", error=error, success=success)


if __name__ == "__main__":
    app.run()
