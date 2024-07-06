from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy

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
    profile_picture = db.Column(db.String(1000))

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
    category = db.Column(db.String(100))
    niche = db.Column(db.String(100))
    followers = db.Column(db.Integer)
    instagram = db.Column(db.String(256))
    youtube = db.Column(db.String(256))
    twitter = db.Column(db.String(256))
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))
    adrequest_id = db.Column(db.Integer, db.ForeignKey('AdRequest.id'))

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
    goals = db.relationship('CampaignGoal', backref='campaign')
    sponsor_id = db.Column(db.Integer, db.ForeignKey('Sponsor.id'))

    def __repr__(self):
        return f'<Campaign {self.name}>'

class CampaignGoal(db.Model):
    __tablename__ = 'CampaignGoal'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaign.id'))
    goal = db.Column(db.String(100))
    completed = db.Column(db.Boolean)

class AdRequest(db.Model):
    __tablename__ = 'AdRequest'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaign.id'))
    requirements = db.Column(db.String(2000))
    influencer = db.relationship('Influencer', backref='adrequest', uselist=False)
    payment_amount = db.Column(db.Integer)
    status = db.Column(db.String(20))
