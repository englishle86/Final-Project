from flask import Flask, g, render_template, request, redirect, url_for, session
from flask_session import Session
import datetime
import sqlite3
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import login_required
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy import select

app = Flask(__name__)
# path to base directory
basedir = os.path.abspath(os.path.dirname(__file__))
app.config["SQLALCHEMY_DATABASE_URI"] = 'sqlite:///' + os.path.join(basedir, 'tracking.db')

# initialize the database
db = SQLAlchemy(app)
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
Session(app)

#create database model
class users(db.Model):
    #create column
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(200), nullable=False)
    labor_balance = db.Column(db.Float, nullable=False, default=0.0)
    password_hash = db.Column(db.String(200), nullable=False)

# create function to return a string when we add something
    def __repr__(self):
        return '<name %r>' % self.id

@app.route("/")
#@login_required
def index():
# --------------- using this instead of login for right now until everything else is working    
    try:
        id = session["user_id"]
        rows = db.session.execute(select(users.username, users.labor_balance).where(users.id == id)).first()
        name = rows[0]
        balance = rows[1]
        date = datetime.datetime.today().strftime('%m-%d')
        print(date)
        return render_template("index.html", name=name, date=date, balance=balance)

    except:
        return render_template("login.html")

@app.route("/login", methods=["GET", "POST"])
def login():
    session.clear()
    if request.method == "GET":
        return render_template("login.html")
    
    if request.method == 'POST':
        # check to see if login forms completed
        if not request.form.get("username"):
            return("Cannot Leave Fields Blank")
        if not request.form.get("password"):
            return("Cannot Leave Fields Blank")
        
        else:
            name = request.form.get("username")
            #query for username and password
            get_hash = db.session.execute(select(users.password_hash).where(users.username == name)).first()
            
            try: 
                check_password_hash(get_hash[0], request.form.get("password"))
            except: 
                return ("invalid username or password")
            
            id = db.session.execute(select(users.id).where(users.username == name)).first()
            session["user_id"] = id[0]
            return redirect("/")
    
    
@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "GET":
        return render_template("register.html")
    
    if request.method == "POST":
        # check that forms are completed
        if not request.form.get("username"):
            return("Cannot leave username field blank")
        if not request.form.get("password"):
            return("Cannot leave field blank")
        pword = request.form.get("password")
        user = request.form.get("username")
        # check for password confirmation match
        if pword != request.form.get("confirmation"):
            return("Password did not match")

        # create hash for password
        hash = generate_password_hash(pword)
        print(hash)
        # check to see if username already exists
        try: 
            rows = db.execute(select(users).filter_by(username=user))
            return render_template("error.html", error=rows)

        except:
            new_user = users(username=user, password_hash=hash)
            # commit to database and redirect to index
            try:
                db.session.add(new_user)
                db.session.commit()
                return redirect("/")
            except:
                return("there was an error")