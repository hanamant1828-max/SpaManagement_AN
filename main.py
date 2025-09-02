from app import app
import routes  # noqa: F401

# Import all route modules
from modules.auth import auth_views
from modules.dashboard import dashboard_views
from modules.bookings import bookings_views
from modules.clients import clients_views
from modules.staff import staff_views
from modules.billing import billing_views
from modules.packages import packages_views
from modules.inventory import inventory_views, simple_inventory_views, professional_inventory_views, inventory_category_views, supplier_views
from modules.expenses import expenses_views
from modules.reports import reports_views
from modules.services import services_views, service_category_views
from modules.settings import settings_views
from modules.notifications import notifications_views
from modules.checkin import checkin_views


if __name__ == "__main__":
    print("Starting Flask application on 0.0.0.0:5000")
    app.run(host="0.0.0.0", port=5000, debug=True, threaded=True)