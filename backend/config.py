"""
Application configuration
"""
import os

# set the database
BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:

    # Set SECRET_KEY from environment variable or use a default for development
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Set SQLALCHEMY_DATABASE_URI from environment variable or default to a local SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        "sqlite:///" + os.path.join(BASE_DIR, "instance", "perth_explorer.db")
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
