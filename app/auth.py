import os, uuid

from flask import Blueprint, redirect, render_template, url_for, current_app
from flask_login import login_user, logout_user

from . import bcrypt, db
from forms import InfluencerRegistrationForm, LoginForm, SponsorRegistrationForm
from models import Influencer, Sponsor, User
from utils.decorators import anonymous_required

auth_bp = Blueprint('auth', __name__)

@auth_bp.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    form = LoginForm()

    if form.validate_on_submit():
        umail = form.umail.data.lower()
        password = form.password.data

        user = User.query.filter_by(username=umail).first() or User.query.filter_by(email=umail).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main.home'))
        return render_template('auth/login.html', form=form, error='Invalid credentials')

    return render_template('auth/login.html', form=form)

@auth_bp.route('/register', methods=['GET'])
@anonymous_required
def register():
    return render_template('auth/register.html')

@auth_bp.route('/register/influencer', methods=['GET', 'POST'])
@anonymous_required
def register_influencer():
    form = InfluencerRegistrationForm()

    if form.validate_on_submit():
        username = form.username.data.lower()
        email = form.email.data.lower()
        password = form.password1.data
        name = form.name.data
        category = form.category.data
        niche = form.niche.data
        reach = form.reach.data
        instagram = form.instagram.data
        youtube = form.youtube.data
        twitter = form.twitter.data
        photo = form.profile_picture.data

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        extension = photo.filename[photo.filename.rfind('.'):]
        filename = f'{username}{extension}'
        photo.save(os.path.join(current_app.instance_path, 'media', 'profile_pictures', filename))

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            user_type='influencer',
            profile_picture=filename,
        )

        influencer = Influencer(
            name=name,
            category=category,
            niche=niche,
            followers=reach,
            instagram=instagram,
            youtube=youtube,
            twitter=twitter,
        )

        db.session.add(influencer)
        db.session.commit()

        user.influencer = influencer
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('main.home'))
    return render_template('auth/influencer.html', form=form)

@auth_bp.route('/register/sponsor', methods=['GET', 'POST'])
@anonymous_required
def register_sponsor():
    form = SponsorRegistrationForm()

    if form.validate_on_submit():
        username = form.username.data.lower()
        email = form.email.data.lower()
        password = form.password1.data
        company_name = form.company_name.data
        industry = form.industry.data
        budget = form.budget.data
        photo = form.profile_picture.data

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')
        extension = photo.filename[photo.filename.rfind('.'):]
        filename = f'{uuid.uuid4()}{extension}'
        photo.save(os.path.join(current_app.instance_path, 'media', 'profile_pictures', filename))

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            user_type='sponsor',
            profile_picture=filename,
        )

        sponsor = Sponsor(
            company_name=company_name,
            industry=industry,
            budget=budget,
        )

        db.session.add(sponsor)
        db.session.commit()

        user.sponsor = sponsor
        db.session.add(user)
        db.session.commit()

        login_user(user)
        return redirect(url_for('main.home'))
    return render_template('auth/sponsor.html', form=form)

@auth_bp.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('main.home'))
