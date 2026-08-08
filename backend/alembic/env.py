import sys
import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool

from alembic import context

# ---------------------------------------------------------------------------
# Make sure the backend directory is on sys.path so that `app.*` imports work
# when Alembic is invoked from the backend directory.
# ---------------------------------------------------------------------------
backend_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if backend_dir not in sys.path:
    sys.path.insert(0, backend_dir)

# ---------------------------------------------------------------------------
# Import Base (which carries the metadata) and all models so that their
# table definitions are registered on Base.metadata before autogenerate runs.
# ---------------------------------------------------------------------------
from app.database import Base          # noqa: E402
import app.models                      # noqa: E402, F401  — registers all models
from app.config import settings        # noqa: E402

# Alembic Config object (gives access to values in alembic.ini).
config = context.config

# Override sqlalchemy.url with the value from our pydantic settings so that
# there is a single source of truth for the database URL.
config.set_main_option("sqlalchemy.url", settings.DATABASE_URL)

# Interpret the config file for Python logging (if present).
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Metadata for 'autogenerate' support.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    Configures the context with just a URL so no live database connection
    is required.  Useful for generating SQL scripts to review or apply manually.
    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    Creates an Engine, connects to the database, and runs all pending
    migrations in a transaction.
    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
