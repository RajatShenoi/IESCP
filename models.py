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
    sponsor_id = db.Column(db.Integer, db.ForeignKey('Sponsor.id'), nullable=True)
    influencer_id = db.Column(db.Integer, db.ForeignKey('Influencer.id'), nullable=True)
    profile_picture = db.Column(db.String(1000))

class Sponsor(db.Model):
    __tablename__ = 'Sponsor'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_name = db.Column(db.String(100))
    industry = db.Column(db.String(100))
    budget = db.Column(db.Integer)
    user = db.relationship('User', backref='sponsor', uselist=False)

class Influencer(db.Model):
    __tablename__ = 'Influencer'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100))
    category = db.Column(db.String(100))
    followers = db.Column(db.Integer)
    instagram = db.Column(db.String(256))
    youtube = db.Column(db.String(256))
    twitter = db.Column(db.String(256))
    user = db.relationship('User', backref='influencer', uselist=False)