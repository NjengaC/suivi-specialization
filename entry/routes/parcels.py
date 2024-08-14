from entry.forms import LoginRiderForm, RegistrationForm, LoginForm, UpdateAccountForm, RiderRegistrationForm, ParcelForm, UpdateRiderForm, ForgotPasswordForm, ResetPasswordForm
from flask import Blueprint, session, render_template, flash, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
from entry.models import User, Rider, Parcel, FAQ
from entry.sms_service import send_bulk_sms
from sqlalchemy.exc import IntegrityError
from datetime import datetime, timedelta
from geopy.geocoders import Nominatim
from flask_mail import Message, Mail
from geopy.distance import geodesic
from entry import app, db, bcrypt
from sqlalchemy import or_
from flask import session
from entry import mail
import geopy.exc
import retrying
import requests
import secrets
import stripe
import atexit
import json
import os

scheduler = BackgroundScheduler()

parcel = Blueprint('parcel', __name__)
secret_key = os.getenv('STRIPE_SECRET_KEY')
publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')

stripe_keys = {
        "secret_key": secret_key,
        "publishable_key": publishable_key,
        }

stripe.api_key = stripe_keys['secret_key']

@parcel.route('/track_parcel')
def track_parcel():
    return render_template('track_parcel.html')

@parcel.route('/get_parcel_status')
def get_parcel_status():
    tracking_number = request.args.get('tracking_number')
    if tracking_number:
        parcel = Parcel.query.filter_by(tracking_number=tracking_number).first()
        if parcel:
            return jsonify({
                'status': parcel.status,
                'expected_arrival': parcel.expected_arrival,
                'pickup_location': parcel.pickup_location,
                'delivery_location': parcel.delivery_location
            }), 200
        else:
            return jsonify({'error': 'Parcel not found'}), 404
    else:
        return jsonify({'error': 'Tracking number not provided'}), 400

@parcel.route('/request_pickup', methods=['POST', 'GET'])
@login_required
def request_pickup():
    form = ParcelForm()
    step = request.args.get('step', '1')

    if request.method == 'POST':
        if step == '1':
            session['delivery_location'] = form.delivery_location.data
            return redirect(url_for('parcel.request_pickup', step='2'))

        elif step == '2':
            session['pickup_location'] = form.pickup_location.data
            return redirect(url_for('parcel.request_pickup', step='3'))
        elif step == '3':
            response = requests.post(url_for('parcel.get_coordinates', _external=True), json={
                'pickup_location': session.get('pickup_location'),
                'delivery_location': session.get('delivery_location')
            })

            if response.ok:
                data = response.json()
                session['pickup_coords'] = {
                    'lat': data.get('pickup_lat'),
                    'lng': data.get('pickup_lng')
                }
                session['delivery_coords'] = {
                    'lat': data.get('delivery_lat'),
                    'lng': data.get('delivery_lng')
                }
                return redirect(url_for('parcel.request_pickup', session=session, step='4'))
            else:
                flash('Unable to get coordinates. Please try again.', 'error')
                return redirect(url_for('parcel.request_pickup', step='2'))

        elif step == '4':
            # Save receiver's information
            session['receiver_name'] = form.receiver_name.data
            session['receiver_contact'] = form.receiver_contact.data

            # Create the parcel entry in the database
            parcel = Parcel(
                sender_name=current_user.username,
                sender_email=current_user.email,
                sender_contact=current_user.user_contact,
                receiver_name=session['receiver_name'],
                receiver_contact=session['receiver_contact'],
                pickup_location=session['pickup_location'],
                delivery_location=session['delivery_location'],
                description="Testing Parcel"
            )

            db.session.add(parcel)
            db.session.commit()

            closest_rider = allocate_parcel(parcel)
            if closest_rider:
                flash('Rider Allocated. Check your email for more details', 'success')
            else:
                start_scheduler()
                flash('Allocation in progress. Please wait for a rider to be assigned', 'success')

    return render_template('request_pickup.html', form=form, step=step, key=stripe_keys['publishable_key'])


