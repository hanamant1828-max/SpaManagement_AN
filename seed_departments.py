
#!/usr/bin/env python3
"""
Seed departments table with sample data
"""
from app import app, db
from models import Department

def seed_departments():
    """Add sample departments to the database"""
    with app.app_context():
        # Check if departments already exist
        existing_count = Department.query.count()
        if existing_count > 0:
            print(f"Departments table already has {existing_count} entries.")
            return

        # Sample departments for a spa/salon
        departments_data = [
            {
                'name': 'spa_services',
                'display_name': 'Spa Services',
                'description': 'Body treatments, massages, and wellness services',
                'is_active': True
            },
            {
                'name': 'facial_services',
                'display_name': 'Facial Services',
                'description': 'Facial treatments, skincare, and beauty services',
                'is_active': True
            },
            {
                'name': 'hair_salon',
                'display_name': 'Hair Salon',
                'description': 'Hair cutting, styling, and treatments',
                'is_active': True
            },
            {
                'name': 'nail_services',
                'display_name': 'Nail Services',
                'description': 'Manicures, pedicures, and nail art',
                'is_active': True
            },
            {
                'name': 'reception',
                'display_name': 'Reception',
                'description': 'Front desk and customer service',
                'is_active': True
            },
            {
                'name': 'management',
                'display_name': 'Management',
                'description': 'Administrative and management roles',
                'is_active': True
            },
            {
                'name': 'wellness',
                'display_name': 'Wellness Center',
                'description': 'Holistic wellness and therapy services',
                'is_active': True
            }
        ]

        # Add departments to database
        added_count = 0
        for dept_data in departments_data:
            # Check if department with this name already exists
            existing = Department.query.filter_by(name=dept_data['name']).first()
            if not existing:
                dept = Department(**dept_data)
                db.session.add(dept)
                added_count += 1
                print(f"Added department: {dept_data['display_name']}")

        try:
            db.session.commit()
            print(f"Successfully added {added_count} departments to the database.")
        except Exception as e:
            db.session.rollback()
            print(f"Error adding departments: {str(e)}")

if __name__ == '__main__':
    seed_departments()
