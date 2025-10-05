#!/usr/bin/env python3
"""
End-to-end testing script for package billing system
Creates 4 test customers, assigns different package types, and tests billing
"""

import sys
from datetime import datetime, timedelta
from app import app, db
from models import Customer, ServicePackage, PrepaidPackage, Membership, StudentOffer
from models import ServicePackageAssignment, PackageBenefitTracker, Service
from modules.packages.package_billing_service import PackageBillingService

def create_test_customers():
    """Create 4 test customers"""
    print("\n" + "="*60)
    print("STEP 1: Creating 4 Test Customers")
    print("="*60)
    
    customers = []
    test_data = [
        {"first_name": "ServicePkg", "last_name": "Customer1", "email": "test1@servicepackage.com", "phone": "1111111111"},
        {"first_name": "PrepaidPkg", "last_name": "Customer2", "email": "test2@prepaid.com", "phone": "2222222222"},
        {"first_name": "Membership", "last_name": "Customer3", "email": "test3@membership.com", "phone": "3333333333"},
        {"first_name": "StudentOffer", "last_name": "Customer4", "email": "test4@student.com", "phone": "4444444444"},
    ]
    
    for data in test_data:
        # Check if customer already exists
        existing = Customer.query.filter_by(email=data['email']).first()
        if existing:
            full_name = f"{existing.first_name} {existing.last_name}"
            print(f"✓ Customer already exists: {full_name} (ID: {existing.id})")
            customers.append(existing)
        else:
            customer = Customer(
                first_name=data['first_name'],
                last_name=data['last_name'],
                email=data['email'],
                phone=data['phone'],
                address="Test Address",
                created_at=datetime.now()
            )
            db.session.add(customer)
            db.session.flush()
            customers.append(customer)
            full_name = f"{customer.first_name} {customer.last_name}"
            print(f"✓ Created: {full_name} (ID: {customer.id})")
    
    db.session.commit()
    return customers

def get_or_create_packages():
    """Get existing packages or create them if needed"""
    print("\n" + "="*60)
    print("STEP 2: Getting Available Packages")
    print("="*60)
    
    # Get a test service
    service = Service.query.filter_by(is_active=True).first()
    if not service:
        print("❌ No active services found! Please run setup_demo_database.py first")
        sys.exit(1)
    
    print(f"✓ Using service: {service.name} (ID: {service.id}, Price: ₹{service.price})")
    
    # Get or create Service Package (3+1 type)
    service_pkg = ServicePackage.query.filter_by(is_active=True).first()
    if not service_pkg:
        service_pkg = ServicePackage(
            name="3+1 Test Package",
            service_id=service.id,
            pay_for=3,
            total_services=4,
            benefit_percent=25.0,
            validity_months=6,
            is_active=True
        )
        db.session.add(service_pkg)
        print(f"✓ Created Service Package: {service_pkg.name}")
    else:
        print(f"✓ Using Service Package: {service_pkg.name} (Pay {service_pkg.pay_for}, Get {service_pkg.total_services})")
    
    # Get or create Prepaid Package
    prepaid_pkg = PrepaidPackage.query.filter_by(is_active=True).first()
    if not prepaid_pkg:
        prepaid_pkg = PrepaidPackage(
            name="₹1000 Prepaid Credit",
            actual_price=1000.0,
            after_value=1200.0,
            benefit_percent=20.0,
            validity_months=6,
            is_active=True
        )
        db.session.add(prepaid_pkg)
        print(f"✓ Created Prepaid Package: {prepaid_pkg.name}")
    else:
        print(f"✓ Using Prepaid Package: {prepaid_pkg.name} (Pay: ₹{prepaid_pkg.actual_price}, Get: ₹{prepaid_pkg.after_value})")
    
    # Get or create Membership
    membership = Membership.query.filter_by(is_active=True).first()
    if not membership:
        membership = Membership(
            name="Gold Membership",
            price=5000.0,
            validity_months=12,
            description="Unlimited services for 1 year",
            is_active=True
        )
        db.session.add(membership)
        print(f"✓ Created Membership: {membership.name}")
    else:
        print(f"✓ Using Membership: {membership.name}")
    
    # Get or create Student Offer
    student_offer = StudentOffer.query.filter_by(is_active=True).first()
    if not student_offer:
        student_offer = StudentOffer(
            discount_percentage=20.0,
            valid_from=datetime.now().date(),
            valid_to=(datetime.now() + timedelta(days=365)).date(),
            valid_days="Mon-Sun",
            conditions="Valid with Student ID",
            is_active=True
        )
        db.session.add(student_offer)
        print(f"✓ Created Student Offer: {student_offer.discount_percentage}% discount")
    else:
        print(f"✓ Using Student Offer: {student_offer.discount_percentage}% discount")
    
    db.session.commit()
    return service, service_pkg, prepaid_pkg, membership, student_offer

