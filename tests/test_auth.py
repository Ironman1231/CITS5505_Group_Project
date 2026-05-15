import pytest
from werkzeug.security import generate_password_hash

from backend.app import app, db
from backend.models import User


@pytest.fixture
def client():
    app.config["TESTING"] = True
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///:memory:"
    app.config["WTF_CSRF_ENABLED"] = False
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
            yield client
            db.session.remove()
            db.drop_all()


# [Unit Test] Register new user successfully
def test_register_new_user_successfully(client):
    # POST valid registration data with unique username, email, and matching passwords
    response = client.post(
        "/register.html",
        data={
            "username": "newuser",
            "email": "newuser@example.com",
            "password": "securepassword123",
            "confirm_password": "securepassword123",
        },
        follow_redirects=True,
    )

    # Verify the response status code is 200
    assert response.status_code == 200

    # Verify the new user exists in the database with the correct username and email
    with app.app_context():
        user = User.query.filter_by(username="newuser").first()
        assert user is not None
        assert user.username == "newuser"
        assert user.email == "newuser@example.com"
