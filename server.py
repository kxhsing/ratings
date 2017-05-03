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
            flash("You are logged in")
            return redirect("/")
        else:
            flash("Password is incorrect, please try again")
            return redirect("/login")

    # else:
    #     if User.query.filter(User.email==email).one().password

    return redirect("/")

@app.route('/users')
def user_list():
    """Show list of users."""

    users = User.query.all()
    return render_template("user_list.html", users=users)

if __name__ == "__main__":
    # We have to set debug=True here, since it has to be True at the
    # point that we invoke the DebugToolbarExtension
    app.debug = True
    app.jinja_env.auto_reload = app.debug  # make sure templates, etc. are not cached in debug mode

    connect_to_db(app)

    # Use the DebugToolbar
    DebugToolbarExtension(app)


    
    app.run(port=5000, host='0.0.0.0')
