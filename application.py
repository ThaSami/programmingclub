import re
import os
from cs50 import SQL
from flask import Flask, flash, redirect, render_template, request, session, url_for, send_from_directory,jsonify
from flask_session import Session
from passlib.apps import custom_app_context as pwd_context
from tempfile import mkdtemp
from datetime import datetime
from helpers import *
from flask_jsglue import JSGlue
import requests

# configure application
app = Flask(__name__)
JSGlue(app)


# Ensure templates are auto-reloaded
app.config["TEMPLATES_AUTO_RELOAD"] = True

# Ensure responses aren't cached
@app.after_request
def after_request(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Expires"] = 0
    response.headers["Pragma"] = "no-cache"
    return response

# configure session to use filesystem (instead of signed cookies)
app.config["SESSION_FILE_DIR"] = mkdtemp()
app.config["SESSION_PERMANENT"] = False
app.config["SESSION_TYPE"] = "filesystem"
app.config['src-noconflict']="ace-builds/src-noconflict"
app.config['static2']="static/register"
app.config['static3']="static/login"
app.config['static4']="static/API"
Session(app)

# configure CS50 Library to use SQLite database
db = SQL("sqlite:///judge.db")

# Custom static data
@app.route('/ace-builds/src-noconflict/<path:filename>')
def custom_static(filename):
    return send_from_directory(app.config['src-noconflict'], filename)


# Custom static data
@app.route('/static/register/<path:filename>')
def custom_static2(filename):
    return send_from_directory(app.config['static2'], filename,as_attachment=True)
    
@app.route('/static/login/<path:filename>')
def custom_static3(filename):
    return send_from_directory(app.config['static3'], filename,as_attachment=True)    

  
@app.route('/static/API/<path:filename>')
def custom_static4(filename):
    return send_from_directory(app.config['static4'], filename,as_attachment=True)    


@app.route("/change", methods=["GET", "POST"])
@login_required
def change():
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("oldpass"):
            return apology("must provide username")

        # ensure password was submitted
        elif not request.form.get("newpass"):
            return apology("must provide password")
            
        elif not request.form.get("newpass2"):
            return apology("must provide password")  
            
        elif request.form.get("newpass") != request.form.get("newpass2"):
            return apology("Passwords don't match")
        pas=db.execute("SELECT user_password FROM user Where user_id=:id",id=session["user_id"])
        
        if not pwd_context.verify(request.form.get("oldpass"), pas[0]["user_password"]):
            return apology("Wrong pass")
            
        db.execute("UPDATE user SET user_password=:hash Where user_id=:id",id=session["user_id"],hash=pwd_context.hash(request.form.get("newpass")))       
            
        flash("password Changed Sucesfully")
        
        return redirect(url_for("index"))
    return render_template("change.html")
    
    
    
    

@app.route("/")
@login_required
def index():

    return apology("News Will be here, GO to Practice")

@app.route("/contests")
@login_required
def contests():
    
    
    return apology("TO BE ANNOUNCED") 

@app.route("/ladder")
@login_required
def ladder():
    return apology("YOU BETTER USE THE STAIRS") 

@app.route("/aboutus")
@login_required
def aboutus():
    
    return apology("A TEAM OF HIGHLY TRAINED...") 

@app.route("/practice",methods=["POST","GET"])
@login_required
def practice():
    
    if request.method == "POST":
        if not request.form.get("select"):
            flash("Choose PROBLEM!!")
            return render_template("practice.html")
        data=db.execute("SELECT * FROM problems WHERE header=:header",header=request.form.get("select"))
        return render_template("practice.html",data=data)
    return render_template("practice.html")    
@app.route("/login", methods=["GET", "POST"])
def login():
    """Log user in."""

    # forget any user_id
    session.clear()

    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("email"):
            return apology("must provide Email")

        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")

        # query database for username
        rows = db.execute("SELECT * FROM user WHERE user_email = :email", email=request.form.get("email"))

        # ensure username exists and password is correct
        if len(rows) != 1 or not pwd_context.verify(request.form.get("password"), rows[0]["user_password"]):
            return apology2("YOU SHALL NOT PASS!")

        # remember which user has logged in
        session["user_id"] = rows[0]["user_id"]
        
        flash('You were successfully logged in')
        # redirect user to home page
        return redirect(url_for("index"))
        
    # else if user reached route via GET (as by clicking a link or via redirect)
    else:
        return render_template("login.html")

@app.route("/logout")
def logout():
    """Log user out."""

    # forget any user_id
    session.clear()
    
    
    flash('You were successfully logged out')
    # redirect user to login form
    return redirect(url_for("login"))

        
        
@app.route("/register", methods=["GET", "POST"])
def register():
   
    
    # if user reached route via POST (as by submitting a form via POST)
    if request.method == "POST":

        # ensure username was submitted
        if not request.form.get("username"):
            return apology("must provide username")
        # ensure email was submitted    
        if not request.form.get("email"):
            
            return apology("must provide Email")
        # ensure univId was submitted    
        if not request.form.get("univid"):
            
            return apology("must provide University ID")    
        # ensure password was submitted
        elif not request.form.get("password"):
            return apology("must provide password")
            
        elif not request.form.get("password2"):
            return apology("must provide password")    
        
        elif request.form.get("password") != request.form.get("password2"):
            return apology("Passwords don't match")
    
        rows = db.execute("SELECT * FROM user WHERE user_name = :username OR user_email= :email OR user_univID = :univid", username=request.form.get("username"),email=request.form.get("email"),univid=request.form.get("univid"))
        if rows:
            if request.form.get("username") == rows[0]["user_name"]:
                return apology("UserName already Exists")
            elif request.form.get("email") == rows[0]["user_email"]:
                return apology("Email already Exists")    
            elif request.form.get("univid") == rows[0]["user_univID"]:
                return apology("University ID already exists")
        insertion = db.execute("INSERT INTO user (user_name,user_password,user_email,user_univID) VALUES(:username,:hash,:email,:univID)",username=request.form.get("username"),hash=pwd_context.hash(request.form.get("password")),email=request.form.get("email"),univID=request.form.get("univid"))
        
        if not insertion:
         return apology("Username/Email is already Exist")
    
        rows = db.execute("SELECT * FROM user WHERE user_name = :username", username=request.form.get("username"))
          # remember which user has logged in
        session["user_id"] = rows[0]["user_id"]

        flash('You were successfully Registerd!')
        # redirect user to home page
        return redirect(url_for("index"))
        
    else:
        return render_template("register.html")
