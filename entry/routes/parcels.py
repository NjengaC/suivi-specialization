from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
import json
from entry import mail
from entry.models import User, Rider, Parcel, FAQ
from sqlalchemy.exc import IntegrityError
from entry import app, db, bcrypt
from flask_mail import Message, Mail
from sqlalchemy import or_
import stripe
from entry.forms import LoginRiderForm, RegistrationForm, LoginForm, UpdateAccountForm, RiderRegistrationForm, ParcelForm, UpdateRiderForm, ForgotPasswordForm, ResetPasswordForm
import secrets
from geopy.distance import geodesic
from geopy.geocoders import Nominatim
import retrying
import geopy.exc


parcel = Blueprint('parcel', __name__)


@parcel.route('/track_parcel')
def track_parcel():
    # Implement the functionality for sending parcels here
    return render_template('track_parcel.html')

@parcel.route('/get_parcel_status')
def get_parcel_status():
    tracking_number = request.args.get('tracking_number')
    if tracking_number:
        parcel = Parcel.query.filter_by(tracking_number=tracking_number).first()
        if parcel:
            return jsonify({
                'status': parcel.status,
                'expected_arrival': parcel.expected_arrival
            }), 200
        else:
            return jsonify({'error': 'Parcel not found'}), 404
    else:
        return jsonify({'error': 'Tracking number not provided'}), 400


@parcel.route('/request_pickup', methods=['GET', 'POST'])
def request_pickup():
    form = ParcelForm()
    if form.validate_on_submit():
        parcel = Parcel(
            sender_name=form.sender_name.data,
            sender_email=form.sender_email.data,
            sender_contact=form.sender_contact.data,
            receiver_name=form.receiver_name.data,
            receiver_contact=form.receiver_contact.data,
            pickup_location=form.pickup_location.data,
            delivery_location=form.delivery_location.data,
            description=form.description.data
        )
        db.session.add(parcel)
        db.session.commit()
        #Allocate parcel to the nearest unoccupied rider
        allocation_result = allocate_parcel()
        if allocation_result['success']:
            send_rider_details_email(parcel.sender_email, allocation_result, parcel.tracking_number)
            flash(f'Rider Allocated. Check your email for more details')
#            return render_template('payment.html', results=allocation_result                    )
            return redirect(url_for('payment.verify_payment'))
        else:
            flash('Allocation in progress. Please wait for a rider to be assigned', 'success')
            return redirect(url_for('payment.verify_payment'))
#            return render_template('payment.html', result = allocation_result)
    return render_template('request_pickup.html', form=form)



def allocate_parcel():
    """
    Allocates pending parcel deliveries to available riders
    """
    pending_parcels = Parcel.query.filter_by(status='pending').all()
    available_riders = Rider.query.filter_by(status='available').all()
    allocated_parcels = []

    for parcel in pending_parcels:
        if not available_riders:
            break  # Break if no available riders left

        pickup_location = parcel.pickup_location
        closest_rider = None
        min_distance = float('inf')

        available_riders_excluding_denied = [rider for rider in available_riders if rider.id != parcel.rider_id]

        for rider in available_riders_excluding_denied:
            distance = calculate_distance(pickup_location, rider.current_location)
            if distance < min_distance:
                closest_rider = rider
                min_distance = distance

        if closest_rider:
            parcel.status = 'allocated'
            parcel.rider_id = closest_rider.id
            closest_rider.status = 'unavailable'
            db.session.commit()
            notify_rider_new_assignment(closest_rider.email, parcel, closest_rider)
            allocated_parcels.append(parcel)

    if allocated_parcels:
        closest_rider_details = {
            'id': closest_rider.id,
            'name': closest_rider.name,
            'contact': closest_rider.contact_number,
            'vehicle_type': closest_rider.vehicle_type,
            'vehicle_registration': closest_rider.vehicle_registration
        }
        result = {
            'success': True,
            'allocated_parcels': allocated_parcels,
            'closest_rider': closest_rider_details
        }
    else:
        result = {
            'success': False,
            'message': 'No available riders, parcel allocation pending'
        }

    return result


