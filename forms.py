from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Optional


class FlashcardForm(FlaskForm):
    topic_id = SelectField("Topic", coerce=int, validators=[DataRequired()])
    subtopic_id = SelectField("Subtopic", coerce=int, validators=[Optional()])
    new_subtopic = StringField("New subtopic", validators=[Optional()])
    plaintiff = StringField("Plaintiff", validators=[DataRequired()])
    defendant = StringField("Defendant (optional)", validators=[Optional()])
    facts = TextAreaField("Facts", validators=[DataRequired()])
    submit = SubmitField("Add Flashcard")


class TopicForm(FlaskForm):
    name = StringField("Topic Name", validators=[DataRequired()])
    submit = SubmitField("Create Topic")
