from flask import Blueprint, render_template, redirect, send_file, url_for, request, flash
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from . import db, login_manager
from .models import User, Area, Location, QuestionForm
from .forms import LoginForm, QuestionEntryForm
from PyPDFForm import PdfWrapper
import os
import tempfile
from flask import after_this_request
from datetime import datetime
from PyPDF2 import PdfReader, PdfWriter

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
    forms = QuestionForm.query.order_by(
        QuestionForm.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', locations=locations, forms=forms)


@main.route('/add_form', methods=['GET', 'POST'])
@login_required
def add_form():
    locations = Location.query.all()

    if request.method == 'POST':
        form_data = request.form

        # Get checkbox flags
        is_eligible_register_info = form_data.get(
            'is_eligible_register_info') == 'on'
        is_eligible_food_handler_info = form_data.get(
            'is_eligible_food_handler_info') == 'on'
        is_eligible_processing_info = form_data.get(
            'is_eligible_processing_info') == 'on'
        is_eligible_food_storage_info = form_data.get(
            'is_eligible_food_storage_info') == 'on'

        # Create a new form instance
        form = QuestionForm()

        # Relationships
        form.location_id = int(form_data.get('location'))
        form.user_id = current_user.id

        # General
        form.is_eligible_register_info = is_eligible_register_info
        if is_eligible_register_info:
            form.premises_registered = -1
            form.certificate_displayed = -1
            form.not_convicted = int(form_data.get('not_convicted'))
            form.food_not_destroyed = int(
                form_data.get('food_not_destroyed'))
            form.sum_general_details = 10 + form.not_convicted + form.food_not_destroyed
        else:
            form.premises_registered = int(
                form_data.get('premises_registered'))
            form.certificate_displayed = int(
                form_data.get('certificate_displayed'))
            form.not_convicted = int(form_data.get('not_convicted'))
            form.food_not_destroyed = int(
                form_data.get('food_not_destroyed'))
            form.sum_general_details = form.premises_registered + \
                form.certificate_displayed + form.not_convicted + form.food_not_destroyed

        # Building
        form.safe_water = int(form_data.get('safe_water'))
        form.cleanliness = int(form_data.get('cleanliness'))
        form.pests_animals = int(form_data.get('pests_animals'))
        form.sound_pollution = int(form_data.get('sound_pollution'))
        form.toilets_cleanliness = int(
            form_data.get('toilets_cleanliness'))
        form.sum_building_details = form.safe_water + form.cleanliness + \
            form.pests_animals + form.sound_pollution + form.toilets_cleanliness

        # Food Handler
        form.is_eligible_food_handler_info = is_eligible_food_handler_info
        if is_eligible_food_handler_info:
            form.medical_certificates = -1
            form.proper_clothing = -1
            form.unhygienic_behaviour = -1
            form.clean_utensils = -1
            form.sum_food_handler = 20
        else:
            form.medical_certificates = int(
                form_data.get('medical_certificates'))
            form.proper_clothing = int(form_data.get('proper_clothing'))
            form.unhygienic_behaviour = int(
                form_data.get('unhygienic_behaviour'))
            form.clean_utensils = int(form_data.get('clean_utensils'))
            form.sum_food_handler = form.medical_certificates + \
                form.proper_clothing + form.unhygienic_behaviour + form.clean_utensils

        # Processing and Serving
        form.is_eligible_processing_info = is_eligible_processing_info
        if is_eligible_processing_info:
            form.walls_hygienic = -1
            form.floor_hygienic = -1
            form.ceiling_hygienic = -1
            form.food_surfaces_clean = -1
            form.wastewater_disposal = -1
            form.closed_bins = -1
            form.sum_processing_and_serving = 20
        else:
            form.walls_hygienic = int(form_data.get('walls_hygienic'))
            form.floor_hygienic = int(form_data.get('floor_hygienic'))
            form.ceiling_hygienic = int(form_data.get('ceiling_hygienic'))
            form.food_surfaces_clean = int(
                form_data.get('food_surfaces_clean'))
            form.wastewater_disposal = int(
                form_data.get('wastewater_disposal'))
            form.closed_bins = int(form_data.get('closed_bins'))
            form.sum_processing_and_serving = form.walls_hygienic + form.floor_hygienic + \
                form.ceiling_hygienic + form.food_surfaces_clean + \
                form.wastewater_disposal + form.closed_bins

        # Food Storage
        form.is_eligible_food_storage_info = is_eligible_food_storage_info
        if is_eligible_food_storage_info:
            form.cooked_food_closed = -1
            form.cooked_food_temp = -1
            form.cooked_food_container = -1
            form.cooked_food_contam_prevented = -1
            form.uncooked_food_contam_prevented = int(
                form_data.get('uncooked_food_contam_prevented'))
            form.sum_food_storage = 16 + form.uncooked_food_contam_prevented
        else:
            form.cooked_food_closed = int(
                form_data.get('cooked_food_closed'))
            form.cooked_food_temp = int(form_data.get('cooked_food_temp'))
            form.cooked_food_container = int(
                form_data.get('cooked_food_container'))
            form.cooked_food_contam_prevented = int(
                form_data.get('cooked_food_contam_prevented'))
            form.uncooked_food_contam_prevented = int(
                form_data.get('uncooked_food_contam_prevented'))
            form.sum_food_storage = form.cooked_food_closed + form.cooked_food_temp + \
                form.cooked_food_container + form.cooked_food_contam_prevented + \
                form.uncooked_food_contam_prevented

        form.sum_all = form.sum_general_details + form.sum_building_details + \
            form.sum_food_handler + form.sum_processing_and_serving + form.sum_food_storage

        # Grade
        if (form.sum_all >= 75) and (form.sum_all <= 100):
            form.grade = 'A'
        elif (form.sum_all >= 50) and (form.sum_all < 75):
            form.grade = 'B'
        elif (form.sum_all >= 25) and (form.sum_all < 50):
            form.grade = 'C'
        else:
            form.grade = 'D'

        db.session.add(form)
        db.session.commit()

        flash("Inspection form saved successfully!", "success")
        return redirect(url_for('main.dashboard'))

    return render_template('add_form.html', locations=locations)


@main.route('/forms/<int:location_id>')
@login_required
def view_forms(location_id):
    forms = QuestionForm.query.filter_by(location_id=location_id).order_by(
        QuestionForm.created_at.desc()).all()
    location = Location.query.get_or_404(location_id)
    return render_template('view_forms.html', forms=forms, location=location)


@main.route('/edit_form/<int:form_id>', methods=['GET', 'POST'])
@login_required
def edit_form(form_id):
    form = QuestionForm.query.get_or_404(form_id)
    locations = Location.query.all()

    if request.method == 'POST':
        form_data = request.form

        # Get checkbox flags
        form.is_eligible_register_info = form_data.get(
            'is_eligible_register_info') == 'on'
        form.is_eligible_food_handler_info = form_data.get(
            'is_eligible_food_handler_info') == 'on'
        form.is_eligible_processing_info = form_data.get(
            'is_eligible_processing_info') == 'on'
        form.is_eligible_food_storage_info = form_data.get(
            'is_eligible_food_storage_info') == 'on'

        # General
        if form.is_eligible_register_info:
            form.premises_registered = -1
            form.certificate_displayed = -1
            form.not_convicted = int(form_data.get('not_convicted'))
            form.food_not_destroyed = int(form_data.get('food_not_destroyed'))
            form.sum_general_details = 10 + form.not_convicted + form.food_not_destroyed
        else:
            form.premises_registered = int(
                form_data.get('premises_registered'))
            form.certificate_displayed = int(
                form_data.get('certificate_displayed'))
            form.not_convicted = int(form_data.get('not_convicted'))
            form.food_not_destroyed = int(form_data.get('food_not_destroyed'))
            form.sum_general_details = (
                form.premises_registered + form.certificate_displayed +
                form.not_convicted + form.food_not_destroyed
            )

        # Building
        form.safe_water = int(form_data.get('safe_water'))
        form.cleanliness = int(form_data.get('cleanliness'))
        form.pests_animals = int(form_data.get('pests_animals'))
        form.sound_pollution = int(form_data.get('sound_pollution'))
        form.toilets_cleanliness = int(form_data.get('toilets_cleanliness'))
        form.sum_building_details = (
            form.safe_water + form.cleanliness + form.pests_animals +
            form.sound_pollution + form.toilets_cleanliness
        )

        # Food Handler
        if form.is_eligible_food_handler_info:
            form.medical_certificates = -1
            form.proper_clothing = -1
            form.unhygienic_behaviour = -1
            form.clean_utensils = -1
            form.sum_food_handler = 20
        else:
            form.medical_certificates = int(
                form_data.get('medical_certificates'))
            form.proper_clothing = int(form_data.get('proper_clothing'))
            form.unhygienic_behaviour = int(
                form_data.get('unhygienic_behaviour'))
            form.clean_utensils = int(form_data.get('clean_utensils'))
            form.sum_food_handler = (
                form.medical_certificates + form.proper_clothing +
                form.unhygienic_behaviour + form.clean_utensils
            )

        # Processing and Serving
        if form.is_eligible_processing_info:
            form.walls_hygienic = -1
            form.floor_hygienic = -1
            form.ceiling_hygienic = -1
            form.food_surfaces_clean = -1
            form.wastewater_disposal = -1
            form.closed_bins = -1
            form.sum_processing_and_serving = 20
        else:
            form.walls_hygienic = int(form_data.get('walls_hygienic'))
            form.floor_hygienic = int(form_data.get('floor_hygienic'))
            form.ceiling_hygienic = int(form_data.get('ceiling_hygienic'))
            form.food_surfaces_clean = int(
                form_data.get('food_surfaces_clean'))
            form.wastewater_disposal = int(
                form_data.get('wastewater_disposal'))
            form.closed_bins = int(form_data.get('closed_bins'))
            form.sum_processing_and_serving = (
                form.walls_hygienic + form.floor_hygienic +
                form.ceiling_hygienic + form.food_surfaces_clean +
                form.wastewater_disposal + form.closed_bins
            )

        # Food Storage
        if form.is_eligible_food_storage_info:
            form.cooked_food_closed = -1
            form.cooked_food_temp = -1
            form.cooked_food_container = -1
            form.cooked_food_contam_prevented = -1
            form.uncooked_food_contam_prevented = int(
                form_data.get('uncooked_food_contam_prevented'))
            form.sum_food_storage = 16 + form.uncooked_food_contam_prevented
        else:
            form.cooked_food_closed = int(form_data.get('cooked_food_closed'))
            form.cooked_food_temp = int(form_data.get('cooked_food_temp'))
            form.cooked_food_container = int(
                form_data.get('cooked_food_container'))
            form.cooked_food_contam_prevented = int(
                form_data.get('cooked_food_contam_prevented'))
            form.uncooked_food_contam_prevented = int(
                form_data.get('uncooked_food_contam_prevented'))
            form.sum_food_storage = (
                form.cooked_food_closed + form.cooked_food_temp + form.cooked_food_container +
                form.cooked_food_contam_prevented + form.uncooked_food_contam_prevented
            )

        # Final Total
        form.sum_all = (
            form.sum_general_details + form.sum_building_details +
            form.sum_food_handler + form.sum_processing_and_serving +
            form.sum_food_storage
        )

        # Grade
        if (form.sum_all >= 75) and (form.sum_all <= 100):
            form.grade = 'A'
        elif (form.sum_all >= 50) and (form.sum_all < 75):
            form.grade = 'B'
        elif (form.sum_all >= 25) and (form.sum_all < 50):
            form.grade = 'C'
        else:
            form.grade = 'D'

        db.session.commit()

        return redirect(url_for('main.dashboard'))

    return render_template("edit_form.html", form=form, locations=locations, getattr=getattr)


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
        category_of_premise = request.form.get(
            'category_of_premise', '').strip()

        owner_name = request.form.get('owner_name', '').strip()
        owner_nic = request.form.get('owner_nic', '').strip()
        owner_address = request.form.get('owner_address', '').strip()

        contact_number = request.form.get('contact_number', '').strip()
        owner_contact_number = request.form.get(
            'owner_contact_number', '').strip()

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

@main.route('/edit-location/<int:location_id>', methods=['GET', 'POST'])
@login_required
def edit_location(location_id):
    location = Location.query.get_or_404(location_id)
    areas = Area.query.all()

    if request.method == 'POST':
        location.area_id = request.form.get('area_id', type=int)
        location.name_of_premise = request.form.get('name_of_premise', '').strip()
        location.address_of_premise = request.form.get('address_of_premise', '').strip()
        location.gs_area = request.form.get('gs_area', '').strip()
        location.category_of_premise = request.form.get('category_of_premise', '').strip()

        location.owner_name = request.form.get('owner_name', '').strip()
        location.owner_nic = request.form.get('owner_nic', '').strip()
        location.owner_address = request.form.get('owner_address', '').strip()

        location.contact_number = request.form.get('contact_number', '').strip()
        location.owner_contact_number = request.form.get('owner_contact_number', '').strip()

        # TODO: think about this later
        # maybe remove it... huh
        if all([
            location.area_id, location.name_of_premise, location.address_of_premise,
            location.gs_area, location.category_of_premise, location.owner_name,
            location.owner_nic, location.owner_address, location.contact_number,
            location.owner_contact_number
        ]):
            try:
                db.session.commit()
                flash("Location updated successfully!", "success")
                return redirect(url_for('main.dashboard'))
            except Exception as e:
                db.session.rollback()
                flash(f"An error occurred: {str(e)}", "danger")
        else:
            flash("Please fill in all required fields.", "error")

    return render_template('edit_location.html', location=location, areas=areas)


@main.route('/locations')
@login_required
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
        query = query.filter(
            Location.category_of_premise.ilike(f"%{category}%"))

    locations = query.order_by(Location.id.asc()).all()
    areas = Area.query.all()

    return render_template('locations.html', locations=locations, areas=areas, selected_area_id=area_id)


@main.route("/gen_pdf")
@login_required
def gen_pdf():
    locations = Location.query.all()
    return render_template('gen_pdf.html', locations=locations)


@main.route('/pdf')
@login_required
def generate_pdf():
    qry_id = request.args.get('id', '').strip().lower()
    qry_count = request.args.get('count', '').strip().lower()
    qry_fill_location = request.args.get('fill_location', '').strip() == "1"

    if qry_count:
        try:
            if qry_count == 'all':
                rec_count = 6
            else:
                rec_count = int(qry_count)
        except:
            rec_count = 6
    else:
        rec_count = 6

    data = {}

    res_location = Location.query.get_or_404(qry_id)
    res_forms = QuestionForm.query.filter_by(location_id=qry_id).order_by(
        QuestionForm.created_at.asc()).limit(rec_count).all()
    print(rec_count, res_forms)

    if not res_forms:
        print("Form not found")

    if qry_fill_location:
        data['name_of_premise'] = res_location.name_of_premise
        data['address_of_premise'] = res_location.address_of_premise
        data['gs_area'] = res_location.gs_area
        data['category_of_premise'] = res_location.category_of_premise
        data['owner_name'] = res_location.owner_name
        data['owner_nic'] = res_location.owner_nic
        data['owner_address'] = res_location.owner_address
        data['contact_number'] = res_location.contact_number
        data['owner_contact_number'] = res_location.owner_contact_number

    # Fill all columns in pdf
    for row_num, res_form in enumerate(res_forms, start=1):
        # Date
        data[f'date{row_num}'] = res_form.created_at.strftime('%d/%m')

        # General Details
        if not res_form.is_eligible_register_info:
            data[f'd{row_num}_q1_1'] = res_form.premises_registered
            data[f'd{row_num}_q1_2'] = res_form.certificate_displayed
        else:
            data[f'd{row_num}_q1_s1'] = 10
        data[f'd{row_num}_q1_3'] = res_form.not_convicted
        data[f'd{row_num}_q1_4'] = res_form.food_not_destroyed
        data[f'd{row_num}_q1_sum'] = res_form.sum_general_details

        # Building Details
        data[f'd{row_num}_q2_1'] = res_form.safe_water
        data[f'd{row_num}_q2_2'] = res_form.cleanliness
        data[f'd{row_num}_q2_3'] = res_form.pests_animals
        data[f'd{row_num}_q2_4'] = res_form.sound_pollution
        data[f'd{row_num}_q2_5'] = res_form.toilets_cleanliness
        data[f'd{row_num}_q2_sum'] = res_form.sum_building_details

        # Food Handler
        if not res_form.is_eligible_food_handler_info:
            data[f'd{row_num}_q3_1'] = res_form.medical_certificates
            data[f'd{row_num}_q3_2'] = res_form.proper_clothing
            data[f'd{row_num}_q3_3'] = res_form.unhygienic_behaviour
            data[f'd{row_num}_q3_4'] = res_form.clean_utensils
            data[f'd{row_num}_q3_sum'] = res_form.sum_food_handler
        else:
            data[f'd{row_num}_q3_s1'] = 20
            data[f'd{row_num}_q3_sum'] = 20

        # Processing and Serving
        if not res_form.is_eligible_processing_info:
            data[f'd{row_num}_q4_1'] = res_form.walls_hygienic
            data[f'd{row_num}_q4_2'] = res_form.floor_hygienic
            data[f'd{row_num}_q4_3'] = res_form.ceiling_hygienic
            data[f'd{row_num}_q4_4'] = res_form.food_surfaces_clean
            data[f'd{row_num}_q4_5'] = res_form.wastewater_disposal
            data[f'd{row_num}_q4_6'] = res_form.closed_bins
            data[f'd{row_num}_q4_sum'] = res_form.sum_processing_and_serving
        else:
            data[f'd{row_num}_q4_s1'] = 20
            data[f'd{row_num}_q4_sum'] = 20

        # Food Storage
        if not res_form.is_eligible_food_storage_info:
            data[f'd{row_num}_q5_1'] = res_form.cooked_food_closed
            data[f'd{row_num}_q5_2'] = res_form.cooked_food_temp
            data[f'd{row_num}_q5_3'] = res_form.cooked_food_container
            data[f'd{row_num}_q5_4'] = res_form.cooked_food_contam_prevented
            # leave d1_q5_s1 empty
        else:
            data[f'd{row_num}_q5_s1'] = 16
        data[f'd{row_num}_q5_5'] = res_form.uncooked_food_contam_prevented
        data[f'd{row_num}_q5_sum'] = res_form.sum_food_storage

        # Final Stuff
        data[f'd{row_num}_f_sum'] = res_form.sum_all
        data[f'd{row_num}_f_percentage'] = int(
            (data[f'd{row_num}_f_sum'] / 100) * 100)

        # The grading is done as follows, based on the percentage:
        #   75 - 100: A
        #   50 - 74: B
        #   25 - 49: C
        #   0 - 24: D
        data[f'd{row_num}_f_grade'] = res_form.grade

    filled_pdf = PdfWrapper("pdf/template-si.pdf").fill(data)

    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as tmp_file:
        tmp_file.write(filled_pdf.read())
        tmp_file_path = tmp_file.name

    # Set metadata using PyPDF2
    reader = PdfReader(tmp_file_path)
    writer = PdfWriter()

    writer.append_pages_from_reader(reader)
    writer.add_metadata({
        "/Author": "Hirusha Adikari",
        "/Producer": "PHI System by @hirushaadi",
        "/Title": f"H800 for {res_location.name_of_premise}",
        "/Keywords": f"H800 (2021),PHI,MOH,{res_location.area.name}",
        "/Creator": f"{current_user.name}",
    })

    # Save the updated PDF with metadata
    with open(tmp_file_path, "wb") as f:
        writer.write(f)

    @after_this_request
    def remove_file(response):
        try:
            os.remove(tmp_file_path)
        except Exception as e:
            print(f"Failed to delete temp file: {e}")
        return response

    return send_file(
        tmp_file_path,
        mimetype="application/pdf",
        as_attachment=True,
        download_name=f"{datetime.now().strftime('%Y%m%d_%H_%M_%S')}.pdf"
    )
