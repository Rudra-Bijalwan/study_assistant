from flask import Flask
from flask import redirect, render_template, request
from extensions import db
from flask_login import UserMixin

app = Flask(__name__)

app.config['SECRET_KEY'] = 'very_secret@8'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

import models


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    # when form submitted
    if request.method == "POST":
        pass

    # user clicks on the login button
    else:
        return render_template("login.html")



@app.route('/register', methods=['GET', 'POST'])
def register():
    # when form submitted
    if request.method == "POST":
        pass

    # user clicks on the register button
    else:
        return render_template("register.html")


if __name__ == "__main__":
    app.run(debug=True)