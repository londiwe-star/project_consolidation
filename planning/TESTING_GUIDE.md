# Testing Guide

## Unit Testing

### Running All Tests

```bash
python manage.py test news
```

### Running Specific Test Class

```bash
python manage.py test news.tests.ArticleAPITests
```

### Running Specific Test Method

```bash
python manage.py test news.tests.ArticleAPITests.test_list_articles
```

### Running Tests with Verbose Output

```bash
python manage.py test news -v 2
```

### Coverage Testing

```bash
pip install coverage
coverage run --source='news' manage.py test news
coverage report
coverage html  # Generate HTML report
```

## API Testing with cURL

### Test Article Creation

```bash
# First, login
curl -c cookies.txt -b cookies.txt \
  -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "journalist1", "password": "password123"}'

# Create article
curl -b cookies.txt \
  -X POST http://localhost:8000/api/articles/ \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Article",
    "content": "Article content here...",
    "summary": "Summary",
    "publisher_id": 1
  }'
```

### Test Authentication

```bash
# Valid login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "admin_password"}'

# Invalid login
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "wrong_password"}'
```

## API Testing with Postman

### Setting Up Postman

1. Download Postman from postman.com
2. Create new collection "News API"
3. Add requests for each endpoint

### Example Request

**Name:** Get Articles
- **Method:** GET
- **URL:** http://localhost:8000/api/articles/
- **Headers:** Content-Type: application/json
- **Auth:** Basic Auth with credentials

## Performance Testing

### Load Testing with Apache Bench

```bash
# Install Apache Bench
sudo apt install apache2-utils

# Test endpoint with 1000 requests, 10 concurrent
ab -n 1000 -c 10 http://localhost:8000/api/articles/
```

### Load Testing with Locust

```bash
pip install locust

# Create locustfile.py
# Run load test
locust -f locustfile.py --host=http://localhost:8000
```

**Example locustfile.py:**
```python
from locust import HttpUser, task, between

class NewsUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(1)
    def list_articles(self):
        self.client.get("/api/articles/")
    
    @task(2)
    def article_detail(self):
        self.client.get("/api/articles/1/")
    
    @task(1)
    def create_article(self):
        self.client.post("/api/articles/", json={
            "title": "Test",
            "content": "Content",
            "summary": "Summary",
            "publisher_id": 1
        })
```

## Integration Testing

### Test Workflow: Publisher Creation to Article Approval

```python
from django.test import TestCase, Client
from news.models import CustomUser, Publisher, Article

class WorkflowIntegrationTest(TestCase):
    def setUp(self):
        self.client = Client()
        
        # Create users
        self.editor = CustomUser.objects.create_user(
            username='editor',
            password='password',
            role='editor'
        )
        
        self.journalist = CustomUser.objects.create_user(
            username='journalist',
            password='password',
            role='journalist'
        )
        
        # Create publisher
        self.publisher = Publisher.objects.create(
            name="Test Publisher"
        )
    
    def test_complete_publishing_workflow(self):
        # Login as journalist
        self.client.login(username='journalist', password='password')
        
        # Create article
        article = Article.objects.create(
            title="Test Article",
            content="Test content",
            summary="Test",
            author=self.journalist,
            publisher=self.publisher
        )
        
        self.assertFalse(article.is_approved)
        
        # Login as editor
        self.client.logout()
        self.client.login(username='editor', password='password')
        
        # Approve article
        article.is_approved = True
        article.approved_by = self.editor
        article.save()
        
        # Verify
        self.assertTrue(article.is_approved)
        self.assertEqual(article.approved_by, self.editor)
```

## Test Categories

### Model Tests
- CustomUser creation and role assignment
- Article creation and approval
- Publisher management
- Subscription management

### API Tests
- Authentication and authorization
- CRUD operations for all models
- Permission checks
- Pagination and filtering

### Signal Tests
- Email notifications on approval
- Twitter posting
- Subscriber notifications

### Form Validation Tests
- Article form validation
- User registration form
- Publisher form

## Debugging Tests

### Run Tests with Python Debugger

```bash
python -m pdb manage.py test news.tests.ArticleTests.test_create_article
```

### Print Debug Information

```python
def test_article_creation(self):
    article = Article.objects.create(...)
    print(f"Article created: {article.id}")  # This will show in test output
```

### Check Test Database State

```bash
# Keep test database for inspection
python manage.py test news --keepdb

# Inspect with shell
python manage.py dbshell
```

## Continuous Integration

### GitHub Actions Example

**.github/workflows/tests.yml:**
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    
    services:
      mariadb:
        image: mariadb:latest
        options: >-
          --health-cmd="mysqladmin ping"
          --health-interval=10s
          --health-timeout=5s
          --health-retries=3
        env:
          MYSQL_ROOT_PASSWORD: root
          MYSQL_DATABASE: news_db
    
    steps:
    - uses: actions/checkout@v2
    - uses: actions/setup-python@v2
      with:
        python-version: 3.10
    
    - name: Install dependencies
      run: |
        pip install -r requirements.txt
    
    - name: Run tests
      run: python manage.py test news
```

## Test Coverage Targets

- Overall: > 80%
- Critical paths: > 95%
- Views/APIs: > 85%
- Models: > 90%

## Performance Benchmarks

### Expected Response Times

- List articles: < 500ms
- Get article detail: < 200ms
- Create article: < 300ms
- Article approval: < 1s
- User registration: < 500ms

### Database Benchmarks

- Query all articles (1000 records): < 100ms
- Filter by publisher: < 50ms
- Full text search: < 200ms
