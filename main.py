from app import app
from flask_login import login_required
import routes  # This already imports all the module views
import os

# Import integrated billing views
try:
    import modules.billing.integrated_billing_views
    print("Integrated billing views loaded successfully")
except ImportError as e:
    print(f"Warning: Could not load integrated billing views: {e}")

# Initialize default data and routes in a more robust way
def initialize_app():
    try:
        with app.app_context():
            print("Initializing default data...")
            from routes import create_default_data
            create_default_data()
            
            # Always ensure demo data is populated for fresh installations
            try:
                from models import User
                user_count = User.query.count()
                if user_count <= 1:  # Only admin or no users
                    print("🔄 Populating demo data for fresh installation...")
                    import subprocess
                    result = subprocess.run(['python', 'populate_local_demo_data.py'], 
                                          capture_output=True, text=True, check=False)
                    if result.returncode == 0:
                        print("✅ Demo data populated successfully")
                    else:
                        print(f"⚠️ Demo data population warning: {result.stderr}")
                else:
                    print(f"✅ Database has {user_count} users - demo data already present")
            except Exception as demo_error:
                print(f"Note: Could not populate demo data: {demo_error}")
                
    except Exception as e:
        print(f"Warning: Could not initialize default data: {e}")
        print("Application will start with limited functionality")

if __name__ == "__main__":
    print("Starting Spa Management System...")
    initialize_app()
    # Use Replit's PORT environment variable or default to 5000
    port = int(os.environ.get('PORT', 5000))
    print(f"Starting Flask application on 0.0.0.0:{port}")
    # Configure for Replit deployment
    app.run(
        host="0.0.0.0", 
        port=port, 
        debug=False, 
        threaded=True,
        use_reloader=False
    )