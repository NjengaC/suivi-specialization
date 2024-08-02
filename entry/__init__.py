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


from entry.routes.main_routes import main
from entry.routes.auth_routes import auth
from entry.routes.rider_routes import rider
from entry.routes.parcels import parcel
from entry.routes.password import password
from entry.routes.payment import payment

app.register_blueprint(main)
app.register_blueprint(auth)
app.register_blueprint(rider)
app.register_blueprint(parcel)
app.register_blueprint(password)
app.register_blueprint(payment)
