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

# Configure the database - Using SQLite for simplicity
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///spa_management.db"

# SQLite doesn't need complex pooling configuration
app.config["SQLALCHEMY_ENGINE_OPTIONS"] = {
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
    # Import models here for ORM mapping
    import models  # noqa: F401
    
    # Check if we need to initialize database with new schema
    import os
    if not os.path.exists("spa_management.db"):
        logging.info("Initializing fresh database with Prisma-style schema...")
        try:
            # Create the database with new schema directly
            import sqlite3
            conn = sqlite3.connect('spa_management.db')
            cursor = conn.cursor()
            
            # Create Service table with new schema
            cursor.execute('''
                CREATE TABLE service (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    "basePrice" DECIMAL(10,2) NOT NULL,
                    "durationMinutes" INTEGER NOT NULL,
                    active BOOLEAN DEFAULT 1,
                    description TEXT,
                    category_id INTEGER,
                    category VARCHAR(50),
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create Package table with new schema
            cursor.execute('''
                CREATE TABLE package (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    description TEXT,
                    "listPrice" DECIMAL(10,2) NOT NULL,
                    "discountType" VARCHAR(20) NOT NULL,
                    "discountValue" DECIMAL(10,2),
                    "totalPrice" DECIMAL(10,2) NOT NULL,
                    "validityDays" INTEGER,
                    "maxRedemptions" INTEGER,
                    "targetAudience" VARCHAR(20) NOT NULL,
                    category VARCHAR(50),
                    active BOOLEAN DEFAULT 1,
                    "createdAt" DATETIME DEFAULT CURRENT_TIMESTAMP,
                    "updatedAt" DATETIME DEFAULT CURRENT_TIMESTAMP,
                    -- Legacy compatibility fields
                    package_type VARCHAR(50) DEFAULT 'regular',
                    duration_months INTEGER,
                    validity_days INTEGER,
                    total_sessions INTEGER DEFAULT 1,
                    credit_amount REAL DEFAULT 0.0,
                    discount_percentage REAL DEFAULT 0.0,
                    student_discount REAL DEFAULT 0.0,
                    min_guests INTEGER DEFAULT 1,
                    membership_benefits TEXT,
                    sort_order INTEGER DEFAULT 0,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create other new tables
            cursor.execute('''
                CREATE TABLE package_service (
                    "packageId" VARCHAR(50),
                    "serviceId" VARCHAR(50),
                    quantity INTEGER NOT NULL,
                    id INTEGER,
                    package_id VARCHAR(50),
                    service_id VARCHAR(50),
                    sessions_included INTEGER,
                    service_discount REAL DEFAULT 0.0,
                    original_price REAL,
                    discounted_price REAL,
                    PRIMARY KEY ("packageId", "serviceId"),
                    FOREIGN KEY ("packageId") REFERENCES package(id),
                    FOREIGN KEY ("serviceId") REFERENCES service(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE customer (
                    id VARCHAR(50) PRIMARY KEY,
                    name VARCHAR(100) NOT NULL,
                    phone VARCHAR(20),
                    email VARCHAR(120)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE customer_package (
                    id VARCHAR(50) PRIMARY KEY,
                    "customerId" VARCHAR(50) NOT NULL,
                    "packageId" VARCHAR(50) NOT NULL,
                    "purchaseDate" DATETIME DEFAULT CURRENT_TIMESTAMP,
                    "expiryDate" DATETIME,
                    "remainingRedemptions" INTEGER,
                    status VARCHAR(20) NOT NULL,
                    FOREIGN KEY ("customerId") REFERENCES customer(id),
                    FOREIGN KEY ("packageId") REFERENCES package(id)
                )
            ''')
            
            cursor.execute('''
                CREATE TABLE redemption (
                    id VARCHAR(50) PRIMARY KEY,
                    "customerPackageId" VARCHAR(50) NOT NULL,
                    "serviceId" VARCHAR(50) NOT NULL,
                    quantity INTEGER DEFAULT 1,
                    "redeemedAt" DATETIME DEFAULT CURRENT_TIMESTAMP,
                    "staffId" VARCHAR(50),
                    note TEXT,
                    FOREIGN KEY ("customerPackageId") REFERENCES customer_package(id),
                    FOREIGN KEY ("serviceId") REFERENCES service(id)
                )
            ''')
            
            conn.commit()
            conn.close()
            logging.info("Prisma-style database schema created successfully")
            
        except Exception as e:
            logging.error(f"Failed to create new database schema: {e}")
            # Fallback to normal table creation
            db.create_all()
            logging.info("Fallback: Database tables created normally")
    else:
        logging.info("Using existing database")
        
    # Initialize other existing tables for legacy functionality
    try:
        db.create_all()
        logging.info("Legacy tables ensured")
    except Exception as e:
        logging.error(f"Legacy table creation failed: {e}")