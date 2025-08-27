#!/usr/bin/env python3
"""
Add 10 sample services and 10 sample packages to the spa management system
"""
import sys
sys.path.append('.')

from app import app, db
from models import Service, Package, PackageService, Category
from datetime import datetime, date

def add_sample_services():
    """Add 10 realistic spa/salon services"""
    
    # Check if services already exist
    existing_services = Service.query.count()
    if existing_services >= 10:
        print(f"Found {existing_services} existing services. Skipping service creation.")
        return
    
    services_data = [
        {
            'name': 'Deep Tissue Massage',
            'description': 'Therapeutic massage targeting muscle tension and knots using firm pressure',
            'duration': 60,
            'price': 120.00,
            'category': 'Massage Therapy'
        },
        {
            'name': 'Swedish Relaxation Massage', 
            'description': 'Gentle, flowing massage strokes to promote relaxation and stress relief',
            'duration': 60,
            'price': 100.00,
            'category': 'Massage Therapy'
        },
        {
            'name': 'Hot Stone Therapy',
            'description': 'Massage using heated volcanic stones to release muscle tension',
            'duration': 90,
            'price': 150.00,
            'category': 'Massage Therapy'
        },
        {
            'name': 'European Facial',
            'description': 'Classic facial with cleansing, exfoliation, and moisturizing',
            'duration': 75,
            'price': 85.00,
            'category': 'Facial Treatments'
        },
        {
            'name': 'Anti-Aging Facial',
            'description': 'Advanced facial with peptides and collagen boost treatment',
            'duration': 90,
            'price': 130.00,
            'category': 'Facial Treatments'
        },
        {
            'name': 'Hair Cut & Style',
            'description': 'Professional haircut with wash, cut, and styling',
            'duration': 45,
            'price': 65.00,
            'category': 'Hair Services'
        },
        {
            'name': 'Hair Color & Highlights',
            'description': 'Full hair coloring or highlight service with professional products',
            'duration': 120,
            'price': 180.00,
            'category': 'Hair Services'
        },
        {
            'name': 'Manicure & Pedicure',
            'description': 'Complete nail care service including cuticle care and polish',
            'duration': 90,
            'price': 75.00,
            'category': 'Nail Services'
        },
        {
            'name': 'Body Wrap Treatment',
            'description': 'Detoxifying body wrap with natural ingredients and moisturizers',
            'duration': 90,
            'price': 110.00,
            'category': 'Body Treatments'
        },
        {
            'name': 'Eyebrow Threading & Tinting',
            'description': 'Precision eyebrow shaping and tinting service',
            'duration': 30,
            'price': 45.00,
            'category': 'Beauty Services'
        }
    ]
    
    print("Creating sample services...")
    created_services = []
    
    for service_data in services_data:
        service = Service(
            name=service_data['name'],
            description=service_data['description'],
            duration=service_data['duration'],
            price=service_data['price'],
            category=service_data['category'],
            is_active=True,
            created_at=datetime.utcnow()
        )
        db.session.add(service)
        created_services.append(service)
    
    try:
        db.session.commit()
        print(f"✅ Successfully created {len(created_services)} services!")
        for service in created_services:
            print(f"   • {service.name} - ${service.price:.2f} ({service.duration} min)")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating services: {e}")
        return []
    
    return created_services

