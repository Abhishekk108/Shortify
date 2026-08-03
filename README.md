# Shortify

A full-stack URL shortener built with **FastAPI** and **React**. Users register/login via JWT, create short links, manage them from a protected dashboard, and view click analytics.

---

## Features

- **JWT Authentication** — Secure register/login with JWT tokens
- **Protected Dashboard** — Access restricted to authenticated users
- **User-specific URLs** — Each link tied to its owner
- **URL Shortening** — Convert long URLs into short links
- **Custom Aliases** — Optional memorable aliases
- **Click Analytics** — Track clicks and summary stats
- **Search & Delete** — Filter and remove links from the dashboard
- **Responsive UI** — Works across desktop and mobile

---

## Tech Stack

| Layer                | Technology            |
| -------------------- | --------------------- |
| Frontend             | React + Vite          |
| UI                   | React Router + Axios  |
| Backend              | Python + FastAPI      |
| Authentication       | JWT via `python-jose` |
| Password Hashing     | Passlib               |
| Validation / Schemas | Pydantic              |
| ORM                  | SQLAlchemy            |
| Database             | SQLite                |
| Migrations           | Alembic               |
| Server               | Uvicorn               |

---

## Project Structure

```text
shortify/
├── backend/
│   ├── app/
│   │   ├── crud/              # DB access helpers
│   │   ├── dependencies/      # Auth dependencies
│   │   ├── models/            # SQLAlchemy models
│   │   ├── routers/           # Auth, URL, analytics endpoints
│   │   ├── schemas/           # Pydantic schemas
│   │   ├── services/          # Shortener + validation logic
│   │   └── utils/             # JWT and rate-limit utilities
│   ├── alembic/               # Database migrations
│   ├── tests/                 # Backend test suite
│   ├── .env.example
│   └── requirements.txt
├── frontend/
│   ├── src/
│   ├── package.json
│   └── vite.config.js
└── README.md
```

---

## Backend Setup

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate     # macOS/Linux

pip install -r requirements.txt
copy .env.example .env

uvicorn app.main:app --reload
```

- API: `http://localhost:8000`
- Docs: `http://localhost:8000/docs`

---

## Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

- UI: `http://localhost:5173`

---

## Environment Variables

Set these in `backend/.env` (see `.env.example`):

| Variable                      | Default                   | Description                     |
| ----------------------------- | ------------------------- | -------------------------------- |
| `DATABASE_URL`                | `sqlite:///./shortify.db` | SQLAlchemy DB connection string |
| `BASE_DOMAIN`                 | `http://localhost:8000`   | Public domain for short URLs    |
| `FRONTEND_ORIGIN`             | `http://localhost:5173`   | Allowed CORS origin             |
| `SECRET_KEY`                  | `change-me-in-production` | JWT signing secret              |
| `ALGORITHM`                   | `HS256`                   | JWT algorithm                   |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                      | Access token lifetime           |

---

## Authentication Flow

```text
Register → Login → Receive JWT → Access Protected APIs
```

1. Register via `/api/auth/register`
2. Login via `/api/auth/login`
3. Receive a JWT access token
4. Send it as `Authorization: Bearer <token>` on protected requests

---

## API Overview

### Authentication

| Method | Endpoint              | Description             |
| ------ | ---------------------- | ------------------------ |
| POST   | `/api/auth/register`  | Create a new account     |
| POST   | `/api/auth/login`     | Login, receive JWT       |
| GET    | `/api/auth/me`        | Get current user         |

### URLs & Analytics

| Method | Endpoint                 | Description                    |
| ------ | ------------------------ | ------------------------------- |
| GET    | `/health`                | Health check                    |
| POST   | `/api/urls`              | Create a short URL              |
| GET    | `/api/urls`              | List current user's URLs        |
| GET    | `/api/urls/{id}`         | Get a single owned URL          |
| DELETE | `/api/urls/{id}`         | Delete an owned URL             |
| GET    | `/{short_code}`          | Redirect to destination         |
| GET    | `/api/analytics/summary` | Dashboard summary analytics     |

---


## Deployment

Built for local dev, but adaptable to production with:

- Managed PostgreSQL or SQLite database
- Hosted FastAPI server (Railway, Render, Azure App Service)
- Static frontend hosting (Netlify, Vercel)
- Secure env vars for `SECRET_KEY` and CORS

Also enable HTTPS, set a real `BASE_DOMAIN`, and rotate the JWT secret.

---

## Future Improvements

- Password reset and email verification
- Role-based authorization for admin operations
- Time-series analytics and detailed click reports
- Profile editing and account deletion
- Frontend auth flow and route guard tests

---

## License

MIT License — see the repository license file for details.