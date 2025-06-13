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

    # PHI Area - Location relationship
    area_id = db.Column(db.Integer, db.ForeignKey('area.id'), nullable=False)
    area = db.relationship('Area', backref=db.backref('locations', lazy=True))

    # Basic
    name_of_premise = db.Column(db.String(200), nullable=False)
    address_of_premise = db.Column(db.String(300), nullable=False)
    gs_area = db.Column(db.String(100), nullable=False)
    category_of_premise = db.Column(db.String(100), nullable=False)
    
    # Owner's Info
    owner_name = db.Column(db.String(100), nullable=False)
    owner_nic = db.Column(db.String(20), nullable=False)
    owner_address = db.Column(db.String(300), nullable=False)
    
    # Contact Number
    contact_number = db.Column(db.String(20), nullable=False)  # Contact of premise
    owner_contact_number = db.Column(db.String(20), nullable=False)  # Contact of owner
    
    
class QuestionForm(db.Model):
    # Basic Details
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # General Details
    premises_registered = db.Column(db.Integer, nullable=False)
    certificate_displayed = db.Column(db.Integer, nullable=False)
    not_convicted = db.Column(db.Integer, nullable=False)
    food_not_destroyed = db.Column(db.Integer, nullable=False)

    # Building Details
    safe_water = db.Column(db.Integer, nullable=False)
    cleanliness = db.Column(db.Integer, nullable=False)
    pests_animals = db.Column(db.Integer, nullable=False)
    sound_pollution = db.Column(db.Integer, nullable=False)
    toilets_cleanliness = db.Column(db.Integer, nullable=False)

    # Food Handler
    medical_certificates = db.Column(db.Integer, nullable=False)
    proper_clothing = db.Column(db.Integer, nullable=False)
    unhygienic_behaviour = db.Column(db.Integer, nullable=False)
    clean_utensils = db.Column(db.Integer, nullable=False)

    # Processing and Serving
    walls_hygienic = db.Column(db.Integer, nullable=False)
    floor_hygienic = db.Column(db.Integer, nullable=False)
    ceiling_hygienic = db.Column(db.Integer, nullable=False)
    food_surfaces_clean = db.Column(db.Integer, nullable=False)
    wastewater_disposal = db.Column(db.Integer, nullable=False)
    closed_bins = db.Column(db.Integer, nullable=False)

    # Food Storage
    cooked_food_closed = db.Column(db.Integer, nullable=False)
    cooked_food_temp = db.Column(db.Integer, nullable=False)
    cooked_food_container = db.Column(db.Integer, nullable=False)
    cooked_food_contam_prevented = db.Column(db.Integer, nullable=False)
    uncooked_food_contam_prevented = db.Column(db.Integer, nullable=False)

    # Inspection Record - Location relationship
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    location = db.relationship('Location', backref=db.backref('forms', lazy=True))

    # Inspection Record - User relationship (see who created it)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('forms', lazy=True))
