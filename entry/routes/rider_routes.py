from flask import Blueprint, render_template, flash, redirect, url_for, request, jsonify
from flask_login import login_user, current_user, logout_user, login_required
from entry import db, bcrypt, mail
from entry.forms import RiderRegistrationForm, LoginRiderForm, UpdateRiderForm, ParcelForm
from entry.models import Rider, Parcel
from sqlalchemy.exc import IntegrityError
from flask_mail import Message, Mail
from functools import wraps
import logging


rider = Blueprint('rider', __name__)


def rider_login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'rider':
            return redirect(url_for('rider.login_rider', next=request.url))
        return f(*args, **kwargs)
    return decorated_function


@rider.route('/register_rider', methods=['GET', 'POST'])
def register_rider():
    form = RiderRegistrationForm()
    if current_user.is_authenticated:
        return redirect(url_for('rider.login_rider'))
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_rider = Rider(
            name=form.name.data,
            contact_number=form.contact_number.data,
            email=form.email.data,
            vehicle_type=form.vehicle_type.data,
            vehicle_registration=form.vehicle_registration.data,
            area_of_operation=form.area_of_operation.data,
            password=hashed_password,
            role='rider'
        )
        db.session.add(new_rider)
        try:
            db.session.commit()
            welcome_msg = render_template('welcome_rider_mail.html', rider=new_rider, login_url=url_for('rider.login_rider', _external=True))
            msg = Message('Welcome to Suivi!', recipients=[new_rider.email])
            msg.html = welcome_msg
            mail.send(msg)

            flash('Rider registration successful!', 'success')
            return redirect(url_for('rider.login_rider'))
        except IntegrityError:
            db.session.rollback()
            flash('User with the provided details already exists. Please check Name, Contact, or Vehicle Registration', 'danger')
    return render_template('register_rider.html', title='Register Rider', form=form)


@rider.route('/login_rider', methods=['GET', 'POST'])
def login_rider():
    if current_user.is_authenticated and current_user.role == 'rider':
        return redirect(url_for('rider.rider_authenticated'))
    form = LoginRiderForm()
    if form.validate_on_submit():
        rider = Rider.query.filter_by(contact_number=form.contact_number.data).first()
        if rider and bcrypt.check_password_hash(rider.password, form.password.data):
            login_user(rider)
            pending_assignments = Parcel.query.filter_by(rider_id=rider.id).filter(Parcel.status.in_(['allocated', 'shipped', 'in_progress'])).first()
            flash('Rider login successful!', 'success')
            return render_template('rider_authenticated.html', title='Rider\'s dashboard', user=rider, assignment=pending_assignments)
        else:
            flash('Invalid password. Please try again.', 'danger')
    return render_template('login_rider.html', title='Rider Login', form=form)


@rider.route('/rider_authenticated')
@rider_login_required
def rider_authenticated():
    rider = Rider.query.filter_by(contact_number=current_user.contact_number).first()
    pending_assignments = Parcel.query.filter_by(rider_id=current_user.id).filter(Parcel.status.in_(['allocated', 'shipped', 'in_progress'])).first()
    return render_template('rider_authenticated.html', title='Rider\'s dashboard', user=current_user, assignment=pending_assignments)


@rider.route('/edit_rider_profile', methods=['GET', 'POST'])
@rider_login_required
def edit_rider_profile():
    form = UpdateRiderForm()
    if request.method == 'GET':
        form.email.data = current_user.email
        form.name.data = current_user.name
        form.contact_number.data = current_user.contact_number
        form.vehicle_type.data = current_user.vehicle_type
        form.vehicle_registration.data = current_user.vehicle_registration
        form.area_of_operation.data = current_user.area_of_operation
        form.current_location.data = current_user.current_location
    elif request.method == 'POST':
        if form.validate_on_submit():
            current_user.email = form.email.data
            current_user.username = form.name.data
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
            current_user.vehicle_type = form.vehicle_type.data
            current_user.vehicle_registration = form.vehicle_registration.data
            current_user.area_of_operation = form.area_of_operation.data
            current_user.current_location = form.current_location.data
            db.session.commit()
            flash('Your account has been updated successfully!', 'success')
            return redirect(url_for('rider.rider_authenticated'))
    return render_template('edit_rider_profile.html', title='Edit Profile', form=form, user=current_user)


@rider.route('/view_rider_history', methods=['GET', 'POST'])
@rider_login_required
def view_rider_history():
    if current_user.is_authenticated:
        # Query parcels for the current rider
        parcels = Parcel.query.filter_by(rider_id=current_user.id).all()

        # Separate parcels by status
        open_orders = [parcel for parcel in parcels if parcel.status in ['in_progress', 'shipped']]
        closed_orders = [parcel for parcel in parcels if parcel.status == 'arrived']

        return render_template('view_rider_history.html',
                               open_orders=open_orders,
                               closed_orders=closed_orders)
    else:
        flash('Log in to view your parcels history!', 'danger')
        return render_template('login_rider.html')


@rider.route('/rider_dashboard', methods=['GET', 'POST'])
@rider_login_required
def rider_dashboard():
    pending_assignments = Parcel.query.filter(Parcel.status == 'allocated', Parcel.rider_id==rider.id).first()
    return render_template('rider_dashboard.html', rider=current_user)


@rider.route('/toggle_rider_status/<rider_id>', methods=['POST'])
@rider_login_required
def toggle_rider_status(rider_id):
    """
    Toggles the status of the rider between available and unavailable
    """
    logging.info(f"Received rider_id: {rider_id}")
    rider = Rider.query.filter_by(id=rider_id).first()
    if rider:
        rider.status = 'unavailable' if rider.status == 'available' else 'available'
        db.session.commit()
        return jsonify({'status': rider.status})
    return jsonify({'error': 'Rider not found'}), 404


@rider.route('/update_location', methods=['POST'])
def update_location():
    data = request.json
    rider_id = data.get('rider_id')
    new_location = data.get('current_location')

    if not rider_id or not new_location:
        return jsonify({"error": "Missing rider_id or current_location"}), 400

    rider = Rider.query.get(rider_id)
    if not rider:
        return jsonify({"error": "Rider not found"}), 404

    rider.current_location = new_location
    db.session.commit()

    return jsonify({"success": "Location updated successfully"}), 200
