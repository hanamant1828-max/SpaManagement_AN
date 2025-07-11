# Installation Guide - Spa & Salon Digital Business Suite

## System Requirements

### Hardware Requirements
- **Minimum**: 2GB RAM, 10GB storage, dual-core processor
- **Recommended**: 4GB+ RAM, 50GB+ storage, quad-core processor
- **Network**: Stable internet connection for cloud deployment

### Software Requirements
- **Operating System**: Linux (Ubuntu 20.04+), macOS, or Windows 10+
- **Python**: Version 3.11 or higher
- **Database**: PostgreSQL 12+ or SQLite (development only)
- **Web Browser**: Chrome 90+, Firefox 88+, Safari 14+, Edge 90+

## Installation Methods

### Method 1: Local Development Setup

#### 1. Download Project Files
```bash
# If using git
git clone <repository-url>
cd spa-salon-management

# Or download and extract ZIP file
```

#### 2. Create Virtual Environment
```bash
# Create virtual environment
python -m venv spa_env

# Activate virtual environment
# On Linux/macOS:
source spa_env/bin/activate
# On Windows:
spa_env\Scripts\activate
```

#### 3. Install Dependencies
```bash
# Install all required packages
pip install -r requirements.txt

# Or install manually:
pip install flask flask-sqlalchemy flask-login flask-wtf
pip install gunicorn psycopg2-binary werkzeug wtforms
pip install email-validator flask-dance oauthlib pyjwt
```

#### 4. Database Setup

**Option A: PostgreSQL (Recommended for Production)**
```bash
# Install PostgreSQL
sudo apt-get install postgresql postgresql-contrib  # Ubuntu
brew install postgresql  # macOS

# Create database
sudo -u postgres createdb spa_salon_db
sudo -u postgres createuser spa_user
sudo -u postgres psql -c "ALTER USER spa_user WITH PASSWORD 'secure_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE spa_salon_db TO spa_user;"
```

**Option B: SQLite (Development Only)**
```bash
# SQLite will be created automatically
```

#### 5. Environment Configuration
```bash
# Create .env file
cat << EOF > .env
DATABASE_URL=postgresql://spa_user:secure_password@localhost/spa_salon_db
SESSION_SECRET=your-very-secure-secret-key-here-make-it-long-and-random
FLASK_ENV=development
FLASK_DEBUG=True
EOF

# Or set environment variables directly
export DATABASE_URL="postgresql://spa_user:secure_password@localhost/spa_salon_db"
export SESSION_SECRET="your-very-secure-secret-key-here"
```

#### 6. Initialize Database
```bash
# Run database initialization scripts
python create_comprehensive_permissions.py
python assign_comprehensive_permissions.py

# Create default admin user (optional)
python -c "
from app import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    admin = User(
        username='admin',
        email='admin@spa.local',
        password_hash=generate_password_hash('admin123'),
        full_name='System Administrator',
        role_id=1,  # Admin role
        is_active=True
    )
    db.session.add(admin)
    db.session.commit()
    print('Admin user created: admin/admin123')
"
```

#### 7. Start Application
```bash
# Development server
python main.py

# Or using Gunicorn (recommended)
gunicorn --bind 0.0.0.0:5000 --reload main:app

# Access application at http://localhost:5000
```

### Method 2: Production Deployment

#### 1. Server Setup (Ubuntu 20.04+)
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv postgresql postgresql-contrib nginx supervisor

# Create application user
sudo useradd -m -s /bin/bash spa
sudo su - spa
```

#### 2. Application Setup
```bash
# Clone application
git clone <repository-url> spa-salon-app
cd spa-salon-app

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

#### 3. Database Configuration
```bash
# PostgreSQL setup
sudo -u postgres createdb spa_production
sudo -u postgres createuser spa_prod_user
sudo -u postgres psql -c "ALTER USER spa_prod_user WITH PASSWORD 'very_secure_production_password';"
sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE spa_production TO spa_prod_user;"
```

#### 4. Environment Variables
```bash
# Create production environment file
cat << EOF > /home/spa/spa-salon-app/.env
DATABASE_URL=postgresql://spa_prod_user:very_secure_production_password@localhost/spa_production
SESSION_SECRET=$(openssl rand -base64 32)
FLASK_ENV=production
FLASK_DEBUG=False
EOF
```

#### 5. Initialize Production Database
```bash
cd /home/spa/spa-salon-app
source venv/bin/activate
python create_comprehensive_permissions.py
python assign_comprehensive_permissions.py
```

#### 6. Gunicorn Configuration
```bash
# Create Gunicorn configuration
cat << EOF > /home/spa/spa-salon-app/gunicorn.conf.py
bind = "127.0.0.1:5000"
workers = 4
worker_class = "sync"
worker_connections = 1000
max_requests = 1000
max_requests_jitter = 100
preload_app = True
timeout = 30
keepalive = 2
user = "spa"
group = "spa"
EOF
```

