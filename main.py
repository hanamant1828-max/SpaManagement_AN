from app import app
from flask_login import login_required
import routes  # This already imports all the module views

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
            
            # Try to restore data from Replit DB if available
            try:
                from replit import db as replit_db
                if 'users' in replit_db and len(replit_db['users']) > 1:  # More than just admin
                    print("🔄 Restoring data from Replit DB...")
                    import subprocess
                    subprocess.run(['python', 'database_migration.py', 'import'], check=False)
                    print("✅ Data restored from Replit DB")
            except Exception as restore_error:
                print(f"Note: Could not restore from Replit DB: {restore_error}")
            
            # Professional inventory views removed
                
    except Exception as e:
        print(f"Warning: Could not initialize default data: {e}")
        print("Application will start with limited functionality")

if __name__ == "__main__":
    print("Starting Spa Management System...")
    initialize_app()
    print("Starting Flask application on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=False, threaded=True)