# Shortify

A full-stack URL shortener built with **FastAPI** and **React**. Convert long URLs into short, shareable links, track click analytics, and manage everything through a clean dashboard.

---

## Features

- **Shorten URLs** — Generate a unique short code for any valid URL
- **Custom Aliases** — Optionally define your own short code
- **Redirect** — Visiting a short URL redirects to the original destination
- **Dashboard** — View, search, and manage all your links in one place
- **Click Analytics** — Track total clicks, timestamps, and referrer data per link
- **Responsive UI** — Works on mobile, tablet, and desktop

---

## Tech Stack

| Layer | Technology |
|---|---|
| Frontend | React + Vite + Tailwind CSS |
| HTTP Client | Axios |
| Routing | React Router |
| Backend | Python + FastAPI |
| ORM | SQLAlchemy |
| Database | SQLite |
| Migrations | Alembic |
| Server | Uvicorn |

---

## Project Structure

```
shortify/
├── backend/        # FastAPI app (API, models, services)
├── frontend/       # React + Vite app (UI)
├── .gitignore
└── README.md
```

---

## Getting Started

### Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate          # Windows
# source venv/bin/activate    # macOS/Linux

pip install -r requirements.txt

# Copy env config
copy .env.example .env

# Start the dev server
uvicorn app.main:app --reload
```

API available at `http://localhost:8000`  
Swagger docs at `http://localhost:8000/docs`

### Frontend

```bash
cd frontend
npm install
npm run dev
```

UI available at `http://localhost:5173`

---

## API Overview

| Method | Endpoint | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/api/urls` | Create a short URL |
| GET | `/api/urls` | List all URLs |
| GET | `/api/urls/{id}` | Get URL details |
| DELETE | `/api/urls/{id}` | Delete a URL |
| GET | `/{short_code}` | Redirect to original URL |
| GET | `/api/urls/{id}/analytics` | Click analytics for a URL |
| GET | `/api/analytics/summary` | Overall stats summary |

---

## Environment Variables

See `backend/.env.example` for all required config values.

| Variable | Default | Description |
|---|---|---|
| `DATABASE_URL` | `sqlite:///./shortify.db` | SQLAlchemy database URL |
| `BASE_DOMAIN` | `http://localhost:8000` | Base domain for building short URLs |
| `FRONTEND_ORIGIN` | `http://localhost:5173` | Allowed CORS origin |
