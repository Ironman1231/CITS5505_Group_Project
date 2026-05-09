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
from .models import CheckIn, Comment, Photo, User

# import cloudflare R2
import boto3
from dotenv import load_dotenv

from werkzeug.utils import secure_filename
import uuid

EXPLORE_CATEGORIES = {
    "food": "Food & Drink",
    "study": "Study Spot",
    "nature": "Nature",
    "nightlife": "Nightlife",
    "shopping": "Shopping",
    "other": "Other",
}
EXPLORE_SORT_OPTIONS = {
    "newest": "Newest First",
    "rating": "Highest Rated",
}
CATETORIES = ["food", "study", "nature", "nightlife", "shopping", "other"]


def escape_like_search(value):
    """Escape SQL LIKE wildcard characters before building a search pattern."""
    return value.replace("\\", "\\\\").replace("%", "\\%").replace("_", "\\_")


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

# set up cloudflare s3
s3 = boto3.client(
    's3',
    endpoint_url=f"https://{os.getenv("CLOUDFLARE_ACCOUNT_ID")}.r2.cloudflarestorage.com",
    aws_access_key_id=os.getenv('CLOUDFLARE_ACCESS_KEY_ID'),
    aws_secret_access_key=os.getenv("CLOUDFLARE_SECRET_ACCESS_KEY"),
    region_name="auto"
)

# upload image to cloudflare R2
def upload_image(file, filename):
    """Upload an image to R2 and return the public URL"""
    bucket = os.getenv("CLOUDFLARE_BUCKET_NAME")

    s3.upload_fileobj(
        file,
        bucket,
        filename,
        ExtraArgs={"ContentType": file.content_type}
    )

    # return the public URL
    public_url = os.getenv("CLOUDFLARE_PUBLIC_URL")
    return f"{public_url}/{filename}"

# test: upload a test file
try:
    s3.put_object(
        Bucket=os.getenv('CLOUDFLARE_BUCKET_NAME'),
        Key='test.txt',
        Body=b'hello world'
    )
    print("Upload successful!")
except Exception as e:
    print("Upload failed:", e)


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
    check_ins = CheckIn.query.order_by(CheckIn.created_at.desc()).all()
    markers = [
        {"lat": c.lat, "lng": c.lng, "title": c.title, "category": c.category}
        for c in check_ins if c.lat is not None and c.lng is not None
    ]
    return render_template("index.html", check_ins=check_ins, markers=markers)

@app.route("/explore")    
def explore_alias():
    return redirect(url_for("explore"))
@app.route("/explore.html")
def explore():
    """Render the explore page with database-backed filters and sorting."""
    selected_category = request.args.get("category", "").strip()
    selected_min_rating = request.args.get("min_rating", "").strip()
    selected_sort = request.args.get("sort", "newest").strip() or "newest"

    if selected_category not in EXPLORE_CATEGORIES:
        selected_category = ""
    if selected_sort not in EXPLORE_SORT_OPTIONS:
        selected_sort = "newest"

    min_rating_value = None
    if selected_min_rating:
        try:
            min_rating_value = float(selected_min_rating)
        except ValueError:
            selected_min_rating = ""

    query = CheckIn.query
    if selected_category:
        query = query.filter(CheckIn.category == selected_category)
    if min_rating_value is not None:
        query = query.filter(CheckIn.rating >= min_rating_value)

    if selected_sort == "rating":
        query = query.order_by(CheckIn.rating.desc(), CheckIn.created_at.desc())
    else:
        query = query.order_by(CheckIn.created_at.desc())

    check_ins = query.all()
    filters = {
        "category": selected_category,
        "min_rating": selected_min_rating,
        "sort": selected_sort,
    }
    return render_template(
        "explore.html",
        check_ins=check_ins,
        filters=filters,
        category_options=EXPLORE_CATEGORIES,
        sort_options=EXPLORE_SORT_OPTIONS,
    )


@app.route("/checkin-details")
def checkin_details_alias():
    return redirect(url_for("checkin_details"))
@app.route("/checkin_details.html")
def checkin_details():
    """Redirect the old prototype URL to the latest available detail page."""
    check_in = CheckIn.query.order_by(CheckIn.created_at.desc()).first()
    if not check_in:
        return redirect(url_for("explore"))
    return redirect(url_for("checkin_detail", checkin_id=check_in.id))


@app.route("/checkins/<int:checkin_id>")
def checkin_detail(checkin_id):
    """Render one selected check-in from the database."""
    check_in = db.get_or_404(CheckIn, checkin_id)
    photos = check_in.photos.order_by(Photo.display_order.asc(), Photo.id.asc()).all()
    comments = check_in.comments.order_by(Comment.created_at.desc()).all()
    comments_count = len(comments)
    favourites_count = check_in.favourites.count()
    category = check_in.category if check_in.category in EXPLORE_CATEGORIES else "other"
    detail_map = {
        "lat": check_in.lat,
        "lng": check_in.lng,
        "title": check_in.title,
        "category": EXPLORE_CATEGORIES.get(category, category.title()),
    }
    return render_template(
        "checkin_details.html",
        check_in=check_in,
        photos=photos,
        comments=comments,
        comments_count=comments_count,
        favourites_count=favourites_count,
        category_key=category,
        category_label=EXPLORE_CATEGORIES.get(category, category.title()),
        detail_map=detail_map,
    )

    
