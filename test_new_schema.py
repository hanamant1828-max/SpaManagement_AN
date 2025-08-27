#!/usr/bin/env python3
"""
Test script for the new Prisma-style schema models
"""

from app import app, db
from models import Service, Package, PackageService, Customer, CustomerPackage, Redemption
from decimal import Decimal
from datetime import datetime, timedelta

def test_schema():
    """Test the new schema with sample data"""
    with app.app_context():
        try:
            # Create a test service
            service = Service(
                name="Deep Cleansing Facial",
                basePrice=Decimal("75.00"),
                durationMinutes=60,
                active=True
            )
            db.session.add(service)
            db.session.flush()  # Get the ID
            
            print(f"✅ Created service: {service.name} (ID: {service.id})")
            
            # Create a test package
            package = Package(
                name="Wellness Package",
                description="Complete wellness experience",
                listPrice=Decimal("150.00"),
                discountType="PERCENT",
                discountValue=Decimal("20.00"),
                totalPrice=Decimal("120.00"),
                validityDays=90,
                maxRedemptions=3,
                targetAudience="ALL",
                category="Wellness",
                active=True
            )
            db.session.add(package)
            db.session.flush()
            
            print(f"✅ Created package: {package.name} (ID: {package.id})")
            
            # Create package-service relationship
            package_service = PackageService(
                packageId=package.id,
                serviceId=service.id,
                quantity=2
            )
            db.session.add(package_service)
            
            print(f"✅ Created package-service relationship: {package_service.quantity} sessions")
            
            # Create a test customer
            customer = Customer(
                name="Jane Doe",
                phone="+1234567890",
                email="jane.doe@example.com"
            )
            db.session.add(customer)
            db.session.flush()
            
            print(f"✅ Created customer: {customer.name} (ID: {customer.id})")
            
            # Create customer package purchase
            customer_package = CustomerPackage(
                customerId=customer.id,
                packageId=package.id,
                purchaseDate=datetime.utcnow(),
                expiryDate=datetime.utcnow() + timedelta(days=90),
                remainingRedemptions=2,
                status="ACTIVE"
            )
            db.session.add(customer_package)
            db.session.flush()
            
            print(f"✅ Created customer package: {customer_package.id}")
            
            # Create a redemption
            redemption = Redemption(
                customerPackageId=customer_package.id,
                serviceId=service.id,
                quantity=1,
                redeemedAt=datetime.utcnow(),
                staffId="staff_001",
                note="First session redeemed"
            )
            db.session.add(redemption)
            
            print(f"✅ Created redemption: {redemption.id}")
            
            # Commit all changes
            db.session.commit()
            
            # Test queries
            print("\n🔍 Testing queries:")
            
            # Get all services
            services = Service.query.filter_by(active=True).all()
            print(f"📊 Active services: {len(services)}")
            
            # Get all packages
            packages = Package.query.filter_by(active=True).all()
            print(f"📦 Active packages: {len(packages)}")
            
            # Get customer packages
            customer_packages = CustomerPackage.query.filter_by(status="ACTIVE").all()
            print(f"👤 Active customer packages: {len(customer_packages)}")
            
            # Get redemptions
            redemptions = Redemption.query.all()
            print(f"🎫 Total redemptions: {len(redemptions)}")
            
            print("\n✅ Schema test completed successfully!")
            
        except Exception as e:
            print(f"❌ Error during schema test: {e}")
            db.session.rollback()
            raise

if __name__ == "__main__":
    test_schema()