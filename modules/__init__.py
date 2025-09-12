"""
Main modules package - imports all module views
"""

# Import all module views to register routes
from .auth import auth_views
from .dashboard import dashboard_views
from .bookings import bookings_views
from .clients import clients_views
from .staff import staff_views
from .inventory import views as inventory_views
from .services import services_views

# Import remaining modules
# from .billing import billing_views  # Removed - billing_views.py deleted
from .expenses import expenses_views
from .settings import settings_views
from .reports import reports_views
from .packages import packages_views
from .checkin import checkin_views
from .notifications import notifications_views
# from .notifications import notifications_views
# from .packages import packages_views
# from .reviews import reviews_views
# from .communications import communications_views
# from .promotions import promotions_views
# from .waitlist import waitlist_views
# from .product_sales import product_sales_views
# from .recurring_appointments import recurring_appointments_views
# from .business_settings import business_settings_views
# from .role_management import role_management_views