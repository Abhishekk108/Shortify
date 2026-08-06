from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

from app.config import settings

# PostgreSQL uses connection pooling by default — no driver-specific
# connect_args are needed.  The old SQLite check_same_thread workaround
# has been removed; psycopg2 is thread-safe out of the box.
engine = create_engine(
    settings.DATABASE_URL,
    # pool_pre_ping keeps stale connections from causing errors after a
    # database restart or network interruption.
    pool_pre_ping=True,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """FastAPI dependency that provides a database session per request."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
