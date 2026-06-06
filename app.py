import os
from pydoc_data.topics import topics
import random
from flask import Flask, render_template, request, redirect, url_for, flash
from models import db, Topic, Subtopic, Flashcard
from forms import TopicForm, FlashcardForm

app = Flask(__name__, instance_relative_config=True)

# Instance folder
os.makedirs(app.instance_path, exist_ok=True)

# SQLite path
app.config["SQLALCHEMY_DATABASE_URI"] = (
    "sqlite:///" + os.path.join(app.instance_path, "app.db")
)

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev")

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

    topic_id = request.args.get("topic", type=int)
    selected_topic = Topic.query.get(topic_id) if topic_id else None

    if not selected_topic and topics:
        selected_topic = topics[0]

    subtopics_for_topic = Subtopic.query.order_by(Subtopic.name).all()
    
    flashcard_form.subtopic_id.choices = [(-1, "Choose subtopic")] + [
        (subtopic.id, subtopic.name) for subtopic in subtopics_for_topic
    ]

    subtopics_by_topic = {
        str(topic.id): [
            {"id": subtopic.id, "name": subtopic.name}
            for subtopic in Subtopic.query.filter_by(topic_id=topic.id).order_by(Subtopic.name).all()
        ]
        for topic in topics
    }

    all_flashcards = Flashcard.query.order_by(Flashcard.id.desc()).all()

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
        topic_id = flashcard_form.topic_id.data
        selected_topic = Topic.query.get(topic_id)
        if not selected_topic:
            flash("Select a valid topic.", "warning")
            return redirect(url_for("flashcards", topic=topic_id))

        new_subtopic_name = flashcard_form.new_subtopic.data.strip()
        subtopic = None

        if new_subtopic_name:
            subtopic = Subtopic.query.filter_by(
                name=new_subtopic_name,
                topic_id=selected_topic.id,
            ).first()
            if not subtopic:
                subtopic = Subtopic(name=new_subtopic_name, topic_id=selected_topic.id)
                db.session.add(subtopic)
                db.session.commit()
        elif flashcard_form.subtopic_id.data and flashcard_form.subtopic_id.data != -1:
            subtopic = Subtopic.query.get(flashcard_form.subtopic_id.data)

        if not subtopic:
            flash("Choose or add a subtopic before saving a flashcard.", "warning")
            return redirect(url_for("flashcards", topic=selected_topic.id) if selected_topic else url_for("flashcards"))

        plaintiff = flashcard_form.plaintiff.data.strip()
        defendant = flashcard_form.defendant.data.strip() or None
        facts = flashcard_form.facts.data.strip()

        db.session.add(
            Flashcard(
                plaintiff=plaintiff,
                defendant=defendant,
                facts=facts,
                topic_id=selected_topic.id,
                subtopic_id=subtopic.id,
            )
        )
        db.session.commit()
        flash("Flashcard saved.", "success")
        return redirect(url_for("flashcards", topic=selected_topic.id) if selected_topic else url_for("flashcards"))

    return render_template(
        "flashcards.html",
        topics=topics,
        topic_form=topic_form,
        flashcard_form=flashcard_form,
        selected_topic=selected_topic,
        flashcards=all_flashcards,
        subtopics_by_topic=subtopics_by_topic,
        selected_topic_id=selected_topic.id if selected_topic else None,
    )

@app.route("/flashcards/add-subtopic", methods=["POST"])
def add_subtopic():
    topic_id = request.form.get("topic_id", type=int)
    subtopic_name = request.form.get("subtopic_name", "").strip()
    
    if not topic_id or not subtopic_name:
        flash("Topic and subtopic name are required.", "warning")
        return redirect(request.referrer or url_for("flashcards"))
    
    selected_topic = Topic.query.get(topic_id)
    if not selected_topic:
        flash("Invalid topic.", "warning")
        return redirect(url_for("flashcards"))
    
    existing = Subtopic.query.filter_by(name=subtopic_name, topic_id=topic_id).first()
    if existing:
        flash(f"Subtopic '{subtopic_name}' already exists for {selected_topic.name}.", "warning")
        return redirect(url_for("flashcards", topic=topic_id))
    
    new_subtopic = Subtopic(name=subtopic_name, topic_id=topic_id)
    db.session.add(new_subtopic)
    db.session.commit()
    flash(f"Subtopic '{subtopic_name}' created.", "success")
    return redirect(url_for("flashcards", topic=topic_id))

