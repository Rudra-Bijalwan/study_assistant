from flask import Flask
from flask import redirect, render_template, request


app = Flask(__name__)


@app.route('/')
def index():
    pass


@app.route('/login')
def login():
    pass


@app.route('/signup')
def signup():
    pass