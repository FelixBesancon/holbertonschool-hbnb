# HBnB Evolution – Part 4
## Full-Stack Integration (Frontend)

---

## 1. Overview

This part of the HBnB Evolution project adds a dynamic frontend that communicates with the authenticated backend built in Part 3.

The application now integrates:

 - JWT-based authentication
 - Role-based access control (admin vs user)
 - Persistent storage with SQLAlchemy (SQLite for development)
 - Fully mapped relational database
 - Dynamic frontend pages served from `front/`

This phase connects the backend API to a functional HTML/CSS/JS user interface.

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
├── front/
│   ├── index.html
│   ├── login.html
│   ├── place.html
│   ├── add_review.html
│   ├── scripts.js
│   ├── styles.css
│   └── images/
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

### front/
Static frontend served alongside the Flask API.

 - `index.html` — lists all available places with price filter
 - `login.html` — login form (JWT token stored client-side)
 - `place.html` — detail view of a place with amenities and reviews
 - `add_review.html` — authenticated form to submit a review
 - `scripts.js` — all dynamic logic (fetch API, DOM manipulation, auth)
 - `styles.css` — styling
 - `images/` — static assets (icons, logo)

### config.py
**Handles environment configuration**:
 - `SQLALCHEMY_DATABASE_URI` — SQLite by default (`sqlite:///hbnb.db`), overridable via `DATABASE_URL` env var
 - `SECRET_KEY` — overridable via `SECRET_KEY` env var
 - `SQLALCHEMY_TRACK_MODIFICATIONS = False`

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
   - cd holbertonschool-hbnb/part4

2. **Install dependencies**:
   - pip install -r requirements.txt

3. **Set environment variables** (optional):
   - export FLASK_ENV=development

4. **Run the application**:
   - python run.py

---

## 8. Setup & Testing

### Prerequisites
- Python 3.8+
- Virtual environment tool (venv)

### Backend Setup (API)

1. Navigate to the project directory:
   ```bash
   cd holbertonschool-hbnb/part4/hbnb
   ```

2. Create and activate virtual environment:
   ```bash
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Create a test user in the database:
   ```bash
   python - <<'PY'
   from app import create_app, db
   from app.models.user import User
   
   app = create_app()
   with app.app_context():
       db.create_all()
       
       # Create a test user
       user = User(
           first_name='Demo',
           last_name='User',
           email='demo.user@hbnb.io',
           password='demo1234',
           is_admin=False
       )
       db.session.add(user)
       db.session.commit()
       print('Test user created: demo.user@hbnb.io')
   PY
   ```

5. Start the backend API:
   ```bash
   python run.py
   ```
   The API will run on http://127.0.0.1:5000

### Frontend Setup

1. In a new terminal, navigate to the front directory:
   ```bash
   cd holbertonschool-hbnb/part4/hbnb/front
   ```

2. Start a local web server:
   ```bash
   python -m http.server 8000
   ```
   The frontend will be available at http://localhost:8000

### Testing Authentication (Task 2)

1. Open http://localhost:8000/login.html in your browser
2. Enter the test credentials:
   - **Email:** demo.user@hbnb.io
   - **Password:** demo1234
3. Click "Login"
4. Expected result:
   - JWT token stored in cookie (`token`)
   - Redirect to index.html
   - Successful login message

### API Testing with curl

Test the login endpoint directly:
```bash
curl -X POST http://127.0.0.1:5000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"demo.user@hbnb.io","password":"demo1234"}'
```

Expected response:
```json
{
    "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJmcmVzaCI6ZmFsc2UsImlhdCI6MTc3NTQ4MDAzMywianRpIjoiM2ViMjM2ZWMtNmQzZS00ZmE0LWJhZmMtZDAxMzYwODEyM2UxIiwidHlwZSI6ImFjY2VzcyIsInN1YiI6ImM1MjFkYWM2LThiMWMtNDg5MC1iMzdjLTQxMWJhYzBjNjE1NyIsIm5iZiI6MTc3NTQ4MDAzMywiY3NyZiI6IjBhZWJmN2JhLTg5MmYtNGFmNy04Y2RhLTE5NmExMGE3ZGE0YyIsImV4cCI6MTc3NTQ4MDkzMywiaXNfYWRtaW4iOmZhbHNlfQ.JfMa4sBtmsqr-7-JmW19E21NOLrARcKOWrIO7-TvnfU"
}
```

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
 - Dynamic frontend (HTML/CSS/JS)
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

## 13. Author

Project developed as part of the Holberton School curriculum.

Contributor:
- **Felix Besançon**: https://github.com/FelixBesancon
