# Spa & Salon Digital Business Suite

A comprehensive web-based management system for spa and salon businesses with role-based access control, appointment booking, client management, inventory tracking, billing, and advanced business analytics.

## 🌟 Features Overview

### Core Business Modules (13)
1. **Dashboard** - Real-time business metrics and KPIs
2. **Smart Booking & Calendar** - Unified appointment management
3. **Staff Management** - Employee profiles, schedules, and performance
4. **Client Management** - Complete customer profiles and history
5. **Face Recognition Check-In** - Biometric client identification
6. **WhatsApp & Communications** - Multi-channel messaging system
7. **Billing & Payment System** - Invoice generation and payment tracking
8. **Subscription Packages** - Package sales and management
9. **Inventory & Product Tracking** - Stock management with alerts
10. **Reports & Insights** - Business analytics and reporting
11. **User & Access Control** - Role-based permission system
12. **Daily Expense Tracker** - Business expense management
13. **System Management** - Configuration and administration

### Advanced Features
- **Client Communications** - Track all customer interactions
- **Marketing Promotions** - Discount and campaign management
- **Client Waitlist** - Professional queuing system
- **Product Sales (POS)** - Retail sales with inventory sync
- **Recurring Appointments** - Automated scheduling
- **Customer Reviews** - Review collection and analytics
- **Business Settings** - Configurable parameters

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Modern web browser

### Installation

1. **Clone or Download** the project files
2. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
   
3. **Set Environment Variables**:
   ```bash
   export DATABASE_URL="postgresql://user:password@localhost/spa_db"
   export SESSION_SECRET="your-secret-key-here"
   ```

4. **Initialize Database**:
   ```bash
   python create_comprehensive_permissions.py
   python assign_comprehensive_permissions.py
   ```

5. **Start Application**:
   ```bash
   gunicorn --bind 0.0.0.0:5000 --reuse-port --reload main:app
   ```

6. **Access Application**: Open `http://localhost:5000`

## 👤 User Roles & Permissions

### Administrator (Full Access)
- Complete system access with all 132 permissions
- System configuration and role management
- User management and security settings
- Business analytics and reporting

### Manager (75+ Permissions)
- Staff scheduling and performance management
- Client relationship management
- Inventory and supplier management
- Financial reporting and analytics
- Marketing campaign management

### Staff (20+ Permissions)
- Daily appointment management
- Client check-in and service delivery
- Basic inventory viewing
- Point-of-sale operations
- Communication with clients

### Cashier (15+ Permissions)
- Billing and payment processing
- Package sales and redemption
- Product sales (POS)
- Basic reporting for transactions
- Client payment history

## 📱 How to Use

### Dashboard
- **Overview**: Real-time business metrics
- **Today's Stats**: Appointments, revenue, client count
- **Charts**: Revenue trends and appointment analytics
- **Quick Actions**: Access to frequently used features

### Appointment Management
1. **View Calendar**: See all appointments in monthly/weekly view
2. **Book Appointment**: 
   - Select client, service, staff, and time
   - Add notes and special requirements
   - Confirm booking with automatic notifications
3. **Check-In**: Use face recognition or manual check-in
4. **Reschedule**: Drag-and-drop or edit appointment details

### Client Management
1. **Add New Client**:
   - Personal information and contact details
   - Preferences, allergies, and notes
   - Communication preferences
2. **Client History**: View all past appointments and services
3. **Loyalty Tracking**: Monitor visit frequency and spending
4. **Face Registration**: Capture biometric data for check-in

### Staff Management
1. **Staff Profiles**: Personal info, skills, and specialties
2. **Schedule Management**: Set availability and working hours
3. **Performance Tracking**: Monitor bookings and revenue
4. **Commission Tracking**: Calculate and track earnings

### Inventory Management
1. **Product Catalog**: Manage services, products, and supplies
2. **Stock Levels**: Track quantities and set reorder points
3. **Low Stock Alerts**: Automatic notifications for restocking
4. **Supplier Management**: Track vendors and purchase orders

### Billing & Payments
1. **Invoice Generation**: Automatic billing after services
2. **Payment Processing**: Multiple payment methods
3. **Package Sales**: Sell and track service packages
4. **Financial Reports**: Revenue, expenses, and profit analysis

## 🔧 System Administration

### Role Management
1. **Access**: System Management → Role Management
2. **Create Role**: Define new roles with specific permissions
3. **Assign Permissions**: Use dropdown interface to select from 132 permissions
4. **Permission Matrix**: View complete role-permission mapping

### System Configuration
- **Business Settings**: Tax rates, policies, operating hours
- **Categories**: Service types, product categories, expense types
- **Departments**: Organize staff into departments
- **System Settings**: Application-wide configuration

### Data Management
- **Backup**: Regular database backups recommended
- **Reports**: Export data for external analysis
- **Maintenance**: Monitor system performance and logs

## 🛡️ Security Features

- **Role-Based Access Control**: 132 granular permissions
- **CSRF Protection**: Form validation and security
- **Session Management**: Secure user authentication
- **Password Hashing**: Secure credential storage
- **Input Validation**: Prevent malicious data entry

## 📊 Business Analytics

### Dashboard Metrics
- Daily/Monthly revenue tracking
- Appointment completion rates
- Client retention statistics
- Staff performance indicators

### Reports Available
- **Revenue Reports**: Financial performance over time
- **Client Analytics**: Demographics and behavior
- **Staff Performance**: Individual and team metrics
- **Inventory Reports**: Stock levels and usage
- **Custom Reports**: Flexible data analysis

## 💼 Business Workflows

### Daily Operations
1. **Morning Setup**: Check today's appointments and staff schedule
2. **Client Check-In**: Use face recognition or manual process
3. **Service Delivery**: Update appointment status and notes
4. **Payment Processing**: Handle billing and payments
5. **Inventory Updates**: Track product usage and sales

### Weekly Management
- Review staff performance and schedules
- Analyze revenue and client trends
- Update inventory and reorder supplies
- Process staff commissions and payroll

### Monthly Administration
- Generate comprehensive business reports
- Review and update system settings
- Analyze client retention and growth
- Plan marketing campaigns and promotions

## 🔌 API Endpoints

### Role Management
- `GET /role-management` - Role management interface
- `POST /api/roles` - Create new role
- `GET /api/roles/<id>/permissions` - Get role permissions
- `POST /api/roles/<id>/permissions` - Update role permissions
- `DELETE /api/roles/<id>` - Delete role

### System Management
- `GET /system-management` - System configuration
- `POST /api/system/backup` - Create system backup
- `GET /api/system/logs` - View system logs

## 🚨 Troubleshooting

### Common Issues
1. **Database Connection**: Check DATABASE_URL environment variable
2. **Permission Errors**: Verify user role and permissions
3. **Face Recognition**: Ensure camera permissions enabled
4. **Login Issues**: Check username/password and session settings

### Support
- Check system logs for detailed error messages
- Verify all environment variables are set correctly
- Ensure database migrations are complete
- Contact system administrator for role-specific issues

## 📋 License

This software is designed for commercial spa and salon operations. Please ensure compliance with local business regulations and data protection laws.

## 🔄 Updates & Maintenance

- Regular database backups recommended
- Monitor system performance and logs
- Update user permissions as business needs change
- Review and update business settings periodically

---

*For technical support or customization requests, please contact your system administrator.*