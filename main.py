from app import app
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
            
            # Import additional inventory views
            try:
                import modules.inventory.inventory_category_views  # noqa: F401
                import modules.inventory.inventory_views  # noqa: F401
                print("Additional inventory views loaded successfully")
            except ImportError as e:
                print(f"Warning: Could not load additional inventory views: {e}")
                
    except Exception as e:
        print(f"Warning: Could not initialize default data: {e}")
        print("Application will start with limited functionality")

if __name__ == "__main__":
    print("Starting Spa Management System...")
    initialize_app()
    print("Starting Flask application on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)