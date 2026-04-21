"""
Application entry point.
"""


import os
# Import the Flask framework and related functions for creating the app, handling redirects, rendering templates, and generating URLs
from flask import Flask, redirect, render_template, url_for

# Use package imports
from .config import Config
from .extensions import db, migrate

app = Flask(__name__, template_folder="../frontend/template", static_folder="../frontend/static")

app.config.from_object(Config) # Load configuration from the Config class in config.py

db.init_app(app) # Initialize the SQLAlchemy extension with the Flask app
migrate.init_app(
    app,
    db,
    directory=os.path.join(app.root_path, "migrations")
) # Use backend/migrations as the migration directory

# Import models so Flask-Migrate can detect all tables
from . import models

@app.route("/")
@app.route("/index.html")
def index():
    """Render the home page prototype"""
    return render_template("index.html")



@app.route("/explore")
def explore_alias():
    return redirect(url_for("explore"))
@app.route("/explore.html")
def explore():
    """Render the explore page prototype"""
    return render_template("explore.html")


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
@app.route("/new-checkin.html")
def new_checkin():
    """Render the new check-in page prototype"""
    return render_template("new-checkin.html")


@app.route("/profile")
def profile_alias():
    return redirect(url_for("profile"))
@app.route("/profile.html")
def profile():
    """Render the user profile page prototype"""
    return render_template("profile.html")


@app.route("/login")
def login_alias():
    return redirect(url_for("login"))
@app.route("/login.html")
def login():
    """Render the login page prototype"""
    return render_template("login.html")


@app.route("/register")
def register_alias():
    """Redirect to the registration page prototype"""
    return redirect(url_for("register"))
@app.route("/register.html")
def register():
    return render_template("register.html")

@app.route("/navbar.html")
def navbar():
    """Render the navigation bar prototype"""
    return render_template("navbar.html")


if __name__ == "__main__":
    app.run(debug=True)
