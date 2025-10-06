
#!/usr/bin/env python3
"""
Test script for student offer billing functionality
"""
from app import app, db
from models import Customer, StudentOffer, ServicePackageAssignment, Service
from datetime import datetime, timedelta

def test_student_offer_billing():
    """Test student offer creation, assignment, and billing"""
    
    with app.app_context():
        print("=" * 60)
        print("STUDENT OFFER BILLING TEST")
        print("=" * 60)
        
        # Step 1: Create a test customer
        print("\n1️⃣ Creating test customer...")
        test_customer = Customer(
            first_name="Student",
            last_name="TestUser",
            phone="9999999999",
            email="student.test@example.com",
            is_active=True
        )
        db.session.add(test_customer)
        db.session.commit()
        print(f"✅ Created customer: {test_customer.full_name} (ID: {test_customer.id})")
        
        # Step 2: Check if student offer exists or create one
        print("\n2️⃣ Checking for student offer...")
        student_offer = StudentOffer.query.filter_by(is_active=True).first()
        
        if not student_offer:
            print("Creating new student offer...")
            student_offer = StudentOffer(
                discount_percentage=30.0,
                valid_from=datetime.now().date(),
                valid_to=(datetime.now() + timedelta(days=180)).date(),
                valid_days="Mon-Fri",
                conditions="Valid with Student ID only",
                is_active=True
            )
            db.session.add(student_offer)
            db.session.commit()
            print(f"✅ Created student offer with 30% discount (ID: {student_offer.id})")
        else:
            print(f"✅ Using existing student offer: {student_offer.discount_percentage}% discount (ID: {student_offer.id})")
        
        # Step 3: Assign student offer to customer
        print("\n3️⃣ Assigning student offer to customer...")
        assignment = ServicePackageAssignment(
            customer_id=test_customer.id,
            package_type='student_offer',
            package_reference_id=student_offer.id,
            service_id=None,  # Student offers apply to all services
            assigned_on=datetime.utcnow(),
            expires_on=student_offer.valid_to,
            price_paid=0.0,  # Student offers are free discounts
            discount=0.0,
            status='active',
            notes='Test assignment for student offer billing',
            total_sessions=0,
            used_sessions=0,
            remaining_sessions=0,
            credit_amount=0,
            used_credit=0,
            remaining_credit=0
        )
        db.session.add(assignment)
        db.session.commit()
        print(f"✅ Assigned student offer to {test_customer.full_name}")
        
        # Step 4: Display test billing scenario
        print("\n4️⃣ Test Billing Scenario:")
        print("-" * 60)
        
        # Get a sample service
        sample_service = Service.query.filter_by(is_active=True).first()
        if sample_service:
            original_price = float(sample_service.price)
            discount_amount = (original_price * student_offer.discount_percentage) / 100
            final_price = original_price - discount_amount
            
            print(f"Service: {sample_service.name}")
            print(f"Original Price: ₹{original_price:.2f}")
            print(f"Student Discount ({student_offer.discount_percentage}%): -₹{discount_amount:.2f}")
            print(f"Final Price: ₹{final_price:.2f}")
        
        print("\n5️⃣ Test Instructions:")
        print("-" * 60)
        print(f"1. Go to Integrated Billing page")
        print(f"2. Select customer: {test_customer.full_name} (Phone: {test_customer.phone})")
        print(f"3. Add any service to the billing")
        print(f"4. Verify that the student discount ({student_offer.discount_percentage}%) is automatically applied")
        print(f"5. Check that 'Package Benefits' shows the discount amount")
        print(f"6. Complete the billing and verify the invoice")
        
        print("\n" + "=" * 60)
        print("✅ TEST SETUP COMPLETE")
        print("=" * 60)
        
        return {
            'customer_id': test_customer.id,
            'customer_name': test_customer.full_name,
            'offer_id': student_offer.id,
            'discount_percentage': student_offer.discount_percentage,
            'assignment_id': assignment.id
        }

if __name__ == '__main__':
    result = test_student_offer_billing()
    print(f"\nTest customer ID: {result['customer_id']}")
    print(f"Student offer discount: {result['discount_percentage']}%")
