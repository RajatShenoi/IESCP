import os
import uuid

from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, url_for, current_app
from flask_login import current_user
from sqlalchemy import or_

from . import db
from forms import AdOfferManageForm, EditCampaignForm, EditSponsorForm, NewAdRequestForm, NewCampaignForm, SearchForm
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
            goal=form.goal.data,
            niche=form.niche.data,
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

@sponsor_bp.route('/sponsor/campaigns/<int:id>/manage/<int:ad_id>/decline', methods=['GET'])
@sponsor_required
def declineAdOffer(id, ad_id):
    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
    campaign = Campaign.query.filter_by(id=id, sponsor_id=sponsor.id).first()
    ad = AdRequest.query.filter_by(id=ad_id, campaign_id=campaign.id).first()

    if campaign is None or ad is None or sponsor is None or ad.status != 'pending':
        return redirect(url_for('sponsor.campaigns'))
    
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
    return redirect(url_for('sponsor.campaign', id=id))

@sponsor_bp.route('/sponsor/campaigns/<int:id>/manage/<int:ad_id>/accept', methods=['GET'])
@sponsor_required
def acceptAdOffer(id, ad_id):
    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
    campaign = Campaign.query.filter_by(id=id, sponsor_id=sponsor.id).first()
    ad = AdRequest.query.filter_by(id=ad_id, campaign_id=campaign.id).first()

    if campaign is None or ad is None or sponsor is None or ad.status != 'pending':
        return redirect(url_for('sponsor.campaigns'))
    
    if ad.current_quote.user_id == current_user.id:
        flash('You cannot accept this offer as you\'ve made the latest negotiation. Kindly wait for the response.', 'danger')
        return redirect(url_for('sponsor.campaign', id=id))
    
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
    return redirect(url_for('sponsor.campaign', id=id))

@sponsor_bp.route('/sponsor/campaigns/<int:id>/manage/<int:ad_id>/negotiate', methods=['POST'])
@sponsor_required
def negotiateAdOffer(id, ad_id):
    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
    campaign = Campaign.query.filter_by(id=id, sponsor_id=sponsor.id).first()
    ad = AdRequest.query.filter_by(id=ad_id, campaign_id=campaign.id).first()

    if campaign is None or ad is None or sponsor is None or ad.status != 'pending':
        return redirect(url_for('sponsor.campaigns'))
    
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
    return redirect(url_for('sponsor.campaign', id=id))

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
    adofferform = AdOfferManageForm()
    if form.validate_on_submit():
        campaign.name = form.name.data
        campaign.description = form.description.data
        campaign.start_date = form.start_date.data
        campaign.end_date = form.end_date.data
        campaign.budget = form.budget.data
        campaign.niche = form.niche.data
        campaign.goal = form.goal.data
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
        addofferform=adofferform,
    )

@sponsor_bp.route('/sponsor/campaigns/<int:id>/delete', methods=['GET'])
@sponsor_required
def deleteCampaign(id):
    sponsor = Sponsor.query.filter_by(user_id=current_user.id).first()
    campaign = Campaign.query.filter_by(id=id, sponsor_id=sponsor.id).first()

    if campaign is None or len(campaign.adrequests) > 0:
        return redirect(url_for('sponsor.campaigns'))
    
    os.remove(os.path.join(current_app.instance_path, 'media', 'campaign_images', campaign.image))
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully.', 'success')
    return redirect(url_for('sponsor.campaigns'))

@sponsor_bp.route('/sponsor/find', methods=['GET', 'POST'])
@sponsor_required
def findInfluencers():
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
    return render_template('dash/sponsor/find.html', influencers=influencers, form=form)

@sponsor_bp.route('/sponsor/find/<username>', methods=['GET'])
@sponsor_required
def influencer(username):
    user = User.query.filter_by(username=username).first()
    influencer = Influencer.query.filter_by(user=user).first()
    if influencer is None:
        return redirect(url_for('sponsor.findInfluencers'))
    return render_template('dash/sponsor/influencer.html', influencer=influencer)

@sponsor_bp.route('/sponsor/editProfile', methods=['GET', 'POST'])
@sponsor_required
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
        return redirect(url_for('sponsor.editProfile'))
    return render_template('dash/sponsor/edit_profile.html', form=form)
