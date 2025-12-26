# Django News Application

A comprehensive news platform built with Django featuring role-based access control, article management, subscriptions, automated notifications, and a RESTful API.

## Features

### User Roles & Permissions
- **Readers**: View articles, subscribe to publishers and journalists
- **Journalists**: Create, edit, and submit articles for approval
- **Editors**: Review and approve articles for publication

### Core Functionality
- Custom user authentication with role-based access control
- Article creation and approval workflow
- Publisher and journalist profiles
- Subscription system (subscribe to publishers or individual journalists)
- Automated email notifications when articles are approved
- Automatic posting to X (Twitter) when articles are published
- RESTful API with subscription-based filtering
- Comprehensive unit tests for API endpoints

## Technology Stack

- **Backend**: Django 4.2+
- **Database**: MariaDB
- **API**: Django REST Framework
- **Email**: Django Email System
- **External APIs**: X (Twitter) API v2

## Installation & Setup

This project can be run in two ways:
1. **Virtual Environment (venv)** - For local development
2. **Docker** - For containerized deployment

---

## Option 1: Running with Virtual Environment

### Prerequisites
- Python 3.8 or higher
- MariaDB 10.5+ (or MySQL 8.0+)
- pip (Python package manager)

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd news-application-development
```

### Step 2: Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate

# On Mac/Linux:
source venv/bin/activate
```

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**Note**: On some systems, you may need to use `pip3` instead of `pip`.

### Step 4: Configure Database

Create a MariaDB database:

```sql
CREATE DATABASE news_db CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
CREATE USER 'news_user'@'localhost' IDENTIFIED BY 'your_password';
GRANT ALL PRIVILEGES ON news_db.* TO 'news_user'@'localhost';
FLUSH PRIVILEGES;
```

### Step 5: Environment Configuration

Create a `.env` file in the project root directory with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration
DB_NAME=news_db
DB_USER=news_user
DB_PASSWORD=your_password
DB_HOST=localhost
DB_PORT=3306

# Email Configuration (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@newsapp.com

# Twitter API Configuration (optional)
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret
TWITTER_BEARER_TOKEN=your-bearer-token

# Logging Configuration (optional)
ENABLE_FILE_LOGGING=False
LOGS_DIR=
```

**Important Security Notes:**
- Never commit the `.env` file to version control
- Generate a secure `SECRET_KEY` using: `python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"`
- For Gmail, use an App Password instead of your regular password
- The `.env` file is already excluded in `.gitignore`

### Step 6: Run Database Migrations

**This step is critical!** You must run migrations before starting the server:

```bash
# Create migration files (if needed)
python manage.py makemigrations

# Apply migrations to create database tables
python manage.py migrate
```

### Step 7: Create Superuser

```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user.

### Step 8: Collect Static Files (Optional)

```bash
python manage.py collectstatic
```

### Step 9: Run Development Server

```bash
python manage.py runserver
```

Visit `http://127.0.0.1:8000/` in your browser.

---

## Option 2: Running with Docker

### Prerequisites
- Docker 20.10+
- Docker Compose 2.0+

### Step 1: Clone the Repository

```bash
git clone <repository-url>
cd news-application-development
```

### Step 2: Environment Configuration

Create a `.env` file in the project root directory with the following variables:

```env
# Django Settings
SECRET_KEY=your-secret-key-here
DEBUG=True
ALLOWED_HOSTS=localhost,127.0.0.1

# Database Configuration (for Docker, use 'db' as host)
DB_NAME=news_db
DB_USER=news_user
DB_PASSWORD=news_password
DB_HOST=db
DB_PORT=3306

# Email Configuration (for notifications)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@newsapp.com

# Twitter API Configuration (optional)
TWITTER_API_KEY=your-api-key
TWITTER_API_SECRET=your-api-secret
TWITTER_ACCESS_TOKEN=your-access-token
TWITTER_ACCESS_TOKEN_SECRET=your-access-token-secret
TWITTER_BEARER_TOKEN=your-bearer-token

# Logging Configuration (optional)
ENABLE_FILE_LOGGING=False
LOGS_DIR=
```

**Note**: The database credentials in `.env` should match those in `docker-compose.yml` for the `db` service.

### Step 3: Build and Start Containers

```bash
# Build and start all services
docker-compose up --build
```

This will:
1. Build the Django application container
2. Start the MariaDB database container
3. **Automatically run migrations** (configured in the Dockerfile)
4. Start the Django development server

### Step 4: Access the Application

Once the containers are running, visit `http://localhost:8000/` in your browser.

### Step 5: Create Superuser (in Docker)

Open a new terminal and run:

```bash
# Execute command in the web container
docker-compose exec web python manage.py createsuperuser
```

### Important Docker Commands

```bash
# Stop containers
docker-compose down

# Stop containers and remove volumes (clears database)
docker-compose down -v

# View logs
docker-compose logs -f

# Execute commands in the web container
docker-compose exec web python manage.py <command>

# Rebuild after code changes
docker-compose up --build
```

### Database Migrations in Docker

Migrations are automatically run when the container starts (configured in the Dockerfile). However, if you need to run migrations manually:

```bash
docker-compose exec web python manage.py makemigrations
docker-compose exec web python manage.py migrate
```

---

## Usage Guide