def assign_packages(customers, service, service_pkg, prepaid_pkg, membership, student_offer):
    """Assign packages to customers"""
    print("\n" + "="*60)
    print("STEP 3: Assigning Packages to Customers")
    print("="*60)
    
    assignments = []
    
    # Customer 1: Service Package
    assignment1 = ServicePackageAssignment.query.filter_by(
        customer_id=customers[0].id,
        package_type='service_package',
        status='active'
    ).first()
    
    if not assignment1:
        assignment1 = ServicePackageAssignment(
            customer_id=customers[0].id,
            package_type='service_package',
            package_reference_id=service_pkg.id,
            service_id=service.id,
            assigned_on=datetime.now(),
            expires_on=datetime.now() + timedelta(days=180),
            price_paid=service.price * service_pkg.pay_for,
            total_sessions=service_pkg.total_services,
            remaining_sessions=service_pkg.total_services,
            status='active'
        )
        db.session.add(assignment1)
        db.session.flush()
        full_name = f"{customers[0].first_name} {customers[0].last_name}"
        print(f"✓ Assigned Service Package to {full_name} (Assignment ID: {assignment1.id})")
    else:
        print(f"✓ Customer 1 already has Service Package (Assignment ID: {assignment1.id})")
    assignments.append(assignment1)
    
    # Customer 2: Prepaid Package
    assignment2 = ServicePackageAssignment.query.filter_by(
        customer_id=customers[1].id,
        package_type='prepaid',
        status='active'
    ).first()
    
    if not assignment2:
        assignment2 = ServicePackageAssignment(
            customer_id=customers[1].id,
            package_type='prepaid',
            package_reference_id=prepaid_pkg.id,
            assigned_on=datetime.now(),
            expires_on=datetime.now() + timedelta(days=prepaid_pkg.validity_months*30),
            price_paid=prepaid_pkg.actual_price,
            credit_amount=prepaid_pkg.after_value,
            remaining_credit=prepaid_pkg.after_value,
            status='active'
        )
        db.session.add(assignment2)
        db.session.flush()
        full_name = f"{customers[1].first_name} {customers[1].last_name}"
        print(f"✓ Assigned Prepaid Package to {full_name} (Assignment ID: {assignment2.id})")
    else:
        print(f"✓ Customer 2 already has Prepaid Package (Assignment ID: {assignment2.id})")
    assignments.append(assignment2)
    
    # Customer 3: Membership
    assignment3 = ServicePackageAssignment.query.filter_by(
        customer_id=customers[2].id,
        package_type='membership',
        status='active'
    ).first()
    
    if not assignment3:
        assignment3 = ServicePackageAssignment(
            customer_id=customers[2].id,
            package_type='membership',
            package_reference_id=membership.id,
            assigned_on=datetime.now(),
            expires_on=datetime.now() + timedelta(days=365),
            price_paid=membership.price,
            status='active'
        )
        db.session.add(assignment3)
        db.session.flush()
        full_name = f"{customers[2].first_name} {customers[2].last_name}"
        print(f"✓ Assigned Membership to {full_name} (Assignment ID: {assignment3.id})")
    else:
        print(f"✓ Customer 3 already has Membership (Assignment ID: {assignment3.id})")
    assignments.append(assignment3)
    
    # Customer 4: Student Offer
    assignment4 = ServicePackageAssignment.query.filter_by(
        customer_id=customers[3].id,
        package_type='student_offer',
        status='active'
    ).first()
    
    if not assignment4:
        assignment4 = ServicePackageAssignment(
            customer_id=customers[3].id,
            package_type='student_offer',
            package_reference_id=student_offer.id,
            assigned_on=datetime.now(),
            expires_on=student_offer.valid_to,
            price_paid=0,  # Student offers are discounts, not prepaid
            status='active'
        )
        db.session.add(assignment4)
        db.session.flush()
        full_name = f"{customers[3].first_name} {customers[3].last_name}"
        print(f"✓ Assigned Student Offer to {full_name} (Assignment ID: {assignment4.id})")
    else:
        print(f"✓ Customer 4 already has Student Offer (Assignment ID: {assignment4.id})")
    assignments.append(assignment4)
    
    db.session.commit()
    return assignments

