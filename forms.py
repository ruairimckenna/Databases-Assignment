from flask_wtf import FlaskForm
from wtforms import SelectField, StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, Length, Optional


class FlashcardForm(FlaskForm):
    topic_id = SelectField("Topic", coerce=int, validators=[DataRequired()])
    subtopic_id = SelectField("Subtopic", coerce=int, validators=[Optional()])
    new_subtopic = StringField("New subtopic", validators=[Optional()])
    plaintiff = StringField(
        "Plaintiff/Principle",
        validators=[DataRequired(), Length(max=50)],
    )
    defendant = StringField("Defendant (optional)", validators=[Optional(), Length(max=50)])
    facts = TextAreaField("Facts", validators=[DataRequired()])
    submit = SubmitField("Add Flashcard")


class TopicForm(FlaskForm):
    name = StringField("Topic Name", validators=[DataRequired()])
    submit = SubmitField("Create Topic")
