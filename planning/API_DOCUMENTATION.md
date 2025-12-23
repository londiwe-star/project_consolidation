# REST API Documentation

## Overview

The News API provides RESTful endpoints for managing articles, publishers, users, and subscriptions. Authentication is required for most endpoints.

## Base URL

```
http://localhost:8000/api/
```

## Authentication

All API requests require authentication. Use one of the following methods:

### Session Authentication (Web Browser)
```bash
# Login first to obtain session cookie
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{"username": "user", "password": "pass"}'
```

### Basic Authentication
```bash
curl -u username:password http://localhost:8000/api/articles/
```

## Endpoints

### 1. Articles

#### List Articles
```
GET /api/articles/
```

**Query Parameters:**
- `approved=true` - Only approved articles
- `author_id=1` - Articles by specific author
- `publisher_id=1` - Articles from publisher
- `page=1` - Pagination
- `search=keyword` - Search in title/content

**Response:**
```json
{
  "count": 150,
  "next": "http://localhost:8000/api/articles/?page=2",
  "previous": null,
  "results": [
    {
      "id": 1,
      "title": "Breaking News",
      "content": "Article content...",
      "summary": "Brief summary",
      "author": {"id": 5, "username": "john_doe"},
      "publisher": {"id": 2, "name": "Tech Daily"},
      "is_approved": true,
      "published_at": "2024-01-15T10:30:00Z",
      "view_count": 245,
      "created_at": "2024-01-15T10:00:00Z"
    }
  ]
}
```

#### Get Article Detail
```
GET /api/articles/{id}/
```

**Response:**
```json
{
  "id": 1,
  "title": "Breaking News",
  "content": "Full article content...",
  "summary": "Brief summary",
  "author": {"id": 5, "username": "john_doe", "email": "john@example.com"},
  "publisher": {"id": 2, "name": "Tech Daily"},
  "approved_by": {"id": 3, "username": "editor_jane"},
  "is_approved": true,
  "published_at": "2024-01-15T10:30:00Z",
  "view_count": 245,
  "created_at": "2024-01-15T10:00:00Z",
  "updated_at": "2024-01-15T11:00:00Z"
}
```

#### Create Article
```
POST /api/articles/
```

**Required Fields:**
```json
{
  "title": "New Article Title",
  "content": "Article content here...",
  "summary": "Brief summary",
  "publisher_id": 2
}
```

**Response:** 201 Created with article object

**Error Codes:**
- `400` - Invalid data
- `401` - Not authenticated
- `403` - User not journalist

#### Update Article
```
PUT /api/articles/{id}/
PATCH /api/articles/{id}/
```

**Allowed Fields:**
- title
- content
- summary
- featured_image_url

**Response:** 200 OK with updated article

#### Delete Article
```
DELETE /api/articles/{id}/
```

**Requirements:** Author or Editor role

**Response:** 204 No Content

#### Approve Article
```
POST /api/articles/{id}/approve/
```

**Requirements:** Editor role

**Response:**
```json
{
  "status": "approved",
  "message": "Article approved successfully",
  "published_at": "2024-01-15T12:00:00Z"
}
```

**Side Effects:**
- Sends email notification to article author
- Posts to Twitter if configured
- Sends notification emails to subscribers

### 2. Publishers

#### List Publishers
```
GET /api/publishers/
```

**Response:**
```json
{
  "count": 15,
  "results": [
    {
      "id": 1,
      "name": "Tech Daily",
      "description": "Latest tech news",
      "website": "https://techdaily.com",
      "subscriber_count": 1250,
      "article_count": 456
    }
  ]
}
```

#### Get Publisher Detail
```
GET /api/publishers/{id}/
```

**Response includes:**
- Publisher info
- Recent articles
- Editor list
- Journalist list

#### Create Publisher
```
POST /api/publishers/
```

**Requirements:** Editor or Admin role

**Fields:**
```json
{
  "name": "News Agency",
  "description": "Description",
  "website": "https://example.com",
  "logo_url": "https://example.com/logo.png"
}
```

### 3. Users

#### List Users
```
GET /api/users/
```

**Filters:**
- `role=journalist` - Filter by role
- `is_active=true`

#### Get User Profile
```
GET /api/users/{id}/
GET /api/users/me/ - Current user
```

#### Update Profile
```
PATCH /api/users/me/
```

**Allowed Fields:**
```json
{
  "first_name": "John",
  "last_name": "Doe",
  "email": "john@example.com"
}
```

#### Change Password
```
POST /api/users/me/change-password/
```

**Required:**
```json
{
  "old_password": "current_password",
  "new_password": "new_password"
}
```

### 4. Subscriptions

#### List My Subscriptions
```
GET /api/subscriptions/
```

**Response:**
```json
{
  "count": 5,
  "results": [
    {
      "id": 1,
      "publisher": {"id": 2, "name": "Tech Daily"},
      "journalist": null,
      "created_at": "2024-01-01T00:00:00Z"
    },
    {
      "id": 2,
      "publisher": null,
      "journalist": {"id": 5, "username": "john_doe"},
      "created_at": "2024-01-05T00:00:00Z"
    }
  ]
}
```

#### Subscribe to Publisher
```
POST /api/subscriptions/
```

**Data:**
```json
{
  "publisher_id": 2
}
```

**Response:** 201 Created

#### Subscribe to Journalist
```
POST /api/subscriptions/
```

**Data:**
```json
{
  "journalist_id": 5
}
```

#### Unsubscribe
```
DELETE /api/subscriptions/{id}/
```

**Response:** 204 No Content

### 5. Authentication

#### Login
```
POST /api/login/
```

**Data:**
```json
{
  "username": "john_doe",
  "password": "password123"
}
```

**Response:**
```json
{
  "user": {"id": 5, "username": "john_doe", "role": "journalist"},
  "message": "Login successful"
}
```

#### Logout
```
POST /api/logout/
```

**Response:**
```json
{
  "message": "Logout successful"
}
```

#### Register
```
POST /api/register/
```

**Data:**
```json
{
  "username": "newuser",
  "email": "new@example.com",
  "password": "secure_password",
  "first_name": "John",
  "last_name": "Doe",
  "role": "reader"
}
```

## Error Responses

### 400 Bad Request
```json
{
  "error": "Invalid input",
  "details": {
    "title": ["This field is required."]
  }
}
```

### 401 Unauthorized
```json
{
  "detail": "Authentication credentials were not provided."
}
```

### 403 Forbidden
```json
{
  "detail": "You do not have permission to perform this action."
}
```

### 404 Not Found
```json
{
  "detail": "Not found."
}
```

### 500 Internal Server Error
```json
{
  "error": "Internal server error",
  "message": "Error details..."
}
```

## Rate Limiting

- 1000 requests per hour per user
- 100 requests per minute

## Pagination

Default page size: 10

```
GET /api/articles/?page=2&page_size=20
```

## Filtering & Search

### Article Filters
```
GET /api/articles/?approved=true&author_id=5&publisher_id=2
```

### User Filters
```
GET /api/users/?role=journalist&is_active=true
```

### Search
```
GET /api/articles/?search=climate+change
```

## Sorting

Available sort fields (prefix with `-` for descending):
- `created_at`
- `published_at`
- `view_count`
- `title`

```
GET /api/articles/?ordering=-published_at
```

## CORS

CORS is enabled for the API.

```
GET /api/articles/
Access-Control-Allow-Origin: *
```

## Webhooks (Future)

Planned webhook events:
- `article.created`
- `article.approved`
- `article.published`
- `subscription.created`
