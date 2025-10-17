#!/usr/bin/env python3

import os
import sys

# Set required environment variables if not present
if not os.environ.get("SESSION_SECRET"):
    os.environ["SESSION_SECRET"] = "1578063aca108928c78100b516702a5765d2d05e85b4fb8bb29a75db0bfc34ca"

# DATABASE_URL is automatically set by Replit's PostgreSQL service
if os.environ.get("DATABASE_URL"):
    print("✅ DATABASE_URL available")

# Import app for gunicorn
from app import app  # noqa: F401

# Set PORT from environment if available (for Replit deployment)
port = int(os.environ.get("PORT", 5000))

def main():
    """Main application entry point for development server"""
    print("🚀 Starting Spa Management System...")
    print(f"📡 Server will be available at: http://0.0.0.0:{port}")
    print("🌐 Access via webview or browser")

    try:
        print("✅ App imported successfully")
        # Start the server (development mode)
        app.run(host="0.0.0.0", port=port, debug=True, threaded=True)

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("💡 Check if all required modules are available")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("💡 Check the error details above")
        sys.exit(1)

if __name__ == "__main__":
    main()