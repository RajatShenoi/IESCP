import os
import uuid
from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import or_

from . import db
from forms import EditSponsorForm, SearchForm
from models import Campaign, Sponsor
from utils.decorators import admin_required

admin_bp = Blueprint('admin', __name__)

@admin_bp.route('/admin', methods=['GET'])
@admin_required
def dashboard():
    return render_template('dash/admin/home.html')

@admin_bp.route('/admin/editProfile', methods=['GET', 'POST'])
@admin_required
def editProfile():
    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()

    form = EditSponsorForm(obj=sponsor)
    if form.validate_on_submit():
        sponsor.company_name = form.company_name.data
        sponsor.industry = form.industry.data
        sponsor.budget = form.budget.data

        current_user.email = form.email.data

        photo = form.profile_picture.data
        if photo != None and photo.filename != current_user.profile_picture and photo.filename != '':
            extension = photo.filename[photo.filename.rfind('.'):]
            filename = f'{uuid.uuid4()}{extension}'
            photo.save(os.path.join(current_app.instance_path, 'media', 'profile_pictures', filename))
            os.remove(os.path.join(current_app.instance_path, 'media', 'profile_pictures', current_user.profile_picture))
            current_user.profile_picture = filename

        db.session.commit()
        flash('Company Profile updated successfully.', 'success')
        return redirect(url_for('admin.editProfile'))
    return render_template('dash/sponsor/edit_profile.html', form=form)

@admin_bp.route('/admin/supervise', methods=['GET', 'POST'])
@admin_required
def supervise():
    campaigns = Campaign.query.all()
    campaigns.sort(key=lambda x: x.end_date, reverse=True)
    form = SearchForm()
    if form.validate_on_submit():
        search_term = f'%{form.search.data.strip()}%'
        campaigns = Campaign.query.filter(
            or_(
                Campaign.name.ilike(search_term),
                Campaign.description.ilike(search_term),
                Campaign.start_date.ilike(search_term),
                Campaign.end_date.ilike(search_term),
                Campaign.tnc.ilike(search_term),
                Campaign.niche.ilike(search_term),
            )
        ).all()
        campaigns.sort(key=lambda x: x.end_date, reverse=True)
    return render_template('dash/admin/supervise.html', campaigns=campaigns, form=form)

@admin_bp.route('/admin/campaign/<int:id>', methods=['GET', 'POST'])
@admin_required
def viewCampaign(id):
    campaign = Campaign.query.filter_by(id=id).first()

    if campaign is None:
        flash('Campaign not found.', 'danger')
        return redirect(url_for('admin.supervise'))
    
    return render_template('dash/admin/campaign.html', campaign=campaign)