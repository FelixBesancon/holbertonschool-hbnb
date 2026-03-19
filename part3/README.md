# HBnB Evolution – Part 3
## Authentication & Database Integration

---

## 1. Overview

This part of the HBnB Evolution project introduces authentication, authorization, and database persistence to transform the application into a secure and production-ready backend.

The application now integrates:

 - JWT-based authentication
 - Role-based access control (admin vs user)
 - Persistent storage with SQLAlchemy (SQLite for development)
 - Fully mapped relational database
 - Database schema visualization using Mermaid.js

This phase marks the transition from a prototype (in-memory storage) to a real-world backend architecture.

---

## 2. Project Structure

```text
hbnb/
├── app/
│   ├── __init__.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │       ├── __init__.py
│   │       ├── users.py
│   │       ├── places.py
│   │       ├── reviews.py
│   │       ├── amenities.py
│   │       ├── auth.py
│   ├── models/
│   │   ├── __init__.py
│   │   ├── basemodel.py
│   │   ├── user.py
│   │   ├── place.py
│   │   ├── review.py
│   │   ├── amenity.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── facade.py
│   ├── persistence/
│   │   ├── __init__.py
│   │   ├── repository.py
│   │   ├── user_repository.py
├── test_db/
│   ├── test_db.py
├── schema.sql
├── run.py
├── config.py
├── requirements.txt
```

---

## 3. Directories & Files

### app/__init__.py
Application Factory updated to:
 - Load configuration (Config)
 - Initialize extensions:
    - SQLAlchemy
    - JWT Manager
    - Bcrypt
 - Register API namespaces

### app/api/v1/
Contains REST API endpoints.

**auth.py**
 - Login endpoint
 - JWT token generation
**Other endpoints** (users, places, reviews, amenities) **now include**:
 - Authentication checks
 - Authorization rules

### app/models/
Defines database models mapped with SQLAlchemy.

**basemodel.py**
 - Abstract class (__abstract__ = True)
 - Provides:
   - UUID primary key
   - timestamps
   - validation helpers

**user.py**
 - Stores hashed password (bcrypt)
 - Includes is_admin role
 - Relationships:
   - one-to-many with Place
   - one-to-many with Review

**place.py**
 - Linked to a User (owner)
 - Many-to-many with Amenity
 - One-to-many with Review

**review.py**
 - Linked to User and Place

**amenity.py**
 - Shared across multiple places

### app/services/
**facade.py**
 - Centralizes business logic
 - Applies validation rules
 - Handles authorization logic (ownership, admin rights)

### app/persistence/
**Implements database persistence.**
 - repository.py
   - Replaces in-memory storage
   - Handles CRUD operations via SQLAlchemy
 - user_repository.py
   - Handles CRUD operation specific for User instances

### requirements.txt
 - flask
 - flask-restx
 - sqlalchemy
 - flask-sqlalchemy
 - flask-bcrypt
 - flask-jwt-extended

### config.py
**Handles environment configuration**:
 - SQLite (development)
 - MySQL (production-ready setup)

### run.py
**Application entry point.**

---

## 4. Authentication & Authorization

### JWT Authentication

 - Users authenticate via login endpoint
 - Receive a JWT token
 - Token required for protected routes

### Role-Based Access Control
 - Regular users:
   - Can manage their own data only

 - Admin users:
   - Full access to all resources
   - Can bypass ownership restrictions

---

## 5. Database Integration

 - SQLAlchemy ORM used for persistence
 - SQLite used for development
 - Ready for MySQL in production

### Relationships implemented:
 - User → Place (one-to-many)
 - User → Review (one-to-many)
 - Place → Review (one-to-many)
 - Place ↔ Amenity (many-to-many via place_amenity)

---

## 6. Database Schema (ER Diagram)

The database structure is visualized using Mermaid.js.
**The diagram represents**:
 - Tables
 - Attributes
 - Relationships

```mermaid
erDiagram
    USERS {
        UUID id PK
        string first_name
        string last_name
        string email
        string password
        boolean is_admin
        datetime created_at
        datetime updated_at
    }

    PLACES {
        UUID id PK
        string title
        string description
        float price
        float latitude
        float longitude
        UUID user_id FK
        datetime created_at
        datetime updated_at
    }

    REVIEWS {
        UUID id PK
        string text
        int rating
        UUID user_id FK
        UUID place_id FK
        datetime created_at
        datetime updated_at
    }

    AMENITIES {
        UUID id PK
        string name
        datetime created_at
        datetime updated_at
    }

    PLACE_AMENITY {
        UUID place_id FK
        UUID amenity_id FK
    }

    USERS ||--o{ PLACES : owns
    USERS ||--o{ REVIEWS : writes
    PLACES ||--o{ REVIEWS : has
    PLACES ||--o{ PLACE_AMENITY : has
    AMENITIES ||--o{ PLACE_AMENITY : includes
```

---

## 7. Installation

1. **Clone the repository**:
   - git clone https://github.com/AdeleM-prog/holbertonschool-hbnb.git
   - cd holbertonschool-hbnb/part3

2. **Install dependencies**:
   - pip install -r requirements.txt

3. **Set environment variables** (optional):
   - export FLASK_ENV=development

4. **Run the application**:
   - python run.py

---

## 8. Database Testing

SQL scripts are provided to generate and test the database schema independently of the ORM.

### Files
- `schema.sql` — full database schema in raw SQL
- `test_db/test_db.py` — generates initial data and runs full CRUD tests with cascade verification

### Run the tests
```bash
python3 test_db/test_db.py
```

### What is tested:
- CREATE: admin user, 2 regular users, 2 places, 3 amenities, 1 review
- READ: all entities with joins
- UPDATE: place price, review text/rating, user name
- DELETE: user deletion with cascade verification (place, reviews, amenity links)

---

## 9. API Documentation

Available at:
 - http://localhost:5000/api/v1/

---

## 10. Key Features

 - JWT Authentication
 - Role-based authorization (admin / user)
 - Persistent database with SQLAlchemy
 - Clean architecture (API / Service / Persistence)
 - Secure password hashing (bcrypt)
 - Full CRUD with database
 - Data validation & integrity
 - ER Diagram visualization with Mermaid

---

## 11. Validation Rules

 - Required fields enforced
 - Types validated
 - Value constraints applied
 - Passwords securely hashed
 - Sensitive data (password) never exposed

---

## 12. Architectural Principles

 - Application Factory Pattern
 - RESTful API design
 - Separation of concerns
 - Repository pattern
 - Facade pattern
 - ORM with SQLAlchemy
 - Secure authentication system
 - Scalable architecture

---

## 13. Authors

Project developed as part of the Holberton School curriculum.

Team:
- **Adele Megelink**: https://github.com/AdeleM-prog
- **Felix Besançon**: https://github.com/FelixBesancon
