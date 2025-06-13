from . import db
from flask_login import UserMixin
from datetime import datetime

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    username = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    last_accessed = db.Column(db.DateTime, default=datetime.utcnow)

class Area(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), unique=True)

class Location(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    owner_name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), nullable=False)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)

    area = db.relationship('Area', backref=db.backref('locations', lazy=True))


class QuestionForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    cockroaches = db.Column(db.Boolean)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id')) 

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    location = db.relationship('Location', backref=db.backref('forms', lazy=True))
    user = db.relationship('User', backref=db.backref('forms', lazy=True)) 
