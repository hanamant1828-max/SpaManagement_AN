
from app import app, db
from models import Category

def create_expense_categories():
    """Create expense categories for spa operations"""
    
    expense_categories = [
        {
            'name': 'office_supplies',
            'display_name': 'Office Supplies',
            'description': 'Paper, pens, stationery, printing materials',
            'category_type': 'expense',
            'color': '#6c757d',
            'icon': 'fas fa-paperclip'
        },
        {
            'name': 'spa_products',
            'display_name': 'Spa Products',
            'description': 'Oils, creams, towels, spa consumables',
            'category_type': 'expense',
            'color': '#28a745',
            'icon': 'fas fa-spa'
        },
        {
            'name': 'client_refreshments',
            'display_name': 'Client Refreshments',
            'description': 'Tea, coffee, snacks for clients',
            'category_type': 'expense',
            'color': '#fd7e14',
            'icon': 'fas fa-coffee'
        },
        {
            'name': 'equipment_maintenance',
            'display_name': 'Equipment Maintenance',
            'description': 'Repairs, servicing of spa equipment',
            'category_type': 'expense',
            'color': '#dc3545',
            'icon': 'fas fa-tools'
        },
        {
            'name': 'utilities',
            'display_name': 'Utilities',
            'description': 'Electricity, water, internet bills',
            'category_type': 'expense',
            'color': '#17a2b8',
            'icon': 'fas fa-bolt'
        },
        {
            'name': 'transportation',
            'display_name': 'Transportation',
            'description': 'Travel expenses, fuel, taxi fares',
            'category_type': 'expense',
            'color': '#6f42c1',
            'icon': 'fas fa-car'
        },
        {
            'name': 'marketing',
            'display_name': 'Marketing & Advertising',
            'description': 'Promotional materials, advertisements',
            'category_type': 'expense',
            'color': '#e83e8c',
            'icon': 'fas fa-bullhorn'
        },
        {
            'name': 'staff_meals',
            'display_name': 'Staff Meals',
            'description': 'Food and beverages for staff',
            'category_type': 'expense',
            'color': '#20c997',
            'icon': 'fas fa-utensils'
        },
        {
            'name': 'cleaning_supplies',
            'display_name': 'Cleaning Supplies',
            'description': 'Sanitizers, detergents, cleaning equipment',
            'category_type': 'expense',
            'color': '#ffc107',
            'icon': 'fas fa-spray-can'
        },
        {
            'name': 'miscellaneous',
            'display_name': 'Miscellaneous',
            'description': 'Other unexpected expenses',
            'category_type': 'expense',
            'color': '#6c757d',
            'icon': 'fas fa-question-circle'
        }
    ]
    
    with app.app_context():
        for cat_data in expense_categories:
            existing = Category.query.filter_by(name=cat_data['name']).first()
            if not existing:
                category = Category(**cat_data)
                db.session.add(category)
                print(f"Created category: {cat_data['display_name']}")
            else:
                print(f"Category already exists: {cat_data['display_name']}")
        
        db.session.commit()
        print("✅ All expense categories created successfully!")

if __name__ == '__main__':
    create_expense_categories()
