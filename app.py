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
        # 1) CHECK WHETHER USERNAME EXISTS IN THE DB
        # a) define existing_user variable
        # b) get the (lowercase) username from the form
        # c) search 'users' collection to find first instance of username
        # d) if username found, assign it to existing_user
        # e) else existing_user undefined
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # 2) USERNAME ALREADY EXISTS
        # a) if existing_user = Truthy (has a value)
        if existing_user:
            # i) return error message
            flash(request.form.get("username")
                 + " already exists. Nice try, replicant.")
            # ii) redirect to registration page
            return redirect(url_for("register"))

        # 3) USERNAME DOESN'T EXIST
        else:
            # a) create a dictionary containing the user info
            register = {
                "username": request.form.get("username").lower(),
                "password": generate_password_hash(request.form.get("password"))
            }
            # b) insert the dictionary into the users collection
            mongo.db.users.insert_one(register)

            # c) add the newly created user into the session cookie
            session["member"] = request.form.get("username").lower()
            # d) display registration success message
            flash("Registration successful, "
                    + request.form.get("username") 
                    + ". Welcome, human.")
            # e) redirect the member to their member's area
            return redirect(url_for("members", member=session["member"]))

    return render_template("register.html")


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        # 1) CHECK WHETHER USERNAME EXISTS (AS ABOVE)
        # (if found, existing_username is assigned user's document)
        existing_user = mongo.db.users.find_one(
            {"username": request.form.get("username").lower()})

        # 2) USERNAME EXISTS - CHECK PASSWORD
        if existing_user:
            # a) hashed passwords match (input/db)
            if check_password_hash(
                    existing_user["password"], request.form.get("password")):
                        # i) set session variable 'member' to this username
                        session["member"] = request.form.get("username").lower()
                        # ii) send the member to their member's area
                        return redirect(url_for("members", member=session["member"]))
            # b) passwords don't match
            else:
                # i) return incorrect flash message
                flash("Username and/or password incorrect."
                         + " Thought Police dispatched.")                
                # ii) reload login page
                return redirect(url_for("login"))

        # 3) USERNAME DOESN'T EXIST
        else:
            # a) return incorrect flash message
            flash("Username and/or password incorrect."
                    + " Thought Police dispatched.")
            # b) reload login page
            return redirect(url_for("login"))

    return render_template("login.html")


@app.route("/members/<member>", methods=["GET", "POST"])
def members(member):
    # 1) DEFINE THE MEMBER VARIABLE
    # a) take the session["member"] and find its instance in the db
    # b) since this will return doc, only return the ["username"] attribute
    member = mongo.db.users.find_one(
        {"username": session["member"]})["username"]
    # 2) IF LOGGED IN, RENDER MEMBERS TEMPLATE
    #    & PASS IT MEMBER VARIABLE
    if session["member"]:
        return render_template("members.html", member=member)

    # 3) IF NOT LOGGED IN RETURN USER TO LOGIN PAGE
    else:
        return redirect(url_for("login"))


@app.route("/logout")
def logout():
    # 1) DEFINE NEW VARIABLE MEMBER
    member = session["member"]
    # 2) REMOVE THE SESSION COOKIE
    session.clear()
    # 3) DISPLAY PERSONAL MESSAGE CONFIRMING LOG OUT
    flash("May the force be with you, " + member + ".")
    # 4) REDIRECT USER TO LOGIN PAGE
    return redirect(url_for("index"))


@app.route("/add_film", methods=["GET", "POST"])
def add_film():
    # 1) UPON SUBMIT (POST) ADD THE FILM & DISPLAY MESSAGE
    if request.method == "POST":
        # a) create film dict. that contains form elments
        film = {
            "title": request.form.get("title"),
            "year": request.form.get("year"),
            "director": request.form.get("director"),
            "synopsis": request.form.get("synopsis"),
            "image_url": request.form.get("image_url"),
            # i) member form field is disabled so we must set it here
            "member": session["member"]
        }
        # b) insert film dict. into mongodb films collection
        mongo.db.films.insert_one(film)
        # c) display message thanking user
        flash(
            "I have always depended on the kindness of strangers. Film added!")
        # d) return the user to the member's area
        return redirect(url_for("members", member=session["member"]))
    
    # 2) DEFAULT VIEW ACTION - RENDER TEMPLATE
    return render_template("add_film.html")