@retrying.retry(wait_exponential_multiplier=1000, wait_exponential_max=10000)
def geocode_with_retry(geolocator, location):
    """
    retrying decorator incase the nominatim encouters challenges while loading
    """
    return geolocator.geocode(location)


def calculate_distance(location1, location2):
    """
    Implements distance calculation logic
    It uses the location format: (latitude, longitude)
    """
    user_agent = 'MyGeocodingApp/1.0 (victorcyrus01@gmail.com)'
    geolocator = Nominatim(user_agent=user_agent)
    location1 = geolocator.geocode(location1)
    location2 = geolocator.geocode(location2)
    current = location1.latitude, location1.longitude
    pickup_location = location2.latitude, location2.longitude

    distance = geodesic(pickup_location, current).kilometers
    return distance


def notify_rider_new_assignment(rider_email, parcel, rider):
    """
    Trigger notification when assigning a parcel to a rider
    """
    msg = Message('New Delivery Assignment', recipients=[rider_email])
    html_content = render_template('new_assignment_email.html', parcel=parcel, rider=rider)
    msg.html = html_content
    mail.send(msg)


def send_rider_details_email(recipient_email, allocation_result, tracking_number):
    msg = Message('Parcel Allocation Details', recipients=[recipient_email])
    html_content = render_template('rider_details_email.html', **allocation_result, tracking_number=tracking_number)
    msg.html = html_content
    mail.send(msg)


@parcel.route('/update_assignment', methods=['POST'])
def update_assignment():
    data = request.json
    parcel_id = data.get('parcel_id')
    action = data.get('action')

    assignment = Parcel.query.filter_by(id=parcel_id).filter(or_(Parcel.status == 'allocated', Parcel.status == 'shipped', Parcel.status == 'in_progress')).first()
    if assignment:
        if action == 'accept':
            assignment.status = 'in_progress'
            db.session.commit()
            flash("You have accepted parcel pick-up! We are waiting", 'success')
            return jsonify({'success': True})
        elif action == 'reject':
            rider = Rider.query.filter_by(id=assignment.rider_id).first()
            if rider:
                rider.status = 'available'
            assignment.status = 'pending'
            assignment.rider_id = None
            db.session.commit()
            flash("You have Rejected parcel pickup!, contact admin if that was unintentional", 'danger')
            allocate_parcel()
        elif action == 'shipped':
            assignment.status = 'shipped'
            db.session.commit()
            return jsonify({'success': True})
        elif action == 'arrived':
            assignment.status = 'arrived'
            rider = Rider.query.filter_by(id=assignment.rider_id).first()
            if rider:
                rider.status = 'available'
            db.session.commit()
            return jsonify({'success': True})
        else:
            return jsonify({'error': 'Invalid action'}), 400
    else:
        return jsonify({'error': 'Assignment not found or already accepted/denied'}), 404
    return redirect(url_for('main.home'))


@parcel.route('/view_parcel_history', methods=['GET', 'POST'])
def view_parcel_history():
    if current_user.is_authenticated:
        parcels = Parcel.query.filter_by(sender_email=current_user.email).all()

        # Separate parcels by status
        allocated_parcels = [parcel for parcel in parcels if parcel.status == 'allocated']
        in_progress_parcels = [parcel for parcel in parcels if parcel.status == 'in_progress']
        shipped_parcels = [parcel for parcel in parcels if parcel.status == 'shipped']
        arrived_parcels = [parcel for parcel in parcels if parcel.status == 'arrived']

        return render_template('view_parcel_history.html',
                               allocated_parcels=allocated_parcels,
                               in_progress_parcels=in_progress_parcels,
                               shipped_parcels=shipped_parcels,
                               arrived_parcels=arrived_parcels)
        return render_template('view_parcel_history.html', parcels=parcels)
    else:
        return render_template('view_parcel_history.html')
        flash('Log in to view your parcels history!', 'danger')