@app.route("/flashcards/delete-subtopic/<int:subtopic_id>", methods=["POST"])
def delete_subtopic(subtopic_id):
    subtopic = Subtopic.query.get(subtopic_id)
    if not subtopic:
        flash("Subtopic not found.", "warning")
        return redirect(request.referrer or url_for("flashcards"))
    
    topic_id = subtopic.topic_id
    card_count = Flashcard.query.filter_by(subtopic_id=subtopic_id).count()
    
    if card_count > 0:
        flash(f"Cannot delete subtopic with {card_count} flashcard(s). Delete the flashcards first.", "warning")
        return redirect(url_for("flashcards", topic=topic_id))
    
    db.session.delete(subtopic)
    db.session.commit()
    flash(f"Subtopic deleted.", "success")
    return redirect(url_for("flashcards", topic=topic_id))

@app.route("/flashcards/edit/<int:card_id>", methods=["GET", "POST"])
def edit_flashcard(card_id):
    card = Flashcard.query.get(card_id)
    if not card:
        flash("Flashcard not found.", "warning")
        return redirect(url_for("flashcards"))

    topics = Topic.query.order_by(Topic.name).all()
    flashcard_form = FlashcardForm()
    flashcard_form.topic_id.choices = [(topic.id, topic.name) for topic in topics]

    topic_id = card.topic_id
    selected_topic = Topic.query.get(topic_id)
    subtopics_for_topic = Subtopic.query.filter_by(topic_id=topic_id).order_by(Subtopic.name).all() if selected_topic else []
    flashcard_form.subtopic_id.choices = [(-1, "Choose subtopic")] + [
        (subtopic.id, subtopic.name) for subtopic in subtopics_for_topic
    ]

    if flashcard_form.validate_on_submit():
        new_topic_id = flashcard_form.topic_id.data
        new_topic = Topic.query.get(new_topic_id)
        if not new_topic:
            flash("Select a valid topic.", "warning")
            return redirect(url_for("flashcards"))

        new_subtopic_name = flashcard_form.new_subtopic.data.strip()
        subtopic = None

        if new_subtopic_name:
            subtopic = Subtopic.query.filter_by(
                name=new_subtopic_name,
                topic_id=new_topic.id,
            ).first()
            if not subtopic:
                subtopic = Subtopic(name=new_subtopic_name, topic_id=new_topic.id)
                db.session.add(subtopic)
                db.session.commit()
        elif flashcard_form.subtopic_id.data and flashcard_form.subtopic_id.data != -1:
            subtopic = Subtopic.query.get(flashcard_form.subtopic_id.data)

        if not subtopic:
            flash("Choose or add a subtopic before saving a flashcard.", "warning")
            return redirect(url_for("flashcards", topic=new_topic.id))

        card.plaintiff = flashcard_form.plaintiff.data.strip()
        card.defendant = flashcard_form.defendant.data.strip() or None
        card.facts = flashcard_form.facts.data.strip()
        card.topic_id = new_topic.id
        card.subtopic_id = subtopic.id
        db.session.commit()
        flash("Flashcard updated.", "success")
        return redirect(url_for("flashcards", topic=new_topic.id))

    if request.method == "GET":
        flashcard_form.topic_id.data = card.topic_id
        flashcard_form.subtopic_id.data = card.subtopic_id
        flashcard_form.plaintiff.data = card.plaintiff
        flashcard_form.defendant.data = card.defendant
        flashcard_form.facts.data = card.facts

    return render_template(
        "edit_flashcard.html",
        flashcard_form=flashcard_form,
        card=card,
        topics=topics,
    )

@app.route("/flashcards/delete/<int:card_id>", methods=["POST"])
def delete_flashcard(card_id):
    card = Flashcard.query.get(card_id)
    topic_id = None
    if card:
        topic_id = card.topic_id
        db.session.delete(card)
        db.session.commit()
        flash("Flashcard deleted.", "success")
    else:
        flash("Flashcard not found.", "warning")
    return redirect(url_for("flashcards", topic=topic_id) if topic_id else url_for("flashcards"))

@app.route("/study")
def study():
    topics = Topic.query.order_by(Topic.name).all()
    topic_id = request.args.get("topic", type=int)
    selected_topic = None

    if topic_id:
        selected_topic = Topic.query.get(topic_id)
    elif topics:
        selected_topic = topics[0]

    cards = []
    study_subtopics = []
    if selected_topic:
        cards = Flashcard.query.filter_by(topic_id=selected_topic.id).order_by(Flashcard.id).all()
        study_subtopics = sorted({card.subtopic.name for card in cards if card.subtopic})

    return render_template(
        "study.html",
        topics=topics,
        selected_topic=selected_topic,
        cards=cards,
        study_subtopics=study_subtopics,
    )

