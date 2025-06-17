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
    
    def __repr__(self):
        return f'<Area {self.id} Name:- {self.name}>' 


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
    
    def __repr__(self):
        return f"<Location {self.id} name_of_premise:- {self.name_of_premise} owner_name: {self.owner_name}>"
    
    
class QuestionForm(db.Model):
    # Basic Details
    id = db.Column(db.Integer, primary_key=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # General Details
    # (optional) - set to -1
    is_eligible_register_info = db.Column(db.Boolean, nullable=False)
    premises_registered = db.Column(db.Integer, nullable=False)
    certificate_displayed = db.Column(db.Integer, nullable=False)
    # (required)
    not_convicted = db.Column(db.Integer, nullable=False)
    food_not_destroyed = db.Column(db.Integer, nullable=False)
    sum_general_details = db.Column(db.Integer, nullable=False)

    # Building Details
    safe_water = db.Column(db.Integer, nullable=False)
    cleanliness = db.Column(db.Integer, nullable=False)
    pests_animals = db.Column(db.Integer, nullable=False)
    sound_pollution = db.Column(db.Integer, nullable=False)
    toilets_cleanliness = db.Column(db.Integer, nullable=False)
    sum_building_details = db.Column(db.Integer, nullable=False)

    # Food Handler
    # (optional) - set to -1
    is_eligible_food_handler_info = db.Column(db.Boolean, nullable=False)
    medical_certificates = db.Column(db.Integer, nullable=False)
    proper_clothing = db.Column(db.Integer, nullable=False)
    unhygienic_behaviour = db.Column(db.Integer, nullable=False)
    clean_utensils = db.Column(db.Integer, nullable=False)
    sum_food_handler = db.Column(db.Integer, nullable=False)

    # Processing and Serving
    # (optional) - set to -1
    is_eligible_processing_info = db.Column(db.Boolean, nullable=False)
    walls_hygienic = db.Column(db.Integer, nullable=False)
    floor_hygienic = db.Column(db.Integer, nullable=False)
    ceiling_hygienic = db.Column(db.Integer, nullable=False)
    food_surfaces_clean = db.Column(db.Integer, nullable=False)
    wastewater_disposal = db.Column(db.Integer, nullable=False)
    closed_bins = db.Column(db.Integer, nullable=False)
    sum_processing_and_serving = db.Column(db.Integer, nullable=False)

    # Food Storage
    # (optional) - set to -1
    is_eligible_food_storage_info = db.Column(db.Boolean, nullable=False)
    cooked_food_closed = db.Column(db.Integer, nullable=False)
    cooked_food_temp = db.Column(db.Integer, nullable=False)
    cooked_food_container = db.Column(db.Integer, nullable=False)
    cooked_food_contam_prevented = db.Column(db.Integer, nullable=False)
    # (required)
    uncooked_food_contam_prevented = db.Column(db.Integer, nullable=False)
    sum_food_storage = db.Column(db.Integer, nullable=False)
    
    # Finals
    sum_all = db.Column(db.Integer, nullable=False)
    grade = db.Column(db.String(1), nullable=False)

    # Inspection Record - Location relationship
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), nullable=False)
    location = db.relationship('Location', backref=db.backref('forms', lazy=True))

    # Inspection Record - User relationship (see who created it)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    user = db.relationship('User', backref=db.backref('forms', lazy=True))

    def __repr__(self):
        return f"<QuestionForm {self.id} created_at: {self.created_at} location_name:- {self.location.name_of_premise}>"
