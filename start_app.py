
#!/usr/bin/env python3

import os
import sys

# Set required environment variables
os.environ["SESSION_SECRET"] = "1578063aca108928c78100b516702a5765d2d05e85b4fb8bb29a75db0bfc34ca"
os.environ["DATABASE_URL"] = "postgresql://replit:postgres@localhost:5432/spa_management"

print("🚀 Starting Spa Management System...")
print("📡 Environment configured")

try:
    from app import app
    print("✅ App imported successfully")
    
    # Start the server
    app.run(host="0.0.0.0", port=5000, debug=True)
    
except Exception as e:
    print(f"❌ Error starting app: {e}")
    print("💡 Trying alternative startup method...")
    
    # Alternative startup
    import subprocess
    subprocess.run([sys.executable, "main.py"])
