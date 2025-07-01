from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Optional

from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.infrastructure.database import DatabaseManager
from core.infrastructure.database.models import Product, User
from core.infrastructure.repositories import ProductRepository, UserRepository
from core.internal.models import ProductCreate, ProductUpdate, UserCreate
from logger import LoggerBuilder

logger = LoggerBuilder("Shop - Service").add_stream_handler().build()


class ShopService:
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

    # USER OPERATIONS
    async def create_user(self, user_data: UserCreate) -> User:
        """
        Create a new user or return existing user if telegram_id exists.

        Args:
            user_data: User creation data

        Returns:
            User: Created or existing user

        Raises:
            ValueError: If user creation fails
        """
        async with self._get_session() as session:
            user_repo = self.db_manager.get_repo(UserRepository, session)

            # Check for existing user first
            existing_user = await user_repo.get(user_data.telegram_id)
            if existing_user:
                logger.info(f"User already exists: {existing_user}")
                return existing_user

            try:
                user = await user_repo.create(user_data)
                logger.info(f"Created new user: {user}")
                return user
            except IntegrityError as e:
                await session.rollback()
                # Handle race condition
                existing_user = await user_repo.get(user_data.telegram_id)
                if existing_user:
                    logger.warning("Race condition handled for user creation")
                    return existing_user
                logger.error(f"User creation failed: {str(e)}")
                raise ValueError("Failed to create user") from e

    # PRODUCT OPERATIONS
    async def add_product(self, product_data: ProductCreate) -> Product:
        """
        Add a new product to catalog.

        Args:
            product_data: Product creation data

        Returns:
            Product: Created product

        Raises:
            ValueError: If product creation fails
        """
        async with self._get_session() as session:
            product_repo = self.db_manager.get_repo(ProductRepository, session)

            try:
                product = await product_repo.create(product_data)
                logger.info(f"Created product ID: {product.id}")
                return product
            except IntegrityError as e:
                await session.rollback()
                logger.error(f"Product creation failed: {str(e)}")
                raise ValueError("Failed to create product") from e

    async def delete_product(self, product_id: int) -> bool:
        """
        Delete product by ID.

        Args:
            product_id: ID of product to delete

        Returns:
            bool: True if deleted, False if not found
        """
        async with self._get_session() as session:
            product_repo = self.db_manager.get_repo(ProductRepository, session)

            try:
                success = await product_repo.delete(product_id)
                if success:
                    logger.info(f"Deleted product ID: {product_id}")
                else:
                    logger.warning(f"Product not found for deletion: {product_id}")
                return success
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Product deletion failed: {str(e)}")
                raise

    async def update_product(
        self, product_id: int, product_data: ProductUpdate
    ) -> Optional[Product]:
        """
        Update product details.

        Args:
            product_id: ID of product to update
            product_data: New product data

        Returns:
            Optional[Product]: Updated product or None if not found
        """
        async with self._get_session() as session:
            product_repo = self.db_manager.get_repo(ProductRepository, session)

            try:
                product = await product_repo.update(product_id, product_data)
                if product:
                    logger.info(f"Updated product ID: {product.id}")
                else:
                    logger.warning(f"Product not found for update: {product_id}")
                return product
            except SQLAlchemyError as e:
                await session.rollback()
                logger.error(f"Product update failed: {str(e)}")
                raise

    async def get_all_products(
        self, *, skip: int = 0, limit: int = 100, filters: Optional[dict] = None
    ) -> List[Product]:
        """
        Get paginated list of products with optional filtering.

        Args:
            skip: Number of items to skip
            limit: Maximum number of items to return
            filters: Optional filter criteria

        Returns:
            List[Product]: List of products
        """
        async with self._get_session() as session:
            product_repo = self.db_manager.get_repo(ProductRepository, session)

            products = await product_repo.get_multi(
                skip=skip, limit=limit, filters=filters
            )

            logger.info(f"Retrieved {len(products)} products")
            return products

    async def get_product(self, product_id: int) -> Optional[Product]:
        """
        Get single product by ID.

        Args:
            product_id: ID of product to retrieve

        Returns:
            Optional[Product]: Product if found, None otherwise
        """
        async with self._get_session() as session:
            product_repo = self.db_manager.get_repo(ProductRepository, session)

            product = await product_repo.get(product_id)
            if product:
                logger.debug(f"Retrieved product ID: {product_id}")
            else:
                logger.debug(f"Product not found: {product_id}")
            return product
