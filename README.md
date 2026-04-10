# TaskFlow — REST API & Dashboard

A full-stack task management application featuring a RESTful Python/Flask backend with JWT authentication, SQLite database, and a responsive frontend dashboard.

Built as a portfolio project to demonstrate REST API design, database modeling, and full-stack development skills.

---

## Features

- **JWT Authentication** — Secure register/login with access & refresh tokens
- **Full CRUD** — Create, read, update, and delete tasks via REST endpoints
- **Filtering & Pagination** — Filter tasks by status or priority; paginate large result sets
- **Task Stats Endpoint** — Aggregated counts by status and priority
- **Frontend Dashboard** — Live UI that consumes the API with real-time updates
- **Input Validation** — Server-side validation with descriptive error responses

---

## Tech Stack

| Layer     | Technology                        |
|-----------|-----------------------------------|
| Backend   | Python 3, Flask                   |
| Database  | SQLite + SQLAlchemy ORM           |
| Auth      | JWT (flask-jwt-extended)          |
| Frontend  | HTML, CSS, Vanilla JavaScript     |
| CORS      | flask-cors                        |

---

## Project Structure

```
task-api/
├── run.py                  # App entry point
├── requirements.txt
├── app/
│   ├── __init__.py         # App factory
│   ├── models.py           # SQLAlchemy models (User, Task)
│   └── routes/
│       ├── auth.py         # /api/auth — register, login, refresh, me
│       ├── tasks.py        # /api/tasks — full CRUD + stats
│       └── views.py        # Serves the frontend dashboard
└── templates/
    └── index.html          # Dashboard frontend
```

---

## Getting Started

### 1. Clone the repository

```bash
git clone https://github.com/Davis013/task-api.git
cd task-api
```

### 2. Create a virtual environment

```bash
python -m venv venv
source venv/bin/activate      # Windows: venv\Scripts\activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Run the server

```bash
python run.py
```

Visit `http://localhost:5000` to open the dashboard.

---

## API Reference

### Auth

| Method | Endpoint              | Description                    | Auth Required |
|--------|-----------------------|--------------------------------|---------------|
| POST   | /api/auth/register    | Create a new account           | No            |
| POST   | /api/auth/login       | Login and receive JWT tokens   | No            |
| POST   | /api/auth/refresh     | Get a new access token         | Refresh token |
| GET    | /api/auth/me          | Get current user profile       | Yes           |

### Tasks

| Method | Endpoint              | Description                        | Auth Required |
|--------|-----------------------|------------------------------------|---------------|
| GET    | /api/tasks            | List all tasks (filter/paginate)   | Yes           |
| POST   | /api/tasks            | Create a new task                  | Yes           |
| GET    | /api/tasks/:id        | Get a single task                  | Yes           |
| PUT    | /api/tasks/:id        | Update a task                      | Yes           |
| DELETE | /api/tasks/:id        | Delete a task                      | Yes           |
| GET    | /api/tasks/stats      | Get task counts by status/priority | Yes           |

### Query Parameters (GET /api/tasks)

| Param    | Values                        | Description          |
|----------|-------------------------------|----------------------|
| status   | todo, in_progress, done       | Filter by status     |
| priority | low, medium, high             | Filter by priority   |
| page     | integer (default: 1)          | Page number          |
| per_page | integer (default: 10, max 50) | Results per page     |
| sort     | created_at, updated_at        | Sort field           |
| order    | asc, desc                     | Sort direction       |

---

## Example Requests

### Register
```bash
curl -X POST http://localhost:5000/api/auth/register \
  -H "Content-Type: application/json" \
  -d '{"username": "brandon", "email": "brandon@email.com", "password": "secret123"}'
```

### Create a Task
```bash
curl -X POST http://localhost:5000/api/tasks \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer <your_token>" \
  -d '{"title": "Build portfolio", "priority": "high", "status": "in_progress"}'
```

### Get Tasks Filtered by Status
```bash
curl http://localhost:5000/api/tasks?status=in_progress \
  -H "Authorization: Bearer <your_token>"
```

---

## Data Models

### User
| Field         | Type     | Notes              |
|---------------|----------|--------------------|
| id            | Integer  | Primary key        |
| username      | String   | Unique             |
| email         | String   | Unique             |
| password_hash | String   | bcrypt hashed      |
| created_at    | DateTime |                    |

### Task
| Field       | Type     | Notes                          |
|-------------|----------|--------------------------------|
| id          | Integer  | Primary key                    |
| title       | String   | Required                       |
| description | Text     | Optional                       |
| status      | String   | todo / in_progress / done      |
| priority    | String   | low / medium / high            |
| due_date    | DateTime | Optional, ISO 8601             |
| created_at  | DateTime |                                |
| updated_at  | DateTime | Auto-updated on change         |
| user_id     | Integer  | Foreign key → users.id         |

---

## License

MIT License — free to use, modify, and distribute.
