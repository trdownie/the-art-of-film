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
            reviews = list(mongo.db.reviews.find())
            films = list(mongo.db.films.find())
            # d) display registration success message
            flash("Registration successful, "
                    + request.form.get("username") 
                    + ". Welcome, human.")
            # e) redirect the member to their member's area
            return redirect(url_for("members", member=session["member"], reviews=reviews, films=films))

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
                        reviews = list(mongo.db.reviews.find())
                        films = list(mongo.db.films.find())
                        # ii) send the member to their member's area
                        return redirect(url_for("members", member=session["member"], reviews=reviews, films=films))
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
        {"username": session["member"]})
    # 2) IF LOGGED IN, RENDER MEMBERS TEMPLATE
    #    & PASS IT MEMBER VARIABLE
    if session["member"]:
        reviews = list(mongo.db.reviews.find())
        films = list(mongo.db.films.find())
        return render_template("members.html", member=member, reviews=reviews, films=films)

    # 3) IF NOT LOGGED IN RETURN USER TO LOGIN PAGE
    else:
        return redirect(url_for("login"))


@app.route("/edit_member/<member_id>", methods=["GET", "POST"])
def edit_member(member_id):
    # 1) DEFINE THE MEMBER DICT. FOR USE
    member = mongo.db.users.find_one(
        {"username": session["member"]})
    # 2) ON SUBMIT, UPDATE MEMBER DETAILS
    if request.method == "POST":
        # a) use the update method
        mongo.db.users.update(
            # i) find the user document
            {"_id": ObjectId(member_id)},
            # ii) use the $set method to add/update items
            {'$set': {
                    "tagline": request.form.get("tagline"),
                    "film": request.form.get("film"),
                    "quote": request.form.get("quote"),
                    "character": request.form.get("character"),
                    "creator": request.form.get("creator"),
                }
            }
        )
        # b) display a success message
        flash("Here's looking at you, kid.")
        reviews = list(mongo.db.reviews.find())
        films = list(mongo.db.films.find())
        # c) return the user back to the updated Member's Area
        return redirect(url_for("members", member=member, reviews=reviews, films=films))

    # 2) DEFAULT VIEW ACTION: DISPLAY PRE-POPULATED EDIT MEMBER TEMPLATE
    return render_template("edit_member.html", member=member)


@app.route("/delete_member/<member_id>")
def delete_member(member_id):
    # 1) REMOVE THE MEMBER FROM THE DB COLLECTION
    mongo.db.users.remove(
        {"_id": ObjectId(member_id)})
    # 2) REMOVE THE SESSION COOKIE
    session.clear()
    # 3) RETURN A FLASH MESSAGE
    flash("Wait a minute, wait a minute. You ain't heard nothin' yet!")
    # 4) RETURN THE USER TO THE INDEX
    return redirect(url_for("index"))


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
        reviews = list(mongo.db.reviews.find())
        films = list(mongo.db.films.find())
        # d) return the user to the member's area
        return redirect(url_for("members",
                member=session["member"], reviews=reviews, films=films))
    
    # 2) DEFAULT VIEW ACTION - RENDER TEMPLATE
    return render_template("add_film.html")


@app.route("/film/<film_id>", methods=["GET", "POST"])
def film(film_id):
    # 1) LOCATE THE FILM IN THE DATABASE USING THE ID

    # 2) LOCATE ALL ASSOCIATED REVIEWS IN THE DATABASE
    # 3) UPDATE THE FILM'S AVERAGE SCORE
    scores = list(mongo.db.reviews.aggregate(
        [{"$group": {
            "_id": "$film_id",
            "ultimate_score": {"$avg": "$ultimate_score"},
            "visual_average": {"$avg": "$metrics.visual"},
            "auditory_average": {"$avg": "$metrics.auditory"},
            "dialogue_average": {"$avg": "$metrics.dialogue"},
            "emotive_average": {"$avg": "$metrics.emotive"},
            "symbolism_average": {"$avg": "$metrics.symbolism"},
            }
        }]
    ))
    ultimate_score = scores[0]["ultimate_score"]
    visual_average = scores[0]["visual_average"]
    auditory_average = scores[0]["auditory_average"]
    dialogue_average = scores[0]["dialogue_average"]
    emotive_average = scores[0]["emotive_average"]
    symbolism_average = scores[0]["symbolism_average"]

    mongo.db.films.find_one_and_update(
        {"_id": ObjectId(film_id)},
        {"$set": {
            "ultimate_score": ultimate_score,
            "visual_average": visual_average,
            "auditory_average": auditory_average,
            "dialogue_average": dialogue_average,
            "emotive_average": emotive_average,
            "symbolism_average": symbolism_average,
            }
        }
    )
    reviews = mongo.db.reviews.find({"film_id": film_id})
    film = mongo.db.films.find_one(
        {"_id": ObjectId(film_id)})
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

    # 2) DEFAULT VIEW ACTION: DISPLAY PRE-POPULATED EDIT FORM TEMPLATE
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
    reviews = list(mongo.db.reviews.find())
    films = list(mongo.db.films.find())
    return render_template("members.html", member=session["member"], reviews=reviews, films=films)


