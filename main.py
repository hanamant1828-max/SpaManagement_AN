from app import app
import routes  # This already imports all the module views

# Initialize default data and routes
try:
    with app.app_context():
        from routes import create_default_data
        create_default_data()
        
        # Import inventory views
        import modules.inventory.inventory_category_views  # noqa: F401
        import modules.inventory.inventory_views  # noqa: F401
        
except Exception as e:
    print(f"Warning: Could not initialize default data: {e}")

if __name__ == "__main__":
    print("Starting Flask application on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)