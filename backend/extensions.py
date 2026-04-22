"""
Flask extensions
Initialised here without an app instance to avoid circular imports.
Bound to the app in app.py via db.init_app(app).
"""
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db = SQLAlchemy()
migrate = Migrate()
