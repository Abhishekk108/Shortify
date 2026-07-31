from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.middleware import SlowAPIMiddleware

from app.config import settings
from app.routers import analytics, redirect, urls
from app.utils.rate_limit import limiter

app = FastAPI(
    title="Shortify API",
    description="A URL shortener API built with FastAPI and SQLAlchemy.",
    version="0.1.0",
)

# Attach limiter to app state (required by slowapi)
app.state.limiter = limiter

# 429 handler for rate limit violations
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Rate limiting middleware
app.add_middleware(SlowAPIMiddleware)

# CORS — allow requests from the Vite frontend dev server
app.add_middleware(
    CORSMiddleware,
    allow_origins=[settings.FRONTEND_ORIGIN],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers — redirect must be LAST so /{short_code} doesn't shadow /api/* routes
app.include_router(urls.router, prefix="/api/urls", tags=["URLs"])
app.include_router(analytics.router, prefix="/api", tags=["Analytics"])
app.include_router(redirect.router)


@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    """Catch-all handler for unhandled exceptions."""
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health", tags=["Health"])
def health_check():
    """Simple liveness probe."""
    return {"status": "ok"}
