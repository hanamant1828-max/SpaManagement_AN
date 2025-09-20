import os
from flask import Flask, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase
from werkzeug.middleware.proxy_fix import ProxyFix
from flask_login import LoginManager


class Base(DeclarativeBase):
    pass


db = SQLAlchemy(model_class=Base)

# create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET")
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1) # needed for url_for to generate with https

# configure the database, relative to the app instance folder
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Configure cache control for Replit webview
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['WTF_CSRF_ENABLED'] = False  # Disable CSRF for development in Replit

# Initialize the app with the extension, flask-sqlalchemy >= 3.0.x
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

# Basic routes removed to avoid conflicts with main application routes

with app.app_context():
    # Make sure to import the models here or their tables won't be created
    import models  # noqa: F401
    # Import inventory models for database creation
    from modules.inventory import models as inventory_models  # noqa: F401
    
    try:
        # Try to create tables, but handle conflicts gracefully
        db.create_all()
        print("Database initialized successfully")
    except Exception as e:
        print(f"Database already exists or conflict detected: {e}")
        print("Continuing with existing database...")
    
    # Import and register basic routes
    try:
        # Import only essential routes without complex module dependencies
        import routes
        print("Routes imported successfully")
    except Exception as e:
        print(f"Warning: Could not import all routes: {e}")
        print("Application will continue with basic functionality")