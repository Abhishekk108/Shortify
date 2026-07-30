"""
seed.py — Insert sample data for local development.

Safe to run multiple times: checks for existing records before inserting.

Usage:
    python seed.py
(from the backend/ directory with the venv activated)
"""

import sys
import os
from datetime import datetime, timedelta

# Ensure the backend directory is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.database import SessionLocal
from app.models.url import Url
from app.models.click import Click


SAMPLE_URLS = [
    {
        "original_url": "https://www.github.com/features/copilot",
        "short_code": "ghcop",
        "custom_alias": "github-copilot",
    },
    {
        "original_url": "https://fastapi.tiangolo.com/tutorial/",
        "short_code": "fapi",
        "custom_alias": "fastapi-docs",
    },
    {
        "original_url": "https://docs.sqlalchemy.org/en/20/orm/",
        "short_code": "sqla",
        "custom_alias": None,
    },
]


def seed() -> None:
    db = SessionLocal()
    try:
        inserted_urls: list[Url] = []

        for data in SAMPLE_URLS:
            existing = db.query(Url).filter(Url.short_code == data["short_code"]).first()
            if existing:
                print(f"  [SKIP] Url short_code={data['short_code']!r} already exists (id={existing.id})")
                inserted_urls.append(existing)
            else:
                url = Url(
                    original_url=data["original_url"],
                    short_code=data["short_code"],
                    custom_alias=data["custom_alias"],
                    created_at=datetime.utcnow(),
                    is_active=True,
                    click_count=0,
                )
                db.add(url)
                db.flush()  # get the id before committing
                print(f"  [INSERT] Url id={url.id} short_code={url.short_code!r} -> {url.original_url}")
                inserted_urls.append(url)

        db.commit()

        # Refresh so we have the DB-assigned ids available
        for url in inserted_urls:
            db.refresh(url)

        # ----------------------------------------------------------------
        # Sample clicks — 2–3 clicks linked to the first two URL records
        # ----------------------------------------------------------------
        sample_clicks = [
            {
                "url": inserted_urls[0],
                "clicked_at": datetime.utcnow() - timedelta(hours=3),
                "ip_address": "203.0.113.42",
                "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
                "referrer": "https://www.google.com/",
            },
            {
                "url": inserted_urls[0],
                "clicked_at": datetime.utcnow() - timedelta(hours=1),
                "ip_address": "198.51.100.7",
                "user_agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15",
                "referrer": "https://twitter.com/",
            },
            {
                "url": inserted_urls[1],
                "clicked_at": datetime.utcnow() - timedelta(minutes=30),
                "ip_address": "192.0.2.55",
                "user_agent": "python-httpx/0.27.0",
                "referrer": None,
            },
        ]

        for click_data in sample_clicks:
            url_obj: Url = click_data["url"]
            # Check for an existing click with same url_id + clicked_at to avoid duplicates
            existing_click = (
                db.query(Click)
                .filter(
                    Click.url_id == url_obj.id,
                    Click.clicked_at == click_data["clicked_at"],
                )
                .first()
            )
            if existing_click:
                print(
                    f"  [SKIP] Click url_id={url_obj.id} clicked_at={click_data['clicked_at']} already exists"
                )
            else:
                click = Click(
                    url_id=url_obj.id,
                    clicked_at=click_data["clicked_at"],
                    ip_address=click_data["ip_address"],
                    user_agent=click_data["user_agent"],
                    referrer=click_data["referrer"],
                )
                db.add(click)
                db.flush()
                print(
                    f"  [INSERT] Click id={click.id} url_id={click.url_id} "
                    f"ip={click.ip_address} clicked_at={click.clicked_at}"
                )

                # Keep click_count denormalized on the Url row
                url_obj.click_count += 1

        db.commit()
        print("\nSeed complete.")

    except Exception as exc:
        db.rollback()
        print(f"ERROR: {exc}", file=sys.stderr)
        raise
    finally:
        db.close()


if __name__ == "__main__":
    print("Seeding database...")
    seed()
