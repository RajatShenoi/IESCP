from datetime import datetime
import os
import uuid
from flask import Blueprint, current_app, flash, redirect, render_template, request, url_for
from flask_login import current_user
from sqlalchemy import or_

from . import db
from forms import EditSponsorForm, SearchForm
from models import Campaign, Influencer, Quote, Sponsor, User
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
    
    if campaign.flagged:
        flash('This campaign has been flagged.', 'danger')
    
    return render_template('dash/admin/campaign.html', campaign=campaign)

@admin_bp.route('/admin/campaign/<int:id>/flag', methods=['GET'])
@admin_required
def flagCampaign(id):
    campaign = Campaign.query.filter_by(id=id).first()
    if campaign is None:
        flash('Campaign not found.', 'danger')
        return redirect(url_for('admin.supervise'))
    
    for adreq in campaign.adrequests:
        if adreq.status == 'pending':
            quote = Quote(
                amount=0,
                message='This offer has been closed because the campaign was flagged.',
                user_id=current_user.id,
                adrequest_id=adreq.id,
                created_at=datetime.now(),
            )
            adreq.status = 'declined'
            db.session.add(quote)
            db.session.commit()
    
    campaign.flagged = True
    db.session.commit()
    return redirect(url_for('admin.viewCampaign', id=id))

@admin_bp.route('/admin/campaign/<int:id>/unflag', methods=['GET'])
@admin_required
def unflagCampaign(id):
    campaign = Campaign.query.filter_by(id=id).first()
    if campaign is None:
        flash('Campaign not found.', 'danger')
        return redirect(url_for('admin.supervise'))
    
    campaign.flagged = False
    db.session.commit()
    flash('Campaign un-flagged successfully.', 'success')
    return redirect(url_for('admin.viewCampaign', id=id))

@admin_bp.route('/admin/find', methods=['GET', 'POST'])
@admin_required
def find():
    influencers = Influencer.query.all()    
    form = SearchForm()
    if form.validate_on_submit():
        search_term = f'%{form.search.data.strip()}%'
        influencers = Influencer.query.filter(
            or_(
                Influencer.name.ilike(search_term),
                Influencer.category.ilike(search_term),
                Influencer.niche.ilike(search_term),
                Influencer.followers.ilike(search_term),
                Influencer.instagram.ilike(search_term),
                Influencer.youtube.ilike(search_term),
                Influencer.twitter.ilike(search_term),
            )
        ).all()
    return render_template('dash/admin/find.html', influencers=influencers, form=form)

@admin_bp.route('/admin/find/<username>', methods=['GET'])
@admin_required
def viewInfluencer(username):
    user = User.query.filter_by(username=username).first()
    influencer = Influencer.query.filter_by(user=user).first()
    if influencer is None:
        flash('Influencer not found.', 'danger')
        return redirect(url_for('admin.find'))
    if user.flagged:
        flash('This influencer has been flagged.', 'danger')
    return render_template('dash/admin/influencer.html', influencer=influencer)

@admin_bp.route('/admin/influencer/<username>/flag', methods=['GET'])
@admin_required
def flagUser(username):
    user = User.query.filter_by(username=username).first()
    influencer = Influencer.query.filter_by(user=user).first()
    if influencer is None:
        flash('Influencer not found.', 'danger')
        return redirect(url_for('admin.find'))
    
    for adreq in influencer.adrequests:
        if adreq.status == 'pending':
            quote = Quote(
                amount=0,
                message='This offer has been closed because the influencer was flagged.',
                user_id=current_user.id,
                adrequest_id=adreq.id,
                created_at=datetime.now(),
            )
            adreq.status = 'declined'
            db.session.add(quote)
            db.session.commit()
    
    influencer.user.flagged = True
    db.session.commit()
    return redirect(url_for('admin.viewInfluencer', username=username))

@admin_bp.route('/admin/influencer/<username>/unflag', methods=['GET'])
@admin_required
def unflagUser(username):
    user = User.query.filter_by(username=username).first()
    influencer = Influencer.query.filter_by(user=user).first()
    if influencer is None:
        flash('Influencer not found.', 'danger')
        return redirect(url_for('admin.find'))
    
    influencer.user.flagged = False
    db.session.commit()
    flash('Influencer un-flagged successfully.', 'success')
    return redirect(url_for('admin.viewInfluencer', username=username))