# Database Schema Documentation

## Entity Relationship Diagram (ERD)

```
┌─────────────────────────────────────────┐
│         news_customuser                 │
├─────────────────────────────────────────┤
│ id (PK)                                 │
│ username                                │
│ email                                   │
│ password_hash                           │
│ first_name                              │
│ last_name                               │
│ role (Reader/Editor/Journalist/Admin)   │
│ is_active                               │
│ created_at                              │
│ updated_at                              │
│ groups (M2M)                            │
└──────────────┬──────────────────────────┘
               │
       ┌───────┴────────┬─────────┐
       │                │         │
       ▼                ▼         ▼
   [Author]        [Editor]  [Subscriber]
       │                │         │
┌──────┴──────┐ ┌──────┴──────┐  │
│    Article  │ │  Approval   │  │
└─────────────┘ └─────────────┘  │
                                 │
                    ┌────────────┘
                    ▼
        ┌───────────────────────┐
        │  Subscription         │
        │  (Reader → Pub/Auth)  │
        └───────────────────────┘
                    │
                    ├──────────┬────────────┐
                    ▼          ▼            ▼
                Publisher   Journalist  Reader
```

## Table Schemas

### 1. auth_user (Django Built-in)
```sql
CREATE TABLE auth_user (
    id INT PRIMARY KEY AUTO_INCREMENT,
    password VARCHAR(255) NOT NULL,
    username VARCHAR(150) UNIQUE NOT NULL,
    email VARCHAR(254) NOT NULL,
    is_staff BOOLEAN DEFAULT 0,
    is_active BOOLEAN DEFAULT 1,
    date_joined DATETIME DEFAULT CURRENT_TIMESTAMP,
    first_name VARCHAR(150),
    last_name VARCHAR(150)
);
```

### 2. news_customuser (Custom Extension)
```sql
CREATE TABLE news_customuser (
    user_ptr_id INT PRIMARY KEY,
    role VARCHAR(20) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_ptr_id) REFERENCES auth_user(id)
);

-- Indexes
CREATE INDEX idx_customuser_role ON news_customuser(role);
```

**Role Values:**
- `reader` - Regular user who reads articles
- `journalist` - User who writes articles
- `editor` - User who approves articles
- `admin` - System administrator

### 3. news_publisher
```sql
CREATE TABLE news_publisher (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(255) NOT NULL UNIQUE,
    description TEXT,
    website VARCHAR(500),
    logo_url VARCHAR(500),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    created_by_id INT,
    FOREIGN KEY (created_by_id) REFERENCES news_customuser(user_ptr_id)
);

-- Indexes
CREATE INDEX idx_publisher_name ON news_publisher(name);
CREATE INDEX idx_publisher_created_by ON news_publisher(created_by_id);
```

### 4. news_article
```sql
CREATE TABLE news_article (
    id INT PRIMARY KEY AUTO_INCREMENT,
    title VARCHAR(255) NOT NULL,
    content LONGTEXT NOT NULL,
    summary TEXT,
    featured_image_url VARCHAR(500),
    author_id INT NOT NULL,
    publisher_id INT,
    is_approved BOOLEAN DEFAULT 0,
    approved_by_id INT,
    published_at DATETIME,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    view_count INT DEFAULT 0,
    FOREIGN KEY (author_id) REFERENCES news_customuser(user_ptr_id),
    FOREIGN KEY (publisher_id) REFERENCES news_publisher(id),
    FOREIGN KEY (approved_by_id) REFERENCES news_customuser(user_ptr_id),
    UNIQUE KEY unique_article (title, author_id)
);

-- Indexes
CREATE INDEX idx_article_author ON news_article(author_id);
CREATE INDEX idx_article_publisher ON news_article(publisher_id);
CREATE INDEX idx_article_approved ON news_article(is_approved);
CREATE INDEX idx_article_published ON news_article(published_at);
CREATE INDEX idx_article_created ON news_article(created_at);
```

