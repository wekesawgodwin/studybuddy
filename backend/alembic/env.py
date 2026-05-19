# backend/alembic/env.py

import os
from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from alembic import context

# Import Base and all models so Alembic can detect the schema.
# Every model file must be imported here — if a model is missing,
# Alembic will not generate a migration for its table.
from app.db.session import Base
from app.models.user import User       # noqa: F401 — import needed for autogenerate
from app.models.otp import OTPCode     # noqa: F401 — import needed for autogenerate

# Alembic Config object — provides access to values in alembic.ini
config = context.config

# Set up Python logging from the alembic.ini [loggers] section
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# Tell Alembic what the target schema looks like.
# autogenerate compares this metadata against the live database
# to figure out what CREATE TABLE / ALTER TABLE statements to generate.
target_metadata = Base.metadata

# Read DATABASE_URL from the environment and inject it into the config.
# This overrides the %(DATABASE_URL)s placeholder in alembic.ini.
DATABASE_URL = os.environ.get("DATABASE_URL")
if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL environment variable is not set")

config.set_main_option("sqlalchemy.url", DATABASE_URL)


def run_migrations_offline() -> None:
    """
    Run migrations in offline mode.
    This generates SQL scripts without connecting to the database.
    Useful for reviewing what a migration will do before applying it.
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
    """
    Run migrations in online mode.
    This connects to the database and applies migrations directly.
    This is what `alembic upgrade head` uses.
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


# Alembic calls this file as a script — choose online or offline mode
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()