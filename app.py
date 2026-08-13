import os
from dotenv import load_dotenv
from flask import Flask
from flask import redirect, render_template, request, url_for
from extensions import db
from flask_login import LoginManager, login_required, login_user, logout_user
from forms import RegisterForm, LoginForm
from models import User, Subject, Upload, Summary, Flashcard, FlashcardReview
from werkzeug.security import generate_password_hash, check_password_hash

load_dotenv()

app = Flask(__name__)

# configuration
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


@app.route('/')
@login_required
def home():
    return render_template("home.html")


@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    # when valid form submitted
    if form.validate_on_submit():
        user = db.session.scalar(
            db.select(User).where(User.username == form.username.data)
        )

        if user:
            if check_password_hash(user.password_hash, form.password.data):
                login_user(user)
                return redirect(url_for("home"))
            else:
                # wrong pass entered
                return render_template("login.html", form=form, message="Incorrect username or password!")
        # user doesn't exist
        else:
            return render_template("login.html", form=form, message="Incorrect username or password!")
        
    return render_template("login.html", form=form)


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))



@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegisterForm()

    # when valid form submitted
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        password_hash = generate_password_hash(password)
        
        new_user = User(username=username, password_hash=password_hash)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for("login"))


    return render_template("register.html", form=form)


if __name__ == "__main__":
    app.run(debug=True)