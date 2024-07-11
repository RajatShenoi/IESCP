import datetime

from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed
from wtforms import StringField, PasswordField, IntegerField, URLField, EmailField, ValidationError, DateTimeLocalField, BooleanField, TextAreaField
from wtforms.widgets import NumberInput
from wtforms.validators import DataRequired, Length

from models import User

ALLOWED_IMAGES = ['jpg', 'png', 'jpeg']

class InfluencerRegistrationForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired(), Length(min=3, max=20)])
    name = StringField('Name:', validators=[DataRequired(), Length(min=3, max=100)])
    email = EmailField('Email:', validators=[DataRequired()])
    password1 = PasswordField('Password:', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    category = StringField('Category:', validators=[DataRequired()])
    niche = StringField('Niche:', validators=[DataRequired()])
    reach = IntegerField('Reach:', validators=[DataRequired()], widget=NumberInput(min=1000))
    instagram = URLField('Instagram:', validators=[DataRequired()])
    youtube = URLField('YouTube:', validators=[DataRequired()])
    twitter = URLField('Twitter:', validators=[DataRequired()])
    profile_picture = FileField('Profile Picture:', validators=[FileRequired('File was empty.'), FileAllowed(ALLOWED_IMAGES, f'{", ".join(ALLOWED_IMAGES)} files only.')], render_kw={'accept': f'.{",.".join(ALLOWED_IMAGES)}'})

    def validate_username(form, field):
        if not field.data.isalnum():
            raise ValidationError('Username can be alphanumeric only. [A-Z, a-z, 0-9]')
        if User.query.filter_by(username=field.data.lower()).first():
            raise ValidationError('Username already exists.')
    
    def validate_email(form, field):
        if '+' in field.data:
            raise ValidationError('Email cannot contain \'+\'.')
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already associated with another account.')
    
    def validate_password1(form, field):
        if form.password2.data != field.data:
            raise ValidationError('Passwords do not match.')
        
    def validate_password2(form, field):
        if form.password1.data != field.data:
            raise ValidationError('Passwords do not match.')

class SponsorRegistrationForm(FlaskForm):
    username = StringField('Username:', validators=[DataRequired(), Length(min=3, max=16)])
    company_name = StringField('Company Name:', validators=[DataRequired(), Length(min=3, max=100)])
    email = EmailField('Company Email:', validators=[DataRequired()])
    password1 = PasswordField('Password:', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    industry = StringField('Industry:', validators=[DataRequired()])
    budget = IntegerField('Budget:', validators=[DataRequired()], widget=NumberInput(min=1000))
    profile_picture = FileField('Profile Picture:', validators=[FileRequired('File was empty.'), FileAllowed(ALLOWED_IMAGES, f'{", ".join(ALLOWED_IMAGES)} files only.')], render_kw={'accept': f'.{",.".join(ALLOWED_IMAGES)}'})

    def validate_username(form, field):
        if not field.data.isalnum():
            raise ValidationError('Username can be alphanumeric only. [A-Z, a-z, 0-9]')
        if User.query.filter_by(username=field.data.lower()).first():
            raise ValidationError('Username already exists.')
    
    def validate_email(form, field):
        if '+' in field.data:
            raise ValidationError('Email cannot contain \'+\'.')
        if User.query.filter_by(email=field.data.lower()).first():
            raise ValidationError('Email already associated with another account.')
    
    def validate_password1(form, field):
        if form.password2.data != field.data:
            raise ValidationError('Passwords do not match.')
        
    def validate_password2(form, field):
        if form.password1.data != field.data:
            raise ValidationError('Passwords do not match.')
        
class LoginForm(FlaskForm):
    umail = StringField('Username / Email:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])

class NewCampaignForm(FlaskForm):
    name = StringField('Campaign Name:', validators=[DataRequired()])
    description = TextAreaField('Description:', validators=[DataRequired(), Length(min=10, max=2000)])
    start_date = DateTimeLocalField('Start Date:', validators=[DataRequired()], render_kw={'min': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")})
    end_date = DateTimeLocalField('End Date:', validators=[DataRequired()], render_kw={'min': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")})
    budget = IntegerField('Budget:', validators=[DataRequired()], widget=NumberInput(min=5))
    image = FileField('Image:', validators=[FileRequired('File was empty.'), FileAllowed(ALLOWED_IMAGES, f'{", ".join(ALLOWED_IMAGES)} files only.')], render_kw={'accept': f'.{",.".join(ALLOWED_IMAGES)}'})
    public = BooleanField('Public:', validators=[])

class EditCampaignForm(NewCampaignForm):
    image = FileField('Image:', validators=[FileAllowed(ALLOWED_IMAGES, f'{", ".join(ALLOWED_IMAGES)} files only.')], render_kw={'accept': f'.{",.".join(ALLOWED_IMAGES)}'})