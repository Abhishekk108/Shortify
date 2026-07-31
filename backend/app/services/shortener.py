import random
import string

from sqlalchemy.orm import Session

from app.models.url import Url

# Base62 character set: lowercase + uppercase + digits
BASE62_CHARS = string.ascii_letters + string.digits  # a-z, A-Z, 0-9


def generate_short_code(length: int = 6) -> str:
    """Generate a random base62 short code of the given length."""
    return "".join(random.choices(BASE62_CHARS, k=length))


def get_unique_short_code(db: Session, length: int = 6) -> str:
    """
    Generate a short code that doesn't already exist in the database.

    Retries up to 10 times. Raises RuntimeError if no unique code is found.
    """
    for _ in range(10):
        code = generate_short_code(length)
        existing = db.query(Url).filter(Url.short_code == code).first()
        if existing is None:
            return code

    raise RuntimeError(
        f"Unable to generate a unique short code after 10 attempts (length={length}). "
        "Consider increasing code length."
    )
