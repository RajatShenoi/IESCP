import os, uuid

from flask import Blueprint, jsonify, render_template, request, current_app
from flask_jwt_extended import create_access_token, get_jwt_identity, jwt_required
from flask_login import login_user, logout_user
from werkzeug.security import generate_password_hash, check_password_hash

from . import bcrypt, db
from forms import InfluencerRegistrationForm, LoginForm, SponsorRegistrationForm
from models import Influencer, Sponsor, User
from utils.decorators import anonymous_required

auth_bp = Blueprint('auth', __name__)

# TODO: Validation for all routes

def save_profile_picture(photo):
    extension = photo.filename[photo.filename.rfind('.'):]
    filename = f'{uuid.uuid4()}{extension}'
    photo.save(os.path.join(current_app.instance_path, 'media', 'profile_pictures', filename))
    return filename

@auth_bp.route('/api/login', methods=['POST'])
def login():
    data = request.json
    umail = data.get('umail', '').lower()
    password = data.get('password', '')

    user = User.query.filter((User.username == umail) | (User.email == umail)).first()

    if user and check_password_hash(user.password, password):
        token = create_access_token(identity=str({"id": user.id, "user_type": user.user_type}))
        return jsonify({"access_token": token, "message": "Login successful"}), 200

    return jsonify({"error": "Invalid credentials. Please try again."}), 401

@auth_bp.route('/api/register', methods=['GET'])
@anonymous_required
def register():
    return render_template('auth/register.html')

@auth_bp.route('/api/register/influencer', methods=['POST'])
def register_influencer():
    data = request.form
    photo = request.files.get('profile_picture')

    if not photo:
        return jsonify({"error": "Profile picture is required"}), 400
    
    if not photo.filename:
        return jsonify({"error": "Invalid file upload"}), 400
    
    if photo and photo.filename == '':
        return jsonify({"error": "Profile picture file is empty"}), 400

    
    try:
        username = data['username'].lower().strip()
        email = data['email'].lower().strip()
        about = data['about']
        password = data['password1']
        name = data['name']
        category = data['category']
        niche = data['niche']
        reach = data['reach']
        instagram = data.get('instagram')
        youtube = data.get('youtube')
        twitter = data.get('twitter')

        hashed_password = generate_password_hash(password)
        filename = save_profile_picture(photo)

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({"error": "User already exists"}), 400

        user = User(
            username=username,
            email=email,
            password=hashed_password,
            user_type='influencer',
            profile_picture=filename,
        )

        influencer = Influencer(
            name=name,
            about=about,
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

        token = create_access_token(identity={"id": user.id, "user_type": "influencer"})
        return jsonify({"access_token": token, "message": "Influencer registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to register influencer: {str(e)}"}), 500

@auth_bp.route('/api/register/sponsor', methods=['POST'])
def register_sponsor():
    data = request.form
    photo = request.files.get('profile_picture')
    print(data)
    print(photo)
    
    if not photo:
        return jsonify({"error": "Profile picture is required"}), 400
    
    if not photo.filename:
        return jsonify({"error": "Invalid file upload"}), 400
    
    if photo and photo.filename == '':
        return jsonify({"error": "Profile picture file is empty"}), 400

    try:
        username = data['username'].lower().strip()
        email = data['email'].lower().strip()
        password = data['password1']
        company_name = data['company_name']
        industry = data['industry']
        budget = data['budget']

        hashed_password = generate_password_hash(password)
        filename = save_profile_picture(photo)

        if User.query.filter((User.username == username) | (User.email == email)).first():
            return jsonify({"error": "User already exists"}), 400

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

        token = create_access_token(identity=str({"id": user.id, "user_type": "sponsor"}))
        return jsonify({"access_token": token, "message": "Sponsor registered successfully"}), 201

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Failed to register sponsor: {str(e)}"}), 500

@auth_bp.route('/api/logout', methods=['POST'])
@jwt_required()
def logout():
    # TODO: Invalidate token logic could be added if using token blacklisting
    return jsonify({"message": "Logout successful"}), 200
