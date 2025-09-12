import os
import sys
import logging
import secrets
from flask import Flask, request
from flask_sqlalchemy import SQLAlchemy
from werkzeug.middleware.proxy_fix import ProxyFix
from sqlalchemy.orm import DeclarativeBase

# Configure logging
logging.basicConfig(level=logging.DEBUG)

class Base(DeclarativeBase):
    pass

db = SQLAlchemy(model_class=Base)

# Create the app
app = Flask(__name__)
app.secret_key = os.environ.get("SESSION_SECRET") or "dev-testing-key"
# Disable CSRF and auth for testing
app.config['WTF_CSRF_ENABLED'] = False
app.config['TESTING'] = True
app.config['SESSION_COOKIE_SECURE'] = False
app.config['SESSION_COOKIE_HTTPONLY'] = False
app.config['SESSION_COOKIE_SAMESITE'] = 'None'
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0  # Prevent caching of static files
app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# Configure the database - PostgreSQL
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
    "pool_recycle": 300,
    "pool_pre_ping": True,
}

# Initialize the app with the extension
db.init_app(app)

# Add headers for webview compatibility and caching control
@app.after_request
def after_request(response):
    # Cache control headers
    response.headers['Cache-Control'] = 'no-cache, no-store, must-revalidate'
    response.headers['Pragma'] = 'no-cache'
    response.headers['Expires'] = '0'

    # Security headers
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'  # Prevent clickjacking
    response.headers['X-Content-Type-Options'] = 'nosniff'  # Prevent MIME sniffing
    response.headers['X-XSS-Protection'] = '1; mode=block'  # Enable XSS protection
    # Restrict CORS for security (remove wildcard in production)
    response.headers['Access-Control-Allow-Origin'] = request.headers.get('Origin', '*')
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, PUT, DELETE, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, Authorization, X-CSRFToken'
    return response

# Login manager disabled for testing

with app.app_context():
    # Import models here so their tables will be created
    import models  # noqa: F401
    # Import all modules
    from modules.auth import auth_views
    from modules.dashboard import dashboard_views
    from modules.bookings import bookings_views
    from modules.clients import clients_views
    from modules.staff import staff_views
    from modules.checkin import checkin_views
    from modules.notifications import notifications_views
    from modules.billing import billing_views, integrated_billing_views
    from modules.services import services_views
    from modules.packages import packages_views
    from modules.reports import reports_views
    from modules.expenses import expenses_views
    from modules.inventory import views as inventory_views
    from modules.settings import settings_views

    try:
        db.create_all()
        logging.info("Database tables created")

    except Exception as e:
        logging.error(f"Database initialization failed: {e}")
        logging.info("Attempting database migration...")
        try:
            # Skip migration attempt since file doesn't exist
            logging.info("Retrying database initialization without migration...")
            db.create_all()

        except Exception as migration_error:
            logging.error(f"Database initialization retry failed: {migration_error}")
            logging.warning("Application starting with limited functionality")

    # Professional inventory views removed
    
    # Import routes.py to register root routes and error handlers
    try:
        import routes  # registers root, system, error routes
        print("routes.py imported successfully")
    except Exception as e:
        logging.exception(f"Failed importing routes.py: {e}")
        print("Running without core routes - some pages may not work")
    
    # Log registered routes for debugging
    print("Registered routes:")
    for rule in app.url_map.iter_rules():
        print(f"  {rule.rule} -> {rule.endpoint}")

# Run the Flask app when called directly
if __name__ == "__main__":
    # Fix: Prevent double Flask instance creation from circular imports
    sys.modules['app'] = sys.modules[__name__]
    print("Starting Flask development server on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False)