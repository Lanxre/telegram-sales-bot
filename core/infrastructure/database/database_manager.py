from typing import AsyncGenerator, Dict, Type

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


class DatabaseManager:
    def __init__(
        self,
        config: DatabaseSettings,
        echo: bool = False,
        repositories: list[Type] = None,
    ):
        self.engine = self.create_engine(config, echo=echo)
        self.session_pool = self.create_session_pool()
        self._repository_registry: Dict[str, Type] = {}
        if repositories:
            for repo_class in repositories:
                self.register_repository(repo_class)

    @staticmethod
    def create_engine(config: DatabaseSettings, echo: bool = False) -> AsyncEngine:
        try:
            if config.driver == "aiosqlite":
                # SQLite configuration
                database_url = config.sqlite_url
                engine = create_async_engine(
                    database_url,
                    echo=echo,
                    connect_args={"check_same_thread": False},  # Required for SQLite
                )
            else:
                # PostgreSQL configuration
                database_url = config.postgresql_url
                engine = create_async_engine(
                    database_url,
                    echo=echo,
                )
            return engine
        except Exception as e:
            logger.error(f"Connection error: {str(e)}")
            raise

    def create_session_pool(self) -> async_sessionmaker[AsyncSession]:
        session_pool = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False,
            autoflush=False,  # Added for better SQLite compatibility
        )
        return session_pool

    async def get_db_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Provide an AsyncSession for database operations."""
        async with self.session_pool() as session:
            try:
                yield session
                await session.commit()
            except SQLAlchemyError as e:
                logger.error(f"Session error: {str(e)}")
                await session.rollback()
                raise
            except Exception as e:
                logger.error(f"Session error: {str(e)}")
                await session.rollback()
                raise

    def register_repository(self, repository_class: Type) -> None:
        """Register a repository class for dynamic instantiation."""
        if not hasattr(repository_class, "__name__"):
            raise ValueError("Repository class must have a __name__ attribute")
        self._repository_registry[repository_class.__name__] = repository_class

    def get_repository(self, repository_class: Type, session: AsyncSession):
        """Get an instance of the specified repository class with the given session."""
        repo_class = self._repository_registry.get(repository_class.__name__)
        if not repo_class:
            raise ValueError(f"Repository {repository_class.__name__} not registered")
        return repo_class(session)

    def get_repo(self, repository_class: Type, session: AsyncSession):
        """Return a repository instance for the given class and session."""
        return self.get_repository(repository_class, session)

    def get_registered_repositories(self) -> list[str]:
        """Return a list of registered repository names."""
        return list(self._repository_registry.keys())