@app.route("/film/<film_id>", methods=["GET", "POST"])
def film(film_id):
    # 1) LOCATE THE FILM IN THE DATABASE USING THE ID
    film = mongo.db.films.find_one(
        {"_id": ObjectId(film_id)})
    reviews = mongo.db.reviews.find({"film_id": film_id})
    # 2) RETURN THE FILM AS AN OBJECT
    #    WHILE RENDERING THE FILM'S OWN UNIQUE PAGE
    return render_template("film.html", film=film, reviews=reviews)


@app.route("/edit_film/<film_id>", methods=["GET", "POST"])
def edit_film(film_id):
    # 1) ON SUBMIT, UPDATE FILM DETAILS
    if request.method == "POST":
        # a) create a dict. that contains the updated film details
        updated_film = {
            "title": request.form.get("title"),
            "year": request.form.get("year"),
            "director": request.form.get("director"),
            "synopsis": request.form.get("synopsis"),
            "image_url": request.form.get("image_url"),
        }
        # b) using the film's unique id, find and update this film
        mongo.db.films.update({"_id": ObjectId(film_id)}, updated_film)
        # c) display a success message (of sorts)
        flash("It's alive! It's alive!")
        # d) return the user back to the updated film page
        return redirect(url_for("film", film_id=film_id))

    # 2) DEFAULT VIEW ACTION: DISPLAY EDIT FORM TEMPLATE
    # a) create a film object that contains the film info
    film = mongo.db.films.find_one({"_id": ObjectId(film_id)})
    # b) render the page and pass the film id & film object
    return render_template("edit_film.html", film_id=film_id, film=film)


@app.route("/delete_film/<film_id>")
def delete_film(film_id):
    # 1) REMOVE THE FILM FROM THE DB COLLECTION
    mongo.db.films.remove(
        {"_id": ObjectId(film_id)})
    # 2) RETURN A FLASH MESSAGE
    flash("Hasta la vista, baby.")
    # 3) RETURN THE USER TO THE MEMBER'S AREA
    return render_template("members.html", member=session["member"])


@app.route("/add_review/<film_id>", methods=["GET", "POST"])
def add_review(film_id):
    # 1) UPON SUBMIT (POST) ADD THE REVIEW & DISPLAY MESSAGE
    if request.method == "POST":
        # a) create review dict. that contains form elments
        review = {
            "film_id": film_id,
            "title": request.form.get("title"),
            "review": request.form.get("review"),
            "metric_1": request.form.get("metric_1"),
            "metric_2": request.form.get("metric_2"),
            "metric_3": request.form.get("metric_3"),
            "metric_4": request.form.get("metric_4"),
            "metric_5": request.form.get("metric_5"),
            # i) member form field is disabled so we must set it here
            "member": session["member"]
        }
        # b) insert review dict. into mongodb review collection
        mongo.db.reviews.insert_one(review)
        # c) display message thanking user
        flash(
            "Well, nobody's perfect.")
        # d) redirect user to the film page
        return redirect(url_for("film", film_id=film_id))

    # 2) DEFAULT VIEW ACTION - RENDER TEMPLATE
    # a) define film dict. from database
    film = mongo.db.films.find_one({"_id": ObjectId(film_id)})
    # b) render template for add review
    return render_template("add_review.html", film_id=film_id, film=film)


@app.route("/edit_review/<review_id>", methods=["GET", "POST"])
def edit_review(review_id):
    film_id = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})["film_id"]
    # 1) ON SUBMIT, UPDATE FILM DETAILS
    if request.method == "POST":
        # a) create a dict. that contains the updated film details
        updated_review = {
            "film_id": film_id,
            "title": request.form.get("title"),
            "review": request.form.get("review"),
            "metric_1": request.form.get("metric_1"),
            "metric_2": request.form.get("metric_2"),
            "metric_3": request.form.get("metric_3"),
            "metric_4": request.form.get("metric_4"),
            "metric_5": request.form.get("metric_5"),
            # i) member form field is disabled so we must set it here
            "member": session["member"]
        }
        # b) using the film's unique id, find and update this film
        mongo.db.reviews.update({"_id": ObjectId(review_id)}, updated_review)
        # c) display a success message (of sorts)
        flash("My mother thanks you. My father thanks you. My sister thanks you. And I thank you.")
        # d) return the user back to the updated film page
        return redirect(url_for("film", film_id=film_id))

    # 2) DEFAULT VIEW ACTION: DISPLAY EDIT FORM TEMPLATE
    # a) create a film object that contains the film info
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    # b) render the page and pass the film id & film object
    return render_template("edit_review.html", film_id=film_id, review=review)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
