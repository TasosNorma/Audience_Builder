from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField
from wtforms.validators import DataRequired, URL, Length

class UrlSubmit(FlaskForm):
    url = StringField('Url',validators=[DataRequired(),URL()])
    submit = SubmitField('Submit Url')


class PromptForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    template = TextAreaField('Template', validators=[DataRequired()])
    submit = SubmitField('Save Changes')