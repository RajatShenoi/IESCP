from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired
from wtforms import StringField, PasswordField, SubmitField, IntegerField, URLField, EmailField
from wtforms.widgets import NumberInput
from wtforms.validators import DataRequired

class InfluencerRegistrationForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired()])
    name = StringField('Name:', validators=[DataRequired()])
    email = EmailField('Email:', validators=[DataRequired()])
    password1 = PasswordField('Password:', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    category = StringField('Category:', validators=[DataRequired()])
    reach = IntegerField('Reach:', validators=[DataRequired()], widget=NumberInput(min=1000))
    instagram = URLField('Instagram:', validators=[DataRequired()])
    youtube = URLField('YouTube:', validators=[DataRequired()])
    twitter = URLField('Twitter:', validators=[DataRequired()])
    profile_picture = FileField('Profile Picture:', validators=[FileRequired()])
    submit = SubmitField('Register')