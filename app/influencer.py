from datetime import datetime
import os
import random
import uuid
from flask import Blueprint, current_app, flash, redirect, render_template, url_for
from flask_login import current_user
from sqlalchemy import or_

from . import db
from forms import AdOfferManageForm, EditInfluencerForm, NewAdRequestInfForm, SearchForm
from models import AdRequest, Campaign, Influencer, Quote, User
from utils.decorators import influencer_required

influencer_bp = Blueprint('influencer', __name__)

@influencer_bp.route('/influencer', methods=['GET'])
@influencer_required
def dashboard():
    user = User.query.filter_by(id=current_user.id).first()
    influencer = Influencer.query.filter_by(user_id=user.id).first()

    addofferform = AdOfferManageForm()

    return render_template('dash/influencer/home.html', influencer=influencer, addofferform=addofferform)

@influencer_bp.route('/influencer/find', methods=['GET', 'POST'])
@influencer_required
def findCampaigns():
    campaigns = Campaign.query.filter_by(public=True).filter(Campaign.end_date > datetime.now(), Campaign.start_date <= datetime.now())

    form = SearchForm()
    if form.validate_on_submit():
        search_term = f'%{form.search.data.strip()}%'
        campaigns = campaigns.filter(
            or_(
                Campaign.name.ilike(search_term),
                Campaign.description.ilike(search_term),
                Campaign.start_date.ilike(search_term),
                Campaign.end_date.ilike(search_term),
                Campaign.tnc.ilike(search_term),
                Campaign.niche.ilike(search_term),
            )
        )
    return render_template('dash/influencer/find.html', campaigns=campaigns.all(), form=form)

@influencer_bp.route('/influencer/find/<int:id>', methods=['GET', 'POST'])
@influencer_required
def viewCampaign(id):
    campaign = Campaign.query.filter_by(public=True, id=id).filter(Campaign.end_date > datetime.now(), Campaign.start_date <= datetime.now()).first()

    if campaign is None:
        return redirect(url_for('influencer.findCampaigns'))
    
    if campaign.flagged:
        flash('This campaign has been flagged and is currently unavailable.', 'danger')
        return redirect(url_for('influencer.findCampaigns'))
    
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()
    adrequests = AdRequest.query.filter_by(campaign_id=campaign.id, influencer_id=influencer.id).all()
    
    form = NewAdRequestInfForm()
    addofferform = AdOfferManageForm()
    if form.validate_on_submit():
        influencer_user = User.query.filter_by(username=current_user.username).first()
        influencer = Influencer.query.filter_by(user_id=influencer_user.id).first()
        ad = AdRequest(
            name=form.name.data,
            requirements=form.requirements.data,
            influencer_id=influencer.id,
            campaign_id=campaign.id,
            status='pending',
        )
        db.session.add(ad)
        db.session.commit()

        quote = Quote(
            amount=form.amount.data, 
            message=form.message.data,
            user_id=current_user.id,
            adrequest_id=ad.id,
            created_at=datetime.now(),
        )
        db.session.add(quote)
        db.session.commit()

        ad.quotes.append(quote)
        influencer.adrequests.append(ad)
        db.session.commit()

        return redirect(url_for('influencer.viewCampaign', id=id))
    return render_template('dash/influencer/campaign.html', campaign=campaign, adform=form, adrequests=adrequests, addofferform=addofferform)

@influencer_bp.route('/influencer/offer/<int:ad_id>/negotiate', methods=['POST'])
@influencer_required
def negotiateAdOffer(ad_id):
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()
    ad = AdRequest.query.filter_by(id=ad_id, influencer_id=influencer.id).first()

    if ad is None or influencer is None or ad.status != 'pending':
        return redirect(url_for('influencer.dashboard'))
    
    form = AdOfferManageForm()
    if form.validate_on_submit():
        quote = Quote(
            amount=form.updated_amount.data,
            message=form.message.data,
            user_id=current_user.id,
            adrequest_id=ad.id,
            created_at=datetime.now(),
        )
        db.session.add(quote)
        db.session.commit()
    return redirect(url_for('influencer.viewCampaign', id=ad.campaign_id))


@influencer_bp.route('/influencer/offer/<int:ad_id>/decline', methods=['GET'])
@influencer_required
def declineAdOffer(ad_id):
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()
    ad = AdRequest.query.filter_by(id=ad_id, influencer_id=influencer.id).first()

    if ad is None or influencer is None or ad.status != 'pending':
        return redirect(url_for('influencer.dashboard'))
    
    quote = Quote(
        amount=ad.current_quote.amount,
        message='This offer has been cancelled / declined.',
        user_id=current_user.id,
        adrequest_id=ad.id,
        created_at=datetime.now(),
    )

    ad.status = 'declined'
    db.session.add(quote)
    db.session.commit()
    return redirect(url_for('influencer.dashboard'))