@app.route("/checkins/<int:checkin_id>/comments", methods=["POST"])
@login_required
def add_comment(checkin_id):
    """Save a logged-in user's comment for one check-in."""
    check_in = db.get_or_404(CheckIn, checkin_id)
    body = request.form.get("body", "").strip()
    if not body:
        flash("Please write a comment before posting.", "danger")
        return redirect(url_for("checkin_detail", checkin_id=check_in.id))
    if len(body) > 1000:
        flash("Comments must be 1000 characters or fewer.", "danger")
        return redirect(url_for("checkin_detail", checkin_id=check_in.id))
    comment = Comment(
        user_id=current_user.id,
        checkin_id=check_in.id,
        body=body,
    )
    db.session.add(comment)
    db.session.commit()
    flash("Comment posted successfully.", "success")
    return redirect(url_for("checkin_detail", checkin_id=check_in.id))


@app.route("/checkins/<int:checkin_id>/favourite", methods=["POST"])
@login_required
def toggle_favourite(checkin_id):
    """Toggle the current user's favourite on a check-in."""
    check_in = db.get_or_404(CheckIn, checkin_id)
    existing = models.Favourite.query.filter_by(
        user_id=current_user.id,
        checkin_id=checkin_id,
    ).first()
    if existing:
        db.session.delete(existing)
        db.session.commit()
        flash("Removed from favourites.", "info")
    else:
        db.session.add(models.Favourite(
            user_id=current_user.id,
            checkin_id=checkin_id,
        ))
        db.session.commit()
        flash("Added to favourites!", "success")
    return redirect(url_for("checkin_detail", checkin_id=checkin_id))


@app.route("/new-checkin")
def new_checkin_alias():
    return redirect(url_for("new_checkin"))

@app.route("/new-checkin.html", methods=["GET", "POST"])
@login_required
def new_checkin():
    if request.method == "POST":
        # get information from the front end by id
        title = request.form.get("title")
        if not title:
            flash("Title is required")
            print("Title is required")
            return redirect(url_for('new_checkin'))
        
        category = request.form.get("category")
        if category not in CATETORIES:
            flash("Category is wrong")
            print("Category is wrong")
            return redirect(url_for('new_checkin'))

        description = request.form.get("description")
        if not description:
            flash("Description is required")
            print("Description is required")
            return redirect(url_for('new_checkin'))
        
        try:
            rating = float(request.form.get("rating"))
            if rating < 1 or rating > 5:
                raise Exception("Bad rating")
        except:
            flash("Invalid rating")
            print("Invalid rating")
            return redirect(url_for('new_checkin'))
        
        try:
            lat = float(request.form.get("lat"))
            lng = float(request.form.get("lng"))
        except:
            flash("Invalid location")
            print("Invalid location")
            return redirect(url_for('new_checkin'))



        # for all data into a dictionary
        form_data = {
            "user_id": current_user.id,
            "title": title,
            "description": description,
            "category": category,
            "rating": rating,
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
            rating = form_data["rating"],
            lat = form_data["lat"],
            lng = form_data["lng"]
        )

        db.session.add(check_in)
        # db.session.commit()
        db.session.flush()

        # image test
        image = request.files.get("input_image")
        if image:
            # generate unqiue filename to avoid conflicts
            ext = image.filename.rsplit('.', 1)[1].lower()
            filename = f"{uuid.uuid4()}.{ext}"
            image_url = upload_image(image, filename)
            
            new_photo = Photo(
                checkin_id = check_in.id,
                url = image_url
            )
            db.session.add(new_photo)
        
        db.session.commit()
        return redirect(url_for("index"))
        

    """Render the new check-in page prototype"""
    return render_template("new-checkin.html")


@app.route("/profile")
@login_required
def profile_alias():
    return redirect(url_for("profile"))
@app.route("/profile.html")
@login_required
def profile():
    """Render the user profile page prototype"""
    user_id = current_user.id
    user = User.query.filter(User.id == user_id).first()

    if not user:
        flash("Please login first", "baduser")
        return render_template("profile.html")
    else:
        check_ins = CheckIn.query.filter(CheckIn.user_id == user.id).all()
        favourites = user.favourites.all()
        # find out the favourite checkins
        favourite_checkin_ids = [f.checkin_id for f in favourites]
        # following is the code to check which checkin ids are in the favourite_checkin_ids
        favourite_check_ins = CheckIn.query.filter(CheckIn.id.in_(favourite_checkin_ids)).all()
        sum_rating = 0
        avg_rating = 0
        if len(check_ins) != 0:
            for check_in in check_ins:
                sum_rating += check_in.rating
            avg_rating = sum_rating / len(check_ins)
        return render_template(
            "profile.html",
            user = user,
            check_ins = check_ins,
            avg_rating = round(avg_rating, 1),
            favourite_check_ins = favourite_check_ins)

@app.route("/profile.html", methods = ["POST"])
@login_required
def update_profile():
    username = request.form.get("new_username")
    bio = request.form.get("new_bio")

    return 1111


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
    if not query:
        return redirect(url_for("explore"))

    search_pattern = f"%{escape_like_search(query)}%"
    check_ins = CheckIn.query.filter(
        (CheckIn.title.ilike(search_pattern, escape="\\")) |
        (CheckIn.description.ilike(search_pattern, escape="\\"))
    ).order_by(CheckIn.created_at.desc()).all()
    return render_template(
        "explore.html",
        check_ins=check_ins,
        search_query=query,
        filters={"category": "", "min_rating": "", "sort": "newest"},
        category_options=EXPLORE_CATEGORIES,
        sort_options=EXPLORE_SORT_OPTIONS,
    )
@app.route("/navbar.html")
def navbar():
    """Render the navigation bar prototype"""
    return render_template("navbar.html")


@app.errorhandler(404)
def not_found(error):
    return render_template("404.html"), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return render_template("500.html"), 500


if __name__ == "__main__":
    app.run(debug=True)
