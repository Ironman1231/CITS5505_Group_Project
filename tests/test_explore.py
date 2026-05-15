import pytest
from werkzeug.security import generate_password_hash

from backend.app import app, db
from backend.models import CheckIn, User


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


def create_user():
    user = User(
        username="exploretester",
        email="exploretester@example.com",
        password_hash=generate_password_hash("password123"),
    )
    db.session.add(user)
    db.session.commit()
    return user


def test_explore_filters_by_category(client):
    with app.app_context():
        user = create_user()
        nature_checkin = CheckIn(
            user_id=user.id,
            title="Kings Park Nature Walk",
            description="A quiet green spot with city views.",
            category="nature",
            rating=4.5,
            lat=-31.9613,
            lng=115.8326,
        )
        food_checkin = CheckIn(
            user_id=user.id,
            title="Campus Coffee Stop",
            description="A convenient place for coffee.",
            category="food",
            rating=4.0,
            lat=-31.9805,
            lng=115.8179,
        )
        db.session.add_all([nature_checkin, food_checkin])
        db.session.commit()

    response = client.get("/explore.html?category=nature")

    assert response.status_code == 200
    page = response.get_data(as_text=True)
    assert "Kings Park Nature Walk" in page
    assert "Campus Coffee Stop" not in page