@influencer_bp.route('/influencer/offer/<int:ad_id>/accept', methods=['GET'])
@influencer_required
def acceptAdOffer(ad_id):
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()
    ad = AdRequest.query.filter_by(id=ad_id, influencer_id=influencer.id).first()

    if ad is None or influencer is None or ad.status != 'pending':
        return redirect(url_for('influencer.dashboard'))
    
    current_quote = ad.current_quote

    if current_quote.user_id == current_user.id:
        flash('You cannot accept this offer as you\'ve made the latest negotiation. Kindly wait for the response.', 'danger')
        return redirect(url_for('influencer.dashboard'))
    
    quote = Quote(
        amount=ad.current_quote.amount,
        message='This offer has been accepted.',
        user_id=current_user.id,
        adrequest_id=ad.id,
        created_at=datetime.now(),
    )

    ad.status = 'ongoing'
    db.session.add(quote)
    db.session.commit()
    return redirect(url_for('influencer.dashboard'))

@influencer_bp.route('/influencer/offer/<int:ad_id>/completed', methods=['GET'])
@influencer_required
def markAdAsCompleted(ad_id):
    influencer = Influencer.query.filter_by(user_id=current_user.id).first()
    ad = AdRequest.query.filter_by(id=ad_id, influencer_id=influencer.id).first()

    if ad is None or influencer is None or ad.status != 'ongoing':
        return redirect(url_for('influencer.dashboard'))
    
    quote = Quote(
        amount=ad.current_quote.amount,
        message='This ad has been marked as completed.',
        user_id=current_user.id,
        adrequest_id=ad.id,
        created_at=datetime.now(),
    )

    ad.status = 'completed'
    db.session.add(quote)
    db.session.commit()
    return redirect(url_for('influencer.dashboard'))

@influencer_bp.route('/influencer/edit-profile', methods=['GET', 'POST'])
@influencer_required
def editProfile():
    user = User.query.filter_by(id=current_user.id).first()
    influencer = Influencer.query.filter_by(user_id=user.id).first()

    form = EditInfluencerForm(obj=influencer)
    if form.validate_on_submit():
        influencer.name = form.name.data
        influencer.about = form.about.data
        influencer.category = form.category.data
        influencer.niche = form.niche.data
        influencer.followers = form.reach.data
        influencer.youtube = form.youtube.data
        influencer.instagram = form.instagram.data
        influencer.twitter = form.twitter.data

        user.email = form.email.data

        photo = form.profile_picture.data
        if photo != None and photo.filename != user.profile_picture and photo.filename != '':
            extension = photo.filename[photo.filename.rfind('.'):]
            filename = f'{uuid.uuid4()}{extension}'
            photo.save(os.path.join(current_app.instance_path, 'media', 'profile_pictures', filename))
            os.remove(os.path.join(current_app.instance_path, 'media', 'profile_pictures', user.profile_picture))
            user.profile_picture = filename

        db.session.commit()
        flash('Profile updated successfully.', 'success')
        return redirect(url_for('influencer.dashboard'))
    return render_template('dash/influencer/edit_profile.html', form=form)

def random_colour():
    r = random.randint(0, 255)
    g = random.randint(0, 255)
    b = random.randint(0, 255)
    return f'rgba({r}, {g}, {b}, 0.2)'

@influencer_bp.route('/influencer/stats', methods=['GET'])
@influencer_required
def stats():
    adRequestCountLabels = ['Pending', 'Ongoing', 'Declined', 'Completed']
    adRequestCountData = [
        sum([1 for ad in current_user.influencer.adrequests if ad.status == 'pending']),
        sum([1 for ad in current_user.influencer.adrequests if ad.status == 'ongoing']),
        sum([1 for ad in current_user.influencer.adrequests if ad.status == 'declined']),
        sum([1 for ad in current_user.influencer.adrequests if ad.status == 'completed'])
    ]

    earningsSplitLabels = [ad.name for ad in current_user.influencer.adrequests if ad.status == 'completed']
    earningsSplitData = [ad.current_quote.amount for ad in current_user.influencer.adrequests if ad.status == 'completed']
    earningsSplitColours = [random_colour() for _ in earningsSplitLabels]
    earningsSplitColourBorder = [f'rgb({colour[5:-6]})' for colour in earningsSplitColours]

    return render_template(
        'dash/influencer/stats.html',
        adRequestCountLabels=adRequestCountLabels,
        adRequestCountData=adRequestCountData,
        earningsSplitLabels=earningsSplitLabels,
        earningsSplitData=earningsSplitData,
        earningsSplitColours=earningsSplitColours,
        earningsSplitColourBorder=earningsSplitColourBorder
    )