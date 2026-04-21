from flask import Flask, render_template
from extensions import db
from flask_migrate import Migrate
from config import Config
import os

app = Flask(__name__, template_folder="../frontend/template", static_folder="../frontend/static")

# set the configuration through the object Config in the config.py
app.config.from_object(Config)
# create a folder named instance
os.makedirs(app.instance_path, exist_ok=True)


# bind SQLAlchemy with app
db.init_app(app)
migrate = Migrate(app, db)

@app.route('/')
def index():
    return render_template("index.html")

@app.route("/checkin_details")
def checkin_details():
    return render_template("checkin_details.html")

@app.route("/login")
def login():
    return render_template("login.html")

@app.route("/register")
def register():
    return render_template("register.html")

if __name__ in "__main__":
    app.run(debug=True)