### For Readers
1. Register with the "Reader" role
2. Browse publishers and journalists
3. Subscribe to publishers or journalists you're interested in
4. View your personalized feed in "My Feed"
5. Receive email notifications when new articles are published

### For Journalists
1. Register with the "Journalist" role
2. Create articles from the Journalist Dashboard
3. Optionally affiliate with publishers
4. Submit articles for editor approval
5. Track article status (Pending/Approved)

### For Editors
1. Register with the "Editor" role
2. Review pending articles in the Editor Dashboard
3. Approve or reject articles
4. When approved, subscribers are automatically notified via email
5. Approved articles are automatically posted to X (Twitter) if configured

### API Access

The REST API is available at `/api/` endpoints:

**Endpoints:**
- `GET /api/articles/` - Get articles from subscriptions
- `GET /api/articles/by_publisher/?publisher_id=X` - Filter by publisher
- `GET /api/articles/by_journalist/?journalist_id=X` - Filter by journalist
- `GET /api/articles/subscriptions/` - View subscription info
- `GET /api/publishers/` - List all publishers
- `GET /api/journalists/` - List all journalists

**Authentication**: Basic Authentication or Session Authentication

**Example Request:**
```bash
curl -u username:password http://127.0.0.1:8000/api/articles/
```

## Running Tests

```bash
# With venv
python manage.py test news

# With Docker
docker-compose exec web python manage.py test news
```

This will test:
- API authentication
- Subscription-based article filtering
- Publisher and journalist filtering
- Permission checks
- Data integrity

## Project Structure

```
news-application-development/
├── news/                      # Main application
│   ├── models.py             # Database models
│   ├── views.py              # View logic
│   ├── forms.py              # Forms
│   ├── serializers.py        # API serializers
│   ├── api_views.py          # API views
│   ├── signals.py            # Django signals for automation
│   ├── tests.py              # Unit tests
│   ├── urls.py               # URL routing
│   └── api_urls.py           # API URL routing
├── news_project/             # Project configuration
│   ├── settings.py           # Django settings
│   ├── urls.py               # Root URL configuration
│   └── wsgi.py              # WSGI configuration
├── templates/                # HTML templates
│   ├── base.html            # Base template
│   └── news/                # App-specific templates
├── docs/                     # Sphinx documentation
│   ├── source/              # Documentation source files
│   └── build/               # Generated documentation
├── manage.py                # Django management script
├── requirements.txt         # Python dependencies
├── Dockerfile               # Docker configuration
├── docker-compose.yml       # Docker Compose configuration
└── README.md               # This file
```

## Documentation

Comprehensive API documentation is available in the `docs/` folder. To build the documentation:

```bash
cd docs
make html  # On Linux/Mac
# or
.\make.bat html  # On Windows
```

The generated documentation will be in `docs/build/html/`.

## Key Models

- **CustomUser**: Extended user model with role-based fields
- **Publisher**: News organizations
- **Article**: News articles with approval workflow
- **Newsletter**: Newsletter content (extendable feature)

## Automated Features

### Email Notifications
When an editor approves an article, the system automatically:
1. Identifies all readers subscribed to the publisher or journalist
2. Sends mass emails with article details
3. Includes a link to read the full article

### X (Twitter) Integration
Upon article approval, the system:
1. Generates a tweet with article title and summary
2. Posts to the configured X account using the API
3. Includes a link back to the article

## Security Features

- Role-based access control (RBAC)
- Group-based permissions
- Password validation
- CSRF protection
- SQL injection prevention (Django ORM)
- Secure session management
- Environment variables for sensitive data

## Troubleshooting

### Database Connection Errors

**With venv:**
- Verify MariaDB is running: `sudo systemctl status mariadb` (Linux) or check services (Windows)
- Check database credentials in `.env`
- Ensure the database exists and user has proper permissions

**With Docker:**
- Check if database container is running: `docker-compose ps`
- Verify database credentials match in `.env` and `docker-compose.yml`
- Check container logs: `docker-compose logs db`

### Migration Errors

**Important**: Always run migrations before starting the server!

**With venv:**
```bash
python manage.py makemigrations
python manage.py migrate
```

**With Docker:**
Migrations run automatically, but you can run manually:
```bash
docker-compose exec web python manage.py migrate
```

### Email Not Sending
- Check your email provider allows SMTP access
- For Gmail, create an App Password instead of using your regular password
- Ensure `EMAIL_USE_TLS` is set to `True`
- Check email configuration in `.env`

### Twitter Posts Not Working
- Verify all Twitter API credentials are correct in `.env`
- Ensure you have "Elevated" access for Twitter API v2
- Check that your app has Read and Write permissions

### Logging Issues
- File logging is disabled by default. To enable, set `ENABLE_FILE_LOGGING=True` and `LOGS_DIR=/path/to/logs` in `.env`
- The `logs/` directory is excluded from Git (see `.gitignore`)

## Development Notes

- The application uses Django Signals (`post_save`) to trigger automated actions
- All API endpoints require authentication
- API results are filtered based on user subscriptions
- Unit tests cover all critical API functionality
- Code follows PEP 8 style guidelines
- Logging can be configured via environment variables

## License

This project is created for educational purposes as part of a Django capstone project.

## Support

For issues or questions, please refer to the Django documentation at https://docs.djangoproject.com/
