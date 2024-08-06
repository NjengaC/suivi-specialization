from flask import Blueprint, render_template, flash, request, redirect, url_for, jsonify
from flask_login import login_user, login_required, logout_user, current_user
import json
from entry import mail
from entry.models import User, Rider, Parcel, FAQ
from sqlalchemy.exc import IntegrityError
from entry import app, db, bcrypt
from flask_mail import Message, Mail
from sqlalchemy import or_

main = Blueprint('main', __name__)

@main.route('/')
@main.route('/home')
def home():
    if current_user.is_authenticated and current_user.role == 'user':
        return redirect(url_for('auth.home_authenticated'))
    elif current_user.is_authenticated and current_user.role == 'rider':
        return redirect(url_for('rider.rider_authenticated'))
    return render_template('home.html', title='Home')

@main.route('/about')
def about():
    return render_template('about.html')

@main.route('/contacts')
def contacts():
    return render_template('contact.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('main.home'))

@main.route('/support', methods=['GET', 'POST'])
def support():
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        comment = request.form.get('comment')

        if not name or not email or not comment:
            flash('Please fill out all fields.', 'error')
        else:
            # Create a Message object for sending email to admin
            msg = Message(subject='User Comment', recipients=['victorcyrus01@gmail.com'])
            msg.body = f"Name: {name}\nEmail: {email}\nComment: {comment}"

            try:
                # Send the email to admin
                mail.send(msg)
                flash('Email sent successfully! Our support team will get back to you shortly', 'success')
            except Exception as e:
                flash('Something unexpected happened! Please try again', 'error')

        # Redirect to the support page after processing the form data
        return redirect(url_for('main.support'))

    if request.method == 'GET':
        search_query = request.args.get('search_query', '').strip()

        if search_query:
            search_words = search_query.split()

            filter_conditions = []

            for word in search_words:
                question_condition = FAQ.question.ilike(f'%{word}%')
                answer_condition = FAQ.answer.ilike(f'%{word}%')

                filter_conditions.append(question_condition)
                filter_conditions.append(answer_condition)

            combined_condition = or_(*filter_conditions)

            existing_faqs = FAQ.query.filter(combined_condition).all()

            faqs_dict = [{'question': faq.question, 'answer': faq.answer} for faq in existing_faqs]
            existing_faqs = jsonify(faqs_dict)
            return existing_faqs

    return render_template('support.html')
