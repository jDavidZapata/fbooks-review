
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
    
    books = db.execute('SELECT title FROM books ORDER BY random() LIMIT 9').fetchall()

    print(books)

    """Check to see if User is in session."""

    user_id = session.get('user_id')

    if (not 'user_id' in session):
        g.user = None

        return render_template("index.html", books=books, error=error)
    else:
        g.user = db.execute(    
            'SELECT * FROM users WHERE id = :id', {"id": user_id,}
        ).fetchone()

        return render_template("index.html", books=books, error=error)
        


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
            return redirect(url_for('index'))

        flash(error)

    return render_template('auth/register.html', error=error)






@app.route('/login', methods=('GET', 'POST'))
def login():
    """Log in a registered user by adding the user id to the session."""
    
    error = None 

    user_id = session.get('user_id')
    if ('user_id' in session):
        g.user = db.execute(    
            'SELECT * FROM users WHERE id = :id', {"id": user_id,}
        ).fetchone()
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
            return redirect(url_for('index'))

        flash(error)
        
    return render_template('auth/login.html', error=error)
    




@app.route('/logout')
def logout():
    """Clear the current session, including the stored user id."""
    session.clear()
    g.user = None
    return redirect(url_for('index'))



@app.route('/search', methods=['GET', 'POST'])
def search():
    error = None

    """Check to see if User is in session."""

    user_id = session.get('user_id')

    if (not 'user_id' in session):
        g.user = None

        return render_template("search.html", error=error)
    else:
        g.user = db.execute(    
            'SELECT * FROM users WHERE id = :id', {"id": user_id,}
        ).fetchone()

        return render_template("search.html", error=error)
  

@app.route('/book', methods=['GET', 'POST'])
def book():
    error = None

    """Check to see if User is in session."""

    user_id = session.get('user_id')

    if (not 'user_id' in session):
        g.user = None

        return render_template("bookpage.html", error=error)
    else:
        g.user = db.execute(    
            'SELECT * FROM users WHERE id = :id', {"id": user_id,}
        ).fetchone()

        return render_template("bookpage.html", error=error)
  
    
@app.route('/create', methods=['GET', 'POST'])
def create():
    error = None

    """Check to see if User is in session."""

    user_id = session.get('user_id')

    if (not 'user_id' in session):
        g.user = None

        return render_template("reviews/create.html", error=error)
    else:
        g.user = db.execute(    
            'SELECT * FROM users WHERE id = :id', {"id": user_id,}
        ).fetchone()

        return render_template("reviews/create.html", error=error)
  
    
 
 
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run()

