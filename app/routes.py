from flask import Blueprint, render_template, redirect, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from .models import User, Area, Location, QuestionForm
from .forms import LoginForm, QuestionEntryForm

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@main.route('/', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            user.last_accessed = db.func.now()
            db.session.commit()
            return redirect(url_for('main.dashboard'))

        flash('Invalid credentials', 'error')

    if current_user.is_authenticated:
        return redirect(url_for('main.dashboard'))
    
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    locations = Location.query.limit(10).all()
    forms = QuestionForm.query.order_by(QuestionForm.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', locations=locations, forms=forms)


@main.route('/add_form', methods=['GET', 'POST'])
@login_required
def add_form():
    locations = Location.query.all()

    if request.method == 'POST':
        try:
            form_data = request.form

            # Get checkbox flags
            is_eligible_food_handler_info = form_data.get('is_eligible_food_handler_info') == 'on'
            is_eligible_processing_info = form_data.get('is_eligible_processing_info') == 'on'
            is_eligible_food_storage_info = form_data.get('is_eligible_food_storage_info') == 'on'

            # Create a new form instance
            form = QuestionForm()

            # Relationships
            form.location_id = int(form_data.get('location'))
            form.user_id = current_user.id

            # General
            form.premises_registered = int(form_data.get('premises_registered'))
            form.certificate_displayed = int(form_data.get('certificate_displayed'))
            form.not_convicted = int(form_data.get('not_convicted'))
            form.food_not_destroyed = int(form_data.get('food_not_destroyed'))

            # Building
            form.safe_water = int(form_data.get('safe_water'))
            form.cleanliness = int(form_data.get('cleanliness'))
            form.pests_animals = int(form_data.get('pests_animals'))
            form.sound_pollution = int(form_data.get('sound_pollution'))
            form.toilets_cleanliness = int(form_data.get('toilets_cleanliness'))

            # Food Handler
            if is_eligible_food_handler_info:
                form.medical_certificates = -1
                form.proper_clothing = -1
                form.unhygienic_behaviour = -1
                form.clean_utensils = -1
            else:
                form.medical_certificates = int(form_data.get('medical_certificates'))
                form.proper_clothing = int(form_data.get('proper_clothing'))
                form.unhygienic_behaviour = int(form_data.get('unhygienic_behaviour'))
                form.clean_utensils = int(form_data.get('clean_utensils'))

            # Processing and Serving
            if is_eligible_processing_info:
                form.walls_hygienic = -1
                form.floor_hygienic = -1
                form.ceiling_hygienic = -1
                form.food_surfaces_clean = -1
                form.wastewater_disposal = -1
                form.closed_bins = -1
            else:
                form.walls_hygienic = int(form_data.get('walls_hygienic'))
                form.floor_hygienic = int(form_data.get('floor_hygienic'))
                form.ceiling_hygienic = int(form_data.get('ceiling_hygienic'))
                form.food_surfaces_clean = int(form_data.get('food_surfaces_clean'))
                form.wastewater_disposal = int(form_data.get('wastewater_disposal'))
                form.closed_bins = int(form_data.get('closed_bins'))

            # Food Storage
            if is_eligible_food_storage_info:
                form.cooked_food_closed = -1
                form.cooked_food_temp = -1
                form.cooked_food_container = -1
                form.cooked_food_contam_prevented = -1
            else:
                form.cooked_food_closed = int(form_data.get('cooked_food_closed'))
                form.cooked_food_temp = int(form_data.get('cooked_food_temp'))
                form.cooked_food_container = int(form_data.get('cooked_food_container'))
                form.cooked_food_contam_prevented = int(form_data.get('cooked_food_contam_prevented'))

            # This is always required and must be submitted normally
            form.uncooked_food_contam_prevented = int(form_data.get('uncooked_food_contam_prevented'))

            # Save to DB
            db.session.add(form)
            db.session.commit()

            flash("Inspection form saved successfully!", "success")
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            db.session.rollback()
            flash(f"Error occurred: {str(e)}", "danger")

    return render_template('add_form.html', locations=locations)


@main.route('/forms/<int:location_id>')
@login_required
def view_forms(location_id):
    forms = QuestionForm.query.filter_by(location_id=location_id).all()
    location = Location.query.get_or_404(location_id)
    return render_template('view_forms.html', forms=forms, location=location)

@main.route('/edit_form/<int:form_id>', methods=['GET', 'POST'])
@login_required
def edit_form(form_id):
    form_record = QuestionForm.query.get_or_404(form_id)
    if form_record.user.id != current_user.id:
        flash("You can only edit your own entries.")
        return redirect(url_for('main.dashboard'))

    locations = Location.query.all()

    if request.method == 'POST':
        try:
            location_id = int(request.form.get('location'))
            cockroaches_value = request.form.get('cockroaches')  # 'True' or 'False'
            cockroaches = cockroaches_value == 'True'

            form_record.location_id = location_id
            form_record.cockroaches = cockroaches
            db.session.commit()
            return redirect(url_for('main.dashboard'))
        except (TypeError, ValueError):
            flash("Invalid input. Please try again.", "error")

    return render_template('edit_form.html', form_record=form_record, locations=locations)



@main.route('/delete_form/<int:form_id>')
@login_required
def delete_form(form_id):
    form_record = QuestionForm.query.get_or_404(form_id)
    if form_record.user.id != current_user.id:
        flash("Unauthorized deletion")
        return redirect(url_for('main.dashboard'))
    db.session.delete(form_record)
    db.session.commit()
    return redirect(url_for('main.dashboard'))

@main.route('/add-location', methods=['GET', 'POST'])
@login_required
def add_location():
    areas = Area.query.all()

    if request.method == 'POST':
        area_id = request.form.get('area_id', type=int)
        name_of_premise = request.form.get('name_of_premise', '').strip()
        address_of_premise = request.form.get('address_of_premise', '').strip()
        gs_area = request.form.get('gs_area', '').strip()
        category_of_premise = request.form.get('category_of_premise', '').strip()
        
        owner_name = request.form.get('owner_name', '').strip()
        owner_nic = request.form.get('owner_nic', '').strip()
        owner_address = request.form.get('owner_address', '').strip()
        
        contact_number = request.form.get('contact_number', '').strip()
        owner_contact_number = request.form.get('owner_contact_number', '').strip()

        print(all([
            area_id, name_of_premise, address_of_premise, gs_area, category_of_premise,
            owner_name, owner_nic, owner_address, contact_number, owner_contact_number
        ]))
        
        if all([
            area_id, name_of_premise, address_of_premise, gs_area, category_of_premise,
            owner_name, owner_nic, owner_address, contact_number, owner_contact_number
        ]):
            new_location = Location(
                area_id=area_id,
                name_of_premise=name_of_premise,
                address_of_premise=address_of_premise,
                gs_area=gs_area,
                category_of_premise=category_of_premise,
                owner_name=owner_name,
                owner_nic=owner_nic,
                owner_address=owner_address,
                contact_number=contact_number,
                owner_contact_number=owner_contact_number
            )
            db.session.add(new_location)
            db.session.commit()
            flash("Location added successfully!", "success")
            return redirect(url_for('main.dashboard'))
        else:
            flash("Please fill in all required fields.", "error")

    return render_template('add_location.html', areas=areas)

@main.route('/locations')
def view_locations():
    search = request.args.get('search', '').strip().lower()
    area_id_raw = request.args.get('area_id', '').strip()
    area_id = int(area_id_raw) if area_id_raw.isdigit() else None
    category = request.args.get('category', '').strip().lower()

    query = Location.query

    if search:
        search_term = f"%{search}%"
        query = query.filter(
            (Location.name_of_premise.ilike(search_term)) |
            (Location.address_of_premise.ilike(search_term)) |
            (Location.owner_name.ilike(search_term)) |
            (Location.owner_nic.ilike(search_term)) |
            (Location.contact_number.ilike(search_term)) |
            (Location.gs_area.ilike(search_term))
        )

    if area_id:
        query = query.filter_by(area_id=area_id)

    if category:
        query = query.filter(Location.category_of_premise.ilike(f"%{category}%"))

    locations = query.order_by(Location.id.desc()).all()
    areas = Area.query.all()

    return render_template('locations.html', locations=locations, areas=areas, selected_area_id=area_id)



