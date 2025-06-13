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
    locations = Location.query.all()
    forms = QuestionForm.query.order_by(QuestionForm.created_at.desc()).limit(10).all()
    return render_template('dashboard.html', locations=locations, forms=forms)

@main.route('/add_form', methods=['GET', 'POST'])
@login_required
def add_form():
    locations = Location.query.all()

    if request.method == 'POST':
        try:
            location_id = int(request.form.get('location'))
            cockroaches_value = request.form.get('cockroaches')  # 'True' or 'False' as strings
            cockroaches = cockroaches_value == 'True'

            q = QuestionForm(
                location_id=location_id,
                cockroaches=cockroaches,
                added_by=current_user.username
            )
            db.session.add(q)
            db.session.commit()
            return redirect(url_for('main.dashboard'))
        except (TypeError, ValueError):
            flash("Invalid input. Please try again.", "error")

    return render_template('add_form.html', locations=locations)


@main.route('/forms/<int:location_id>')
@login_required
def view_forms(location_id):
    forms = QuestionForm.query.filter_by(location_id=location_id).all()
    return render_template('view_forms.html', forms=forms)

@main.route('/edit_form/<int:form_id>', methods=['GET', 'POST'])
@login_required
def edit_form(form_id):
    form_record = QuestionForm.query.get_or_404(form_id)
    if form_record.added_by != current_user.username:
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
    if form_record.added_by != current_user.username:
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
        location_name = request.form.get('location_name', '').strip()
        owner_name = request.form.get('owner_name', '').strip()
        contact_number = request.form.get('contact_number', '').strip()

        if area_id and location_name and owner_name and contact_number:
            new_location = Location(
                area_id=area_id,
                name=location_name,
                owner_name=owner_name,
                contact_number=contact_number
            )
            db.session.add(new_location)
            db.session.commit()
            flash("Location added successfully!", "success")
            return redirect(url_for('main.dashboard'))
        else:
            flash("All fields are required.", "error")

    return render_template('add_location.html', areas=areas)
