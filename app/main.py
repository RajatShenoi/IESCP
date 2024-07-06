from flask import Blueprint, redirect, render_template, url_for
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
    return redirect(url_for('main.home'))
