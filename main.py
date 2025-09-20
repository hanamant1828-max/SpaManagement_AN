
import os
from app import app

# Set required environment variables if not present
if not os.environ.get("SESSION_SECRET"):
    os.environ["SESSION_SECRET"] = "1578063aca108928c78100b516702a5765d2d05e85b4fb8bb29a75db0bfc34ca"
    print("✅ SESSION_SECRET set")

if not os.environ.get("DATABASE_URL"):
    os.environ["DATABASE_URL"] = "postgresql://replit:postgres@localhost:5432/spa_management"
    print("✅ DATABASE_URL set")

if __name__ == "__main__":
    print("🚀 Starting Spa Management System...")
    print("📡 Server will be available at: http://0.0.0.0:5000")
    print("🌐 Access via webview or browser")
    
    try:
        app.run(host="0.0.0.0", port=5000, debug=True)
    except Exception as e:
        print(f"❌ Failed to start server: {e}")
        print("💡 Try running the migration script first")
