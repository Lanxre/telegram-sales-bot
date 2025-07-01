from contextlib import asynccontextmanager
from datetime import datetime, timezone
from typing import AsyncIterator, List

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.infrastructure.database import DatabaseManager
from core.infrastructure.database.models import Dialog, Message
from core.infrastructure.repositories import DialogRepository, MessageRepository
from core.internal.models import DialogCreate, DialogUpdate, MessageCreate
from logger import LoggerBuilder

logger = LoggerBuilder("Dialog - Service").add_stream_handler().build()


class DialogService:
    def __init__(self, db_manager: DatabaseManager):
        self._db_manager = db_manager

    @property
    def db_manager(self) -> DatabaseManager:
        return self._db_manager

    @asynccontextmanager
    async def _get_session(self) -> AsyncIterator[AsyncSession]:
        """Context manager for database sessions with error handling."""
        async with self.db_manager.get_db_session() as session:
            try:
                yield session
            except SQLAlchemyError as e:
                logger.error(f"Database operation failed: {str(e)}")
                raise
            except Exception as e:
                logger.error(f"Unexpected error: {str(e)}")
                raise

    async def create_dialog(
        self, dialog_id: int, user1_id: int, user2_id: int
    ) -> Dialog:
        """
        Create a new dialog between two users.

        Args:
            user1_id: Telegram ID of first user
            user2_id: Telegram ID of second user

        Returns:
            Dialog: Created dialog

        Raises:
            ValueError: If dialog creation fails
        """
        async with self._get_session() as session:
            dialog_repo = self.db_manager.get_repo(DialogRepository, session)

            # First check if dialog already exists between these users
            existing_dialog = await dialog_repo.find_dialog_between_users(
                user1_id, user2_id
            )
            if existing_dialog:
                logger.info(f"Found existing dialog ID: {existing_dialog.id}")
                return existing_dialog

            try:
                dialog_data = DialogCreate(id=dialog_id, user1_id=user1_id, user2_id=user2_id)
                dialog = await dialog_repo.create(dialog_data)
                logger.info(f"Created new dialog ID: {dialog.id}")
                return dialog
            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Dialog creation failed: {str(e)}")
                raise ValueError("Failed to create dialog") from e

    async def create_message(
        self, message_id: int, dialog_id: int, sender_id: int, content: str
    ) -> Message:
        """
        Create a new message in a dialog.

        Args:
            dialog_id: ID of the dialog
            sender_id: Telegram ID of the message sender
            content: Message text content

        Returns:
            Message: Created message

        Raises:
            ValueError: If message creation fails or dialog not found
        """
        async with self._get_session() as session:
            # First check if dialog exists
            dialog_repo = self.db_manager.get_repo(DialogRepository, session)
            dialog = await dialog_repo.get(dialog_id)
            if not dialog:
                raise ValueError(f"Dialog with ID {dialog_id} not found")

            try:
                message_repo = self.db_manager.get_repo(MessageRepository, session)
                message = await message_repo.create(
                    MessageCreate(
                        id=message_id,
                        dialog_id=dialog_id,
                        sender_id=sender_id,
                        content=content,
                    )
                )

                logger.info(f"Created message ID: {message.id} in dialog {dialog_id}")
                return message
            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Message creation failed: {str(e)}")
                raise ValueError("Failed to create message") from e

    async def get_messages_for_user_in_dialog(
        self, dialog_id: int, user_id: int, *, skip: int = 0, limit: int = 100
    ) -> List[Message]:
        """
        Get all messages in a dialog for a specific user.

        Args:
            dialog_id: ID of the dialog
            user_id: Telegram ID of the user
            skip: Number of messages to skip (for pagination)
            limit: Maximum number of messages to return

        Returns:
            List[Message]: List of messages in the dialog

        Raises:
            ValueError: If dialog not found
        """
        async with self._get_session() as session:
            # Verify dialog exists first
            dialog_repo = self.db_manager.get_repo(DialogRepository, session)
            dialog = await dialog_repo.get(dialog_id)
            if not dialog:
                raise ValueError(f"Dialog with ID {dialog_id} not found")

            # Verify user is part of this dialog
            if user_id not in (dialog.user1_id, dialog.user2_id):
                raise ValueError(f"User {user_id} is not part of dialog {dialog_id}")

            message_repo = self.db_manager.get_repo(MessageRepository, session)

            # Get all messages in dialog
            messages = await message_repo.get_multi(
                skip=skip,
                limit=limit,
                filters={"dialog_id": dialog_id},
                order_by="created_at ASC",  # Oldest first
            )

            logger.info(f"Retrieved {len(messages)} messages from dialog {dialog_id}")
            return messages

    async def get_user_dialogs(self, user_id: int) -> List[Dialog]:
        """
        Get all dialogs for a specific user.

        Args:
            user_id: Telegram ID of the user

        Returns:
            List[Dialog]: List of user's dialogs
        """
        async with self._get_session() as session:
            dialog_repo = self.db_manager.get_repo(DialogRepository, session)

            dialogs = await dialog_repo.get_multi(
                filters={"or": [{"user1_id": user_id}, {"user2_id": user_id}]},
                order_by="updated_at DESC",  # Most recently updated first
            )

            logger.info(f"Retrieved {len(dialogs)} dialogs for user {user_id}")
            return dialogs