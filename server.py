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

    return render_template("movie_info.html", movie=movie)


if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
