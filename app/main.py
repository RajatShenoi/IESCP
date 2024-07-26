from flask import Blueprint, current_app, redirect, render_template, send_from_directory, url_for
from flask_login import current_user, login_required

main_bp = Blueprint('main', __name__)

@main_bp.route('/', methods=['GET'])
def home():
    return render_template('home.html')

@main_bp.route('/dashboard', methods=['GET'])
@login_required
def dashboard():
    if current_user.user_type == 'sponsor':
        return redirect(url_for('sponsor.dashboard'))
    elif current_user.user_type == 'influencer':
        return redirect(url_for('influencer.dashboard'))
    elif current_user.user_type == 'admin':
        return redirect(url_for('admin.dashboard'))
    return redirect(url_for('main.home'))

@main_bp.route('/edit-profile', methods=['GET'])
@login_required
def editProfile():
    if current_user.user_type in 'sponsor':
        return redirect(url_for('sponsor.editProfile'))
    elif current_user.user_type == 'influencer':
        return redirect(url_for('influencer.editProfile'))
    elif current_user.user_type == 'admin':
        return redirect(url_for('admin.editProfile'))
    return redirect(url_for('main.home'))

@main_bp.route('/files/campaign/<filename>', methods=['GET'])
def campaign_image(filename):
    return send_from_directory(current_app.instance_path + '/media/campaign_images/', filename)

@main_bp.route('/files/influencer/<filename>', methods=['GET'])
def influencer_picture(filename):
    return send_from_directory(current_app.instance_path + '/media/profile_pictures/', filename)