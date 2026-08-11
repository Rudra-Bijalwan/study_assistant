import os
from dotenv import load_dotenv
from flask import Flask
from flask import redirect, render_template, request, url_for
from extensions import db
from flask_login import LoginManager
from forms import RegisterForm, LoginForm
from models import User, Subject, Upload, Summary, Flashcard, FlashcardReview

load_dotenv()

login_manager = LoginManager()
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

app = Flask(__name__)

# configuration
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager.init_app(app)


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