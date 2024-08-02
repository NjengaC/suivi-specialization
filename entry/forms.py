from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField, DateTimeField
from wtforms.validators import DataRequired, Length, Email, EqualTo, Regexp, Optional, ValidationError
from flask_login import current_user
from entry.models import User, Rider

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Sign Up')

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')

class UpdateAccountForm(FlaskForm):
    username = StringField('Username',
                           validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email',
                        validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Update')

    def validate_username(self, username):
        if username.data != current_user.username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('Username is already taken, please choose another one')
    def validate_email(self, email):
        if email.data != current_user.email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('User with this email is exists, please choose another one')


class UpdateRiderForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(), Length(min=2, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    contact_number = StringField('Contact Number', validators=[DataRequired(),
                                 Regexp(r'^[0-9]{10}$',
                                 message='Please enter a valid 10-digit phone number')])
    vehicle_type = StringField('Vehicle Type', validators=[DataRequired(),
                               Length(min=2, max=50)])
    vehicle_registration = StringField('Vehicle Registration',
                                       validators=[DataRequired(),
                                       Length(min=2, max=50)])
    area_of_operation = StringField('Area of Operation',
                                    validators=[DataRequired(),
                                    Length(min=2, max=100)])
    current_location = StringField('Current Location',
                                   validators=[DataRequired(),
                                   Length(min=5, max=100)])
    submit = SubmitField('Update')

    def validate_name(self, name):
        if name.data != current_user.name:
            rider = Rider.query.filter_by(name=name.data).first()
            if rider:
                raise ValidationError('Name is already taken, please choose another one')
    def validate_email(self, email):
        if email.data != current_user.email:
            rider = Rider.query.filter_by(email=email.data).first()
            if rider:
                raise ValidationError('Rider with this email is exists, please choose another one')



class RiderRegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired(),
		       Length(min=2, max=100)])
    contact_number = StringField('Contact Number', validators=[DataRequired(),
                                 Regexp(r'^[0-9]{10}$',
                                 message='Please enter a valid 10-digit phone number')])
    email = StringField('Email', validators=[Email()])
    vehicle_type = StringField('Vehicle Type', validators=[DataRequired(),
                               Length(min=2, max=50)])
    vehicle_registration = StringField('Vehicle Registration',
                                       validators=[DataRequired(),
				       Length(min=2, max=50)])
    area_of_operation = StringField('Area of Operation',
				    validators=[DataRequired(),
                                    Length(min=2, max=100)])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    current_location = StringField('Current Location',
                                   validators=[DataRequired(),
                                   Length(min=5, max=100)])
    submit = SubmitField('Register')

class LoginRiderForm(FlaskForm):
    contact_number = StringField('Contact Number', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    submit = SubmitField('Login')

class ParcelForm(FlaskForm):
    sender_name = StringField('Sender\'s Name', validators=[DataRequired(), Length(max=100)])
    sender_email = StringField('Sender\'s Email', validators=[DataRequired(), Email(), Length(max=100)])
    sender_contact = StringField('Sender\'s Contact', validators=[DataRequired(), Length(max=20)])
    receiver_name = StringField('Receiver\'s Name', validators=[Length(max=100)])
    receiver_contact = StringField('Receiver\'s Contact', validators=[Length(max=20)])
    pickup_location = StringField('Pickup Location', validators=[DataRequired(), Length(max=255)])
    delivery_location = StringField('Delivery Location', validators=[DataRequired(), Length(max=255)])
    description = TextAreaField('Description', validators=[DataRequired(), Length(max=400)])


class ForgotPasswordForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    submit = SubmitField('Submit')


class ResetPasswordForm(FlaskForm):
    password = PasswordField('New Password', validators=[DataRequired()])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    submit = SubmitField('Reset Password')
