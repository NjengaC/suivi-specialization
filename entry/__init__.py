from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from config import Config
from flask_migrate import Migrate
import logging
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView

load_dotenv()

app = Flask(__name__)
# app.config.from_object(Config)

app.config['SECRET_KEY'] = '5791628bb0b13ce0c676dfde280ba245'
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:new_password@localhost/suivi'
engine = create_engine(app.config['SQLALCHEMY_DATABASE_URI'])
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'yvonnegichovi@gmail.com'
app.config['MAIL_PASSWORD'] = 'qflepxivndrhyaxh'
app.config['MAIL_DEFAULT_SENDER'] = 'yvonnegichovi@gmail.com'

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
mail = Mail(app)

migrate = Migrate(app, db)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialize Flask-Admin
admin = Admin(app, name='Suivi Admin Panel', template_mode='bootstrap4')

from entry.routes.main_routes import main
from entry.routes.auth_routes import auth
from entry.routes.rider_routes import rider
from entry.routes.parcels import parcel
from entry.routes.password import password
from entry.routes.payment import payment
from entry.routes.admin_routes import admin_bp  # Rename to avoid conflict with admin instance

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(rider)
app.register_blueprint(parcel)
app.register_blueprint(password)
app.register_blueprint(payment)
app.register_blueprint(admin_bp)

from entry.models import User, Admin as AdminModel, FAQ, Parcel, Rider

admin.add_view(ModelView(User, db.session, endpoint='user_admin'))
admin.add_view(ModelView(Rider, db.session, endpoint='rider_admin'))
admin.add_view(ModelView(Parcel, db.session, endpoint='parcel_admin'))
admin.add_view(ModelView(FAQ, db.session, endpoint='faq_admin'))
admin.add_view(ModelView(AdminModel, db.session, endpoint='admin_admin'))
