from flask import Blueprint, render_template, flash, redirect, url_for, request
from flask_login import login_user, current_user, login_required
from entry import db, bcrypt, mail
from entry.forms import AdminRegistrationForm, AdminLoginForm, UpdateAdminForm
from entry.models import Admin as AdminModel
from flask_mail import Message
from sqlalchemy.exc import IntegrityError
import logging
from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView

logger = logging.getLogger(__name__)
admin_bp = Blueprint('admin_bp', __name__)


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        # Only allow access if the user is authenticated and is an admin
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to the login page if the user doesn't have access
        return redirect(url_for('auth.login', next=request.url))


class MyModelView(ModelView):
    def is_accessible(self):
        # Only allow access if the user is authenticated and is an admin
        return current_user.is_authenticated and current_user.role == 'admin'

    def inaccessible_callback(self, name, **kwargs):
        # Redirect to the login page if the user doesn't have access
        return redirect(url_for('auth.login', next=request.url))

