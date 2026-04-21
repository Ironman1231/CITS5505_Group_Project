from extensions import db
from datetime import datetime

class User(db.Model):
    __tablename__ = "users"
    id = db.Column(db.integer, primary_key = True)
    username = db.Column(db.String(50), nullable = False)
    email = db.Column(db.String(100), unique = True, nullable = False)
    password_hash = db.Column(db.String(200), nullable = False)
    created_at = db.Column(db.DateTime, default = datetime.now)

class CheckIn(db.Model):
    __tablename__ = "check_in"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    title = db.Column(db.String(50), nullable = False)
    description = db.Column(db.Text)
    category = db.Column(db.String(50))
    rating = db.Column(db.Integer)
    lat = db.Column(db.Float, nullable = False)
    lng = db.Column(db.Float, nullable = False)
    created_at = db.Column(db.DataTime, default = datetime.now)

class Comment(db.Model):
    __tablename__ = "comments"
    id = db.Column(db.Integer, primary_key = True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable = False)
    checkin_id = db.Column(db.Integer, db.ForeignKey("check_in.id"), nullable = False)
    body = db.Column(db.Text, nullable = False)
    created_at = db.Column(db.DataTime, default = datetime.now)