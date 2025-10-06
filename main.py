#!/usr/bin/env python3

import os
import sys
import logging

# Set up basic logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Database will be configured from DATABASE_URL environment variable

# Set PORT from environment if available (for Replit deployment)
port = int(os.environ.get("PORT", 5000))

# Import app at module level for gunicorn/WSGI compatibility
from app import app

def main():
    """Main application entry point with crash guards"""
    logger.info("🚀 Starting Spa Management System...")
    logger.info(f"📡 Server will be available at: http://0.0.0.0:{port}")
    logger.info("🌐 Access via webview or browser")

    try:
        logger.info("✅ App imported successfully")

        # Start the server with host configuration for Replit
        logger.info("🚀 Starting Flask development server...")
        # Configure for Replit proxy compatibility
        app.run(host="0.0.0.0", port=port, debug=True, threaded=True, use_reloader=False)

    except ImportError as e:
        logger.error(f"❌ Import error: {e}")
        logger.error("💡 Check if all required modules are available")
        sys.exit(1)
    except Exception as e:
        logger.error(f"❌ Failed to start server: {e}")
        logger.error("💡 Check the error details above")
        sys.exit(1)

if __name__ == "__main__":
    main()