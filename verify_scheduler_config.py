
#!/usr/bin/env python3
"""
Verify scheduler configuration and environment variables
"""
import os
from app import app, PUBLIC_SCHEDULER_IN_DEV, scheduler_required

def verify_config():
    """Verify the scheduler configuration"""
    print("🔍 Scheduler Configuration Verification")
    print("=" * 40)
    
    # Check environment variable
    env_value = os.environ.get('PUBLIC_SCHEDULER_IN_DEV', 'not set')
    print(f"Environment Variable: PUBLIC_SCHEDULER_IN_DEV = {env_value}")
    
    # Check parsed value in app
    print(f"Parsed in App: PUBLIC_SCHEDULER_IN_DEV = {PUBLIC_SCHEDULER_IN_DEV}")
    
    # Check if decorator exists
    try:
        print(f"Decorator Available: scheduler_required = {scheduler_required}")
        print("✅ scheduler_required decorator is available")
    except NameError:
        print("❌ scheduler_required decorator not found")
    
    # Check routes with Flask app context
    with app.app_context():
        scheduler_routes = []
        for rule in app.url_map.iter_rules():
            if 'shift-scheduler' in rule.rule or 'scheduler' in rule.rule:
                scheduler_routes.append(rule.rule)
        
        print(f"\n📍 Scheduler Routes Found ({len(scheduler_routes)}):")
        for route in scheduler_routes:
            print(f"  - {route}")
    
    print(f"\n{'✅ Configuration looks good!' if PUBLIC_SCHEDULER_IN_DEV else '⚠️  Scheduler bypass is disabled'}")

if __name__ == "__main__":
    verify_config()
