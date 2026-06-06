import os
import random
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Topic, Flashcard
from forms import TopicForm, FlashcardForm

app = Flask(__name__, instance_relative_config=True)

# Instance folder
os.makedirs(app.instance_path, exist_ok=True)

# SQLite path
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(app.instance_path, "app.db")
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = "dev"

db.init_app(app)

# PRESET_TOPICS
PRESET_TOPICS = [
    "Contract Law",
    "Constitutional Law",
    "Company Law",
    "Criminal Law",
    "EU Law",
    "Equity and Trusts",
    "Real Property",
    "The Law of Torts",
]


def init_db():
    db.create_all()
    for topic_name in PRESET_TOPICS:
        if not Topic.query.filter_by(name=topic_name).first():
            db.session.add(Topic(name=topic_name))
    db.session.commit()


@app.route("/")
def home():
    return render_template("index.html")

@app.route("/about")
def about():
    return render_template("about.html")

@app.route("/flashcards", methods=["GET", "POST"])
def flashcards():
    topics = Topic.query.order_by(Topic.name).all()
    topic_form = TopicForm()
    flashcard_form = FlashcardForm()
    flashcard_form.topic_id.choices = [(topic.id, topic.name) for topic in topics]

    if topic_form.validate_on_submit() and topic_form.submit.data:
        topic_name = topic_form.name.data.strip()
        if topic_name:
            if not Topic.query.filter_by(name=topic_name).first():
                db.session.add(Topic(name=topic_name))
                db.session.commit()
                flash(f"Topic '{topic_name}' created.", "success")
            else:
                flash("That topic already exists.", "warning")
        else:
            flash("Please enter a topic name.", "warning")
        return redirect(url_for("flashcards"))

    if flashcard_form.validate_on_submit() and flashcard_form.submit.data:
        question = flashcard_form.question.data.strip()
        answer = flashcard_form.answer.data.strip()
        topic_id = flashcard_form.topic_id.data
        topic = Topic.query.get(topic_id)

        if topic:
            db.session.add(Flashcard(question=question, answer=answer, topic_id=topic_id))
            db.session.commit()
            flash("Flashcard added successfully.", "success")
        else:
            flash("Please select a valid topic.", "warning")
        return redirect(url_for("flashcards"))

    return render_template(
        "flashcards.html",
        topics=topics,
        topic_form=topic_form,
        flashcard_form=flashcard_form,
    )

@app.route("/study")
def study():
    topics = Topic.query.order_by(Topic.name).all()
    topic_id = request.args.get("topic", type=int)
    selected_topic = None

    if topic_id:
        selected_topic = Topic.query.get(topic_id)
    elif topics:
        selected_topic = topics[0]

    return render_template(
        "study.html",
        topics=topics,
        selected_topic=selected_topic,
    )

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    topics = Topic.query.order_by(Topic.name).all()
    selected_topic_id = request.args.get("topic", type=int)
    selected_topic = Topic.query.get(selected_topic_id) if selected_topic_id else None
    flashcard = None
    result = None
    user_answer = ""

    if request.method == "POST":
        card_id = request.form.get("card_id", type=int)
        user_answer = request.form.get("answer", "").strip()
        flashcard = Flashcard.query.get(card_id)
        selected_topic = Topic.query.get(request.form.get("topic_id", type=int))

        if flashcard:
            normalized_answer = flashcard.answer.strip().lower()
            normalized_guess = user_answer.strip().lower()
            if normalized_answer == normalized_guess:
                result = "correct"
            else:
                result = "incorrect"
        else:
            flash("The selected flashcard could not be found.", "warning")
    else:
        if selected_topic and selected_topic.flashcards:
            flashcard = random.choice(selected_topic.flashcards)

    return render_template(
        "quiz.html",
        topics=topics,
        selected_topic=selected_topic,
        flashcard=flashcard,
        result=result,
        user_answer=user_answer,
    )

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)