from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, DateField
from wtforms.validators import InputRequired, Length, ValidationError, EqualTo, Optional
from flask_login import current_user
from extensions import db
from models import User, Subject
from flask_wtf.file import FileField, FileRequired, FileAllowed


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


class SubjectCreate(FlaskForm):
    subject_name = StringField(validators=[InputRequired(), Length(min=2, max=20)],
        render_kw={"placeholder": "Subject Name"})
    submit = SubmitField("Submit")

    def validate_subject_name(self, subject_name):
        existing_subject = db.session.scalar(
            db.select(Subject).where(
                Subject.user_id == current_user.id,
                db.func.lower(Subject.name) == subject_name.data.strip().lower()
            )
        )

        if existing_subject:
            raise ValidationError("You already have a subject with that name.")


class TaskForm(FlaskForm):
    task = StringField(validators=[InputRequired(), Length(min=2, max=30)],
        render_kw={"placeholder": "Task"})
    due_date = DateField(validators=[Optional()])
    submit = SubmitField("Set Task")


class SummaryForm(FlaskForm):
    title = StringField(validators=[InputRequired(), Length(min=2, max=60)],
        render_kw={"placeholder": "Title (e.g. Chapter 3 notes)"})
    file = FileField(validators=[
        FileRequired(message="Please choose a file."),
        FileAllowed(["pdf", "txt"], "Only PDF or TXT files are allowed.")
    ])
    submit = SubmitField("Summarize")