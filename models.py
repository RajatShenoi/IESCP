from datetime import datetime
from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.ext.hybrid import hybrid_property

db = SQLAlchemy()

class User(UserMixin, db.Model):
    __tablename__ = 'User'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(100), unique=True)
    email = db.Column(db.String(100), unique=True)
    password = db.Column(db.String(100))
    user_type = db.Column(db.String(100))
    sponsor = db.relationship('Sponsor', backref='user', uselist=False)
    influencer = db.relationship('Influencer', backref='user', uselist=False)
    quotes = db.relationship('Quote', backref='user')
    profile_picture = db.Column(db.String(1000))
    flagged = db.Column(db.Boolean, default=False)

    def __repr__(self):
        return f'<User {self.username}>'

class Sponsor(db.Model):
    __tablename__ = 'Sponsor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    budget = db.Column(db.Integer)
    campaigns = db.relationship('Campaign', backref='sponsor')
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    
    def __repr__(self):
        return f'<Sponsor {self.company_name}>'

class Influencer(db.Model):
    __tablename__ = 'Influencer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    about = db.Column(db.String(2000))
    category = db.Column(db.String(100))
    niche = db.Column(db.String(100))
    followers = db.Column(db.Integer)
    instagram = db.Column(db.String(100))
    youtube = db.Column(db.String(100))
    twitter = db.Column(db.String(100))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    adrequests = db.relationship('AdRequest', backref='influencer')

    def __repr__(self):
        return f'<Influencer {self.name}>'

class Campaign(db.Model):
    __tablename__ = 'Campaign'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(2000))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    budget = db.Column(db.Integer)
    public = db.Column(db.Boolean)
    adrequests = db.relationship('AdRequest', backref='campaign')
    goal = db.Column(db.Integer)
    niche = db.Column(db.String(20))
    tnc = db.Column(db.String(20000))
    image = db.Column(db.String(1000))
    sponsor_id = db.Column(db.Integer, db.ForeignKey('Sponsor.id'))
    flagged = db.Column(db.Boolean, default=False)

    @hybrid_property
    def current_spends(self):
        return sum([ad.current_quote.amount for ad in self.adrequests if ad.status in ['completed', 'ongoing']])
    
    @hybrid_property
    def current_reach(self):
        return sum([ad.influencer.followers for ad in self.adrequests if ad.status in ['completed', 'ongoing']])

    def __repr__(self):
        return f'<Campaign {self.name}>'

class AdRequest(db.Model):
    __tablename__ = 'AdRequest'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaign.id'))
    requirements = db.Column(db.String(2000))
    influencer_id = db.Column(db.Integer, db.ForeignKey('Influencer.id'))
    quotes = db.relationship('Quote', backref='adrequest')
    status = db.Column(db.String(20))

    @hybrid_property
    def current_quote(self):
        return Quote.query.filter_by(adrequest_id=self.id).order_by(Quote.created_at.desc()).first()
    
class Quote(db.Model):
    __tablename__ = 'Quote'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    amount = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    message = db.Column(db.String(1000), nullable=True)
    adrequest_id = db.Column(db.Integer, db.ForeignKey('AdRequest.id'))
    created_at = db.Column(db.DateTime, default=datetime.now(), nullable=False)

    def __repr__(self):
        return f'<Quote {self.amount}>'