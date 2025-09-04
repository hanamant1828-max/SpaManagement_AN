from app import app
import routes  # This already imports all the module views

if __name__ == "__main__":
    print("Starting Flask application on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)