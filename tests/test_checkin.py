import pytest
from werkzeug.security import generate_password_hash

from backend.app import app, db
from backend.models import CheckIn, User
import io
from unittest.mock import patch

@pytest.fixture
def client():
    # set up a test flask client with an in-memory SQLite database
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///memory:"
    app.config["WTF_CSRF_ENABLED"] = False # disable CSRF for testing
    
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()

@pytest.fixture
def logged_in_client(client):
    # create a test user and log them in
    with app.app_context():
        user = User(
            username = "testuser",
            email = "test@example.com",
            password_hash = generate_password_hash("password123")
        )
        db.session.add(user)
        db.session.commit()
    
    # log in the test user
    client.post(
        "/login.html",
        data = {"identifier": "testuser", "password": "password123"},
        follow_redirects=True
    )
    return client

# Unit Test: Create checkin with invalid rating fails
def test_create_checkin_invalid_rating(logged_in_client):
    # submit a checkin with a rating outside 1-5 should
    # redirect back and not save anything to the database
    response = logged_in_client.post(
        "/new-checkin.html",
        data = {
            "title": "Test Place",
            "category": "nature",
            "description": "A lovely spot",
            "ratinig": "10",
            "lat": "0",
            "lng": "0",
            "input_iamge": (io.BytesIO(b"fake image content"), "test.jpg")
        },
        content_type = "multipart/form-data",
        follow_redirects=True
    )

    # should return 200 (redirected back to the form)
    assert response.status_code == 200

    # verify the checkin was NOT saved to the database
    with app.app_context():
        checkin = CheckIn.query.filter_by(title="Test Place").first()
        assert checkin is None