### 5. news_subscription
```sql
CREATE TABLE news_subscription (
    id INT PRIMARY KEY AUTO_INCREMENT,
    reader_id INT NOT NULL,
    publisher_id INT,
    journalist_id INT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (reader_id) REFERENCES news_customuser(user_ptr_id),
    FOREIGN KEY (publisher_id) REFERENCES news_publisher(id),
    FOREIGN KEY (journalist_id) REFERENCES news_customuser(user_ptr_id),
    CONSTRAINT check_subscription CHECK (publisher_id IS NOT NULL OR journalist_id IS NOT NULL)
);

-- Indexes
CREATE INDEX idx_subscription_reader ON news_subscription(reader_id);
CREATE INDEX idx_subscription_publisher ON news_subscription(publisher_id);
CREATE INDEX idx_subscription_journalist ON news_subscription(journalist_id);
```

### 6. auth_group (Django Built-in)
```sql
CREATE TABLE auth_group (
    id INT PRIMARY KEY AUTO_INCREMENT,
    name VARCHAR(150) UNIQUE NOT NULL
);

-- Insert default groups
INSERT INTO auth_group (name) VALUES ('Reader'), ('Journalist'), ('Editor'), ('Admin');
```

### 7. auth_permission (Django Built-in)
```sql
CREATE TABLE auth_permission (
    id INT PRIMARY KEY AUTO_INCREMENT,
    content_type_id INT NOT NULL,
    codename VARCHAR(100) NOT NULL,
    name VARCHAR(255) NOT NULL,
    FOREIGN KEY (content_type_id) REFERENCES django_content_type(id),
    UNIQUE KEY unique_permission (content_type_id, codename)
);
```

## Relationships

| From | To | Type | Relationship |
|------|----|----|--------------|
| news_customuser | auth_user | 1:1 | User inheritance |
| news_article | news_customuser (author) | N:1 | Author writes Articles |
| news_article | news_customuser (approved_by) | N:1 | Editor approves Articles |
| news_article | news_publisher | N:1 | Article belongs to Publisher |
| news_subscription | news_customuser (reader) | N:1 | Reader has Subscriptions |
| news_subscription | news_publisher | N:1 | Subscription to Publisher |
| news_subscription | news_customuser (journalist) | N:1 | Subscription to Journalist |
| news_customuser | auth_group | M:N | User has Groups (permissions) |

## Sample Queries

### Get all approved articles by a specific journalist
```sql
SELECT a.* FROM news_article a
WHERE a.author_id = ? AND a.is_approved = 1
ORDER BY a.published_at DESC;
```

### Get articles subscribed to by a reader
```sql
SELECT DISTINCT a.* FROM news_article a
INNER JOIN news_subscription s ON (
    a.publisher_id = s.publisher_id OR 
    a.author_id = s.journalist_id
)
WHERE s.reader_id = ? AND a.is_approved = 1
ORDER BY a.published_at DESC;
```

### Get all pending articles for an editor
```sql
SELECT * FROM news_article
WHERE is_approved = 0
ORDER BY created_at ASC;
```

### Get subscriber count per publisher
```sql
SELECT p.name, COUNT(s.id) as subscriber_count
FROM news_publisher p
LEFT JOIN news_subscription s ON p.id = s.publisher_id
GROUP BY p.id, p.name;
```

### Get top journalists by article count
```sql
SELECT u.username, COUNT(a.id) as article_count
FROM news_customuser u
LEFT JOIN news_article a ON u.user_ptr_id = a.author_id
WHERE u.role = 'journalist'
GROUP BY u.user_ptr_id, u.username
ORDER BY article_count DESC
LIMIT 10;
```

## Indexing Strategy

| Table | Column | Index Type | Purpose |
|-------|--------|-----------|---------|
| news_article | author_id | Regular | Fast author lookups |
| news_article | publisher_id | Regular | Fast publisher lookups |
| news_article | is_approved | Regular | Filter approved articles |
| news_article | published_at | Regular | Timeline queries |
| news_subscription | reader_id | Regular | Reader subscriptions |
| news_subscription | publisher_id | Regular | Publisher subscribers |
| news_customuser | role | Regular | Filter by role |

## Constraints

1. **NOT NULL** - Ensure data integrity for critical fields
2. **UNIQUE** - Prevent duplicates on username, article title+author
3. **FOREIGN KEY** - Maintain referential integrity
4. **CHECK** - Subscription must have either publisher or journalist
5. **DEFAULT** - Auto-populate timestamps and status fields
