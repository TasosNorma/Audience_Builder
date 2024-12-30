from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, TextAreaField, PasswordField
from wtforms.validators import DataRequired, URL, Length, Email, EqualTo

class UrlSubmit(FlaskForm):
    url = StringField('Url',validators=[DataRequired(),URL()])
    submit = SubmitField('Submit Url')

class PromptForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    template = TextAreaField('Template', validators=[DataRequired()])
    submit = SubmitField('Save Changes')

class SetupProfileForm(FlaskForm):
    full_name = StringField('Name',validators=[DataRequired()])
    bio = TextAreaField('Bio',validators=[DataRequired()])
    interests_description = TextAreaField('Interests Description', validators=[DataRequired()])
    openai_api_key = TextAreaField('Open AI API key')
    submit = SubmitField('Save Changes')

class ArticleCompareForm(FlaskForm):
    article_url = StringField('Article URL', validators=[DataRequired(), URL()])
    submit = SubmitField('Compare with Profile')

class LoginForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password',validators=[DataRequired()])
    submit = SubmitField('Login')

class RegistrationForm(FlaskForm):
    email = StringField('Email',validators=[DataRequired(),Email()])
    password = PasswordField('Password', validators=[
        DataRequired(),
        Length(min=6, message='Password must be at least 6 characters')
    ])
    confirm_password = PasswordField('Confirm Password', validators=[
        DataRequired(),
        EqualTo('password', message='Passwords must match')
    ])
    submit = SubmitField('Register')

class SettingsForm(FlaskForm):
    openai_api_key = StringField('OpenAI API Key', validators=[DataRequired()])
    submit = SubmitField('Update Settings')