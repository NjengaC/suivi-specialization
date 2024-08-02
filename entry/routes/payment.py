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


payment = Blueprint('payment', __name__)

@payment.route('/payment_success', methods=['POST'])
def payment_success():
    return redirect(url_for('main.home'))


@payment.route('/verify_payment', methods=['GET', 'POST'])
def verify_payment():
    # Extract the token from the request data
    # stripe_token = request.form.get('stripeToken')

    # Here you would perform the necessary steps to verify the payment using the token
    # For demonstration purposes, let's assume the payment is verified successfully
    payment_verified = True

    if payment_verified:
        send_payment_notification_email()
        return redirect(url_for('main.home'))

    else:
        return redirect(url_for('main.home'))

# Function to send email notification to admin
def send_payment_notification_email():
    msg = Message('New Payment Received', recipients=['victorcyrus01@gmai.com'])
    msg.body = 'A new payment has been received. Please check the dashboard for details.'
    mail.send(msg)

    # Optionally, you can also render a template for the email content
    # msg.html = render_template('payment_notification.html', amount=...)

