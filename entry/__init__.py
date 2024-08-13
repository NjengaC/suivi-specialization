from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from flask_login import LoginManager
from flask_mail import Mail
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from dotenv import load_dotenv
from flask_migrate import Migrate
import logging
from flask_admin import Admin
from flask_admin.contrib.sqla import ModelView
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger
import atexit

load_dotenv()

app = Flask(__name__)

from config import Config
app.config.from_object(Config)


db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'auth.login'
login_manager.login_message_category = 'info'
mail = Mail(app)

migrate = Migrate(app, db)
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')



from entry.routes.main_routes import main
from entry.routes.auth_routes import auth
from entry.routes.rider_routes import rider
from entry.routes.parcels import parcel, check_pending_parcels
from entry.routes.password import password
from entry.routes.payment import payment
from entry.routes.admin_routes import admin_bp, MyAdminIndexView, MyModelView



admin = Admin(app, name='Suivi Admin Panel', template_mode='bootstrap4', index_view=MyAdminIndexView())


app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(rider)
app.register_blueprint(parcel)
app.register_blueprint(password)
app.register_blueprint(payment)
app.register_blueprint(admin_bp)

from entry.models import User, Admin as AdminModel, FAQ, Parcel, Rider

admin.add_view(MyModelView(User, db.session, endpoint='user_admin'))
admin.add_view(MyModelView(Rider, db.session, endpoint='rider_admin'))
admin.add_view(MyModelView(Parcel, db.session, endpoint='parcel_admin'))
admin.add_view(MyModelView(FAQ, db.session, endpoint='faq_admin'))
admin.add_view(MyModelView(AdminModel, db.session, endpoint='admin_admin'))
