import os

from flask import Flask, render_template, redirect, url_for
from flask_bcrypt import Bcrypt
from flask_bootstrap import Bootstrap5
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from flask_wtf import CSRFProtect

from utils.decorators import sponsor_required, anonymous_required
from forms import InfluencerRegistrationForm, LoginForm, SponsorRegistrationForm
from models import Influencer, Sponsor, User, db

app = Flask(__name__)
app.config['SECRET_KEY'] = '9nL2hZpiJNzXUfneHq1RdhAu8A1vb9xd'
app.config['TEMPLATES_AUTO_RELOAD'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///db.sqlite3'

bcrypt = Bcrypt(app)
bootstrap = Bootstrap5(app)
csrf = CSRFProtect(app)
login_manager = LoginManager(app)

db.init_app(app)

with app.app_context():
    db.create_all()

@login_manager.user_loader
def load_user(user_id):
    return User.query.filter_by(id=user_id).first()

@login_manager.unauthorized_handler
def unauthorized_callback():
    return redirect(url_for('login'))

@app.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@app.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.user_type == 'sponsor':
        return redirect(url_for('sponsor_dashboard'))
    return redirect(url_for('home'))

@app.route('/dashboard/sponsor', methods=['GET'])
@sponsor_required
def sponsor_dashboard():
    return render_template('dash/sponsor/home.html')

@app.route('/login', methods=['GET', 'POST'])
@anonymous_required
def login():
    form = LoginForm()

    if form.validate_on_submit():
        umail = form.umail.data.lower()
        password = form.password.data

        user = User.query.filter_by(username=umail).first() or User.query.filter_by(email=umail).first()

        if user and bcrypt.check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('home'))
        return render_template('auth/login.html', form=form, error='Invalid credentials')

    return render_template('auth/login.html', form=form)

@app.route('/register', methods=['GET'])
@anonymous_required
def register():
    return render_template('auth/register.html')

@app.route('/register/influencer', methods=['GET', 'POST'])
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
        filename = f'profile_pictures/{username}_{photo.filename}'
        photo.save(os.path.join(app.instance_path, 'media', 'profile_pictures', f'{username}_{photo.filename}'))

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
        return redirect(url_for('home'))
    return render_template('auth/influencer.html', form=form)

@app.route('/register/sponsor', methods=['GET', 'POST'])
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

        hashed_password = bcrypt.generate_password_hash(password).decode('utf-8')

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            user_type='sponsor',
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
        return redirect(url_for('home'))
    return render_template('auth/sponsor.html', form=form)

@app.route('/logout', methods=['GET'])
def logout():
    logout_user()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run()