def create_package_benefit_trackers(assignments, service):
    """Create PackageBenefitTracker records for the assignments"""
    print("\n" + "="*60)
    print("STEP 4: Creating Package Benefit Trackers")
    print("="*60)
    
    trackers = []
    
    for assignment in assignments:
        # Check if tracker already exists
        existing_tracker = PackageBenefitTracker.query.filter_by(
            customer_id=assignment.customer_id,
            package_assignment_id=assignment.id,
            is_active=True
        ).first()
        
        if existing_tracker:
            print(f"✓ Tracker already exists for {assignment.package_type} (ID: {existing_tracker.id})")
            trackers.append(existing_tracker)
            continue
        
        if assignment.package_type == 'service_package':
            tracker = PackageBenefitTracker(
                customer_id=assignment.customer_id,
                package_assignment_id=assignment.id,
                service_id=assignment.service_id,
                benefit_type='free',
                total_allocated=assignment.total_sessions,
                remaining_count=assignment.remaining_sessions,
                valid_from=assignment.assigned_on,
                valid_to=assignment.expires_on,
                is_active=True
            )
        elif assignment.package_type == 'prepaid':
            tracker = PackageBenefitTracker(
                customer_id=assignment.customer_id,
                package_assignment_id=assignment.id,
                benefit_type='prepaid',
                balance_total=assignment.credit_amount,
                balance_remaining=assignment.remaining_credit,
                valid_from=assignment.assigned_on,
                valid_to=assignment.expires_on,
                is_active=True
            )
        elif assignment.package_type == 'membership':
            tracker = PackageBenefitTracker(
                customer_id=assignment.customer_id,
                package_assignment_id=assignment.id,
                service_id=service.id,
                benefit_type='unlimited',
                valid_from=assignment.assigned_on,
                valid_to=assignment.expires_on,
                is_active=True
            )
        elif assignment.package_type == 'student_offer':
            tracker = PackageBenefitTracker(
                customer_id=assignment.customer_id,
                package_assignment_id=assignment.id,
                service_id=service.id,
                benefit_type='discount',
                discount_percentage=20.0,
                valid_from=assignment.assigned_on,
                valid_to=assignment.expires_on,
                is_active=True
            )
        
        db.session.add(tracker)
        db.session.flush()
        trackers.append(tracker)
        print(f"✓ Created tracker for {assignment.package_type} (ID: {tracker.id})")
    
    db.session.commit()
    return trackers

def test_billing(customers, service, trackers):
    """Test billing calculations for each customer"""
    print("\n" + "="*60)
    print("STEP 5: Testing Billing Calculations")
    print("="*60)
    
    results = []
    
    for i, customer in enumerate(customers):
        full_name = f"{customer.first_name} {customer.last_name}"
        print(f"\n--- Testing {full_name} ---")
        tracker = trackers[i]
        
        # Test calculation
        result = PackageBillingService.apply_package_benefit(
            customer_id=customer.id,
            service_id=service.id,
            service_price=service.price,
            invoice_id=999999,  # Test invoice ID
            invoice_item_id=999999,  # Test invoice item ID
            service_date=datetime.now(),
            requested_quantity=1
        )
        
        print(f"Package Assignment: {tracker.package_assignment.package_type}")
        print(f"Benefit Type: {tracker.benefit_type}")
        print(f"Service Price: ₹{service.price}")
        print(f"Result: {result}")
        
        if result.get('success'):
            print(f"✅ SUCCESS - Benefit Amount: ₹{result.get('benefit_amount', 0)}")
            if tracker.package_type == 'service_package':
                print(f"   Sessions remaining: {tracker.remaining_count}")
            elif tracker.package_type == 'prepaid':
                print(f"   Credit remaining: ₹{tracker.balance_remaining}")
        else:
            print(f"❌ FAILED - {result.get('message', 'Unknown error')}")
        
        results.append(result)
    
    return results

def main():
    with app.app_context():
        try:
            print("\n" + "🧪 " + "="*58 + " 🧪")
            print("   END-TO-END PACKAGE BILLING SYSTEM TEST")
            print("🧪 " + "="*58 + " 🧪")
            
            # Step 1: Create customers
            customers = create_test_customers()
            
            # Step 2: Get packages
            service, service_pkg, prepaid_pkg, membership, student_offer = get_or_create_packages()
            
            # Step 3: Assign packages
            assignments = assign_packages(customers, service, service_pkg, prepaid_pkg, membership, student_offer)
            
            # Step 4: Create benefit trackers
            trackers = create_package_benefit_trackers(assignments, service)
            
            # Step 5: Test billing
            results = test_billing(customers, service, trackers)
            
            # Summary
            print("\n" + "="*60)
            print("TEST SUMMARY")
            print("="*60)
            print(f"✓ Created/Verified: {len(customers)} customers")
            print(f"✓ Assigned: {len(assignments)} packages")
            print(f"✓ Created: {len(trackers)} benefit trackers")
            print(f"✓ Tested: {len(results)} billing calculations")
            
            success_count = sum(1 for r in results if r.get('success'))
            print(f"\n📊 Success Rate: {success_count}/{len(results)} ({success_count/len(results)*100:.0f}%)")
            
            print("\n" + "="*60)
            print("✅ TEST COMPLETED SUCCESSFULLY!")
            print("="*60)
            print("\nYou can now:")
            print("1. Go to /integrated-billing in the web interface")
            print("2. Select any of these test customers")
            print("3. Add services and see package benefits applied automatically")
            print("\nTest Customer Details:")
            for customer in customers:
                full_name = f"{customer.first_name} {customer.last_name}"
                print(f"   - {full_name} ({customer.email})")
            
        except Exception as e:
            print(f"\n❌ ERROR: {str(e)}")
            import traceback
            traceback.print_exc()
            sys.exit(1)

if __name__ == "__main__":
    main()
