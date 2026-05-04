"""
Application entry point.
"""

import os

from flask import Flask, flash, redirect, render_template, request, url_for
from flask_login import current_user, login_required, login_user, logout_user
from flask_wtf.csrf import CSRFError
from werkzeug.security import check_password_hash, generate_password_hash

from .config import Config
from .extensions import csrf, db, login_manager, migrate
from . import models  # noqa: F401
from .models import User, CheckIn


# Configure Flask to reuse the existing prototype templates and static files
app = Flask(
    __name__,
    template_folder="../frontend/template",
    static_folder="../frontend/static",
    instance_path=os.path.join(os.path.dirname(__file__), "instance"),
)


# set the configuration through the object Config in the config.py
app.config.from_object(Config)
# create a folder named instance
os.makedirs(app.instance_path, exist_ok=True)

# bind SQLAlchemy with app
db.init_app(app)
migrate.init_app(
    app,
    db,
    directory=os.path.join(app.root_path, "migrations")
) # Use backend/migrations as the migration directory
login_manager.init_app(app)
login_manager.login_view = "login"
login_manager.login_message = "Please log in to access this page."
login_manager.login_message_category = "warning"
csrf.init_app(app)


@login_manager.user_loader
def load_user(user_id):
    """Load the current user for Flask-Login from the SQLAlchemy model."""
    try:
        return db.session.get(User, int(user_id))
    except (TypeError, ValueError):
        return None


@app.errorhandler(CSRFError)
def handle_csrf_error(error):
    """Show a friendly message when a submitted form is missing/has bad CSRF."""
    flash("Security check failed. Please refresh the page and try again.", "danger")
    return redirect(request.referrer or url_for("index"))


@app.route("/")
@app.route("/index.html")
def index():
    import json
    check_ins = CheckIn.query.order_by(CheckIn.created_at.desc()).all()
    markers = json.dumps([
        {"lat": c.lat, "lng": c.lng, "title": c.title, "category": c.category}
        for c in check_ins if c.lat and c.lng])
    return render_template("index.html", check_ins=check_ins, markers=markers)

@app.route("/explore")
def explore_alias():
    return redirect(url_for("explore"))
@app.route("/explore.html")
def explore():
    """Render the explore page prototype"""
    check_ins = CheckIn.query.order_by(CheckIn.created_at.desc()).all()
    return render_template("explore.html", check_ins=check_ins)


@app.route("/checkin-details")
def checkin_details_alias():
    return redirect(url_for("checkin_details"))
@app.route("/checkin_details.html")
def checkin_details():
    """Render the check-in details page prototype"""
    return render_template("checkin_details.html")


@app.route("/new-checkin")
def new_checkin_alias():
    return redirect(url_for("new_checkin"))

@app.route("/new-checkin.html", methods=["GET", "POST"])
@login_required
def new_checkin():
    if request.method == "POST":
        # get information from the front end by id
        title = request.form.get("title")
        category = request.form.get("category")
        description = request.form.get("description")
        lat = float(request.form.get("lat"))
        lng = float(request.form.get("lng"))

        # for all data into a dictionary
        form_data = {
            "user_id": current_user.id,
            "title": title,
            "description": description,
            "category": category,
            "lat": lat,
            "lng": lng
        }

        # get the user id who issue this post
        user = User.query.filter(
            (User.id == form_data["user_id"])
        ).first()

        check_in = CheckIn(
            user_id = user.id,
            title = form_data["title"],
            description = form_data["description"],
            category = form_data["category"],
            lat = form_data["lat"],
            lng = form_data["lng"]
        )

        db.session.add(check_in)
        db.session.commit()

        return redirect(url_for("index"))
        

    """Render the new check-in page prototype"""
    return render_template("new-checkin.html")


@app.route("/profile")
def profile_alias():
    return redirect(url_for("profile"))
@app.route("/profile.html")
def profile():
    """Render the user profile page prototype"""
    return render_template("profile.html")


# Original prototype-only login route:
# @app.route("/login")
# def login_alias():
#     return redirect(url_for("login"))
#
# @app.route("/login.html")
# def login():
#     """Render the login page prototype"""
#     return render_template("login.html")


@app.route("/login")
def login_alias():
    """Redirect to the login page"""
    return redirect(url_for("login"))


@app.route("/login.html", methods=["GET", "POST"])
def login():
    """Log in an existing user and store their identity in the session."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        identifier = request.form.get("identifier", "").strip()
        password = request.form.get("password", "")
        form_data = {"identifier": identifier}

        if not identifier or not password:
            flash("Please enter your username/email and password.", "danger")
            return render_template("login.html", form_data=form_data)

        user = User.query.filter(
            (User.username == identifier) | (User.email == identifier.lower())
        ).first()

        if not user or not check_password_hash(user.password_hash, password):
            flash("Invalid username/email or password.", "danger")
            return render_template("login.html", form_data=form_data)

        login_user(user)

        flash("Logged in successfully.", "success")
        return redirect(url_for("index"))

    return render_template("login.html", form_data={})


@app.route("/logout", methods=["POST"])
@login_required
def logout():
    """Log out the current user with Flask-Login."""
    logout_user()
    flash("You have been logged out.", "success")
    return redirect(url_for("index"))


# Original prototype-only register route:
# @app.route("/register")
# def register_alias():
#     """Redirect to the registration page prototype"""
#     return redirect(url_for("register"))
#
# @app.route("/register.html")
# def register():
#     return render_template("register.html")


@app.route("/register")
def register_alias():
    """Redirect to the registration page"""
    return redirect(url_for("register"))
@app.route("/register.html", methods=["GET", "POST"])
def register():
    """Create a new user account from the registration form."""
    if current_user.is_authenticated:
        return redirect(url_for("index"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        email = request.form.get("email", "").strip().lower()
        password = request.form.get("password", "")
        confirm_password = request.form.get("confirm_password", "")

        form_data = {"username": username, "email": email}

        if not username or not email or not password or not confirm_password:
            flash("Please complete all required fields.", "danger")
            return render_template("register.html", form_data=form_data)

        if password != confirm_password:
            flash("Passwords do not match!", "danger")
            return render_template("register.html", form_data=form_data)

        existing_user = User.query.filter(
            (User.username == username) | (User.email == email)
        ).first()

        if existing_user:
            flash("Username or email is already registered.", "danger")
            return render_template("register.html", form_data=form_data)

        user = User(
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
        )
        db.session.add(user) # Add the new user to the session
        db.session.commit() # Commit the session to save the user to the database

        flash("Account created successfully. Please log in.", "success")
        return redirect(url_for("login"))

    return render_template("register.html", form_data={})
@app.route("/search")
def search():
    query = request.args.get("q", "").strip()
    check_ins = CheckIn.query.order_by(CheckIn.created_at.desc()).all()
    return render_template("explore.html", check_ins=check_ins, search_query=query)
@app.route("/navbar.html")
def navbar():
    """Render the navigation bar prototype"""
    return render_template("navbar.html")


if __name__ == "__main__":
    app.run(debug=True)
