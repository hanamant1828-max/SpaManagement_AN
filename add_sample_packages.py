#!/usr/bin/env python3
"""
Add Sample Package Data for Demo
"""
from app import app, db
from models import Package, PackageService, Service, CustomerPackage, Customer, CustomerPackageSession
from datetime import datetime, date, timedelta
import random

def add_sample_packages():
    with app.app_context():
        print("🎁 Creating sample packages for demo...")
        
        # Get services for package creation
        services = Service.query.all()
        customers = Customer.query.all()
        
        if not services:
            print("❌ No services found. Run add_demo_data.py first!")
            return
        
        # Sample packages data
        packages_data = [
            {
                "name": "Bridal Glow Package",
                "description": "Complete bridal preparation package with facial, hair styling, and makeup",
                "package_type": "regular",
                "validity_days": 30,
                "total_price": 25000.00,
                "discount_percentage": 15.0,
                "services": [
                    {"service_name": "Royal Gold Facial", "sessions": 2},
                    {"service_name": "Bridal Makeup & Hair", "sessions": 1},
                    {"service_name": "Anti-Aging Facial", "sessions": 1}
                ]
            },
            {
                "name": "Relaxation Retreat",
                "description": "Monthly wellness package for stress relief and relaxation",
                "package_type": "regular",
                "validity_days": 60,
                "total_price": 12000.00,
                "discount_percentage": 20.0,
                "services": [
                    {"service_name": "Deep Tissue Massage", "sessions": 3},
                    {"service_name": "Aromatherapy Massage", "sessions": 2},
                    {"service_name": "Hot Stone Therapy", "sessions": 1}
                ]
            },
            {
                "name": "Hair Care Combo",
                "description": "Complete hair care package for healthy and beautiful hair",
                "package_type": "regular",
                "validity_days": 90,
                "total_price": 15000.00,
                "discount_percentage": 25.0,
                "services": [
                    {"service_name": "Keratin Hair Treatment", "sessions": 1},
                    {"service_name": "Hair Spa & Styling", "sessions": 3}
                ]
            },
            {
                "name": "Monthly Beauty Package",
                "description": "Regular monthly beauty maintenance package",
                "package_type": "membership",
                "validity_days": 30,
                "total_price": 8000.00,
                "discount_percentage": 10.0,
                "services": [
                    {"service_name": "Express Facial", "sessions": 2},
                    {"service_name": "Gel Manicure & Art", "sessions": 2},
                    {"service_name": "Diamond Pedicure", "sessions": 1}
                ]
            }
        ]
        
        for pkg_data in packages_data:
            # Check if package already exists
            existing_package = Package.query.filter_by(name=pkg_data["name"]).first()
            if existing_package:
                print(f"Package '{pkg_data['name']}' already exists, skipping...")
                continue
            
            # Create package
            package = Package(
                name=pkg_data["name"],
                description=pkg_data["description"],
                package_type=pkg_data["package_type"],
                validity_days=pkg_data["validity_days"],
                duration_months=max(1, pkg_data["validity_days"] // 30),
                total_price=pkg_data["total_price"],
                discount_percentage=pkg_data["discount_percentage"],
                total_sessions=sum(s["sessions"] for s in pkg_data["services"]),
                is_active=True
            )
            db.session.add(package)
            db.session.flush()  # Get package ID
            
            # Add services to package
            for service_data in pkg_data["services"]:
                service = Service.query.filter_by(name=service_data["service_name"]).first()
                if service:
                    # Calculate discounted price
                    original_price = service.price * service_data["sessions"]
                    discount_amount = original_price * (pkg_data["discount_percentage"] / 100)
                    discounted_price = original_price - discount_amount
                    
                    package_service = PackageService(
                        package_id=package.id,
                        service_id=service.id,
                        sessions_included=service_data["sessions"],
                        service_discount=pkg_data["discount_percentage"],
                        original_price=original_price,
                        discounted_price=discounted_price
                    )
                    db.session.add(package_service)
        
        db.session.commit()
        
        # Assign some packages to customers
        if customers:
            packages = Package.query.all()
            print("📋 Assigning packages to customers...")
            
            for _ in range(min(6, len(customers))):  # Assign to first 6 customers
                customer = random.choice(customers)
                package = random.choice(packages)
                
                # Check if customer already has this package
                existing = CustomerPackage.query.filter_by(
                    client_id=customer.id,
                    package_id=package.id,
                    is_active=True
                ).first()
                
                if not existing:
                    # Create customer package
                    expiry_date = datetime.now() + timedelta(days=package.validity_days)
                    
                    customer_package = CustomerPackage(
                        client_id=customer.id,
                        package_id=package.id,
                        purchase_date=datetime.now(),
                        expiry_date=expiry_date,
                        sessions_used=random.randint(0, package.total_sessions // 2),
                        total_sessions=package.total_sessions,
                        amount_paid=package.total_price,
                        is_active=True
                    )
                    db.session.add(customer_package)
                    db.session.flush()
                    
                    # Create session tracking
                    for package_service in package.services:
                        session_track = CustomerPackageSession(
                            client_package_id=customer_package.id,
                            service_id=package_service.service_id,
                            sessions_total=package_service.sessions_included,
                            sessions_used=random.randint(0, package_service.sessions_included // 2)
                        )
                        db.session.add(session_track)
        
        db.session.commit()
        
        print("✅ Sample packages created successfully!")
        print(f"📊 Total packages: {Package.query.count()}")
        print(f"📊 Customer packages: {CustomerPackage.query.count()}")
        print("🎯 Package Management is ready for your demo!")

if __name__ == "__main__":
    add_sample_packages()