from extensions import db

class User(db.Model):
    __tablename__ = "users"

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.Text, nullable=False)
    password_hash = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    __table_args__ = (
        db.Index("username_unique", "username", unique=True),
    )


class Subject(db.Model):
    __tablename__ = "subjects"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )
    name = db.Column(db.Text, nullable=False)
    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    __table_args__ = (
        db.UniqueConstraint("user_id", "name"),
    )


class Upload(db.Model):
    __tablename__ = "uploads"

    id = db.Column(db.Integer, primary_key=True)

    subject_id = db.Column(
        db.Integer,
        db.ForeignKey("subjects.id"),
        nullable=False
    )

    title = db.Column(db.Text, nullable=False)

    file_path = db.Column(
        db.Text,
        unique=True,
        nullable=False
    )

    file_type = db.Column(db.Text, nullable=False)

    uploaded_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )

    __table_args__ = (
        db.UniqueConstraint("subject_id", "title"),
    )


class Summary(db.Model):
    __tablename__ = "summaries"

    id = db.Column(db.Integer, primary_key=True)

    upload_id = db.Column(
        db.Integer,
        db.ForeignKey("uploads.id"),
        nullable=False
    )

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )


class Flashcard(db.Model):
    __tablename__ = "flashcards"

    id = db.Column(db.Integer, primary_key=True)

    upload_id = db.Column(
        db.Integer,
        db.ForeignKey("uploads.id"),
        nullable=False
    )

    content = db.Column(db.Text, nullable=False)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )


class FlashcardReview(db.Model):
    __tablename__ = "flashcard_review"

    id = db.Column(db.Integer, primary_key=True)

    flashcard_id = db.Column(
        db.Integer,
        db.ForeignKey("flashcards.id"),
        nullable=False
    )

    reviewed_at = db.Column(
        db.DateTime,
        server_default=db.func.current_timestamp()
    )