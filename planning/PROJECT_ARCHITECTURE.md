# Django News Application - Project Architecture

## System Overview

The News Application is a Django-based content management system that enables journalists to publish articles, editors to manage publications, and readers to subscribe to publishers and journalists for curated news content.

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Frontend Layer                           │
│  (HTML Templates + Bootstrap CSS)                            │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┼────────────┐
        │            │            │
   Web Views    REST API    Admin Interface
        │            │            │
└────────────────────┼────────────────────────────────────────┘
│                  Application Layer                          │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Django Views & ViewSets                      │  │
│  │  ├─ ArticleViewSet                                   │  │
│  │  ├─ PublisherViewSet                                │  │
│  │  ├─ UserManagementViews                             │  │
│  │  └─ SubscriptionViews                               │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Business Logic Layer                         │  │
│  │  ├─ Models (CustomUser, Article, Publisher, etc)    │  │
│  │  ├─ Serializers (DRF)                               │  │
│  │  ├─ Forms & Validation                              │  │
│  │  └─ Permission Classes                              │  │
│  └──────────────────────────────────────────────────────┘  │
│  ┌──────────────────────────────────────────────────────┐  │
│  │         Signal Handlers & Utilities                 │  │
│  │  ├─ Email Notifications (Django Signals)            │  │
│  │  ├─ Twitter API Integration                         │  │
│  │  └─ Logging & Monitoring                            │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
                     │
┌────────────────────┴────────────────────────────────────────┐
│                  Data Layer                                 │
│  ┌──────────────────────────────────────────────────────┐  │
│  │          MariaDB Database                            │  │
│  │  ├─ Users Table (CustomUser)                        │  │
│  │  ├─ Articles Table                                  │  │
│  │  ├─ Publishers Table                                │  │
│  │  ├─ Subscriptions Table                             │  │
│  │  └─ Related Tables (Groups, Permissions, etc)       │  │
│  └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Data Flow

### 1. Article Publishing Workflow

```
Journalist creates article
    │
    ▼
Article saved to DB (is_approved=False)
    │
    ▼
Signal triggers email to Editors
    │
    ▼
Editor reviews article
    │
    ├─ Approve: Signal sends notification email
    │            Article posted to Twitter
    │            Subscribers get email notification
    │
    └─ Reject: Email sent to Journalist
```

### 2. Subscription & Content Delivery

```
Reader subscribes to Publisher/Journalist
    │
    ▼
New article approved
    │
    ▼
Check subscriptions
    │
    ├─ Subscriber to Publisher ──► Send email
    ├─ Subscriber to Author ─────► Send email
    └─ Subscriber to Both ───────► Send email (deduplicated)
    │
    ▼
Content available in Reader Dashboard
```

## Component Architecture

### Models (Data Structures)

- **CustomUser** - Extended Django User with role field (Reader, Editor, Journalist)
- **Publisher** - News outlet/organization
- **Article** - News content with approval workflow
- **Subscription** - Links readers to publishers and journalists
- **Group/Permission** - Django's built-in role-based access control

### Views & ViewSets

- **APIViewSets** - REST endpoints for programmatic access
- **TemplateViews** - HTML-based views for web interface
- **PermissionClasses** - Role-based access control

### External Integrations

- **Email Service** - Gmail SMTP for notifications
- **Twitter API** - Auto-posting approved articles
- **Database** - MariaDB with custom configuration

## Key Design Decisions

1. **Custom User Model** - Allows future extensions and role assignment
2. **Group-based Permissions** - Uses Django's permission system for role management
3. **Signal-based Notifications** - Decouples email logic from business logic
4. **REST API** - Enables third-party integrations and mobile apps
5. **Template-based Web UI** - Traditional Django templates for accessibility

## Technology Stack

| Layer | Technology |
|-------|-----------|
| Web Framework | Django 4.2+ |
| API | Django REST Framework |
| Database | MariaDB |
| Task Queue | Django Signals (could extend with Celery) |
| Email | Gmail SMTP |
| External APIs | Twitter/X API v2 |
| Logging | Python Logging Module |
| Authentication | Django Built-in Auth + Custom User |

## Security Architecture

- **Authentication** - Session-based auth for web, Token-based for API
- **Authorization** - Group-based permissions for role management
- **Data Validation** - Django Forms and DRF Serializers
- **CSRF Protection** - Django middleware
- **SQL Injection** - ORM parameterized queries
- **Sensitive Data** - Environment variables for API keys
