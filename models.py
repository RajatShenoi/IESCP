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

class Sponsor(db.Model):
    __tablename__ = 'Sponsor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    budget = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('User.id'))

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

class Campaign(db.Model):
    __tablename__ = 'Campaign'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    description = db.Column(db.String(1000))
    start_date = db.Column(db.DateTime)
    end_date = db.Column(db.DateTime)
    budget = db.Column(db.Integer)
    public = db.Column(db.Boolean)
    goals = db.relationship('CampaignGoal', backref='campaign')

class CampaignGoal(db.Model):
    __tablename__ = 'CampaignGoal'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    campaign_id = db.Column(db.Integer, db.ForeignKey('Campaign.id'))
    goal = db.Column(db.String(100))
    completed = db.Column(db.Boolean)