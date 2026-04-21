"""
Application configuration
"""
import os

basedir = os.path.abspath(os.path.dirname(__file__))


class Config:

    # Set SECRET_KEY from environment variable or use a default for development
    SECRET_KEY = os.environ.get('SECRET_KEY', 'dev-secret-key-change-in-production')
    # Set SQLALCHEMY_DATABASE_URI from environment variable or default to a local SQLite database
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL',
        'sqlite:///' + os.path.join(basedir, 'perthpins.db')
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
