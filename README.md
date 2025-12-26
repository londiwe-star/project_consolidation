# Django News Application

A comprehensive news platform built with Django featuring role-based access control, article management, subscriptions, automated notifications, and a RESTful API.

## Features

- **Role-based Access Control**: Readers, Journalists, and Editors
- **Article Management**: Create, edit, approve, and publish articles
- **Subscription System**: Subscribe to publishers or journalists
- **Automated Notifications**: Email notifications when articles are approved
- **RESTful API**: Subscription-based article filtering
- **Twitter Integration**: Automatic posting to X (Twitter) when articles are published

## Quick Start

Choose one of two setup methods:

### Option 1: Virtual Environment (Recommended for Local Testing)

**Prerequisites:** Python 3.8+ and pip

#### Step 1: Clone Repository
```bash
git clone https://github.com/londiwe-star/project_consolidation.git
cd project_consolidation
```

#### Step 2: Create Virtual Environment
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows (PowerShell):
venv\Scripts\Activate.ps1

# Windows (Command Prompt):
venv\Scripts\activate.bat

# Mac/Linux:
source venv/bin/activate
```

**Note for Windows PowerShell:** If you get an execution policy error, run:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
```

#### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

#### Step 4: Create Environment File
```bash
# Windows (PowerShell):
Copy-Item .env.example .env

# Mac/Linux:
cp .env.example .env
```

The `.env` file is already configured to use SQLite (no database installation needed).

#### Step 5: Run Migrations
```bash
python manage.py migrate
```

#### Step 6: Create Superuser
```bash
python manage.py createsuperuser
```

Follow the prompts to create an admin user.

#### Step 7: Start Server
```bash
python manage.py runserver
```

#### Step 8: Access Application
Open your browser and visit:
- **Home page**: http://127.0.0.1:8000/
- **Admin panel**: http://127.0.0.1:8000/admin/

---

### Option 2: Docker (Recommended for Container Testing)

**Prerequisites:** Docker and Docker Compose installed

#### Step 1: Clone Repository
```bash
git clone https://github.com/londiwe-star/project_consolidation.git
cd project_consolidation
```

#### Step 2: Create Environment File
```bash
cat > .env << 'EOF'
SECRET_KEY=django-insecure-test-key-for-docker-playground
DEBUG=True
ALLOWED_HOSTS=*
USE_SQLITE=True
ENABLE_FILE_LOGGING=False
LOGS_DIR=
EOF
```

#### Step 3: Build and Start Containers
```bash
docker-compose up --build
```

Wait for the output:
```
news_web | Starting development server at http://0.0.0.0:8000/
```

#### Step 4: Access Application

**In Docker Playground:**
- Click the port number **8000** in the Docker Playground interface
- Or use the URL provided by Docker Playground (e.g., `http://ip172-18-0-X-XXXXX-8000.direct.labs.play-with-docker.com`)

**Important:** Do NOT use `0.0.0.0:8000` in your browser. Use the URL provided by Docker Playground or click the port number.

**For Local Docker:**
- Open: http://localhost:8000/

#### Step 5: Create Superuser (New Terminal)
Open a new terminal and run:
```bash
cd project_consolidation
docker-compose exec web python manage.py createsuperuser
```

---

## Testing Commands

### Virtual Environment
```bash
# Activate venv first
venv\Scripts\Activate.ps1  # Windows
# or
source venv/bin/activate   # Mac/Linux

# Run tests
python manage.py test news

# Run migrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Start server
python manage.py runserver
```

### Docker
```bash
# View logs
docker-compose logs -f

# Run tests
docker-compose exec web python manage.py test news

# Run migrations
docker-compose exec web python manage.py migrate

# Create superuser
docker-compose exec web python manage.py createsuperuser

# Stop containers
docker-compose down

# Stop and remove everything (fresh start)
docker-compose down -v
```

---

## API Endpoints

All endpoints require authentication:

- `GET /api/articles/` - Get articles from subscriptions
- `GET /api/articles/by_publisher/?publisher_id=X` - Filter by publisher
- `GET /api/articles/by_journalist/?journalist_id=X` - Filter by journalist
- `GET /api/publishers/` - List all publishers
- `GET /api/journalists/` - List all journalists

**Example:**
```bash
curl -u username:password http://127.0.0.1:8000/api/articles/
```

---

## Project Structure

```
project_consolidation/
├── news/                 # Main application
│   ├── models.py        # Database models
│   ├── views.py         # View logic
│   ├── api_views.py     # API views
│   └── ...
├── news_project/        # Project settings
│   └── settings.py      # Django settings
├── templates/           # HTML templates
├── docs/                # Sphinx documentation
├── manage.py            # Django management
├── requirements.txt     # Dependencies
├── Dockerfile           # Docker configuration
├── docker-compose.yml   # Docker Compose configuration
└── README.md            # This file
```

---

## Documentation

Sphinx documentation is available in the `docs/` folder. To build:

```bash
cd docs
make html  # Linux/Mac
# or
.\make.bat html  # Windows
```

View the documentation at `docs/build/html/index.html`

---

## Troubleshooting

### Virtual Environment Issues

**Activation fails (Windows PowerShell):**
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
venv\Scripts\Activate.ps1
```

**Module not found:**
```bash
# Make sure venv is activated, then:
pip install -r requirements.txt
```

### Docker Issues

**Can't access application in Docker Playground:**
- Do NOT use `0.0.0.0:8000`
- Click the port number (8000) in Docker Playground interface
- Use the URL provided by Docker Playground

**Container won't start:**
```bash
docker-compose down -v
docker-compose build --no-cache
docker-compose up
```

**Migrations fail:**
```bash
docker-compose exec web python manage.py migrate
```

---

## Technology Stack

- **Backend**: Django 4.2+
- **Database**: SQLite (default) or MariaDB
- **API**: Django REST Framework
- **Containerization**: Docker & Docker Compose

---

## License

Educational project for Django capstone.

## Repository

https://github.com/londiwe-star/project_consolidation.git
