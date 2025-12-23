# Troubleshooting Guide

## Common Issues and Solutions

### 1. Database Connection Error

**Error:**
```
django.db.utils.OperationalError: (1045, "Access denied for user 'news_user'@'localhost'")
```

**Causes:**
- Incorrect database credentials
- MariaDB not running
- User doesn't have proper permissions

**Solutions:**
```bash
# Check if MariaDB is running
sudo systemctl status mariadb

# Start MariaDB if stopped
sudo systemctl start mariadb

# Test connection
mysql -u news_user -p -h localhost news_db

# Verify credentials in .env file
cat .env | grep DB_
```

**Reset User Permissions:**
```bash
sudo mysql -u root -p
GRANT ALL PRIVILEGES ON news_db.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

---

### 2. Logging ValueError

**Error:**
```
ValueError: Invalid file path for logging: 
'/path/to/project/logs/django.log' (Permission denied)
```

**Causes:**
- logs directory doesn't exist
- Incorrect file permissions
- Path contains special characters on Windows

**Solutions:**
```bash
# Create logs directory
mkdir -p logs
chmod 755 logs

# Check permissions
ls -la logs/

# Run server as correct user
python manage.py runserver
```

---

### 3. Secret Key Not Configured

**Error:**
```
django.core.exceptions.ImproperlyConfigured: 
The SECRET_KEY setting must not be empty.
```

**Causes:**
- .env file missing SECRET_KEY
- .env file not loaded

**Solutions:**
```bash
# Generate new secret key
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

# Add to .env
echo "SECRET_KEY=your_generated_key" >> .env

# Verify
source venv/bin/activate
python manage.py shell
from django.conf import settings
print(settings.SECRET_KEY)
exit()
```

---

### 4. Port 8000 Already in Use

**Error:**
```
Error: That port is already in use.
```

**Causes:**
- Another Django instance running
- Another application using port 8000

**Solutions:**
```bash
# Find process using port 8000
sudo lsof -ti:8000

# Kill process
sudo kill -9 PID

# Or use different port
python manage.py runserver 8001
```

---

### 5. Module Import Error

**Error:**
```
ModuleNotFoundError: No module named 'rest_framework'
```

**Causes:**
- Virtual environment not activated
- Dependencies not installed
- Wrong Python version

**Solutions:**
```bash
# Activate virtual environment
source venv/bin/activate

# Reinstall dependencies
pip install --upgrade -r requirements.txt

# Verify Python version
python --version  # Should be 3.10+
```

---

### 6. Email Not Sending

**Error:**
```
SMTPAuthenticationError: (535, b'5.7.8 Username and password not accepted')
```

**Causes:**
- Incorrect Gmail credentials
- Gmail 2FA not enabled
- App password not generated
- Less secure apps not enabled

**Solutions:**

**For Gmail:**
1. Enable 2-Factor Authentication
2. Generate App Password:
   - Go to https://myaccount.google.com/apppasswords
   - Select "Mail" and "Windows Computer"
   - Copy 16-character password
3. Add to .env:
   ```
   EMAIL_HOST_USER=your_email@gmail.com
   EMAIL_HOST_PASSWORD=16_char_app_password
   ```

**Test Email:**
```bash
python manage.py shell
from django.core.mail import send_mail

send_mail(
    'Test Subject',
    'Test Message',
    'your_email@gmail.com',
    ['recipient@example.com'],
    fail_silently=False,
)
```

---

### 7. Migration Conflicts

**Error:**
```
CommandError: Conflicting migrations detected
```

**Causes:**
- Multiple migration files for same change
- Git merge conflicts in migrations
- Migration created while branch diverged

**Solutions:**
```bash
# Show migration history
python manage.py showmigrations news

# Merge migrations (if conflict detected)
python manage.py makemigrations news --merge

# Undo last migration
python manage.py migrate news 0001_initial

# Reset all migrations (dangerous - only in development)
rm -rf news/migrations/0*.py
python manage.py makemigrations news
python manage.py migrate
```

---

### 8. Static Files Not Loading

**Error:**
```
Static files (CSS, JS) not loading in browser
```

**Causes:**
- Static files not collected
- STATIC_URL incorrect
- Debug mode disabled

**Solutions:**
```bash
# Collect static files
python manage.py collectstatic --noinput

# Check STATIC_URL in settings
grep STATIC_ news_project/settings.py

# For development, ensure DEBUG=True
# In .env: DEBUG=True
```

---

### 9. Permission Denied Errors

**Error:**
```
PermissionError: [Errno 13] Permission denied: '/var/www/newsapp/logs/django.log'
```

**Causes:**
- Wrong file ownership
- Insufficient permissions
- Running as wrong user

**Solutions:**
```bash
# Check file ownership
ls -la logs/

# Fix ownership
sudo chown -R $USER:$USER logs/

# Or make writable
chmod 777 logs/
```

---

### 10. Superuser Login Not Working

**Error:**
```
Invalid username/password combination
```

**Causes:**
- Password typo
- User not created
- User marked as inactive

**Solutions:**
```bash
# List superusers
python manage.py shell
from news.models import CustomUser
CustomUser.objects.filter(is_superuser=True)
exit()

# Change password
python manage.py changepassword admin

# Recreate superuser
python manage.py createsuperuser

# Check if active
python manage.py shell
user = CustomUser.objects.get(username='admin')
print(user.is_active)
exit()
```

---

### 11. CSRF Token Missing

**Error:**
```
Forbidden (403): CSRF verification failed
```

**Causes:**
- CSRF middleware not enabled
- Missing CSRF token in form
- DEBUG=False without ALLOWED_HOSTS

**Solutions:**
```html
<!-- In Django template, add CSRF token -->
<form method="POST">
    {% csrf_token %}
    <!-- form fields -->
</form>
```

**In settings.py:**
```python
MIDDLEWARE = [
    ...
    'django.middleware.csrf.CsrfViewMiddleware',
    ...
]
```

---

### 12. Time Zone Issues

**Error:**
```
Unexpected time differences in timestamps
```

**Causes:**
- USE_TZ not set
- System timezone incorrect
- Database timezone mismatch

**Solutions:**
```python
# In settings.py
USE_TZ = True
TIME_ZONE = 'UTC'  # or your timezone

# Check current time
python manage.py shell
from django.utils import timezone
print(timezone.now())
exit()
```

## Debugging Tips

### Enable Debug Logging

```python
# Add to settings.py
LOGGING['loggers']['django']['level'] = 'DEBUG'
```

### Test Database Connection

```bash
python manage.py dbshell
SELECT 1;
```

### Inspect Object State

```bash
python manage.py shell
from news.models import Article
article = Article.objects.first()
print(article.__dict__)
exit()
```

### Check Middleware

```bash
python manage.py shell
from django.conf import settings
print(settings.MIDDLEWARE)
exit()
```

## Support Resources

- Django Documentation: https://docs.djangoproject.com
- Django REST Framework: https://www.django-rest-framework.org
- MariaDB Documentation: https://mariadb.com/kb
- Stack Overflow: https://stackoverflow.com/questions/tagged/django
