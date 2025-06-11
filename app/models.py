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
    name = db.Column(db.String(100))
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    owner = db.Column(db.String(100))
    contact = db.Column(db.String(20))
    area = db.relationship('Area', backref=db.backref('locations', lazy=True))

class QuestionForm(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    cockroaches = db.Column(db.Boolean)
    added_by = db.Column(db.String(50))
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
