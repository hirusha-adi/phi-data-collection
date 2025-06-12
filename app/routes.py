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
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            user.last_accessed = db.func.now()
            db.session.commit()
            return redirect(url_for('main.dashboard'))
        flash('Invalid credentials')
    return render_template('login.html', form=form)

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.login'))

@main.route('/dashboard')
@login_required
def dashboard():
    locations = Location.query.all()
    return render_template('dashboard.html', locations=locations)

@main.route('/add_form', methods=['GET', 'POST'])
@login_required
def add_form():
    form = QuestionEntryForm()
    form.area.choices = [(a.id, a.name) for a in Area.query.all()]
    form.location.choices = [(l.id, l.name) for l in Location.query.all()]
    if form.validate_on_submit():
        q = QuestionForm(
            area_id=form.area.data,
            location_id=form.location.data,
            cockroaches=form.cockroaches.data,
            added_by=current_user.username
        )
        db.session.add(q)
        db.session.commit()
        return redirect(url_for('main.dashboard'))
    return render_template('add_form.html', form=form)

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

    form = QuestionEntryForm()
    form.area.choices = [(a.id, a.name) for a in Area.query.all()]
    form.location.choices = [(l.id, l.name) for l in Location.query.all()]

    if request.method == 'GET':
        form.area.data = form_record.area_id
        form.location.data = form_record.location_id
        form.cockroaches.data = form_record.cockroaches

    print(1)
    print(form.cockroaches.data)

    if form.validate_on_submit():
        print(1.2)
        form_record.area_id = form.area.data
        form_record.location_id = form.location.data
        form_record.cockroaches = form.cockroaches.data
        print(2)
        db.session.commit()
        print(3)
        print("Form errors:", form.errors)
        return redirect(url_for('main.dashboard'))

    print(4)
    print("Form errors:", form.errors)
    return render_template('edit_form.html', form=form, form_id=form_id)


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
        area_id = request.form.get('area_id')
        location_name = request.form.get('location_name')
        owner_name = request.form.get('owner_name')
        contact_number = request.form.get('contact_number')

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
            flash("Please fill all the fields.", "error")

    return render_template('add_location.html', areas=areas)
