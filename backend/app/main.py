from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

app = FastAPI(
    title="Shortify API",
    description="A URL shortener API built with FastAPI and SQLAlchemy.",
    version="0.1.0",
)

# CORS — allow requests from the Vite frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health", tags=["Health"])
def health_check():
    """Simple liveness probe."""
    return {"status": "ok"}
