from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo
from extensions import db
from models import User


class RegisterForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
     render_kw={"placeholder": "Username"})
    
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)],
     render_kw={"placeholder": "Password"})
    
    confirm_password = PasswordField(validators=[InputRequired(),
     EqualTo("password", message="Passwords must match"), Length(min=4, max=20)],
     render_kw={"placeholder": "Confirm Password"})

    submit = SubmitField("Register")

    def validate_username(self, username):
        existing_user = db.session.scalar(
            db.select(User).where(User.username == username.data)
        )

        if existing_user:
            raise ValidationError(
                "That username already exists. Please use a different one."
            )


class LoginForm(FlaskForm):
    username = StringField(validators=[InputRequired(), Length(min=4, max=20)],
     render_kw={"placeholder": "Username"})
    
    password = PasswordField(validators=[InputRequired(), Length(min=4, max=20)],
     render_kw={"placeholder": "Password"})
    
    submit = SubmitField("Login")