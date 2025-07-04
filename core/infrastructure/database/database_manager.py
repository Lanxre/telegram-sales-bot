from contextlib import asynccontextmanager
from typing import AsyncGenerator, Dict, Optional, Type, TypeVar

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from config import DatabaseSettings
from logger import LoggerBuilder

logger = LoggerBuilder("DatabaseManager").add_stream_handler().build()

T = TypeVar("T")


class DatabaseManager:
    def __init__(
        self,
        config: DatabaseSettings,
        *,
        echo: bool = False,
        pool_size: int = 5,
        max_overflow: int = 10,
        pool_recycle: int = 3600,
        pool_timeout: int = 30,
        repositories: Optional[list[Type]] = None,
    ):
        """
        Initialize database manager with connection settings.

        Args:
            config: Database configuration settings
            echo: Enable SQL query logging
            pool_size: Number of connections to keep in pool
            max_overflow: Maximum number of connections beyond pool_size
            pool_recycle: Recycle connections after this many seconds
            pool_timeout: Timeout for getting a connection from pool
            repositories: List of repository classes to register
        """
        self.engine = self._create_engine(
            config,
            echo=echo,
            pool_size=pool_size,
            max_overflow=max_overflow,
            pool_recycle=pool_recycle,
            pool_timeout=pool_timeout,
        )
        self.session_pool = self._create_session_pool()
        self._repository_registry: Dict[str, Type] = {}

        if repositories:
            for repo_class in repositories:
                self.register_repository(repo_class)

    @staticmethod
    def _create_engine(
        config: DatabaseSettings,
        *,
        echo: bool = False,
        **engine_kwargs,
    ) -> AsyncEngine:
        """Create async database engine with appropriate configuration."""
        try:
            if config.driver == "aiosqlite":
                database_url = config.sqlite_url
                connect_args = {"check_same_thread": False}
                engine_kwargs.setdefault("connect_args", connect_args)
            else:
                database_url = config.postgresql_url
                # PostgreSQL-specific optimizations
                engine_kwargs.setdefault("pool_pre_ping", True)
                engine_kwargs.setdefault("isolation_level", "AUTOCOMMIT")

            return create_async_engine(
                database_url,
                echo=echo,
                **engine_kwargs,
            )
        except Exception as e:
            logger.error(f"Engine creation error: {str(e)}")
            raise

    def _create_session_pool(self) -> async_sessionmaker[AsyncSession]:
        """Create async session factory with configured settings."""
        return async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,
        )

    @asynccontextmanager
    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide a transactional database session context manager."""
        async with self.session_pool() as session:
            try:
                yield session
                await session.commit()
            except SQLAlchemyError as e:
                logger.error(f"Database error: {str(e)}")
                await session.rollback()
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}", exc_info=True)
                await session.rollback()
                raise
            finally:
                await session.close()

    def register_repository(self, repository_class: Type[T]) -> None:
        """Register a repository class for dynamic instantiation."""
        if not hasattr(repository_class, "__name__"):
            raise ValueError("Repository class must have a __name__ attribute")

        if repository_class.__name__ in self._repository_registry:
            logger.warning(f"Repository {repository_class.__name__} already registered")

        self._repository_registry[repository_class.__name__] = repository_class

    def get_repository(self, repository_class: Type[T], session: AsyncSession) -> T:
        """Get an instance of the specified repository class with the given session."""
        repo_name = repository_class.__name__
        if repo_name not in self._repository_registry:
            raise ValueError(f"Repository {repo_name} not registered")

        return self._repository_registry[repo_name](session)

    def get_repo(self, repository_class: Type[T], session: AsyncSession) -> T:
        """Alias for get_repository."""
        return self.get_repository(repository_class, session)

    def get_registered_repositories(self) -> list[str]:
        """Get names of all registered repositories."""
        return list(self._repository_registry.keys())

    async def dispose(self) -> None:
        """Close all connections in the connection pool."""
        await self.engine.dispose()