#### 7. Supervisor Configuration
```bash
# Create supervisor configuration
sudo cat << EOF > /etc/supervisor/conf.d/spa-salon.conf
[program:spa-salon]
command=/home/spa/spa-salon-app/venv/bin/gunicorn main:app -c /home/spa/spa-salon-app/gunicorn.conf.py
directory=/home/spa/spa-salon-app
user=spa
autostart=true
autorestart=true
stdout_logfile=/var/log/spa-salon/app.log
stderr_logfile=/var/log/spa-salon/error.log
environment=PATH="/home/spa/spa-salon-app/venv/bin"
EOF

# Create log directory
sudo mkdir -p /var/log/spa-salon
sudo chown spa:spa /var/log/spa-salon

# Start application
sudo supervisorctl reread
sudo supervisorctl update
sudo supervisorctl start spa-salon
```

#### 8. Nginx Configuration
```bash
# Create Nginx configuration
sudo cat << EOF > /etc/nginx/sites-available/spa-salon
server {
    listen 80;
    server_name your-domain.com;  # Replace with your domain

    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /static {
        alias /home/spa/spa-salon-app/static;
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
EOF

# Enable site
sudo ln -s /etc/nginx/sites-available/spa-salon /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

#### 9. SSL Certificate (Optional but Recommended)
```bash
# Install Certbot
sudo apt install certbot python3-certbot-nginx

# Get SSL certificate
sudo certbot --nginx -d your-domain.com

# Auto-renewal (already configured by certbot)
```

## Docker Deployment (Alternative)

### 1. Create Dockerfile
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    postgresql-client \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Create non-root user
RUN useradd -m -u 1000 spa && chown -R spa:spa /app
USER spa

# Expose port
EXPOSE 5000

# Run application
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "main:app"]
```

### 2. Create docker-compose.yml
```yaml
version: '3.8'

services:
  db:
    image: postgres:14
    environment:
      POSTGRES_DB: spa_salon
      POSTGRES_USER: spa_user
      POSTGRES_PASSWORD: secure_password
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

  web:
    build: .
    ports:
      - "5000:5000"
    environment:
      DATABASE_URL: postgresql://spa_user:secure_password@db:5432/spa_salon
      SESSION_SECRET: your-secret-key-here
    depends_on:
      - db
    volumes:
      - ./static:/app/static

volumes:
  postgres_data:
```

### 3. Deploy with Docker
```bash
# Build and start services
docker-compose up -d

# Initialize database
docker-compose exec web python create_comprehensive_permissions.py
docker-compose exec web python assign_comprehensive_permissions.py
```

## Post-Installation Setup

### 1. Create Admin User
```bash
# Access application at http://localhost:5000
# Default credentials: admin/admin123 (if created during installation)
```

### 2. Configure Business Settings
1. Login as admin
2. Navigate to System Management → Business Settings
3. Configure:
   - Business name and contact information
   - Tax rates and policies
   - Operating hours
   - Service categories

### 3. Setup User Roles
1. Go to System Management → Role Management
2. Review default roles (Admin, Manager, Staff, Cashier)
3. Adjust permissions as needed
4. Create additional roles if required

### 4. Add Staff Users
1. Navigate to Staff Management
2. Add staff members with appropriate roles
3. Configure schedules and specialties

### 5. Configure Services and Inventory
1. Add services in the Services section
2. Set up inventory items and categories
3. Configure pricing and packages

## Maintenance & Updates

### Regular Maintenance
```bash
# Database backup
pg_dump spa_production > backup_$(date +%Y%m%d).sql

# Log rotation (handled by system)
sudo logrotate -f /etc/logrotate.d/spa-salon

# System updates
sudo apt update && sudo apt upgrade
sudo supervisorctl restart spa-salon
```

### Monitoring
- Check application logs: `/var/log/spa-salon/`
- Monitor database performance
- Review system resource usage

## Troubleshooting

### Common Issues

**Database Connection Error**
```bash
# Check PostgreSQL status
sudo systemctl status postgresql

# Check database connectivity
psql -h localhost -U spa_user -d spa_production
```

**Permission Denied**
```bash
# Check file permissions
sudo chown -R spa:spa /home/spa/spa-salon-app

# Check SELinux (if applicable)
sudo setsebool -P httpd_can_network_connect 1
```

**Application Won't Start**
```bash
# Check supervisor status
sudo supervisorctl status spa-salon

# Check application logs
sudo tail -f /var/log/spa-salon/error.log

# Test Gunicorn directly
cd /home/spa/spa-salon-app
source venv/bin/activate
gunicorn --bind 127.0.0.1:5000 main:app
```

### Getting Help
- Check application logs for detailed error messages
- Verify all environment variables are set
- Ensure database migrations completed successfully
- Contact system administrator for advanced troubleshooting

---

*This installation guide covers the complete setup process for the Spa & Salon Digital Business Suite. Follow the method that best fits your deployment environment.*