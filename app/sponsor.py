from flask import Blueprint, render_template

from utils.decorators import sponsor_required

sponsor_bp = Blueprint('sponsor', __name__)

@sponsor_bp.route('/dashboard/sponsor', methods=['GET'])
@sponsor_required
def dashboard():
    return render_template('dash/sponsor/home.html')
