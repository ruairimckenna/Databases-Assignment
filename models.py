from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class Topic(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class Flashcard(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.String(255), nullable=False)

    topic_id = db.Column(db.Integer, db.ForeignKey('topic.id'), nullable=False)