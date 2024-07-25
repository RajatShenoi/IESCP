from datetime import datetime
from flask import Blueprint, flash, redirect, render_template, url_for
from flask_login import current_user

from . import db
from forms import AdOfferManageForm
from models import AdRequest, Influencer, Quote, User
from utils.decorators import influencer_required

influencer_bp = Blueprint('influencer', __name__)

@influencer_bp.route('/influencer', methods=['GET'])
@influencer_required
def dashboard():
    user = User.query.filter_by(id=current_user.id).first()
    influencer = Influencer.query.filter_by(user_id=user.id).first()

    addofferform = AdOfferManageForm()

    return render_template('dash/influencer/home.html', influencer=influencer, addofferform=addofferform)

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
    return redirect(url_for('influencer.dashboard'))


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