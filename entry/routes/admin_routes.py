from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, login_required
from entry import db, bcrypt, mail
from entry.forms import AdminRegistrationForm, AdminLoginForm, UpdateAdminForm
from entry.models import Admin as AdminModel
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
import logging

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin_bp', __name__)

@admin_bp.route('/register_admin', methods=['GET', 'POST'])
def register_admin():
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.admin_dashboard'))

    form = AdminRegistrationForm()
    if form.validate_on_submit():
        existing_admin = AdminModel.query.filter((AdminModel.username == form.username.data) | (AdminModel.email == form.email.data)).first()
        if existing_admin:
            flash('Username or email already exists. Please choose a different username or email.', 'danger')
            return redirect(url_for('admin_bp.register_admin'))

        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        admin = AdminModel(username=form.username.data, email=form.email.data, password=hashed_password, role='admin')
        db.session.add(admin)

        try:
            db.session.commit()
            welcome_msg = render_template('welcome_admin_mail.html', admin=admin, login_url=url_for('admin_bp.login_admin', _external=True))
            flash('Admin account created', 'success')
            msg = Message('Welcome to Suivi!', recipients=[admin.email])
            msg.html = welcome_msg
            mail.send(msg)
            return redirect(url_for('admin_bp.login_admin'))
        except IntegrityError as e:
            db.session.rollback()
            logger.error(f'IntegrityError: {e}')
            flash('An error occurred while creating the admin account. Please try again.', 'danger')
            return redirect(url_for('admin_bp.register_admin'))
    return render_template('admin_register.html', title='Register Admin', form=form)

@admin_bp.route('/login_admin', methods=['GET', 'POST'])
def login_admin():
    if current_user.is_authenticated:
        return redirect(url_for('admin_bp.admin_dashboard'))
    
    form = AdminLoginForm()
    if form.validate_on_submit():
        admin = AdminModel.query.filter_by(email=form.email.data).first()
        if admin and bcrypt.check_password_hash(admin.password, form.password.data):
            login_user(admin, remember=form.remember.data)
            return redirect(url_for('admin_bp.admin_dashboard'))
        else:
            flash('Login Unsuccessful, please check your email and password', 'danger')
    return render_template('admin_login.html', title='Admin Login', form=form)

@admin_bp.route('/admin_dashboard')
@login_required
def admin_dashboard():
    if current_user.is_authenticated and hasattr(current_user, 'role') and current_user.role == 'admin':
        return render_template('admin_dashboard.html', title='Admin Dashboard')
    else:
        flash('Unauthorized access!', 'danger')
        return redirect(url_for('admin_bp.login_admin'))

@admin_bp.route('/edit_admin_profile', methods=['GET', 'POST'])
@login_required
def edit_admin_profile():
    form = UpdateAdminForm()
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
            return redirect(url_for('admin_bp.admin_dashboard'))
    return render_template('edit_admin_profile.html', title='Edit Profile', form=form, user=current_user)
