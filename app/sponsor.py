import os, uuid

from datetime import datetime
from flask import Blueprint, redirect, render_template, url_for, current_app
from flask_login import current_user

from . import db
from forms import EditCampaignForm, NewAdRequestForm, NewCampaignForm
from models import AdRequest, Campaign, Influencer, Quote, Sponsor, User
from utils.decorators import sponsor_required

sponsor_bp = Blueprint('sponsor', __name__)

@sponsor_bp.route('/sponsor', methods=['GET'])
@sponsor_required
def dashboard():
    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
    campaigns = sponsor.campaigns

    now = datetime.now()
    active_campaigns = sorted([campaign for campaign in campaigns if campaign.start_date <= now <= campaign.end_date], key=lambda x: x.start_date)
    upcoming_campaigns = sorted([campaign for campaign in campaigns if campaign.start_date > now], key=lambda x: x.start_date)
    past_campaigns = sorted([campaign for campaign in campaigns if campaign.end_date < now], key=lambda x: x.start_date, reverse=True)
    
    return render_template(
        'dash/sponsor/home.html',
        campaigns=campaigns,
        active_campaigns=active_campaigns,
        upcoming_campaigns=upcoming_campaigns,
        past_campaigns=past_campaigns,
    )

@sponsor_bp.route('/sponsor/campaigns', methods=['GET', 'POST'])
@sponsor_required
def campaigns():
    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
    campaigns = sponsor.campaigns
    
    form = NewCampaignForm()

    if form.validate_on_submit():
        photo = form.image.data
        extension = photo.filename[photo.filename.rfind('.'):]

        filename = f'{uuid.uuid4()}{extension}'
        photo.save(os.path.join(current_app.instance_path, 'media', 'campaign_images', filename))

        campaign = Campaign(
            name=form.name.data,
            description=form.description.data,
            tnc=form.tnc.data,
            start_date=form.start_date.data,
            end_date=form.end_date.data,
            budget=form.budget.data,
            public=form.public.data,
            sponsor_id=sponsor.id,
            image=filename,
        )
        db.session.add(campaign)
        db.session.commit()
        return redirect(url_for('sponsor.campaign', id=campaign.id))
    
    return render_template(
        'dash/sponsor/campaigns.html',
        form=form,
        campaigns=campaigns,
    )

@sponsor_bp.route('/sponsor/campaigns/<int:id>/createad', methods=['POST'])
@sponsor_required
def createAdRequest(id):
    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
    campaign = Campaign.query.filter_by(id=id, sponsor_id=sponsor.id).first()

    if campaign is None:
        return redirect(url_for('sponsor.campaigns'))

    form = NewAdRequestForm()
    if form.validate_on_submit():
        influencer_user = User.query.filter_by(username=form.influencer.data.lower()).first()
        influencer = Influencer.query.filter_by(user_id=influencer_user.id).first()
        ad = AdRequest(
            name=form.name.data,
            requirements=form.requirements.data,
            influencer_id=influencer.id,
            message=form.message.data,
            campaign_id=campaign.id,
            status='pending',
        )
        db.session.add(ad)
        db.session.commit()

        quote = Quote(
            amount=form.amount.data, 
            proposed_by=current_user,
            adrequest_id=ad.id,
        )
        db.session.add(quote)
        db.session.commit()

        ad.quotes.append(quote)
        influencer.adrequests.append(ad)
        db.session.commit()
    return redirect(url_for('sponsor.campaign', id=id))

@sponsor_bp.route('/sponsor/campaigns/<int:id>', methods=['GET', 'POST'])
@sponsor_required
def campaign(id):
    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
    campaign = Campaign.query.filter_by(id=id, sponsor_id=sponsor.id).first()

    if campaign is None:
        return redirect(url_for('sponsor.campaigns'))

    form = EditCampaignForm(obj=campaign)
    adform = NewAdRequestForm()
    if form.validate_on_submit():
        campaign.name = form.name.data
        campaign.description = form.description.data
        campaign.start_date = form.start_date.data
        campaign.end_date = form.end_date.data
        campaign.budget = form.budget.data
        campaign.public = form.public.data

        photo = form.image.data
        if type(photo) != str and photo.filename != campaign.image and photo.filename != '':
            extension = photo.filename[photo.filename.rfind('.'):]
            filename = f'{uuid.uuid4()}{extension}'
            photo.save(os.path.join(current_app.instance_path, 'media', 'campaign_images', filename))
            os.remove(os.path.join(current_app.instance_path, 'media', 'campaign_images', campaign.image))
            campaign.image = filename

        db.session.commit()
        return redirect(url_for('sponsor.campaign', id=id))
    return render_template(
        'dash/sponsor/campaign.html',
        campaign=campaign,
        form=form,
        adform=adform,
    )