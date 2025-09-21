from .packages_views import *
from .packages_queries import *

# Register customer packages blueprint
try:
    from .routes import packages_bp
    from app import app
    app.register_blueprint(packages_bp)
    print("Customer packages blueprint registered successfully")
except Exception as e:
    print(f"Error registering customer packages blueprint: {e}")