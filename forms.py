import datetime

from flask import flash
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
    about = TextAreaField('About:', validators=[DataRequired(), Length(min=10, max=2000)])
    email = EmailField('Email:', validators=[DataRequired()])
    password1 = PasswordField('Password:', validators=[DataRequired()])
    password2 = PasswordField('Confirm Password:', validators=[DataRequired()])
    category = StringField('Category:', validators=[DataRequired()])
    niche = StringField('Niche:', validators=[DataRequired()])
    reach = IntegerField('Reach:', validators=[DataRequired()], widget=NumberInput(min=1000))
    instagram = StringField('Instagram:', validators=[DataRequired()])
    youtube = StringField('YouTube:', validators=[DataRequired()])
    twitter = StringField('Twitter:', validators=[DataRequired()])
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
        
    def validate_profile_picture(form, field):
        if not field.data:
            raise ValidationError('File was empty.')
        extension = field.data.filename[field.data.filename.rfind('.')+1:]
        if extension not in ALLOWED_IMAGES:
            raise ValidationError(f'Invalid file type. Allowed types: {", ".join(ALLOWED_IMAGES)}')

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
        
    def validate_profile_picture(form, field):
        if not field.data:
            raise ValidationError('File was empty.')
        extension = field.data.filename[field.data.filename.rfind('.')+1:]
        if extension not in ALLOWED_IMAGES:
            raise ValidationError(f'Invalid file type. Allowed types: {", ".join(ALLOWED_IMAGES)}')
        
class LoginForm(FlaskForm):
    umail = StringField('Username / Email:', validators=[DataRequired()])
    password = PasswordField('Password:', validators=[DataRequired()])

class NewCampaignForm(FlaskForm):
    name = StringField('Campaign Name:', validators=[DataRequired()])
    description = TextAreaField('Description:', validators=[DataRequired(), Length(min=10, max=2000)])
    tnc = TextAreaField('Terms & Conditions:', validators=[DataRequired(), Length(min=10, max=20000)])
    start_date = DateTimeLocalField('Start Date:', validators=[DataRequired()], render_kw={'min': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")})
    end_date = DateTimeLocalField('End Date:', validators=[DataRequired()], render_kw={'min': datetime.datetime.now().strftime("%Y-%m-%dT%H:%M")})
    budget = IntegerField('Budget:', validators=[DataRequired()], widget=NumberInput(min=5))
    goal = IntegerField('Goal:', validators=[DataRequired()], widget=NumberInput(min=0))
    image = FileField('Image:', validators=[FileRequired('File was empty.'), FileAllowed(ALLOWED_IMAGES, f'{", ".join(ALLOWED_IMAGES)} files only.')], render_kw={'accept': f'.{",.".join(ALLOWED_IMAGES)}'})
    public = BooleanField('Public:', validators=[])

    def validate_start_date(form, field):
        if field.data < datetime.datetime.now():
            raise ValidationError('Start date cannot be in the past.')
    
    def validate_end_date(form, field):
        if field.data < form.start_date.data:
            raise ValidationError('End date cannot be before start date.')
    
    def validate_image(form, field):
        if not field.data:
            raise ValidationError('File was empty.')
        extension = field.data.filename[field.data.filename.rfind('.')+1:]
        if extension not in ALLOWED_IMAGES:
            raise ValidationError(f'Invalid file type. Allowed types: {", ".join(ALLOWED_IMAGES)}')

class EditCampaignForm(NewCampaignForm):
    image = FileField('Image:', validators=[FileAllowed(ALLOWED_IMAGES, f'{", ".join(ALLOWED_IMAGES)} files only.')], render_kw={'accept': f'.{",.".join(ALLOWED_IMAGES)}'})

    def validate_image(form, field):
        if type(field.data) == str():
            extension = field.data[field.data.rfind('.')+1:]
            if extension not in ALLOWED_IMAGES:
                raise ValidationError(f'Invalid file type. Allowed types: {", ".join(ALLOWED_IMAGES)}')

class NewAdRequestForm(FlaskForm):
    name = StringField('Ad Name:', validators=[DataRequired(), Length(min=3, max=100)])
    requirements = TextAreaField('Requirements:', validators=[DataRequired(), Length(min=10, max=2000)])
    amount = IntegerField('Amount:', validators=[DataRequired()], widget=NumberInput(min=5))
    message = TextAreaField('Message:', validators=[Length(max=1000)])
    influencer = StringField('Influencer:', validators=[DataRequired(), Length(min=3, max=20)])

    def validate_influencer(form, field):
        user = User.query.filter_by(username=field.data.lower()).first()
        if not user:
            flash('Influencer does not exist.', 'danger')
            raise ValidationError('Influencer does not exist.')
        if not user.influencer:
            flash('User is not an influencer.', 'danger')
            raise ValidationError('User is not an influencer.')

class AdOfferManageForm(FlaskForm):
    updated_amount = IntegerField('Amount:', validators=[DataRequired()], widget=NumberInput(min=5))
    message = TextAreaField('Message:', validators=[Length(max=1000)])

class SearchForm(FlaskForm):
    search = StringField('Search:', validators=[])

class NewAdRequestInfForm(NewAdRequestForm):
    influencer = None

    def validate_influencer(form, field):
        pass