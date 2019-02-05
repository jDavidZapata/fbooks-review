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
    '''
    books = db.execute(
        'SELECT * FROM (SELECT * FROM books ORDER BY random() LIMIT 9) TB ORDER BY title ASC').fetchall()
    '''

    """Check to see if User is in session."""
    user_id = session.get('user_id')

    if (not 'user_id' in session):
        g.user = None

        return render_template("index.html", books=books, error=error, book=book)
    
    else:
        g.user = User.query.get(user_id)


        return render_template("index.html", books=books, error=error, book=book)


@app.route('/register', methods=('GET', 'POST'))
def register():
    """ Register a new user. """
    
    """ 
        Redirect to index page.
        #Hashes the password for security.
    """
    error = None
    success = None

    books = Book.query.order_by(func.random()).limit(9).all()

    """ Check if the user is in session. """
    user_id = session.get('user_id')

    if ('user_id' in session):
        g.user = User.query.get(user_id)

        # change to redirect to current page
        return redirect(url_for('index'))

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
            error = 'Email is required.'

        """ Make sure email is not already register. """

        user = User.query.filter_by(email=email).first()

        '''
        user = db.execute("SELECT * FROM users WHERE email IN (:email)",
                          {"email": email}).fetchone()
        '''

        if user is not None:
            error = 'User with email {0} is already registered.'.format(email)

        if error is None:
            """If the email is available, store it in the database and go to the login page. """

            user = User(name=name, password=password, email=email)
            db.session.add(user)
            db.session.commit()

            '''db.execute("INSERT INTO users (name, password, email) VALUES (:name, :password, :email)",
                       {"name": name, "password": password, "email": email})
            db.commit()


            user = db.execute("SELECT * FROM users WHERE email IN (:email)", {
                              "email": email}).fetchone()
            '''

            """Store the user id in a new session and return to the index"""

            session.clear()
            session['user_id'] = user.id

            g.user = user

            success = 'Thank You, For Signing Up.'

            
            # Change to redirect to curent page
            return render_template('index.html', success=success, books=books)

    return render_template('auth/register.html', error=error, books=books)


@app.route('/login', methods=('GET', 'POST'))
def login():
    """ Log in a registered user by adding the user id to the session. """

    error = None
    success = None

    books = Book.query.order_by(func.random()).limit(9).all()

    user_id = session.get('user_id')



    """ If the users id is in the session, then user already loged in. """
    if ('user_id' in session):
        g.user = User.query.get(user_id)

        '''
        g.user = db.execute(
            'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }
        ).fetchone()
        '''

        # change to redirect to current page
        return redirect(url_for('index'))

    if request.method == 'POST':
        """ Get values from form. """

        email = request.form['email']
        password = request.form['password']

        error = None

        """ Get user from database. """
        user = User.query.filter(and_(User.email == email, User.password == (password))).first() 

        '''user = db.execute("SELECT * FROM users WHERE email IN (:email) AND password IN (:password)",
                          {"email": email, "password": password}).fetchone()
        '''

        if user is None:
            error = 'Incorrect Email or Password.'

        if error is None:

            """ Store the user id in a new session and return to the index."""
            session.clear()
            session['user_id'] = user.id

            g.user = user 

            #  g.user = User.query.get(user_id)

            '''g.user = db.execute(
                'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }
            ).fetchone()
            db.close()
            '''

            success = 'Your Now Signed In.'

            return render_template('index.html', success=success, error=error, books=books)

    return render_template('auth/login.html', books=books, error=error)


@app.route('/logout')
def logout():
    """ Long out user. """

    success = None

    """Clear the current session."""
    session.clear()
   
    g.user = None

    success = 'Your Now Loged Out.'

    return redirect(url_for('index'))
    


