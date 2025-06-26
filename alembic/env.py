from logging.config import fileConfig
import logging
from sqlalchemy.ext.asyncio import create_async_engine
from alembic import context
from core.infrastructure.database.models import BaseModel # Import SQLAlchemy models
from config import load_settings

# db
database_settings, _ = load_settings()

# Configure Alembic logging to match main.py
fileConfig(context.config.config_file_name, disable_existing_loggers=False)
logger = logging.getLogger("alembic.env")

# Alembic Config object
config = context.config

# Set target_metadata to your models' metadata
target_metadata = BaseModel.metadata
logger.info(f"Detected tables in metadata: {list(target_metadata.tables.keys())}")

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""
    url = database_settings.sqlite_url
    logger.info("Running migrations in offline mode")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()
        logger.debug("Offline migrations completed")

async def run_migrations_online() -> None:
    """Run migrations in 'online' mode using async engine."""
    connectable = create_async_engine(
        database_settings.sqlite_url,
        pool_pre_ping=True,
    )
    logger.info("Running migrations in online mode")

    async with connectable.connect() as connection:
        await connection.run_sync(
            lambda sync_conn: context.configure(
                connection=sync_conn,
                target_metadata=target_metadata
            )
        )
        await connection.run_sync(lambda _: context.run_migrations())
        logger.debug("Online migrations completed")

    await connectable.dispose()
    logger.debug("Async engine disposed")

if context.is_offline_mode():
    run_migrations_offline()
else:
    import asyncio
    asyncio.run(run_migrations_online())