def string_distance(a, b):
    if not a:
        return len(b)
    if not b:
        return len(a)
    if abs(len(a) - len(b)) > 2:
        return abs(len(a) - len(b))

    dp = [[0] * (len(b) + 1) for _ in range(len(a) + 1)]
    for i in range(len(a) + 1):
        dp[i][0] = i
    for j in range(len(b) + 1):
        dp[0][j] = j
    for i in range(1, len(a) + 1):
        for j in range(1, len(b) + 1):
            cost = 0 if a[i - 1] == b[j - 1] else 1
            dp[i][j] = min(
                dp[i - 1][j] + 1,
                dp[i][j - 1] + 1,
                dp[i - 1][j - 1] + cost,
            )
    return dp[-1][-1]

@app.route("/quiz", methods=["GET", "POST"])
def quiz():
    topics = Topic.query.order_by(Topic.name).all()
    subtopics_by_topic = {
        topic.id: [
            {"id": subtopic.id, "name": subtopic.name}
            for subtopic in Subtopic.query.filter_by(topic_id=topic.id).order_by(Subtopic.name).all()
        ]
        for topic in topics
    }
    selected_topic_id = request.values.get("topic", type=int)
    selected_subtopic_id = request.values.get("subtopic", type=int)
    selected_topic = Topic.query.get(selected_topic_id) if selected_topic_id else None
    selected_subtopic = Subtopic.query.get(selected_subtopic_id) if selected_subtopic_id else None
    flashcard = None
    result = None
    user_answer = ""
    correct_answer = None
    is_finished = False
    score = request.values.get("score", type=int, default=0)
    current_index = request.values.get("current", type=int, default=0)
    card_ids = request.values.get("card_ids", "")
    total = 0
    question_label = "plaintiff/principle/defendant"

    if request.method == "POST":
        action = request.form.get("action")
        selected_topic = Topic.query.get(request.form.get("topic_id", type=int))
        selected_subtopic = Subtopic.query.get(request.form.get("subtopic_id", type=int))
        user_answer = request.form.get("answer", "").strip()
        card_ids = request.form.get("card_ids", "")
        current_index = request.form.get("current", type=int, default=0)
        score = request.form.get("score", type=int, default=0)
        card_ids_list = [int(cid) for cid in card_ids.split(",") if cid]

        if action == "start":
            score = 0
            current_index = 0
            query = Flashcard.query.filter_by(topic_id=selected_topic.id) if selected_topic else Flashcard.query
            if selected_topic and selected_subtopic:
                query = query.filter_by(subtopic_id=selected_subtopic.id)
            cards = query.order_by(Flashcard.id).all() if selected_topic else []
            card_ids_list = [card.id for card in cards]
            card_ids = ",".join(str(card) for card in card_ids_list)
            total = len(card_ids_list)
            flashcard = Flashcard.query.get(card_ids_list[0]) if card_ids_list else None

        elif action == "answer":
            total = len(card_ids_list)
            if card_ids_list and current_index < total:
                card = Flashcard.query.get(card_ids_list[current_index])
                if card:
                    normalized_guess = user_answer.lower()
                    answers = [card.plaintiff or "", card.defendant or ""]
                    is_match = False
                    for ans in answers:
                        normalized_answer = ans.lower()
                        if normalized_guess == normalized_answer or string_distance(normalized_guess, normalized_answer) <= 2:
                            is_match = True
                            correct_answer = ans
                            break
                    if is_match:
                        score += 1
                        result = "correct"
                    else:
                        result = "incorrect"
                        correct_answer = answers[0] if answers[0] else (answers[1] if answers[1] else "N/A")
                    flashcard = card
            
            # Only move to next card if there is one
            if current_index + 1 < total:
                current_index += 1
                flashcard = Flashcard.query.get(card_ids_list[current_index])
                result = None

        elif action == "finish":
            total = len(card_ids_list)
            is_finished = True
            flashcard = None

        if total == 0 and action != "finish":
            flashcard = None

    else:
        if selected_topic:
            query = Flashcard.query.filter_by(topic_id=selected_topic.id)
            if selected_subtopic:
                query = query.filter_by(subtopic_id=selected_subtopic.id)
            cards = query.order_by(Flashcard.id).all()
            total = len(cards)
        else:
            total = 0

    subtopics = []
    if selected_topic:
        subtopics = Subtopic.query.filter_by(topic_id=selected_topic.id).order_by(Subtopic.name).all()

    return render_template(
        "quiz.html",
        topics=topics,
        selected_topic=selected_topic,
        selected_subtopic=selected_subtopic,
        subtopics=subtopics,
        subtopics_by_topic=subtopics_by_topic,
        flashcard=flashcard,
        result=result,
        user_answer=user_answer,
        correct_answer=correct_answer,
        score=score,
        total=total,
        current=current_index,
        card_ids=card_ids,
        question_label=question_label,
        is_finished=is_finished,
    )

if __name__ == "__main__":
    with app.app_context():
        init_db()
    app.run(debug=True)