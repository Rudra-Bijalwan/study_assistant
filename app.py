from flask import Flask
from flask import redirect, render_template, request


app = Flask(__name__)


@app.route('/')
def index():
    return render_template("index.html")


@app.route('/login')
def login():
    pass


@app.route('/register')
def register():
    pass