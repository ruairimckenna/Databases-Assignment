from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    subtopics = db.relationship(
        "Subtopic",
        backref="topic",
        cascade="all, delete-orphan",
        lazy=True,
    )


class Subtopic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("topic.id"), nullable=False)
    flashcards = db.relationship(
        "Flashcard",
        backref="subtopic",
        cascade="all, delete-orphan",
        lazy=True,
    )


class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    plaintiff = db.Column(db.String(120), nullable=False)
    defendant = db.Column(db.String(120), nullable=True)
    facts = db.Column(db.Text, nullable=False)
    topic_id = db.Column(db.Integer, db.ForeignKey("topic.id"), nullable=False)
    subtopic_id = db.Column(db.Integer, db.ForeignKey("subtopic.id"), nullable=False)
