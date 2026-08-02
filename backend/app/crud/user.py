"""
app/crud/user.py — Database access functions for the User model.

All password hashing is delegated to app.security — this module
only receives already-hashed values or plain passwords to verify.
"""
from sqlalchemy.orm import Session

from app.models.user import User
from app.schemas.user import UserCreate
from app.security import hash_password


def get_user_by_email(db: Session, email: str) -> User | None:
    """Return the User with the given email, or None if not found."""
    return db.query(User).filter(User.email == email).first()


def get_user_by_username(db: Session, username: str) -> User | None:
    """Return the User with the given username, or None if not found."""
    return db.query(User).filter(User.username == username).first()


def get_user_by_id(db: Session, user_id: int) -> User | None:
    """Return the User with the given primary key, or None if not found."""
    return db.query(User).filter(User.id == user_id).first()


def create_user(db: Session, payload: UserCreate) -> User:
    """
    Create a new User record.

    The plain-text password from the payload is hashed before persistence.
    The raw password is never stored or logged.
    """
    user = User(
        username=payload.username,
        email=payload.email,
        hashed_password=hash_password(payload.password),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
