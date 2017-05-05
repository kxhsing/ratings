"""Movie Ratings."""

from jinja2 import StrictUndefined

from flask import (Flask, render_template, redirect, request, flash,
                    session, jsonify)
from flask_debugtoolbar import DebugToolbarExtension

from model import User, Rating, Movie, connect_to_db, db


app = Flask(__name__)

# Required to use Flask sessions and the debug toolbar
app.secret_key = "ABC"

# Normally, if you use an undefined variable in Jinja2, it fails
# silently. This is horrible. Fix this so that, instead, it raises an
# error.
app.jinja_env.undefined = StrictUndefined


@app.route('/')
def index():
    """Homepage."""

    return render_template("homepage.html")


# Go to the register form page
@app.route('/register', methods=["GET"])
def register_form():
    """Registration for new user."""

    return render_template("register_form.html")


# After user registers
@app.route('/register', methods=["POST"])
def register_complete():
    """After user registers, adds to db and goes back to homepage."""
    email = request.form.get("email")
    password = request.form.get("password")

    # import pdb; pdb.set_trace()

    if not User.query.filter(User.email==email).all():
        new_user = User(email=email, password=password)

        db.session.add(new_user)
        db.session.commit()
        return redirect("/")
    else:
        flash("User email already exists.")
        return redirect("/register")


@app.route('/login', methods=["GET"])
def login_form():
    """Direct users to login page"""

    return render_template("login_form.html")


@app.route('/login', methods=["POST"])
def login_check():
    """Check if email and password match to database"""
    email = request.form.get("email")
    password = request.form.get("password")

    if not User.query.filter(User.email==email).all():
        flash("User does not exist")
        return redirect("/login")
    else:
        user = User.query.filter(User.email==email).one()
        if password==user.password:
            session['user_id'] = user.user_id 
            flash("You are logged in")
            return redirect("/users/"+str(user.user_id))
        else:
            flash("Password is incorrect, please try again")
            return redirect("/login")

    # else:
    #     if User.query.filter(User.email==email).one().password

    return redirect("/")


@app.route('/logout')
def logout():
    """Logs out user."""
    flash("You are logged out.")
    del session["user_id"]

    return redirect("/")


@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

@app.route('/users/<user_id>')
def user_info(user_id):
    """Show user info"""

    user = User.query.filter(User.user_id==user_id).one()

    user_movie_ratings = []
    for rating in user.ratings:
        each_rating = (rating.movie_id, rating.movie.title, rating.score)
        user_movie_ratings.append(each_rating)

    return render_template("user_info.html", user=user, user_movie_ratings=user_movie_ratings)


@app.route('/movies')
def movie_list():
    """Show list of movies."""

    movies = Movie.query.order_by(Movie.title).all()

    return render_template("movie_list.html", movies=movies)


@app.route('/movies/<movie_id>')
def movie_info(movie_id):
    """Show movie info."""
    movie = Movie.query.filter(Movie.movie_id==movie_id).one()
    user_id = session.get("user_id")

    # Checking if user is logged in
    if 'user_id' in session:
        try: # If user has a rating already
            user_rating = Rating.query.filter(Rating.user_id==session['user_id'],
                                Rating.movie_id==movie_id).one()
        except: # If user does not have a rating
            user_rating = None

    # user_rating = None
    # Checking to see if user is logged in
    # if 'user_id' in session:
    #     r = Rating.query.filter(Rating.user_id==session['user_id'],
    #                             Rating.movie_id==movie_id).all()
    #     # Checking if logged-in user has rated the movie
    #     if r != []:
    #         # Finding the rating object for rated movie
    #         user_rating = r[0]

       # Get average rating of movie

    rating_scores = [r.score for r in movie.ratings]
    avg_rating = float(sum(rating_scores)) / len(rating_scores)

    prediction = None

    # Prediction code: only predict if the user hasn't rated it.

    if (not user_rating) and user_id:
        user = User.query.get(user_id)
        if user:
            prediction = user.predict_rating(movie)

    # THE EYE **********************
    if prediction:
        # User hasn't scored; use our prediction if we made one
        effective_rating = prediction

    elif user_rating:
        # User has already scored for real; use that
        effective_rating = user_rating.score

    else:
        # User hasn't scored, and we couldn't get a prediction
        effective_rating = None

    # Get the eye's rating, either by predicting or using real rating

    the_eye = (User.query.filter_by(email="eye@judgment.com")
                         .one())
    eye_rating = Rating.query.filter_by(
        user_id=the_eye.user_id, movie_id=movie.movie_id).first()

    if eye_rating is None:
        eye_rating = the_eye.predict_rating(movie)

    else:
        eye_rating = eye_rating.score

    if eye_rating and effective_rating:
        difference = abs(eye_rating - effective_rating)

    else:
        # We couldn't get an eye rating, so we'll skip difference
        difference = None

        # Depending on how different we are from the Eye, choose a
    # message

    BERATEMENT_MESSAGES = [
        "I suppose you don't have such bad taste after all.",
        "I regret every decision that I've ever made that has " +
            "brought me to listen to your opinion.",
        "Words fail me, as your taste in movies has clearly " +
            "failed you.",
        "That movie is great. For a clown to watch. Idiot.",
        "Words cannot express the awfulness of your taste."
    ]

    if difference is not None:
        # import pdb; pdb.set_trace()
        beratement = BERATEMENT_MESSAGES[int(difference)]

    else:
        beratement = None

    print beratement
  
    return render_template("movie_info.html",
                            movie=movie,
                            user_rating=user_rating,
                            average=avg_rating,
                            prediction=prediction,
                            beratement=beratement)


@app.route('/add_rating', methods=["POST"])
def add_rating():
    """Adding or updating a rating for a movie"""

    user_id = session['user_id']
    rating = int(request.form.get("rating"))
    movie_id = request.form.get("movie_id")

    try: # If user already has a rating for the movie
        current_rating = Rating.query.filter(Rating.user_id==user_id, 
                            Rating.movie_id==movie_id).one()
        current_rating.score = rating
        db.session.commit()
    except: # Creating new Rating for the user and adding to db
        new_rating = Rating(movie_id=movie_id, user_id=user_id, score=rating)
        db.session.add(new_rating)
        db.session.commit()

    # r = Rating.query.filter(Rating.user_id==user_id,
    #                         Rating.movie_id==movie_id).all()
    # if r != []:
    #     # import pdb; pdb.set_trace()
    #     current_rating = r[0]
    #     current_rating.score = rating
    #     db.session.commit()
    # else: # Insert into DB
    #     new_rating = Rating(movie_id=movie_id, user_id=user_id, score=rating)
    #     db.session.add(new_rating)
    #     db.session.commit()

    return redirect("/movies/" + movie_id)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