@app.route("/add_review/<film_id>", methods=["GET", "POST"])
def add_review(film_id):
    # 1) UPON SUBMIT (POST) ADD THE REVIEW & DISPLAY MESSAGE
    if request.method == "POST":
        metrics = {
            "visual": float(request.form.get("visual")),
            "auditory": float(request.form.get("auditory")),
            "dialogue": float(request.form.get("dialogue")),
            "emotive": float(request.form.get("emotive")),
            "symbolism": float(request.form.get("symbolism"))
        }
        ultimate_score = sum(metrics.values()) / len(metrics.values())
        # a) create review dict. that contains form elments
        review = {
            "film_id": film_id,
            "title": request.form.get("title"),
            "review": request.form.get("review"),
            "ultimate_score": ultimate_score,
            "metrics": metrics,
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
    # 1) CREATE A REVIEW DICT. FROM THE DB USING REVIEW ID
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    # 2) ON SUBMIT, UPDATE REVIEW DETAILS
    if request.method == "POST":
        updated_metrics = {
            "visual": float(request.form.get("visual")),
            "auditory": float(request.form.get("auditory")),
            "dialogue": float(request.form.get("dialogue")),
            "emotive": float(request.form.get("emotive")),
            "symbolism": float(request.form.get("symbolism"))
        }
        ultimate_score = sum(updated_metrics.values()) / len(updated_metrics.values())
        # a) create a new dict. that contains updated review details
        updated_review = {
            # i) film id is not a form field so we must obtain it here
            "film_id": review["film_id"],
            "title": request.form.get("title"),
            "review": request.form.get("review"),
            "ultimate_score": ultimate_score,
            "metrics": updated_metrics,
            # ii) member form field is disabled so we must set it here
            "member": session["member"]
        }
        # b) using the review's unique id, find and update this review
        mongo.db.reviews.update({"_id": ObjectId(review_id)}, updated_review)
        # c) display a success message
        flash("My mother thanks you. My father thanks you. My sister thanks you. And I thank you.")
        # d) return the user back to the updated film page
        return redirect(url_for("film", film_id=review["film_id"]))

    # 3) DEFAULT ACTION: DISPLAY PRE-POPULATED EDIT REVIEW TEMPLATE
    return render_template("edit_review.html", review=review)


@app.route("/delete_review/<review_id>")
def delete_review(review_id):
    # 1) FIND THE REVIEW BEING DELETED USING THE REVIEW ID
    review = mongo.db.reviews.find_one({"_id": ObjectId(review_id)})
    # 2) LOCATE THE CORRECT FILM USING THE FILM ID ATTACHED TO THE REVIEW
    film = mongo.db.films.find_one(
        {"_id": ObjectId(review["film_id"])})
    # 3) DEFINE THE COLLECTION OF REVIEWS ATTACHED TO THE FILM
    reviews = mongo.db.reviews.find({"film_id": review["film_id"]})
    # 4) REMOVE THIS REVIEW FROM THE DB COLLECTION
    mongo.db.reviews.remove(
        {"_id": ObjectId(review_id)})
    # 5) RETURN A FLASH MESSAGE
    flash("I love the smell of napalm in the morning.")
    # 6) RETURN THE USER TO THE FILM PAGE
    return redirect(url_for("film", film_id=film["_id"]))


@app.route("/profile/<username>", methods=["GET", "POST"])
def profile(username):
    # 1) DEFINE THE FULL USER OBJECT
    user = mongo.db.users.find_one(
        {"username": username})
    # 2) DEFINE THE NECESSARY REQUIREMENTS
    reviews = list(mongo.db.reviews.find())
    films = list(mongo.db.films.find())
    # 3) RENDER THE TEMPLATE
    return render_template("profile.html", user=user, reviews=reviews, films=films)


if __name__ == "__main__":
    app.run(host=os.environ.get("IP"),
            port=int(os.environ.get("PORT")),
            debug=True)
