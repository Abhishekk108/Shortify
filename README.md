# Shortify

A full-stack URL shortener built with **FastAPI** and **React**. Guests can shorten URLs publicly with a browser cookie-based `guest_id` for a 3-links-per-day limit, while registered users get unlimited link creation, a protected dashboard, analytics, and full link management.

---

## Features

- **Guest URL Creation** — Public URL shortening for anonymous users with a browser cookie `guest_id` and a 3-links-per-day limit
- **Public URL Shortening** — Anyone can submit a long URL without logging in
- **Unlimited Authenticated Creation** — Logged-in users can create links without the guest daily cap
- **Protected Dashboard** — Authenticated users can manage, search, edit, and delete their links
- **User-specific URLs** — Each link is tied to its owner, or to a guest cookie when anonymous
- **Custom Aliases** — Optional memorable aliases
- **Click Analytics** — Track clicks and summary stats from the dashboard
- **Landing Page Content** — Includes Features, How It Works, and FAQ sections
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

## Database Notes

- The `urls` table supports both authenticated and anonymous link creation.
- `user_id` remains nullable for guest-created links, while `guest_id` is stored as a nullable UUID-like identifier on the URL record for daily guest counting.

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
| ----------------------------- | ------------------------- | ------------------------------- |
| `DATABASE_URL`                | `sqlite:///./shortify.db` | SQLAlchemy DB connection string |
| `BASE_DOMAIN`                 | `http://localhost:8000`   | Public domain for short URLs    |
| `FRONTEND_ORIGIN`             | `http://localhost:5173`   | Allowed CORS origin             |
| `SECRET_KEY`                  | `change-me-in-production` | JWT signing secret              |
| `ALGORITHM`                   | `HS256`                   | JWT algorithm                   |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | `60`                      | Access token lifetime           |

---

## Authentication Flow

```text
Public shorten: Guest or authenticated request → Create short URL
Protected flow: Register → Login → Receive JWT → Access dashboard and analytics
```

1. Publicly shorten a URL via `POST /api/urls` without authentication
2. Register via `/api/auth/register`
3. Login via `/api/auth/login`
4. Receive a JWT access token
5. Send it as `Authorization: Bearer <token>` on protected requests

> Public endpoints include redirect and anonymous URL creation. Protected endpoints include dashboard ownership, analytics, and account-scoped link management.

---

## Working

Shortify follows a simple request lifecycle:

1. The React frontend validates the submitted long URL and prepares a create request.
2. FastAPI receives the request, validates the input again, generates a unique short code or uses a custom alias if provided, and stores the record in the database.
3. The backend returns the newly created short URL to the frontend, where the user can copy or share it.
4. When a visitor opens a short link, the redirect endpoint looks up the code, increments the click count, and issues an HTTP redirect to the original destination.
5. Authenticated users can view analytics, manage their links, and access dashboard summaries tied to their account.

```text
React Frontend → FastAPI API → SQLite Database
                      ↓
                 Redirect flow:
React user clicks /{short_code} → FastAPI lookup → click_count + 1 → HTTP 307 redirect
```

---

## API Overview

### Authentication

| Method | Endpoint             | Description                   |
| ------ | -------------------- | ----------------------------- |
| POST   | `/api/auth/register` | Create a new account (public) |
| POST   | `/api/auth/login`    | Login, receive JWT (public)   |
| GET    | `/api/auth/me`       | Get current user (protected)  |

### URLs & Analytics

| Method | Endpoint                   | Description                                                   |
| ------ | -------------------------- | ------------------------------------------------------------- |
| GET    | `/health`                  | Health check (public)                                         |
| POST   | `/api/urls`                | Create a short URL for guests or authenticated users (public) |
| GET    | `/api/urls`                | List the current authenticated user's URLs (protected)        |
| GET    | `/api/urls/{id}`           | Get a single owned URL (protected)                            |
| DELETE | `/api/urls/{id}`           | Delete an owned URL (protected)                               |
| GET    | `/{short_code}`            | Redirect to destination (public)                              |
| GET    | `/api/analytics/summary`   | Dashboard summary analytics (protected)                       |
| GET    | `/api/urls/{id}/analytics` | View analytics for a single owned URL (protected)             |

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
- Admin moderation controls and stronger abuse-protection tooling
- Time-series analytics and richer click reports
- Profile editing and account deletion
- Frontend auth flow and route guard tests

---

## License

MIT License — see the repository license file for details.
