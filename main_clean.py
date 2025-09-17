from app import app

if __name__ == "__main__":
    print("Starting Spa Management System...")
    print("Skipping initialization to avoid schema conflicts...")
    print("Starting Flask application on 0.0.0.0:5000")
    # Run without initialization to avoid database issues
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)