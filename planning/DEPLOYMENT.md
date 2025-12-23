# Production Deployment Guide

## Pre-Deployment Checklist

- [ ] DEBUG=False in production
- [ ] SECRET_KEY set to strong random value
- [ ] ALLOWED_HOSTS updated with domain
- [ ] Email service configured
- [ ] Twitter API credentials set (if using)
- [ ] HTTPS certificate obtained
- [ ] Database backed up
- [ ] Logs directory configured with rotation
- [ ] Static files will be collected
- [ ] Media files directory configured
- [ ] Environment variables secured

## Deployment Options

### Option 1: VPS Deployment (AWS EC2, DigitalOcean)

#### Initial Server Setup

```bash
# Connect to server
ssh ubuntu@your-server-ip

# Update system
sudo apt update && sudo apt upgrade -y

# Install dependencies
sudo apt install python3.10 python3-pip python3-venv mariadb-server nginx git -y

# Start services
sudo systemctl start mariadb
sudo systemctl enable mariadb
```

#### Application Setup

```bash
# Clone repository
cd /var/www
sudo git clone https://github.com/YOUR_USERNAME/v0-news-application-development.git
cd v0-news-application-development

# Set permissions
sudo chown -R www-data:www-data /var/www/v0-news-application-development
sudo chmod -R 755 /var/www/v0-news-application-development

# Create virtual environment
python3.10 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

#### Database Setup

```bash
# Create database and user
sudo mysql -u root -p << EOF
CREATE DATABASE news_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'strong_password';
GRANT ALL PRIVILEGES ON news_db.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;
EOF
```

#### Configuration

```bash
# Create .env file
nano .env
```

Add:
```
SECRET_KEY=generate_strong_key_here
DEBUG=False
ALLOWED_HOSTS=yourdomain.com,www.yourdomain.com
DB_NAME=news_db
DB_USER=news_user
DB_PASSWORD=strong_password
EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=app_password
```

#### Run Migrations and Collect Static

```bash
python manage.py migrate
python manage.py collectstatic --noinput
python manage.py createsuperuser
```

### Option 2: Docker Deployment

#### Dockerfile

```dockerfile
FROM python:3.10-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application
COPY . .

# Create logs directory
RUN mkdir -p logs

# Collect static files
RUN python manage.py collectstatic --noinput --clear

EXPOSE 8000

