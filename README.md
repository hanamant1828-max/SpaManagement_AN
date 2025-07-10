# Spa & Salon Digital Business Suite

A comprehensive web-based management system for spa and salon businesses, built with Flask and featuring all essential business operations.

## 🌟 Features

### Complete Business Management (13 Modules)
1. **Dashboard** - Real-time business overview with analytics
2. **Smart Booking & Calendar** - Appointment management with color coding
3. **Staff Management** - Employee profiles, schedules, and performance
4. **Client History & Loyalty** - Complete customer profiles and tracking
5. **Face Recognition Check-In** - AI-powered customer check-in system
6. **WhatsApp Notifications** - Automated appointment reminders and alerts
7. **Billing & Payment System** - Invoice generation and payment tracking
8. **Subscription Packages** - Prepaid service bundles management
9. **Inventory & Product Tracking** - Stock management with alerts
10. **Reports & Insights** - Business analytics with charts and trends
11. **User & Access Control** - Role-based permissions and security
12. **Daily Expense Tracker** - Business expense categorization
13. **Expiring Product Alerts** - Product safety and quality control

### Technical Features
- 🎨 **Modern UI** - Professional dark theme with vertical sidebar navigation
- 📱 **Mobile Responsive** - Works seamlessly on all devices
- 🔐 **Secure Authentication** - Role-based access control
- 📊 **Real-time Analytics** - Dashboard with live business metrics
- 🗄️ **PostgreSQL Database** - Robust data storage with relationships
- ⚡ **Performance Optimized** - Connection pooling and health checks

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- PostgreSQL database
- Environment variables (see below)

### Installation

1. **Clone the repository**
   ```bash
   git clone https://github.com/santu5496/SpaManagement.git
   cd SpaManagement
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Set environment variables**
   ```bash
   export SESSION_SECRET="your-secret-key-here"
   export DATABASE_URL="postgresql://user:password@localhost/spa_db"
   ```

4. **Run the application**
   ```bash
   python main.py
   ```

5. **Access the application**
   - Open http://localhost:5000
   - Login with: `admin` / `admin123`

## 🏗️ Architecture

### Backend (Flask)
- **Framework**: Flask with SQLAlchemy ORM
- **Authentication**: Flask-Login with role-based access
- **Forms**: WTForms with CSRF protection
- **Database**: PostgreSQL with automatic table creation

### Frontend
- **UI Framework**: Bootstrap 5 with dark theme
- **Icons**: Font Awesome 6.4.0
- **Charts**: Chart.js for data visualization
- **Layout**: Responsive vertical sidebar navigation

### Database Models
- **User** - Staff and admin accounts with roles
- **Client** - Customer profiles with history
- **Service** - Available treatments and pricing
- **Appointment** - Booking management with status
- **Inventory** - Product and supply tracking
- **Expense** - Business cost management
- **Package** - Subscription service bundles

## 📊 User Roles

### Administrator
- Full system access
- User management
- Financial reports
- System settings

### Manager
- Staff scheduling
- Client management
- Inventory oversight
- Basic reporting

### Staff
- Appointment handling
- Client check-in
- Service recording
- Basic inventory updates

### Cashier
- Payment processing
- Invoice generation
- Basic client lookup
- Daily transactions

## 🔧 Configuration

### Environment Variables
```bash
SESSION_SECRET=your-super-secret-key
DATABASE_URL=postgresql://username:password@host:port/database
```

### Database Setup
The application automatically creates all required tables on first run. Default admin user is created with credentials: `admin` / `admin123`

## 📱 Mobile Support

The application is fully responsive with:
- Collapsible sidebar navigation
- Touch-friendly interface
- Optimized forms and tables
- Mobile-first design approach

## 🛡️ Security Features

- Password hashing with Werkzeug
- CSRF protection on all forms
- Role-based access control
- Session management
- SQL injection prevention

## 📈 Business Intelligence

### Dashboard Analytics
- Today's revenue and appointments
- Monthly trends and comparisons
- Staff performance metrics
- Client retention statistics

### Reporting Features
- Customizable date ranges
- Export to CSV functionality
- Print-friendly layouts
- Visual charts and graphs

## 🔔 Notification System

### WhatsApp Integration (Ready)
- Appointment reminders
- Package expiry alerts
- Thank you messages
- Promotional offers

### System Alerts
- Low stock notifications
- Expiring product warnings
- Upcoming appointment reminders
- Payment due alerts

## 📦 Deployment

### Replit Deployment
1. Fork this repository to Replit
2. Set environment variables in Secrets
3. Run the application
4. Use Replit's deployment feature for production

### Traditional Hosting
1. Set up PostgreSQL database
2. Configure environment variables
3. Install dependencies
4. Run with Gunicorn for production

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For support and questions:
- Create an issue in this repository
- Check the documentation in `replit.md`
- Review the code comments for implementation details

## 🎯 Future Enhancements

- Integration with payment gateways
- Advanced face recognition features
- WhatsApp API integration
- Mobile app development
- Advanced analytics and AI insights

---

**Built with ❤️ for the spa and salon industry**