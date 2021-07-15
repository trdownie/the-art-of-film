import os
from flask import (
    Flask, flash, render_template, redirect, request, session, url_for)
from flask_pymongo import PyMongo
from bson.objectid import ObjectId
from werkzeug.security import generate_password_hash, check_password_hash
if os.path.exists("env.py"):
    import env


app = Flask(__name__)

app.config["MONGO_DBNAME"] = os.environ.get("MONGO_DBNAME")
app.config["MONGO_URI"] = os.environ.get("MONGO_URI")
app.secret_key = os.environ.get("SECRET_KEY")

mongo = PyMongo(app)


@app.route("/")
@app.route("/index")
def index():
    films = mongo.db.films.find()
    return render_template("index.html", films=films)


@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        # 1) check whether username exists in db
        # a) define existing_user variable
        # b) get the (lowercase) username from the form
        # c) search 'users' collection to find first instance of username
        # d) if username found, assign it to existing_user
        # e) else existing_user undefined
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # 2) if existing_user is Truthy (has a value), display error & reload
        if existing_user:
            flash(request.form.get("username")
                 + " already exists. Nice try, replicant.")
            return redirect(url_for("register"))

        # 3) create a dictionary containing the user's (lowercase) username and password
        register = {
            "username": request.form.get("username").lower(),
            "password": generate_password_hash(request.form.get("password"))
        }
        # 4) insert the dictionary containing the user's details into the users collection
        mongo.db.users.insert_one(register)

        # 5) add the newly created user into the session cookie & display success message
        session["user"] = request.form.get("username").lower()
        flash("Registration successful "
                + request.form.get("username") 
                + ". Welcome, human.")

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # 1) check whether username exists in db (as above)
        # (if found, existing_username is assigned user's document)
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # 2) if existing_user exists, check the password
        if existing_user:
            # a) check if hashed passwords match (input/db)
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                # i) passwords match, set session 'user'
                session["user"] = request.form.get("username").lower()
                # ii) return flash message welcoming user
                flash("Welcome, " + request.form.get("username"))
            # b) passwords don't match
            else:
                # i) return incorrect flash message
                flash("Username and/or password incorrect."
                         + " Thought Police dispatched.")                
                # ii) reload login page
                return redirect(url_for("login"))

        # 3) if username entered does not exist
        else:
            # a) return incorrect flash message
            flash("Username and/or password incorrect."
                    + " Thought Police dispatched.")
            # ii) reload login page
            return redirect(url_for("login"))

    return render_template("login.html")


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