@parcel.route('/get_coordinates', methods=['POST'])
def get_coordinates():
    data = request.get_json()
    pickup_location = data.get('pickup_location')
    delivery_location = data.get('delivery_location')

    pickup_lat, pickup_lng = get_lat_lng(pickup_location)
    delivery_lat, delivery_lng = get_lat_lng(delivery_location)

    # Check if both locations were successfully fetched
    if None in (pickup_lat, pickup_lng, delivery_lat, delivery_lng):
        return jsonify({"error": "Could not fetch coordinates for one or both locations"}), 400
    return jsonify({
        "pickup_lat": pickup_lat,
        "pickup_lng": pickup_lng,
        "delivery_lat": delivery_lat,
        "delivery_lng": delivery_lng
        })


def get_lat_lng(location):
    user_agent = 'MyGeocodingApp/1.0 (victorcyrus01@gmail.com)'
    geolocator = Nominatim(user_agent=user_agent)
    location = geolocator.geocode(location)
    return location.latitude, location.longitude


def allocate_parcel(parcel):
    """
    Allocates pending parcel deliveries to available riders
    """
    available_riders = Rider.query.filter_by(status='available').all()

    if not available_riders:
        return None

    pickup_location = parcel.pickup_location
    closest_rider = None
    min_distance = float('inf')

    available_riders_not_rejected = [rider for rider in available_riders if rider.id != parcel.rider_id]

    for rider in available_riders_not_rejected:
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
        send_rider_details_email(parcel.sender_email, closest_rider, parcel.tracking_number)
        sender_message = f"Your parcel has been allocated to a rider. Rider: {closest_rider.name}, Contact: {closest_rider.contact_number}"
        rider_message = f"You have been assigned a new parcel. Pickup from: {parcel.pickup_location}, Deliver to: {parcel.delivery_location}"

        send_bulk_sms(parcel.sender_contact, sender_message)
        send_bulk_sms(closest_rider.contact_number, rider_message)
        return closest_rider
    else:
        return None


def start_scheduler():
    if not scheduler.running:
        scheduler.start()

    if not scheduler.get_job('check_pending_parcels_job'):
        scheduler.add_job(
            func=check_pending_parcels,
            trigger=IntervalTrigger(minutes=5),
            id='check_pending_parcels_job',
            name='Check pending parcels every 5 minutes',
            replace_existing=True
        )

    atexit.register(lambda: scheduler.shutdown())


def check_pending_parcels():
    with app.app_context():
        now = datetime.utcnow()

        pending_parcels_exist = Parcel.query.filter_by(status='pending').first()
        if not pending_parcels_exist:
            print(f"No pending parcels found at {datetime.now()}. Skipping the check.")
            scheduler.remove_job('check_pending_parcels_job')
            return

        pending_parcels = Parcel.query.filter_by(status='pending').all()

        for parcel in pending_parcels:
            time_since_last_update = now - parcel.updated_at

            if time_since_last_update > timedelta(minutes=30):
                notify_sender_parcel_pending(parcel)
            else:
                try:
                    closest_rider = allocate_parcel(parcel)
                    if closest_rider:
                        parcel.status = 'allocated'
                        db.session.commit()
                except Exception as e:
                    print(f"Error allocating parcel {parcel.id}: {e}")

            print(f"Attempted to allocate parcel {parcel.id} at {datetime.now()}")


def notify_sender_parcel_pending(parcel):
    msg = Message(
        subject="Parcel Allocation Delayed",
        recipients=[parcel.sender_email],
        body=f"Dear {parcel.sender_name},\n\nWe apologize for the delay in allocating a rider for your parcel. We are still working on assigning a rider. Please bear with us.\n\nThank you,\nSuivi Delivery Company"
    )
    mail.send(msg)
    print(f"Notification sent to {parcel.sender_email} about pending parcel {parcel.id}")


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


def send_rider_details_email(recipient_email, closest_rider, tracking_number):
    msg = Message('Parcel Allocation Details', recipients=[recipient_email])
    html_content = render_template('rider_details_email.html', rider=closest_rider, tracking_number=tracking_number)
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
            db.session.commit()
            flash("You have Rejected parcel pickup!, contact admin if that was unintentional", 'danger')
            allocate_parcel(assignment)
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
@login_required
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
