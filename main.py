from app import app
from modules.billing.integrated_billing_views import *
print("✅ Integrated billing views imported")

from modules.billing.billing_reports_views import *
from modules.billing.staff_revenue_report_views import *
from modules.billing.client_revenue_report_views import *
from modules.billing.service_revenue_report_views import *
print("✅ Billing reports views imported")

from modules.clients.clients_views import *
print("✅ Clients views imported")

try:
    from modules.checkin import checkin_views
    from modules.checkin import face_recognition_api
    print("✅ Checkin views imported")
except ImportError as e:
    print(f"⚠️ Checkin views import error: {e}")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)