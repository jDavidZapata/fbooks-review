
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



@app.route('/')
def hello():
    return render_template('index.html')
 
@app.route('/home')
def home():
    
    if not session.get('logged_in'):
        return render_template('auth/login.html')
    else:
        return "Hello Boss!  <a href='/logout'>Logout</a>"


@app.route('/register' , methods=['GET','POST'])
def register():
    if request.method == 'GET':
        return render_template('auth/register.html')
    #user = (request.form['name'], request.form['password'], request.form['email'])
    name = request.form['name']
    password = request.form['password']
    email = request.form['email']

    db.execute("INSERT INTO users (name, password, email) VALUES (:name, :password, :email)",
                   {"name": name, "password": password, "email": email,})
    
    #db.session.add(user)
    db.commit()

    flash('User successfully registered')
    return redirect(url_for('login'))

''' 
@app.route('/login',methods=['GET','POST'])
def login():
    if request.method == 'GET':
        return render_template('auth/login.html')
    name = request.form['name']
    password = request.form['password']
    registered_user = User.query.filter_by(name=name,password=password).first()
    
    if registered_user is None:
        flash('Username or Password is invalid' , 'error')
        return redirect(url_for('login'))
    login_user(registered_user)
    flash('Logged in successfully')
    return redirect(request.args.get('next') or url_for('index'))
'''

''' 
@app.route('/login', methods=['POST'])
def login():
 
    POST_USERNAME = str(request.form['name'])
    POST_PASSWORD = str(request.form['password'])
 
    Session = sessionmaker(bind=engine)
    s = Session()
    query = s.query(User).filter(User.name.in_([POST_USERNAME]), User.password.in_([POST_PASSWORD]) )
    result = query.first()
    if result:
        session['logged_in'] = True
    else:
        flash('wrong password!')
    return home()

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        if request.form['name'] != 'admin' or request.form['password'] != 'admin':
            error = 'Invalid Credentials. Please try again.'
        else:
            return redirect(url_for('home'))
    return render_template('login.html', error=error)    
''' 

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'GET':
        return render_template('auth/login.html')

    name = request.form.get("name")
    password = request.form.get("password")
    
    user = db.execute("SELECT * FROM users WHERE name = :name AND password = :password", {"name": name, "password": password}).fetchone()
    if user is None:
        flash('wrong!!!')
        return render_template("auth/login.html", message="Invalid Credentials. Please try again..")
    else:
        session['logged_in'] = True
    return redirect(url_for('home'))




@app.route("/logout")
def logout():
    session['logged_in'] = False
    return home()
 
if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.run()

