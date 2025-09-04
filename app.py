import os
import logging
import secrets
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from flask_wtf.csrf import CSRFProtect
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or "dev-secret-key-for-spa-management-system" or secrets.token_hex(32)
app.config['WTF_CSRF_TIME_LIMIT'] = None  # Disable CSRF token expiration
app.config['WTF_CSRF_ENABLED'] = False
app.config['SESSION_COOKIE_SECURE'] = False  # Allow non-HTTPS for development
app.config['SESSION_COOKIE_HTTPONLY'] = False  # Allow access for webview
app.config['SESSION_COOKIE_SAMESITE'] = 'None'  # Allow cross-site for Replit
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database
app.config["SQLALCHEMY_DATABASE_URI"] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Initialize Flask-Login
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.login_message = 'Please log in to access this page.'

# Initialize CSRF protection
csrf = CSRFProtect(app)

# Add CORS headers for webview compatibility
@app.after_request
def after_request(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization'
    response.headers['X-Frame-Options'] = 'ALLOWALL'
    return response

@login_manager.user_loader
def load_user(user_id):
    from models import User
    return User.query.get(int(user_id))

with app.app_context():
    # Import models here so their tables will be created
    import models  # noqa: F401

    try:
        db.create_all()
        logging.info("Database tables created")

        # Initialize default data
        from routes import create_default_data
        create_default_data()
        
        # Import inventory views
        import modules.inventory.inventory_category_views  # noqa: F401
        import modules.inventory.inventory_views  # noqa: F401
        
    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        logging.info("Attempting database migration...")
        try:
            # Skip migration attempt since file doesn't exist
            logging.info("Retrying database initialization without migration...")
            db.create_all()
            from routes import create_default_data
            create_default_data()
            
            # Import inventory views
            import modules.inventory.inventory_category_views  # noqa: F401
            import modules.inventory.inventory_views  # noqa: F401
            
        except Exception as migration_error:
            logging.error(f"Database initialization retry failed: {migration_error}")
            logging.warning("Application starting with limited functionality")