
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
#Session(app)
app.secret_key = b'_3#y2L"F4Q8z\n\xec]/'

# Set up database
engine = create_engine(os.getenv("DATABASE_URL"))
db = scoped_session(sessionmaker(bind=engine))



@app.route("/", methods=["GET", "POST"])
def index():
    
    error = None

    book = None
    
    books = db.execute('SELECT * FROM books ORDER BY random() LIMIT 9').fetchall()

    db.close()

    print(books)

    """Check to see if User is in session."""

    user_id = session.get('user_id')

    if (not 'user_id' in session):
        g.user = None

        return render_template("index.html", books=books, error=error, book=book)
    else:
        g.user = db.execute(    
            'SELECT * FROM users WHERE id = :id', {"id": user_id,}
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

    user_id = session.get('user_id')

    if ('user_id' in session):

        g.user = db.execute(    
            'SELECT * FROM users WHERE id = :id', {"id": user_id,}
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
        

        user = db.execute("SELECT * FROM users WHERE name = :name AND email = :email", {"name": name, "email": email}).fetchone()
        

        if user is not None:
            error = 'User {0} is already registered.'.format(name)


        if error is None:
            """If the name is available, store it in the database and go to the login page"""

            db.execute("INSERT INTO users (name, password, email) VALUES (:name, :password, :email)",
                   {"name": name, "password": password, "email": email})
            db.commit()
            
            user = db.execute("SELECT * FROM users WHERE name = :name AND email = :email", {"name": name, "email": email}).fetchone()

            """Store the user id in a new session and return to the index"""
            
            session.clear()
            session['user_id'] = user['id']
            g.user = db.execute(    
            'SELECT * FROM users WHERE id = :id', {"id": user_id,}
            ).fetchone()
            db.close()

            # Change to redirect to curent page
            return redirect(url_for('index'))
        

    return render_template('auth/register.html', book=book, error=error)






@app.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered user by adding the user id to the session."""
    
    error = None 

    user_id = session.get('user_id')
    if ('user_id' in session):
        g.user = db.execute(    
            'SELECT * FROM users WHERE id = :id', {"id": user_id,}
        ).fetchone()
        db.close()

        # change to redirect to current page
        return render_template("index.html", error=error)
    
    
    if request.method == 'POST':
        name = request.form['name']
        password = request.form['password']
        
        error = None
        user = db.execute("SELECT * FROM users WHERE name = :name AND password = :password", {"name": name, "password": password}).fetchone()


        if user is None:
            error = 'Incorrect Name or Password.'
        

        if error is None:
            """Store the user id in a new session and return to the index."""
            session.clear()
            session['user_id'] = user['id']
            g.user = db.execute(    
            'SELECT * FROM users WHERE id = :id', {"id": user_id,}
            ).fetchone()
            db.close()

            return redirect(url_for('index'))

        
        
    return render_template('auth/login.html', book=book, error=error)
    




@app.route('/logout')
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    g.user = None
    return redirect(url_for('index'))



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
            'SELECT * FROM users WHERE id = :id', {"id": user_id,}
        ).fetchone()

        db.close()

      
    if request.method == 'POST':
        
        if request.form.get('b_title', None):
            b_title = request.form['b_title']
            books = db.execute("SELECT * FROM books WHERE title ILIKE ('%' || :title || '%')", {"title": b_title,}).fetchall()
            db.close()
            return render_template("search.html", books=books ,error=error, book=book)
    
        elif request.form.get('b_author', None):
            b_author = request.form['b_author']
            books = db.execute("SELECT * FROM books WHERE author ILIKE ('%' || :author || '%')", {"author": b_author,}).fetchall()
            db.close()
            return render_template("search.html", books=books ,error=error, book=book)

        elif request.form.get('b_isbn', None):
            b_isbn = request.form['b_isbn']
            books = db.execute("SELECT * FROM books WHERE isbn ILIKE ('%' || :isbn || '%')", {"isbn": b_isbn,}).fetchall()
            db.close()
            return render_template("search.html", books=books ,error=error, book=book)

        else:
            books = db.execute('SELECT * FROM books ORDER BY random() LIMIT 9').fetchall()
            db.close()
            return render_template("search.html", books=books ,error=error)
        
    books = db.execute('SELECT * FROM books ORDER BY random() LIMIT 9').fetchall()
    db.close()

    return render_template("search.html", books=books, error=error, book=book)

  
@app.route('/book/<string:b_title>' )
def book(b_title):

    error = None

    user_id = session.get('user_id')

    """Check to see if User is in session."""

    if (not 'user_id' in session):
        g.user = None

        
        book = db.execute('SELECT * FROM books WHERE title = :title', {"title": b_title,}).fetchone()
    
        return render_template("bookpage.html", book=book, error=error)

    else:
        g.user = db.execute(    
            'SELECT * FROM users WHERE id = :id', {"id": user_id,}
        ).fetchone()

        db.close()
        
        book = db.execute('SELECT * FROM books WHERE title = :title', {"title": b_title,}).fetchone() 

        session['b_title'] = b_title

        return render_template("bookpage.html", book=book, error=error)



@app.route('/create', methods=['GET', 'POST'])
def create():
    error = None

    """Check to see if User is in session."""

    user_id = session.get('user_id')

    if (not 'user_id' in session):
        g.user = None

        return render_template("bookpage.html", error=error, book=book)
  
    
    if ('b_title' in session):

        b_title = session.get('b_title')

        book = db.execute('SELECT * FROM books WHERE title = :title', {"title": b_title,}).fetchone() 

        g.user = db.execute(    
            'SELECT * FROM users WHERE id = :id', {"id": user_id,}
        ).fetchone()

        db.close()

        
        if request.method == 'POST':

            review_rating = request.form['radio']
            review_text = request.form['reviewtext']
            ruser_id = user_id
            rbook_isbn = book.isbn

            error = None

            if not review_rating:
                error = 'Rating is required.'
            elif not review_text:
                error = 'Review is required.'
            

            # check to see if user id is in the review for that book
            if error is None:


                user_review = db.execute("SELECT * FROM reviews WHERE ruser_id = :ruser_id AND rbook_isbn = :rbook_isbn", {"ruser_id": ruser_id, "rbook_isbn": rbook_isbn}).fetchone()
        

                if user_review is not None:

                    error = 'User {0} has already Reviewed this Book.'.format(name)

                    # Insert Values into Database 

                    db.execute("INSERT INTO reviews (review_rating, review_text, ruser_id, rbook_isbn) VALUES (:review_rating, :review_text, :ruser_id, :rbook_isbn)",
                        {"review_rating": review_rating, "review_text": review_text, "ruser_id": ruser_id, "rbook_isbn": rbook_isbn})
                    db.commit()
 
                    return "success Thank You for creating review"       
        
        return render_template("bookpage.html", error=error, book=book)
   
    

    

    
 
 
if __name__ == "__main__":
    app.secret_key = os.urandom(13)
    app.run()

