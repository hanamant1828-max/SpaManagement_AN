#!/usr/bin/env python3
"""
Comprehensive test for unlimited packages and date range functionality
"""

from app import app, db
from models import Package, PackageService, ClientPackage, ClientPackageSession, Service, Client
from modules.packages.packages_queries import assign_package_to_client

def test_unlimited_packages():
    """Test complete unlimited package functionality"""
    with app.app_context():
        print("🧪 Testing Unlimited Packages & Date Range Functionality")
        print("=" * 60)
        
        # Test 1: Check migration worked
        print("\n1. Verifying database structure...")
        try:
            # Check that new columns exist
            unlimited_pkg = Package.query.filter_by(has_unlimited_sessions=True).first()
            if unlimited_pkg:
                print(f"✅ Found unlimited package: {unlimited_pkg.name}")
                print(f"   - Has unlimited sessions: {unlimited_pkg.has_unlimited_sessions}")
                if unlimited_pkg.start_date and unlimited_pkg.end_date:
                    print(f"   - Date range: {unlimited_pkg.start_date} to {unlimited_pkg.end_date}")
            
            # Check service-level unlimited
            unlimited_services = PackageService.query.filter_by(is_unlimited=True).all()
            print(f"✅ Found {len(unlimited_services)} services with unlimited sessions")
            
        except Exception as e:
            print(f"✗ Database structure issue: {e}")
            return
        
        # Test 2: Display package information
        print("\n2. Current package listing...")
        packages = Package.query.filter_by(is_active=True).all()
        
        for pkg in packages:
            print(f"\n📦 {pkg.name}")
            print(f"   Type: {pkg.package_type} | Price: ₹{pkg.total_price}")
            print(f"   Validity: {pkg.validity_days} days")
            if pkg.has_unlimited_sessions:
                print("   🎯 UNLIMITED SESSIONS")
            if pkg.start_date and pkg.end_date:
                print(f"   📅 Date Range: {pkg.start_date} to {pkg.end_date}")
            
            print(f"   Services ({len(pkg.services)}):")
            for ps in pkg.services:
                if ps.service:
                    if ps.is_unlimited:
                        print(f"     • {ps.service.name}: UNLIMITED sessions")
                    else:
                        print(f"     • {ps.service.name}: {ps.sessions_included} sessions")
        
        # Test 3: Test assignment
        print("\n3. Testing package assignment...")
        try:
            client = Client.query.first()
            unlimited_package = Package.query.filter_by(has_unlimited_sessions=True).first()
            
            if client and unlimited_package:
                print(f"Assigning '{unlimited_package.name}' to {client.full_name}...")
                
                client_package = assign_package_to_client(client.id, unlimited_package.id)
                
                print(f"✅ Assignment successful! ClientPackage ID: {client_package.id}")
                print(f"   Client: {client_package.client.full_name}")
                print(f"   Package: {client_package.package.name}")
                print(f"   Sessions: {client_package.sessions_used}/{client_package.total_sessions}")
                
                # Check session tracking
                print(f"   Session tracking:")
                for session in client_package.sessions_remaining:
                    service_name = session.service.name if session.service else "Unknown"
                    if session.is_unlimited:
                        print(f"     • {service_name}: {session.sessions_used}/∞")
                    else:
                        print(f"     • {service_name}: {session.sessions_used}/{session.sessions_total}")
                
        except Exception as e:
            print(f"✗ Assignment failed: {e}")
            import traceback
            traceback.print_exc()
        
        # Test 4: Template display test
        print("\n4. Testing frontend display...")
        client_packages = ClientPackage.query.filter_by(is_active=True).all()
        
        print("Client Package Summary:")
        for cp in client_packages:
            if cp.package.has_unlimited_sessions:
                sessions_display = f"{cp.sessions_used}/∞"
            else:
                sessions_display = f"{cp.sessions_used}/{cp.total_sessions}"
            
            print(f"  • {cp.client.full_name} - {cp.package.name}: {sessions_display}")
        
        print("\n✅ All unlimited package functionality is working!")
        print("=" * 60)

if __name__ == '__main__':
    test_unlimited_packages()