@app.route('/search', methods=['GET', 'POST'])
def search():
    """ Search for books. """

    error = None
    book = None
    books = None

    """Check to see if User is in session."""
    user_id = session.get('user_id')

    if (not 'user_id' in session):
        g.user = None

    else:
        g.user = User.query.get(user_id)
        '''
        g.user = db.execute(
            'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }
        ).fetchone()
        '''

    if request.method == 'POST':

        """ Get books with title. """
        if request.form.get('b_title', None):

            b_title = request.form['b_title']
            title = '%{}%'.format(b_title)
            books = Book.query.filter(Book.title.ilike(title)).order_by(Book.title.asc()).all()
            '''
            books = db.execute(
                "SELECT * FROM books WHERE title ILIKE ('%' || :title || '%') ORDER BY title ASC", {"title": b_title, }).fetchall()
            '''
            if not books:
                error = 'No Such Title'
            return render_template("search.html", books=books, error=error, book=book)

            """ Get book with author. """
        elif request.form.get('b_author', None):
            b_author = request.form['b_author']
            author = '%{}%'.format(b_author)
            books = Book.query.filter(Book.author.ilike(author)).order_by(Book.title.asc()).all()
            '''
            books = db.execute(
                "SELECT * FROM books WHERE author ILIKE ('%' || :author || '%') ORDER BY title ASC", {"author": b_author, }).fetchall()
            '''
            if not books:
                error = 'No Such Author'
            return render_template("search.html", books=books, error=error, book=book)

            """ Get books with isbn #. """
        elif request.form.get('b_isbn', None):
            b_isbn = request.form['b_isbn']
            isbn = '%{}%'.format(b_isbn)
            books = Book.query.filter(Book.isbn.ilike(isbn)).order_by(Book.title.asc()).all()
            '''
            books = db.execute(
                "SELECT * FROM books WHERE isbn ILIKE ('%' || :isbn || '%') ORDER BY title ASC", {"isbn": b_isbn, }).fetchall()
            '''
            if not books:
                error = 'No Such isbn #'
            return render_template("search.html", books=books, error=error, book=book)

            """ Else get 9 random books. """
        else:
            #  books = Book.query.order_by(func.random().limit(9)).all()
            books = Book.query.order_by(func.random()).limit(9).all()
            '''
            books = db.execute(
                'SELECT * FROM (SELECT * FROM books ORDER BY random() LIMIT 9) TB ORDER BY title ASC').fetchall()
            '''
            return render_template("search.html", books=books, error=error)

    # book = db.execute('SELECT * FROM books WHERE title = :title', {"title": b_title,}).fetchone()
    # book = Book.query.filter_by(title = b_title)

    # books = Book.query.order_by(func.random().limit(9)).all()
    books = Book.query.order_by(func.random()).limit(9).all()
    '''
    books = db.execute(
        'SELECT * FROM (SELECT * FROM books ORDER BY random() LIMIT 9) TB ORDER BY title ASC').fetchall()
    '''
    return render_template("search.html", books=books, error=error, book=book)


