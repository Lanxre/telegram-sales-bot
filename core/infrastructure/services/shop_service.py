from sqlalchemy.exc import IntegrityError

from core.infrastructure.database import DatabaseManager
from core.infrastructure.database.models import User
from core.infrastructure.repositories import UserRepository
from core.internal.models import UserCreate

from logger import LoggerBuilder

logger = LoggerBuilder("Service").add_stream_handler().build()

class ShopService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    async def create_user(self, user_data: UserCreate) -> User:
        """Create a new user or return existing user if telegram_id already exists."""
        async with self.db_manager.session_pool() as session:
            user_repo: UserRepository = self.db_manager.get_repo(
                UserRepository, session
            )
            # Check if user already exists
            existing_user = await user_repo.get(session, user_data.telegram_id)
            if existing_user:
                logger.warning(f"User: '{existing_user.full_name}' already was create")
                return existing_user
            # Create new user if not found
            try:
                user = await user_repo.create(session, user_data)
                await session.commit()
                logger.info(f"User: '{user.full_name}' was create")
                return user
            except IntegrityError:
                # Handle race condition where user was created concurrently
                await session.rollback()
                existing_user = await user_repo.get(session, user_data.telegram_id)
                if existing_user:
                    return existing_user
                raise  # Re-raise if not a duplicate key error
