"""
Database models for PerthPins.

Tables :
- User
- CheckIn
- Photo
- Comment
- Favourite
"""
from datetime import datetime, timezone

# Use package imports so models share the same extension instance as the app.
from .extensions import db

class User(db.Model):
    """Registered PerthPins user"""

    id            = db.Column(db.Integer, primary_key=True)
    username      = db.Column(db.String(64),  unique=True, nullable=False)
    email         = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)  # salted hash via Werkzeug
    avatar_url    = db.Column(db.String(512))
    bio           = db.Column(db.Text)
    created_at    = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    # One user to many check-ins/comments/favourites.
    checkins  = db.relationship('CheckIn', backref='author', lazy='dynamic',
                                cascade='all, delete-orphan')
    comments  = db.relationship('Comment', backref='author', lazy='dynamic',
                                cascade='all, delete-orphan')
    favourites = db.relationship('Favourite', back_populates='user', lazy='dynamic',
                                 cascade='all, delete-orphan')

    def __repr__(self):
        return f'<User {self.username}>'


class CheckIn(db.Model):
    """Location check-in created by a user"""

    __tablename__ = 'checkin'
    id          = db.Column(db.Integer, primary_key=True)
    title       = db.Column(db.String(128), nullable=False)
    description = db.Column(db.Text)
    category    = db.Column(db.String(64))
    rating      = db.Column(db.Float)
    latitude    = db.Column(db.Float)
    longitude   = db.Column(db.Float)
    created_at  = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id     = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)

    # One check-in to many photos/comments/favourites.
    photos   = db.relationship('Photo',   backref='checkin', lazy='dynamic',
                               cascade='all, delete-orphan')
    comments = db.relationship('Comment', backref='checkin', lazy='dynamic',
                               cascade='all, delete-orphan')
    favourites = db.relationship('Favourite', back_populates='checkin', lazy='dynamic',
                                 cascade='all, delete-orphan')

    def __repr__(self):
        return f'<CheckIn {self.title}>'


class Photo(db.Model):
    """Photo attached to a check-in"""

    id            = db.Column(db.Integer, primary_key=True)
    checkin_id    = db.Column(db.Integer, db.ForeignKey('checkin.id'), nullable=False)
    url           = db.Column(db.String(512), nullable=False)
    display_order = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Photo {self.id} checkin={self.checkin_id}>'


class Comment(db.Model):
    """Comment left on a check-in"""

    id         = db.Column(db.Integer, primary_key=True)
    content    = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'),    nullable=False)
    checkin_id = db.Column(db.Integer, db.ForeignKey('checkin.id'), nullable=False)

    def __repr__(self):
        return f'<Comment {self.id} by user={self.user_id}>'


class Favourite(db.Model):
    """Saved check-in relationship between a user and a check-in.
    The table keeps the existing composite primary key, and adds `created_at`
    so future profile/saved-list pages can sort favourites by save time.
    """

    __tablename__ = 'favourite'

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), primary_key=True)
    checkin_id = db.Column(db.Integer, db.ForeignKey('checkin.id'), primary_key=True)
    created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))

    user = db.relationship('User', back_populates='favourites')
    checkin = db.relationship('CheckIn', back_populates='favourites')

    def __repr__(self):
        return f'<Favourite user={self.user_id} checkin={self.checkin_id}>'