def add_sample_packages():
    """Add 10 realistic spa/salon packages"""
    
    # Check if packages already exist
    existing_packages = Package.query.count()
    if existing_packages >= 10:
        print(f"Found {existing_packages} existing packages. Skipping package creation.")
        return
    
    # Get created services
    services = Service.query.all()
    if len(services) < 10:
        print("Not enough services found. Please create services first.")
        return
    
    packages_data = [
        {
            'name': 'Relaxation Retreat Package',
            'description': 'Perfect combination of massage and facial for complete relaxation',
            'package_type': 'regular',
            'duration_months': 3,
            'validity_days': 90,
            'total_sessions': 4,
            'total_price': 350.00,
            'discount_percentage': 15.0,
            'services': [
                {'name': 'Swedish Relaxation Massage', 'sessions': 2},
                {'name': 'European Facial', 'sessions': 2}
            ]
        },
        {
            'name': 'Luxury Spa Experience',
            'description': 'Premium spa package with hot stone massage and anti-aging facial',
            'package_type': 'regular',
            'duration_months': 6,
            'validity_days': 180,
            'total_sessions': 6,
            'total_price': 750.00,
            'discount_percentage': 20.0,
            'services': [
                {'name': 'Hot Stone Therapy', 'sessions': 3},
                {'name': 'Anti-Aging Facial', 'sessions': 3}
            ]
        },
        {
            'name': 'Monthly Maintenance Package',
            'description': 'Regular monthly treatments to maintain your wellness routine',
            'package_type': 'membership',
            'duration_months': 12,
            'validity_days': 365,
            'total_sessions': 12,
            'total_price': 1200.00,
            'discount_percentage': 25.0,
            'services': [
                {'name': 'Deep Tissue Massage', 'sessions': 6},
                {'name': 'European Facial', 'sessions': 6}
            ]
        },
        {
            'name': 'Hair Transformation Package',
            'description': 'Complete hair makeover with cut, color, and styling sessions',
            'package_type': 'regular',
            'duration_months': 4,
            'validity_days': 120,
            'total_sessions': 3,
            'total_price': 280.00,
            'discount_percentage': 12.0,
            'services': [
                {'name': 'Hair Cut & Style', 'sessions': 2},
                {'name': 'Hair Color & Highlights', 'sessions': 1}
            ]
        },
        {
            'name': 'Bridal Beauty Package',
            'description': 'Complete bridal preparation package for your special day',
            'package_type': 'regular',
            'duration_months': 2,
            'validity_days': 60,
            'total_sessions': 5,
            'total_price': 450.00,
            'discount_percentage': 18.0,
            'services': [
                {'name': 'Anti-Aging Facial', 'sessions': 2},
                {'name': 'Hair Cut & Style', 'sessions': 1},
                {'name': 'Manicure & Pedicure', 'sessions': 2}
            ]
        },
        {
            'name': 'Student Wellness Package',
            'description': 'Affordable wellness package designed for students',
            'package_type': 'student_offer',
            'duration_months': 3,
            'validity_days': 90,
            'total_sessions': 6,
            'total_price': 300.00,
            'discount_percentage': 30.0,
            'student_discount': 10.0,
            'services': [
                {'name': 'Swedish Relaxation Massage', 'sessions': 3},
                {'name': 'European Facial', 'sessions': 3}
            ]
        },
        {
            'name': 'Girls Night Out Package',
            'description': 'Perfect package for group celebrations and parties',
            'package_type': 'kitty_party',
            'duration_months': 1,
            'validity_days': 30,
            'total_sessions': 8,
            'total_price': 600.00,
            'discount_percentage': 22.0,
            'min_guests': 4,
            'services': [
                {'name': 'Manicure & Pedicure', 'sessions': 4},
                {'name': 'Eyebrow Threading & Tinting', 'sessions': 4}
            ]
        },
        {
            'name': 'Prepaid Wellness Credits',
            'description': 'Flexible prepaid package - use credits for any service',
            'package_type': 'prepaid',
            'duration_months': 12,
            'validity_days': 365,
            'total_sessions': 1,
            'total_price': 500.00,
            'credit_amount': 550.00,
            'discount_percentage': 0.0,
            'services': []
        },
        {
            'name': 'Body Rejuvenation Package',
            'description': 'Full body treatment package focusing on detox and rejuvenation',
            'package_type': 'regular',
            'duration_months': 3,
            'validity_days': 90,
            'total_sessions': 4,
            'total_price': 420.00,
            'discount_percentage': 15.0,
            'services': [
                {'name': 'Body Wrap Treatment', 'sessions': 2},
                {'name': 'Deep Tissue Massage', 'sessions': 2}
            ]
        },
        {
            'name': 'Executive Stress Relief',
            'description': 'Premium package designed for busy professionals',
            'package_type': 'membership',
            'duration_months': 6,
            'validity_days': 180,
            'total_sessions': 8,
            'total_price': 850.00,
            'discount_percentage': 20.0,
            'membership_benefits': '{"priority_booking": true, "complimentary_refreshments": true, "extended_hours": true}',
            'services': [
                {'name': 'Deep Tissue Massage', 'sessions': 4},
                {'name': 'Hot Stone Therapy', 'sessions': 2},
                {'name': 'Anti-Aging Facial', 'sessions': 2}
            ]
        }
    ]
    
    print("Creating sample packages...")
    created_packages = []
    
    for pkg_data in packages_data:
        # Create the package
        package = Package(
            name=pkg_data['name'],
            description=pkg_data['description'],
            package_type=pkg_data['package_type'],
            duration_months=pkg_data['duration_months'],
            validity_days=pkg_data['validity_days'],
            total_sessions=pkg_data['total_sessions'],
            total_price=pkg_data['total_price'],
            discount_percentage=pkg_data['discount_percentage'],
            student_discount=pkg_data.get('student_discount', 0.0),
            min_guests=pkg_data.get('min_guests', 1),
            credit_amount=pkg_data.get('credit_amount', 0.0),
            membership_benefits=pkg_data.get('membership_benefits'),
            is_active=True,
            created_at=datetime.utcnow()
        )
        
        db.session.add(package)
        db.session.flush()  # Get the package ID
        
        # Add package services
        for service_data in pkg_data['services']:
            service = Service.query.filter_by(name=service_data['name']).first()
            if service:
                package_service = PackageService(
                    package_id=package.id,
                    service_id=service.id,
                    sessions_included=service_data['sessions'],
                    service_discount=0.0,
                    original_price=service.price,
                    discounted_price=service.price
                )
                db.session.add(package_service)
        
        created_packages.append(package)
    
    try:
        db.session.commit()
        print(f"✅ Successfully created {len(created_packages)} packages!")
        for package in created_packages:
            print(f"   • {package.name} - ${package.total_price:.2f} ({package.package_type})")
    except Exception as e:
        db.session.rollback()
        print(f"❌ Error creating packages: {e}")
        return []
    
    return created_packages

def main():
    """Main function to add sample data"""
    with app.app_context():
        print("🏨 Adding sample data to Spa Management System...")
        print("=" * 60)
        
        # Add services first
        services = add_sample_services()
        print()
        
        # Add packages
        packages = add_sample_packages()
        print()
        
        print("=" * 60)
        print("✅ Sample data creation completed!")
        print(f"   Total Services: {Service.query.count()}")
        print(f"   Total Packages: {Package.query.count()}")

if __name__ == "__main__":
    main()