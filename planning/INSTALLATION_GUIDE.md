# Installation Guide

## System Requirements

- **Operating System:** Linux (Ubuntu, Debian, Kali), macOS, or Windows
- **Python:** 3.10 or higher
- **MariaDB:** 10.4 or higher
- **Disk Space:** 500 MB minimum
- **RAM:** 2 GB minimum

## Installation Steps

### Step 1: Clone Repository

```bash
git clone https://github.com/YOUR_USERNAME/v0-news-application-development.git
cd v0-news-application-development
```

### Step 2: Install System Dependencies

#### On Ubuntu/Debian/Kali
```bash
sudo apt update
sudo apt install python3 python3-pip python3-venv mariadb-server mariadb-client libmariadb-dev gcc -y
```

#### On macOS
```bash
# Install Homebrew if not already installed
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

# Install dependencies
brew install python@3.10 mariadb
brew services start mariadb
```

#### On Windows
1. Download Python 3.10+ from python.org
2. Download MariaDB from mariadb.org
3. Install both with default settings

### Step 3: Create Virtual Environment

```bash
python3 -m venv venv
```

#### Activate Virtual Environment

**Linux/macOS:**
```bash
source venv/bin/activate
```

**Windows:**
```bash
venv\Scripts\activate
```

### Step 4: Install Python Dependencies

```bash
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 5: Setup MariaDB Database

#### On Linux/macOS
```bash
sudo systemctl start mariadb
sudo mysql -u root -p
```

#### On Windows
```bash
mysql -u root -p
```

**Run SQL Commands:**
```sql
CREATE DATABASE news_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'strong_password_here';
GRANT ALL PRIVILEGES ON news_db.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;
EXIT;
```

### Step 6: Configure Environment Variables

```bash
cp .env.example .env
nano .env  # or open in your preferred editor
```

**Essential Variables to Update:**
```
SECRET_KEY=generate-a-random-string-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

DB_NAME=news_db
DB_USER=news_user
DB_PASSWORD=strong_password_here
DB_HOST=localhost
DB_PORT=3306

EMAIL_HOST_USER=your_email@gmail.com
EMAIL_HOST_PASSWORD=your_app_password
```

#### Generating SECRET_KEY
```bash
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

#### Gmail App Password Setup
1. Enable 2-factor authentication on Google Account
2. Go to https://myaccount.google.com/apppasswords
3. Select "Mail" and "Windows Computer"
4. Copy the 16-character password
5. Paste into EMAIL_HOST_PASSWORD

### Step 7: Create Logs Directory

```bash
mkdir -p logs
```

### Step 8: Run Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

**Expected Output:**
```
Operations to perform:
  Apply all migrations: admin, auth, contenttypes, news, sessions
Running migrations:
  Applying news.0001_initial... OK
  ...
```

### Step 9: Create Superuser

```bash
python manage.py createsuperuser
```

**Follow Prompts:**
```
Username: admin
Email: admin@example.com
Password: (enter secure password)
Password (again): (confirm)
Superuser created successfully.
```

### Step 10: Create Sample Data (Optional)

```bash
python manage.py shell
```

**Python Shell Commands:**
```python
from news.models import CustomUser, Publisher, Article
from django.utils import timezone

# Create publisher
publisher = Publisher.objects.create(
    name="Tech News Daily",
    description="Latest technology news",
    website="https://technewsdaily.com"
)

# Create journalist
journalist = CustomUser.objects.create_user(
    username="journalist1",
    email="journalist@example.com",
    password="secure_password",
    first_name="John",
    last_name="Reporter",
    role="journalist"
)

# Create editor
editor = CustomUser.objects.create_user(
    username="editor1",
    email="editor@example.com",
    password="secure_password",
    first_name="Jane",
    last_name="Editor",
    role="editor"
)

# Create reader
reader = CustomUser.objects.create_user(
    username="reader1",
    email="reader@example.com",
    password="secure_password",
    first_name="Bob",
    last_name="Reader",
    role="reader"
)

# Reader subscribes
reader.subscribed_publishers.add(publisher)
reader.subscribed_journalists.add(journalist)

# Journalist creates article
article = Article.objects.create(
    title="Breaking: New Tech Released",
    content="Detailed content here...",
    summary="Brief summary",
    author=journalist,
    publisher=publisher
)

# Editor approves
article.is_approved = True
article.approved_by = editor
article.published_at = timezone.now()
article.save()

print("Sample data created!")
exit()
```

### Step 11: Run Development Server

```bash
python manage.py runserver
```

**Expected Output:**
```
Starting development server at http://127.0.0.1:8000/
Quit the server with CONTROL-C.
```

### Step 12: Access Application

- **Main Site:** http://127.0.0.1:8000/
- **Admin Panel:** http://127.0.0.1:8000/admin/
- **API:** http://127.0.0.1:8000/api/

## Platform-Specific Instructions

### Kali Linux Specific
```bash
# May need to install additional libraries
sudo apt install python3-dev libssl-dev libffi-dev -y

# Use python3 explicitly
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Windows PowerShell

If you encounter execution policy errors:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

### macOS with M1/M2 Chip

Some packages may need special handling:
```bash
# Install with --no-binary for some packages
pip install --no-binary :all: mysqlclient
```

## Verification Checklist

- [ ] Python virtual environment created and activated
- [ ] MariaDB running and database created
- [ ] Environment variables configured in .env
- [ ] Logs directory created
- [ ] Migrations applied successfully
- [ ] Superuser created
- [ ] Development server running
- [ ] Can access admin panel at http://127.0.0.1:8000/admin/

## Troubleshooting Installation

### Issue: "No module named 'django'"
**Solution:** Ensure virtual environment is activated and requirements installed
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Issue: "Can't connect to MySQL server"
**Solution:** Verify MariaDB is running
```bash
# Linux
sudo systemctl status mariadb

# macOS
brew services list | grep mariadb

# Windows (check Services app)
```

### Issue: "Permission denied" for logs directory
**Solution:**
```bash
chmod 755 logs
```

### Issue: "ValueError: Invalid file path for logging"
**Solution:** Ensure logs directory exists
```bash
mkdir -p logs
```

## Next Steps

1. Review the README.md for project overview
2. Check PROJECT_ARCHITECTURE.md for system design
3. Read API_DOCUMENTATION.md for API details
4. Follow TESTING_GUIDE.md to run unit tests
5. See DEPLOYMENT.md for production setup