CMD ["gunicorn", "news_project.wsgi:application", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

#### docker-compose.yml

```yaml
version: '3.8'

services:
  web:
    build: .
    container_name: news_app
    ports:
      - "8000:8000"
    environment:
      - DEBUG=False
      - DB_HOST=db
      - ALLOWED_HOSTS=yourdomain.com
    depends_on:
      - db
    volumes:
      - ./logs:/app/logs
      - static_volume:/app/staticfiles
    command: >
      sh -c "python manage.py migrate &&
             gunicorn news_project.wsgi:application --bind 0.0.0.0:8000 --workers 4"

  db:
    image: mariadb:latest
    container_name: news_db
    environment:
      MYSQL_ROOT_PASSWORD: root_password
      MYSQL_DATABASE: news_db
      MYSQL_USER: news_user
      MYSQL_PASSWORD: db_password
    volumes:
      - db_data:/var/lib/mysql
    ports:
      - "3306:3306"

volumes:
  db_data:
  static_volume:
```

**Deploy:**
```bash
docker-compose up -d
docker-compose exec web python manage.py createsuperuser
```

### Option 3: Heroku Deployment

#### Files Required

**Procfile:**
```
web: gunicorn news_project.wsgi
release: python manage.py migrate
worker: python manage.py process_tasks
```

**runtime.txt:**
```
python-3.10.12
```

**Deploy:**
```bash
# Install Heroku CLI
curl https://cli-assets.heroku.com/install.sh | sh

# Login
heroku login

# Create app
heroku create your-app-name

# Set environment variables
heroku config:set SECRET_KEY=your_secret_key
heroku config:set DEBUG=False
heroku config:set ALLOWED_HOSTS=your-app-name.herokuapp.com

# Add MariaDB add-on
heroku addons:create cleardb:ignite

# Deploy
git push heroku main

# Create superuser
heroku run python manage.py createsuperuser

# View logs
heroku logs --tail
```

## Web Server Configuration

### Nginx Setup

**File: /etc/nginx/sites-available/newsapp**

```nginx
upstream django {
    server 127.0.0.1:8000;
}

server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    client_max_body_size 75M;

    location = /favicon.ico { 
        access_log off; 
        log_not_found off; 
    }
    
    location /static/ {
        alias /var/www/v0-news-application-development/staticfiles/;
        expires 30d;
    }
    
    location /media/ {
        alias /var/www/v0-news-application-development/media/;
        expires 7d;
    }
    
    location / {
        proxy_pass http://django;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_redirect off;
    }
}
```

**Enable:**
```bash
sudo ln -s /etc/nginx/sites-available/newsapp /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

### SSL/HTTPS with Let's Encrypt

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot certonly --nginx -d yourdomain.com -d www.yourdomain.com
```

**Update nginx config:**
```nginx
server {
    listen 443 ssl http2;
    server_name yourdomain.com www.yourdomain.com;
    
    ssl_certificate /etc/letsencrypt/live/yourdomain.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/yourdomain.com/privkey.pem;
    
    # ... rest of config
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name yourdomain.com www.yourdomain.com;
    return 301 https://$server_name$request_uri;
}
```

## Application Server Setup

### Gunicorn Configuration

**File: /etc/systemd/system/gunicorn.service**

```ini
[Unit]
Description=Gunicorn application server for Django News App
After=network.target mariadb.service

[Service]
Type=notify
User=www-data
WorkingDirectory=/var/www/v0-news-application-development
EnvironmentFile=/var/www/v0-news-application-development/.env
ExecStart=/var/www/v0-news-application-development/venv/bin/gunicorn \
          --workers 4 \
          --worker-class sync \
          --bind 127.0.0.1:8000 \
          --timeout 30 \
          --access-logfile /var/www/v0-news-application-development/logs/gunicorn_access.log \
          --error-logfile /var/www/v0-news-application-development/logs/gunicorn_error.log \
          news_project.wsgi:application

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

**Enable:**
```bash
sudo systemctl daemon-reload
sudo systemctl enable gunicorn
sudo systemctl start gunicorn
```

## Database Backups

### Automated Backup Script

**File: /usr/local/bin/backup-news-db.sh**

```bash
#!/bin/bash

BACKUP_DIR="/var/backups/news_db"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/news_db_$TIMESTAMP.sql.gz"

# Create backup directory
mkdir -p $BACKUP_DIR

# Create backup
mysqldump -u news_user -p$DB_PASSWORD news_db | gzip > $BACKUP_FILE

# Keep last 30 days of backups
find $BACKUP_DIR -name "news_db_*.sql.gz" -mtime +30 -delete

# Backup to remote (example with rsync)
# rsync -az $BACKUP_FILE remote_server:/backups/

echo "Backup completed: $BACKUP_FILE" | mail -s "DB Backup" admin@example.com
```

**Setup Cron Job:**
```bash
sudo nano /etc/crontab
# Add: 0 2 * * * /usr/local/bin/backup-news-db.sh
```

## Monitoring & Logging

### Centralized Logging

```python
# In settings.py for production
LOGGING['handlers']['syslog'] = {
    'level': 'INFO',
    'class': 'logging.handlers.SysLogHandler',
    'address': '/dev/log',
    'formatter': 'verbose',
}
```

### Health Checks

```bash
# Setup health check endpoint
# Create news/health_check_view.py

curl http://yourdomain.com/health/  # Check if up
```

### Performance Monitoring

```bash
# Install monitoring tools
sudo apt install htop iotop nethogs

# Monitor in real-time
htop
```

## Security Hardening

### Django Security Settings

```python
# Production settings

# HTTPS
SECURE_SSL_REDIRECT = True
SESSION_COOKIE_SECURE = True
CSRF_COOKIE_SECURE = True

# Headers
SECURE_HSTS_SECONDS = 31536000
SECURE_HSTS_INCLUDE_SUBDOMAINS = True
SECURE_HSTS_PRELOAD = True

# Content Security Policy
SECURE_CONTENT_SECURITY_POLICY = {
    "default-src": ("'self'",),
    "script-src": ("'self'", "'unsafe-inline'"),
    "style-src": ("'self'", "'unsafe-inline'"),
}

# ALLOWED_HOSTS must be set
ALLOWED_HOSTS = ['yourdomain.com', 'www.yourdomain.com']
```

### System Security

```bash
# Firewall
sudo ufw enable
sudo ufw allow 80/tcp
sudo ufw allow 443/tcp
sudo ufw allow 22/tcp

# Automatic updates
sudo apt install unattended-upgrades
sudo dpkg-reconfigure -plow unattended-upgrades

# SSH key authentication only
# Disable password authentication in /etc/ssh/sshd_config
PasswordAuthentication no
```

## Performance Optimization

### Database

```python
# Connection pooling
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.mysql',
        'CONN_MAX_AGE': 600,  # Keep connections alive
        ...
    }
}
```

### Caching

```python
# Redis caching
CACHES = {
    'default': {
        'BACKEND': 'django_redis.cache.RedisCache',
        'LOCATION': 'redis://127.0.0.1:6379/1',
    }
}

# Cache API responses
from django.views.decorators.cache import cache_page

@cache_page(60 * 5)  # Cache for 5 minutes
def article_list(request):
    ...
```

### Load Balancing

For multiple servers:

```
┌─────────────────┐
│  Load Balancer  │
│   (HAProxy)     │
└────────┬────────┘
         │
    ┌────┼────┐
    ▼    ▼    ▼
  Web1 Web2 Web3
    └────┬────┘
         │
    ┌────┴──────┐
    ▼           ▼
  DB Master   DB Slave
```

## Scaling Recommendations

- **Small Project** (< 10K users): Single VPS with 2GB RAM
- **Medium Project** (10K-100K users): 2 app servers + database + cache
- **Large Project** (> 100K users): Full load balancing + multi-region
