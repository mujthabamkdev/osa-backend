# 🐍 Online Sharia Academy Backend

FastAPI-based REST API backend for the Online Sharia Academy platform, providing comprehensive Islamic education management with role-based access control.

## 🚀 Features

### 🔐 Authentication & Security

- JWT-based authentication with secure token management
- Role-based access control (Admin, Teacher, Student, Parent)
- Password hashing with bcrypt
- CORS middleware for cross-origin requests
- Request validation with Pydantic

### 👥 User Management

- Multi-role user system with proper permissions
- User registration and authentication
- Profile management and user data handling
- Admin user oversight and management

### 📚 Course Management

- Course creation and management for teachers
- Student enrollment and unenrollment
- Progress tracking for enrolled courses
- Course content organization

### 📝 Learning Tools

- Personal notes system for students
- Progress analytics and reporting
- Academic reports for parents
- Course progress tracking

### 🗄️ Database

- SQLAlchemy ORM with SQLite/PostgreSQL support
- Alembic database migrations
- Proper relationships and constraints
- Data validation and integrity

## 🛠️ Technology Stack

- **FastAPI**: Modern Python web framework
- **SQLAlchemy**: SQL toolkit and ORM
- **Alembic**: Database migration tool
- **Pydantic**: Data validation and serialization
- **SQLite/PostgreSQL**: Database engines
- **JWT**: JSON Web Token authentication
- **bcrypt**: Password hashing
- **pytest**: Testing framework

## 🚦 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip package manager

### Installation

1. **Clone and navigate:**

   ```bash
   cd osa-backend
   ```

2. **Create virtual environment:**

   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

4. **Set environment variables:**

   ```bash
   export DATABASE_URL="sqlite:///./osa.db"
   export JWT_SECRET="your-secret-key-here"
   export CORS_ORIGINS="http://localhost:4200"
   ```

5. **Run database migrations:**

   ```bash
   PYTHONPATH=. alembic upgrade head
   ```

6. **Create test user (optional):**

   ```bash
   PYTHONPATH=. python create_test_user.py
   ```

7. **Start development server:**
   ```bash
   PYTHONPATH=. uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
   ```

### Environment Variables

| Variable               | Description                | Default                 |
| ---------------------- | -------------------------- | ----------------------- |
| `DATABASE_URL`         | Database connection string | `sqlite:///./osa.db`    |
| `JWT_SECRET`           | Secret key for JWT tokens  | Required                |
| `CORS_ORIGINS`         | Allowed CORS origins       | `http://localhost:4200` |
| `JWT_EXPIRATION_HOURS` | JWT token expiration       | `24`                    |

## 📚 API Documentation

### Authentication Endpoints

```http
POST /api/v1/auth/register
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword",
  "fullName": "User Name",
  "role": "student"
}
```

```http
POST /api/v1/auth/login
Content-Type: application/json

{
  "email": "user@example.com",
  "password": "securepassword"
}
```

### User Management

```http
GET /api/v1/users/me
Authorization: Bearer <token>
```

### Course Management

```http
GET /api/v1/courses
POST /api/v1/courses
GET /api/v1/courses/{id}
PUT /api/v1/courses/{id}
DELETE /api/v1/courses/{id}
```

### Student Features

```http
GET /api/v1/students/courses
GET /api/v1/students/available-courses
POST /api/v1/students/enroll
DELETE /api/v1/students/unenroll/{course_id}
GET /api/v1/students/{student_id}/progress
PATCH /api/v1/students/progress/{course_id}
GET /api/v1/students/{student_id}/notes
POST /api/v1/students/{student_id}/notes
PUT /api/v1/students/{student_id}/notes/{note_id}
DELETE /api/v1/students/{student_id}/notes/{note_id}
```

### Parent Features

```http
GET /api/v1/parents/{parent_id}/children
GET /api/v1/students/{child_id}/academic-report
```

### Admin Features

```http
GET /api/v1/admin/stats
GET /api/v1/admin/users
GET /api/v1/admin/courses
```

## 🗄️ Database Schema

### Users Table

```sql
CREATE TABLE users (
    id INTEGER PRIMARY KEY,
    email VARCHAR(255) UNIQUE NOT NULL,
    hashed_password VARCHAR(255) NOT NULL,
    role VARCHAR(50) NOT NULL,
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Courses Table

```sql
CREATE TABLE courses (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    teacher_id INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Notes Table

```sql
CREATE TABLE notes (
    id INTEGER PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    content TEXT NOT NULL,
    student_id INTEGER REFERENCES users(id),
    course_id INTEGER REFERENCES courses(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

## 🧪 Testing

Run the test suite:

```bash
PYTHONPATH=. pytest tests/
```

## 🚀 Deployment

### Using Docker

1. **Build the image:**

   ```bash
   docker build -t osa-backend .
   ```

2. **Run the container:**
   ```bash
   docker run -p 8000:8000 \
     -e DATABASE_URL="postgresql://user:pass@host:5432/db" \
     -e JWT_SECRET="your-secret" \
     osa-backend
   ```

### Using Python

1. **Install dependencies:**

   ```bash
   pip install -r requirements.txt
   ```

2. **Set environment variables**

3. **Run migrations:**

   ```bash
   PYTHONPATH=. alembic upgrade head
   ```

4. **Start server:**
   ```bash
   PYTHONPATH=. uvicorn app.main:app --host 0.0.0.0 --port 8000
   ```

## 📁 Project Structure

```
osa-backend/
├── app/
│   ├── api/v1/
│   │   ├── routes/           # API route handlers
│   │   │   ├── auth.py       # Authentication
│   │   │   ├── users.py      # User management
│   │   │   ├── courses.py    # Course management
│   │   │   ├── students.py   # Student features
│   │   │   ├── parents.py    # Parent features
│   │   │   └── admin.py      # Admin features
│   │   └── deps.py           # Dependencies
│   ├── core/                 # Core functionality
│   │   ├── config.py         # Configuration
│   │   ├── database.py       # Database setup
│   │   ├── security.py       # Security utilities
│   │   └── db.py             # Database session
│   ├── models/               # SQLAlchemy models
│   │   ├── user.py           # User model
│   │   ├── course.py         # Course model
│   │   └── note.py           # Notes model
│   └── schemas/              # Pydantic schemas
│       ├── auth.py           # Auth schemas
│       ├── course.py         # Course schemas
│       └── user.py           # User schemas
├── alembic/                  # Database migrations
├── tests/                    # Test suite
├── Dockerfile                # Docker configuration
├── requirements.txt          # Python dependencies
├── pytest.ini               # Test configuration
└── README.md                # This file
```

## 🤝 Contributing

1. Follow the existing code style
2. Write tests for new features
3. Update documentation
4. Ensure all tests pass
5. Create meaningful commit messages

## 📄 License

MIT License - see LICENSE file for details.</content>
<parameter name="oldString">OnlineShariaAcademy Backend (FastAPI)

Env: DATABASE_URL, JWT_SECRET, CORS_ORIGINS

Local:
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload

API:
POST /api/v1/auth/register
POST /api/v1/auth/login
GET /api/v1/users/me
GET/POST /api/v1/users (admin)
GET/POST /api/v1/courses (auth/teacher)
