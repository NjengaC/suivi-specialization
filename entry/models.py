from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import json
from datetime import datetime
from entry import db, login_manager
import random
from datetime import timedelta
import uuid

@login_manager.user_loader
def load_user(user_id):
    # Check if the user ID corresponds to a Rider
    rider = Rider.query.get(user_id)
    if rider:
        return rider

    # If the user ID doesn't correspond to a Rider, check if it corresponds to a regular User
    user = User.query.get(user_id)
    if user:
        return user

    # If neither Rider nor User is found, return None
    return None

class User(db.Model, UserMixin):
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    reset_password_token = db.Column(db.String(100), nullable=True)

    def __str__(self):
        return f"User('{self.username}', '{self.email}', '{self.password}')"


class Rider(db.Model, UserMixin):
    __tablename__ = 'rider'
    id = db.Column(db.String(36), primary_key=True, default=str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    contact_number = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    vehicle_type = db.Column(db.String(50), nullable=False)
    vehicle_registration = db.Column(db.String(50), unique=True, nullable=False)
    area_of_operation = db.Column(db.String(100), nullable=False)
    availability = db.Column(db.Boolean, default=True)
    current_location = db.Column(db.String(255), nullable=False)
    password = db.Column(db.String(60), nullable=False)
    role = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='available')
    assigned_parcels = db.relationship('Parcel', back_populates='assigned_rider')
    reset_password_token = db.Column(db.String(100), nullable=True)

    def __repr__(self):
        return f"Rider('{self.name}', '{self.contact_number}', '{self.vehicle_type}', '{self.area_of_operation}', '{self.availability}')"
 

class Parcel(db.Model):
    __tablename__ = 'parcel'
    id = db.Column(db.Integer, primary_key=True)
    sender_name = db.Column(db.String(100), nullable=False)
    sender_email = db.Column(db.String(100), nullable=False)
    sender_contact = db.Column(db.String(20), nullable=False)
    receiver_name = db.Column(db.String(100))
    receiver_contact = db.Column(db.String(20))
    pickup_location = db.Column(db.String(255), nullable=False)
    delivery_location = db.Column(db.String(255), nullable=False)
    description = db.Column(db.String(400), nullable=False)
    rider_id = db.Column(db.String(36), db.ForeignKey('rider.id'), nullable=True)
    status = db.Column(db.String(20), default='pending')
    expected_arrival = db.Column(db.String(50))
    tracking_number = db.Column(db.String(50), unique=True, nullable=False)

    assigned_rider = db.relationship('Rider', back_populates='assigned_parcels', overlaps='rider')

    @staticmethod
    def generate_tracking_number():
        return ''.join(random.choices('0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ', k=10))

    def set_expected_arrival(self):
        self.expected_arrival = (datetime.now() + timedelta(days=1)).strftime('%B %d, %Y, %I:%M %p')

    def __init__(self, **kwargs):
        super(Parcel, self).__init__(**kwargs)
        self.tracking_number = self.generate_tracking_number()
        self.set_expected_arrival()

    def __repr__(self):
        return f"Parcel('{self.id}', '{self.sender_name}', '{self.receiver_name}', '{self.status}')"



class Admin(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"Admin('{self.username}', '{self.email}')"


class FAQ(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    question = db.Column(db.String(255), nullable=False)
    answer = db.Column(db.Text, nullable=False)
