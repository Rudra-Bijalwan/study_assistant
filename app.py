import os
from dotenv import load_dotenv
from flask import Flask
from flask import redirect, render_template, request, url_for, abort
from extensions import db
from flask_login import LoginManager, login_required, login_user, logout_user, current_user
from forms import RegisterForm, LoginForm, SubjectCreate, TaskForm, SummaryForm
from models import User, Subject, Summary, Task
from werkzeug.security import generate_password_hash, check_password_hash
from helpers import extract_text, summarize, SummaryError, get_user_subject
from datetime import date

load_dotenv()

app = Flask(__name__)

# configuration
app.config['SECRET_KEY'] = os.getenv("SECRET_KEY")
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["MAX_CONTENT_LENGTH"] = 5 * 1024 * 1024   # 5 MB

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
    today = date.today()

    # tasks not yet done, across all of this user's subjects
    pending = db.session.scalar(
        db.select(db.func.count(Task.id))
        .join(Subject, Task.subject_id == Subject.id)
        .where(Subject.user_id == current_user.id, Task.is_done.is_(False))
    )

    # not done AND due before today (tasks without a due date are never overdue)
    overdue = db.session.scalar(
        db.select(db.func.count(Task.id))
        .join(Subject, Task.subject_id == Subject.id)
        .where(
            Subject.user_id == current_user.id,
            Task.is_done.is_(False),
            Task.due_date < today
        )
    )

    summary_count = db.session.scalar(
        db.select(db.func.count(Summary.id))
        .join(Subject, Summary.subject_id == Subject.id)
        .where(Subject.user_id == current_user.id)
    )

    return render_template("home.html", pending=pending, overdue=overdue,
                           summary_count=summary_count)


@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))

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
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
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


@app.route('/subjects')
@login_required
def subjects():
    # get the subejcts to display for selection
    subjects = db.session.execute(
        db.select(Subject.name, Subject.id).where(
            Subject.user_id == current_user.id,
        )
    ).all()

    return render_template("subjects.html", subjects=subjects)


@app.route('/newsubject', methods=['GET', 'POST'])
@login_required
def newsubject():
    form = SubjectCreate()

    # when valid form submitted
    if form.validate_on_submit():
        subject_name = form.subject_name.data
        user_id = current_user.id
        new_subject = Subject(name=subject_name, user_id=user_id)
        db.session.add(new_subject)
        db.session.commit()

        return redirect(url_for("subject", subject_id=new_subject.id))
    
    return render_template("newsubject.html", form=form)


@app.route("/subjects/<int:subject_id>")
@login_required
def subject(subject_id):
    # get the subject's data to pass to html
    subject = get_user_subject(subject_id)

    return render_template("subject.html", subject=subject)


@app.route("/subjects/<int:subject_id>/delete", methods=["POST"])
@login_required
def deletesubject(subject_id):
    # 404 unless this subject belongs to the logged-in user
    subject = get_user_subject(subject_id)

    # delete the subject's data first, then the subject itself
    db.session.execute(db.delete(Task).where(Task.subject_id == subject.id))
    db.session.execute(db.delete(Summary).where(Summary.subject_id == subject.id))
    db.session.delete(subject)
    db.session.commit()

    return redirect(url_for("subjects"))


@app.route("/subjects/<int:subject_id>/todolist")
@login_required
def todolist(subject_id):
    return render_template("todolist.html", subject_id=subject_id)


@app.route("/subjects/<int:subject_id>/todolist/settasks", methods=['GET', 'POST'])
@login_required
def settasks(subject_id):
    # make sure this subject belongs to the logged-in user
    subject = get_user_subject(subject_id)

    form = TaskForm()
    if form.validate_on_submit():
        task = form.task.data.strip()
        due_date = form.due_date.data
        user_id = current_user.id
        new_task = Task(task=task, due_date=due_date, subject_id=subject.id)
        db.session.add(new_task)
        db.session.commit()

        return redirect(url_for("viewtasks", subject_id=subject.id))

    return render_template("settasks.html", form=form, subject_id=subject.id)


@app.route("/subjects/<int:subject_id>/todolist/viewtasks")
@login_required
def viewtasks(subject_id):
    subject = get_user_subject(subject_id)
    # get the tasks to display for selection
    tasks = db.session.scalars(
        db.select(Task)
        .where(Task.subject_id == subject.id)
        .order_by(Task.is_done, Task.due_date.is_(None), Task.due_date, Task.id)
    ).all()
    if tasks is None:
        abort(404)

    return render_template("viewtasks.html", tasks=tasks, subject=subject, today=date.today())


@app.route("/subjects/<int:subject_id>/todolist/tasks/<int:task_id>/delete", methods=["POST"])
@login_required
def deletetask(subject_id, task_id):
    task = db.first_or_404(
        db.select(Task).join(Subject).where(
            Task.id == task_id,
            Task.subject_id == subject_id,
            Subject.user_id == current_user.id
        ))
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for("viewtasks", subject_id=subject_id))


@app.route("/subjects/<int:subject_id>/todolist/tasks/<int:task_id>/toggle", methods=["POST"])
@login_required
def toggletask(subject_id, task_id):
    # only finds the task if it belongs to a subject owned by this user
    task = db.first_or_404(
        db.select(Task).join(Subject).where(
            Task.id == task_id,
            Task.subject_id == subject_id,
            Subject.user_id == current_user.id
        ))

    task.is_done = not task.is_done
    db.session.commit()

    return redirect(url_for("viewtasks", subject_id=subject_id))


@app.route("/subjects/<int:subject_id>/summarizetext", methods=['GET', 'POST'])
@login_required
def summarizetext(subject_id):
    subject = get_user_subject(subject_id)

    form = SummaryForm()
    error = None

    if form.validate_on_submit():
        try:
            text = extract_text(form.file.data)
            content = summarize(text)
        except SummaryError as e:
            error = str(e)
        else:
            new_summary = Summary(
                subject_id=subject.id,
                title=form.title.data.strip(),
                source_text=text,
                content=content
            )
            db.session.add(new_summary)
            db.session.commit()

            return redirect(url_for("viewsummary", subject_id=subject.id, summary_id=new_summary.id))

    # saved summaries for this subject, newest first
    summaries = db.session.scalars(
        db.select(Summary)
        .where(Summary.subject_id == subject.id)
        .order_by(Summary.created_at.desc(), Summary.id.desc())
    ).all()

    return render_template("summarizetext.html", form=form, subject=subject,
                           summaries=summaries, error=error)


@app.route("/subjects/<int:subject_id>/summaries/<int:summary_id>")
@login_required
def viewsummary(subject_id, summary_id):
    summary = db.first_or_404(
        db.select(Summary).join(Subject).where(
            Summary.id == summary_id,
            Summary.subject_id == subject_id,
            Subject.user_id == current_user.id
        ))

    return render_template("viewsummary.html", summary=summary, subject_id=subject_id)


@app.route("/subjects/<int:subject_id>/summaries/<int:summary_id>/delete", methods=["POST"])
@login_required
def deletesummary(subject_id, summary_id):
    summary = db.first_or_404(
        db.select(Summary).join(Subject).where(
            Summary.id == summary_id,
            Summary.subject_id == subject_id,
            Subject.user_id == current_user.id
        ))
    db.session.delete(summary)
    db.session.commit()

    return redirect(url_for("summarizetext", subject_id=subject_id))


@app.errorhandler(413)
def file_too_large(e):
    return "That file is too large. The maximum size is 5 MB.", 413


if __name__ == "__main__":
    app.run(debug=True)