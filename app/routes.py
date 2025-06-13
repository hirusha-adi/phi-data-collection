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
            location_id = int(request.form.get('location'))
            kwargs = {
                'premises_registered': int(request.form.get('premises_registered')),
                'certificate_displayed': int(request.form.get('certificate_displayed')),
                'not_convicted': int(request.form.get('not_convicted')),
                'food_not_destroyed': int(request.form.get('food_not_destroyed')),
                'safe_water': int(request.form.get('safe_water')),
                'cleanliness': int(request.form.get('cleanliness')),
                'pests_animals': int(request.form.get('pests_animals')),
                'sound_pollution': int(request.form.get('sound_pollution')),
                'toilets_cleanliness': int(request.form.get('toilets_cleanliness')),
                'medical_certificates': int(request.form.get('medical_certificates')),
                'proper_clothing': int(request.form.get('proper_clothing')),
                'unhygienic_behaviour': int(request.form.get('unhygienic_behaviour')),
                'clean_utensils': int(request.form.get('clean_utensils')),
                'walls_hygienic': int(request.form.get('walls_hygienic')),
                'floor_hygienic': int(request.form.get('floor_hygienic')),
                'ceiling_hygienic': int(request.form.get('ceiling_hygienic')),
                'food_surfaces_clean': int(request.form.get('food_surfaces_clean')),
                'wastewater_disposal': int(request.form.get('wastewater_disposal')),
                'closed_bins': int(request.form.get('closed_bins')),
                'cooked_food_closed': int(request.form.get('cooked_food_closed')),
                'cooked_food_temp': int(request.form.get('cooked_food_temp')),
                'cooked_food_container': int(request.form.get('cooked_food_container')),
                'cooked_food_contam_prevented': int(request.form.get('cooked_food_contam_prevented')),
                'uncooked_food_contam_prevented': int(request.form.get('uncooked_food_contam_prevented')),
                'location_id': location_id,
                'user_id': current_user.id
            }

            form = QuestionForm(**kwargs)
            db.session.add(form)
            db.session.commit()
            flash("Inspection form submitted successfully!", "success")
            return redirect(url_for('main.dashboard'))

        except Exception as e:
            flash("Invalid form input. Please correct and try again.", "error")

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
