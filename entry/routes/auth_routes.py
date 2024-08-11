from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, logout_user, login_required
from entry import db, bcrypt, mail
from entry.forms import RegistrationForm, LoginForm, UpdateAccountForm
from entry.models import User
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)
auth = Blueprint('auth', __name__)

@auth.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter((User.username == form.username.data) | (User.email == form.email.data)).first()
        if existing_user:
            flash('Username or email already exists. Please choose a different username or email.', 'danger')
            return redirect(url_for('auth.register'))
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, user_contact=form.user_contact.data, password=hashed_password, role='user')
        db.session.add(user)
        
        try:
            db.session.commit()
            welcome_msg = render_template('welcome_user_mail.html', user=user, login_url=url_for('auth.login', _external=True))
            flash('Account created', 'success')
            msg = Message('Welcome to Suivi!', recipients=[user.email])
            msg.html = welcome_msg
            mail.send(msg)
            return redirect(url_for('auth.login'))
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f'IntegrityError: {e}')
            flash('An error occurred while creating the account. Please try again.', 'danger')
            return redirect(url_for('auth.register'))
    return render_template('register.html', title='Register', form=form)

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('main.home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            return render_template('home_authenticated.html', user=user)
        else:
            flash('Login Unsuccessful, please check your email and password', 'danger')
    return render_template('login.html', title='Login', form=form)


@auth.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = UpdateAccountForm()
    if request.method == 'GET':
        form.email.data = current_user.email
        form.username.data = current_user.username
    elif request.method == 'POST':
        if form.validate_on_submit():
            current_user.email = form.email.data
            current_user.username = form.username.data
            hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
            current_user.password = hashed_password
            db.session.commit()
            flash('Your account has been updated successfully!', 'success')
            return render_template('home.html', title='Home', user=current_user)
    return render_template('edit_profile.html', title='Edit Profile', form=form, user=current_user)


@auth.route('/home_authenticated')
def home_authenticated():
        return render_template('home_authenticated.html', title='suivi-User\'s HomePage', user=current_user)
