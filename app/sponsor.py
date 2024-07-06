from flask import Blueprint, redirect, render_template, url_for
from flask_login import current_user

from . import db
from forms import NewCampaignForm
from models import Campaign, Sponsor
from utils.decorators import sponsor_required

sponsor_bp = Blueprint('sponsor', __name__)

@sponsor_bp.route('/sponsor', methods=['GET'])
@sponsor_required
def dashboard():
    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
    campaigns = sponsor.campaigns
    return render_template(
        'dash/sponsor/home.html',
        campaigns=campaigns,
    )

@sponsor_bp.route('/sponsor/campaigns', methods=['GET', 'POST'])
@sponsor_required
def campaigns():
    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
    campaigns = sponsor.campaigns
    
    form = NewCampaignForm()

    if form.validate_on_submit():
        campaign = Campaign(
            name=form.name.data,
            description=form.description.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data,
            public=form.public.data,
            sponsor_id=sponsor.id,
        )
        db.session.add(campaign)
        db.session.commit()
        return redirect(url_for('sponsor.campaigns'))
    
    return render_template(
        'dash/sponsor/campaigns.html',
        form=form,
        campaigns=campaigns,
    )