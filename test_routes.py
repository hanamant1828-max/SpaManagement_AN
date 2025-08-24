
#!/usr/bin/env python3
"""
Test routes to identify redirect loops
"""
from app import app

def test_routes():
    """Test all registered routes"""
    with app.app_context():
        print("Registered Routes:")
        print("=" * 50)
        
        for rule in app.url_map.iter_rules():
            print(f"{rule.rule:30} -> {rule.endpoint}")
        
        # Check for duplicate routes
        routes = {}
        duplicates = []
        
        for rule in app.url_map.iter_rules():
            if rule.rule in routes:
                duplicates.append((rule.rule, routes[rule.rule], rule.endpoint))
            else:
                routes[rule.rule] = rule.endpoint
        
        if duplicates:
            print("\nDuplicate Routes Found:")
            print("=" * 50)
            for route, first_endpoint, second_endpoint in duplicates:
                print(f"Route: {route}")
                print(f"  First:  {first_endpoint}")
                print(f"  Second: {second_endpoint}")
        else:
            print("\nNo duplicate routes found.")

if __name__ == "__main__":
    test_routes()