@app.route('/book/<string:b_title>')
def book(b_title):
    """ Results for book. """

    error = None

    user_id = session.get('user_id')

    """ Get book from database. And make sure user input is a string if query is None then error. """
    
    #book = Book.query.filter_by(title=b_title).first() 

    ### book = db.session.query(Book, Review).outerjoin(Review, Book.isbn == Review.rbook_isbn).filter(Book.title == (b_title)).all()

    book = db.session.query(Book.title, Book.author, Book.isbn, Book.year, func.round(func.avg(Review.rating), 2).label('round'), func.count(Review.rating).label('count')).outerjoin(Review, Book.isbn == Review.rbook_isbn).filter(Book.title == (b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).all()

    #book = Book.query.options(db.joinedload(Review).joinedload(func.avg(Review.rating).label('round'), Book.isbn == Review.rbook_isbn)).filter(Book.title == (b_title)).all()

    #book = Book.query.options(db.joinedload(Review, Book.isbn == Review.rbook_isbn)).filter(Book.title == (b_title)).all()


    #book = Book.query(Book.title, Book.author, Book.isbn, Book.year, func.round(func.avg(Review.rating), 2), func.count(Review.rating)).outerjoin(Review, Book.isbn == Review.rbook_isbn).filter(Book.title == (b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).first()
    
    print(b_title)

    # book = Book.query.filter_by(title=b_title).first()

    # book = db.session.query(Book, Review).filter(Book.isbn == Review.rbook_isbn, Book.title == (b_title)).group_by(Book.title, Book.author, Book.isbn, Book.id, Book.year, Review.id).all()

    print('book:{}'.format(book))

    if book == []:
        error = 'No Such Book.'
    if book is None:
        error = 'No Such Book.'
      

    """Check to see if User is in session."""

    if (not 'user_id' in session):
        g.user = None
        '''
        book = Book.query.filter(Book, func.round(func.avg(Review.rating), 2), func.count(Review.rating)).join(Reviews).filter(Book.isbn == Review.rbook_isbn, Book.title.in_(b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).first()
        
        book = db.session.query(Book, Review).filter(Book.isbn == Review.rbook_isbn, Book.title.in_(b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).first()
        
        book = db.session.query(Book.title, Book.author, Book.isbn, Book.year, func.avg(Review.rating).label('round'), func.count(Review.rating)).filter(Book.isbn == Review.rbook_isbn, Book.title.in_(b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).first()
        '''
        '''
        book = db.execute('SELECT title, author, isbn, year, round(avg(rating), 2), count(rating) from books left join reviews on isbn = rbook_isbn WHERE title IN (:title) GROUP BY title, author, isbn, year', {
                          "title": b_title, }).fetchone()
        '''
        return render_template("bookpage.html", book=book, error=error)

    else:
        g.user = User.query.get(user_id)
        



        '''
        g.user = db.execute(
            'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }
        ).fetchone()
        '''

        """ Get book from database. """
        '''
        book = db.session.query(Book.title, Book.author, Book.isbn, Book.year, func.avg(Review.rating).label('round'), func.count(Review.rating)).filter(Book.isbn == Review.rbook_isbn, Book.title.in_(b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).first()
        '''

        
        '''
        book = Book.query.filter(Book.title, Book.author, Book.isbn, Book.year, func.round(func.avg(Review.rating), 2), func.count(Review.rating)).join(Reviews.filter(Book.isbn == Review.rbook_isbn, Book.title.in_(b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year)).first()
        book = db.execute('SELECT title, author, isbn, year, round(avg(rating), 2), count(rating) from books left join reviews on isbn = rbook_isbn WHERE title IN (:title) GROUP BY title, author, isbn, year', {
                          "title": b_title, }).fetchone()
        '''

        '''
        b, c = {}, []
        for rowproxy in book:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            # build up the dictionary
            b = {**b, **{[0]: [1]}}
            c.append(b)

        print(c)
        
        '''

        '''
        tup = None
        d, a = {}, []
        for rowproxy in book:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for tup in rowproxy:
                # build up the dictionary
                d = {tup}
            a.append(d)

        print(d)

        '''

        book = [r._asdict() for r in book]

        print('book:{}'.format(book))

        b_isbn = book[0]['isbn']

        b_author = book[0]['author']

        b_year = book[0]['year']

        b_count = book[0]['count']

        b_rating = book[0]['round']

        print(b_isbn)

        

        reviews = Review.query.filter(Review.rbook_isbn == b_isbn).all()
        '''        
        reviews = db.execute('SELECT * FROM reviews WHERE rbook_isbn IN (:rbook_isbn)', {"rbook_isbn": b_isbn, }).fetchall()
        '''
        
        print('reviews:{}'.format(reviews))

        '''
        d, a = {}, []
        for rowproxy in reviews:
            # rowproxy.items() returns an array like [(key0, value0), (key1, value1)]
            for tup in rowproxy.items():
                # build up the dictionary
                d = {**d, **{tup[0]: tup[1]}}
            a.append(d)

        print(a)

        reviews = a
        '''

       

        """ Api request. """

        
        res = requests.get("https://www.goodreads.com/book/review_counts.json", params={"key": os.getenv("API_KEY"), "isbns": b_isbn})
        
        if res.status_code != 200:
            raise Exception("ERROR: API request unsuccessful.")
        
       
        data = res.json()

        """ Take values out of data from Api request. """
        goodr_review_count = data['books'][0]['work_ratings_count']

        goodr_review_rating = data['books'][0]['average_rating']

        """ Put values from data into book. """     

        goodreads = {}



        goodreads['goodr_review_count'] = goodr_review_count

        goodreads['goodr_review_rating'] = goodr_review_rating


        print('goodreads:{}'.format(goodreads))


        book[0]['goodr_review_count'] = goodr_review_count

        book[0]['goodr_review_rating'] = goodr_review_rating


        session['b_title'] = b_title
  
        # session['book'] = book
        # session['reviews'] = reviews   

        print(book)

        
                  
        print('this') 

        return render_template("bookpage.html", book=book, error=error, reviews=reviews)


@app.route('/create', methods=['GET', 'POST'])
def create():
    """ Create review. """

    error = None
    success = None
    book = None

    """Check to see if User is in session."""

    if (not 'user_id' in session):
        g.user = None

        return render_template("bookpage.html", error=error, book=book)

    else:

        user_id = session.get('user_id')
        #book = session.get('book')
        
        b_title = session.get('b_title')

        book = db.session.query(Book.title, Book.author, Book.isbn, Book.year, func.round(func.avg(Review.rating), 2).label('round'), func.count(Review.rating).label('count')).outerjoin(Review, Book.isbn == Review.rbook_isbn).filter(Book.title == (b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).all()

        #book = Book.query.options(db.joinedload(Review, Book.isbn == Review.rbook_isbn)).filter(Book.title == (b_title)).all()


        print(book)

        '''   
        # book = db.execute('SELECT * FROM books WHERE title = :title', {"title": b_title,}).fetchone()
        
        book = db.session.query(Book, func.round(func.avg(Review.rating), 2), func.count(Review.rating)).filter(Book.isbn == Review.rbook_isbn, Book.title.in_(b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).first()

        book = db.execute('SELECT title, author, isbn, year, round(avg(rating), 2), count(rating), review_text from books left join reviews on isbn = rbook_isbn where title IN (:title) group by title, author, isbn, year', {
                          "title": b_title, }).fetchone()
        '''
        g.user = User.query.get(user_id)
        '''
        g.user = db.execute(
            'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }).fetchone()
        '''
        if request.method == 'POST':
            """ Get values from form. """

            rating = request.form['radio']
            review_text = request.form['reviewtext']
            review_user_id = user_id
            #rbook_isbn = book[0]['isbn']
            rbook_isbn = book[0].isbn

            #book = db.session.query(Book.title, Book.author, Book.isbn, Book.year, func.round(func.avg(Review.rating), 2).label('round'), func.count(Review.rating).label('count')).outerjoin(Review, Book.isbn == Review.rbook_isbn).filter(Book.title == (b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).all()

            """ Check for user id in the reviews for that book. """

            if error is None:

                user_review = Review.query.filter(and_(Review.review_user_id == (review_user_id), Review.rbook_isbn == (rbook_isbn))).first()
                

                print('user_review:{}'.format(user_review))
                '''
                user_review = db.execute("SELECT * FROM reviews WHERE review_user_id IN (:review_user_id) AND rbook_isbn IN (:rbook_isbn)", {
                                         "review_user_id": review_user_id, "rbook_isbn": rbook_isbn}).fetchone()
                '''
                if user_review is not None:

                    error = 'You have already Reviewed this Book.'

                else:
                    """ If not reviewed by user, add review. """

                    # book.add_review(review_text, rating, rbook_isbn, review_user_id)

                    review = Review(review_text=review_text, rating=rating, rbook_isbn=rbook_isbn, review_user_id=review_user_id)
                    db.session.add(review)
                    db.session.commit()


                    '''
                    db.execute("INSERT INTO reviews (rating, review_text, review_user_id, rbook_isbn) VALUES (:rating, :review_text, :review_user_id, :rbook_isbn)",
                               {"rating": rating, "review_text": review_text, "review_user_id": review_user_id, "rbook_isbn": rbook_isbn})
                    db.commit()
                    '''
                    success = 'Great Review!!!'

                    #session['book'] = book

                    book = db.session.query(Book.title, Book.author, Book.isbn, Book.year, func.round(func.avg(Review.rating), 2).label('round'), func.count(Review.rating).label('count')).outerjoin(Review, Book.isbn == Review.rbook_isbn).filter(Book.title == (b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).all()

                    b_isbn = book[0].isbn

                    reviews = Review.query.filter(Review.rbook_isbn == b_isbn).all()


                    #book = db.execute('SELECT title, author, isbn, year, round(avg(rating), 2), count(rating) from books left join reviews on isbn = rbook_isbn where title IN (:title) group by title, author, isbn, year', {
                                      #"title": b_title, }).fetchone()

                    return render_template("bookpage.html", error=error, book=book, reviews=reviews, success=success)

        return render_template("bookpage.html", error=error, book=book)


@app.route('/api/book/<isbn>', methods=['GET', 'POST'])
def book_api(isbn):
    """ Api route. """
    
    if request.method == 'GET':
        """Return details about a single book."""
        
        # Make sure book exists.
        book = db.session.query(Book, func.avg(Review.rating).label('round'), func.count(Review.rating)).filter(Book.isbn == Review.rbook_isbn, Book.title.in_(b_title)).group_by(Book.title, Book.author, Book.isbn, Book.year).first()

        '''
        book = db.execute('SELECT title, author, isbn, year, round(avg(rating), 2), count(rating) from books left join reviews on isbn = rbook_isbn where isbn IN (:isbn) group by title, author, isbn, year', {
            "isbn": isbn, }).fetchone()
        '''
        if book is None:
            return jsonify({"error": "Invalid isbn"}), 404

        # Get all info values.
        print('That')
        print(book)
        return jsonify({
            "title": book.title,
            "author": book.author,
            "year": book.year,
            "isbn": book.isbn,
            "review_count": book.count,
            "average_score": str(book.round),
            # "reviews": text
        })



@app.route('/my_books', methods=['GET', 'POST'])
def my_books():
    """ Route for my books. """

    error = None
    success = None
    book = None
    books = None

    """Check to see if User is in session."""

    if (not 'user_id' in session):
        g.user = None

        return render_template("index.html", error=error, book=book, books=books)

    else:

        user_id = session.get('user_id')

        book = session.get('book')

        b_title = session.get('b_title')

        g.user = User.query.get(user_id)
        '''
        g.user = db.execute(
            'SELECT * FROM users WHERE id IN (:id)', {"id": user_id, }).fetchone()
        '''
        return render_template("my_books.html", error=error, book=book, success=success)



'''
    # Execute query to get the review text from each review
    reviews= book.review_text
    
    text = []

    for review in reviews:
        text.append(review.review_text)
'''


if __name__ == "__main__":
    app.secret_key = os.urandom(13)
    app.run()
