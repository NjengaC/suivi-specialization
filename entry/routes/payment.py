from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
import json
from entry.forms import LoginRiderForm, RegistrationForm, LoginForm, UpdateAccountForm, RiderRegistrationForm, ParcelForm, UpdateRiderForm, ForgotPasswordForm, ResetPasswordForm
from entry import mail
from entry.models import User, Rider, Parcel, FAQ
from sqlalchemy.exc import IntegrityError
from entry import app, db, bcrypt
from flask_mail import Message, Mail
from sqlalchemy import or_
import secrets
import os
import stripe

secret_key = os.getenv('STRIPE_SECRET_KEY')
publishable_key = os.getenv('STRIPE_PUBLISHABLE_KEY')

stripe_keys = {
        "secret_key": secret_key,
        "publishable_key": publishable_key,
        }

stripe.api_key = stripe_keys['secret_key']

payment = Blueprint('payment', __name__)

@payment.route('/payment_success', methods=['POST'])
def payment_success():
    return redirect(url_for('main.home'))


@payment.route('/checkout', methods=['GET', 'POST'])
def checkout():
    return render_template('checkout.html',key=stripe_keys['publishable_key'])


@payment.route('/charge', methods=['POST'])
def charge():
    amount = 1000  # Amount in cents

    customer = stripe.Customer.create(
        email='customer@example.com',
        source=request.form['stripeToken']
    )

    charge = stripe.Charge.create(
        customer=customer.id,
        amount=amount,
        currency='usd',
        description='Flask Charge'
    )

    return jsonify({'success': True})


def send_payment_notification_email():
    msg = Message('New Payment Received', recipients=['victorcyrus01@gmai.com'])
    msg.body = 'A new payment has been received. Please check the dashboard for details.'
    mail.send(msg)
