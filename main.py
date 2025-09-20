#!/usr/bin/env python3
import os

# Set required environment variables if not already set
if not os.environ.get("SESSION_SECRET"):
    os.environ["SESSION_SECRET"] = "1578063aca108928c78100b516702a5765d2d05e85b4fb8bb29a75db0bfc34ca"

if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "sqlite:///instance/spa_management.db"

from app import app

if __name__ == "__main__":
    print("Starting Spa Management System...")
    print("Starting Flask application on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)