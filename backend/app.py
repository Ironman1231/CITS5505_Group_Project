from flask import Flask, render_template

app = Flask(__name__, template_folder="../frontend/template", static_folder="../frontend/static")

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