from flask import Flask, render_template
from models import db, Topic, Flashcard

app = Flask(__name__, instance_relative_config=True)

# SQLite database (instance folder style)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///app.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)


@app.route("/")
def home():
    return "Flask + SQLite is working!"


if __name__ == "__main__":
    with app.app_context():
        db.create_all()   # THIS creates instance/app.db automatically
    app.run(debug=True)