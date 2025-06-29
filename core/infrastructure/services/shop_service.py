from typing import List, Optional
from sqlalchemy.exc import IntegrityError

from core.infrastructure.database import DatabaseManager
from core.infrastructure.database.models import User, Product
from core.infrastructure.repositories import UserRepository, ProductRepository
from core.internal.models import UserCreate, ProductCreate, ProductUpdate

from logger import LoggerBuilder

logger = LoggerBuilder("Shop - Service").add_stream_handler().build()

class ShopService:
    def __init__(self, db_manager: DatabaseManager):
        self.db_manager = db_manager

    # USER
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
    
    # PRODUCT
    async def add_product(self, product_data: ProductCreate) -> Product:
        """Add a product to the catalog."""
        async with self.db_manager.session_pool() as session:
            product_repo: ProductRepository = self.db_manager.get_repo(ProductRepository, session)
            product = await product_repo.create(session, product_data)
            await session.commit()
            logger.info(f"Product was create: {product.id}")
            return product

    async def delete_product(self, prodcut_id: int) -> bool:
        async with self.db_manager.session_pool() as session:
            product_repo: ProductRepository = self.db_manager.get_repo(ProductRepository, session)
            is_delete = await product_repo.delete(session, prodcut_id)
            await session.commit()
            logger.info(f"Product was delete: {is_delete}")
            return is_delete

    async def update_product(self, product_id: int,  product_data: ProductUpdate) -> Optional[Product]:
        """Update product details."""
        async with self.db_manager.session_pool() as session:
            product_repo: ProductRepository = self.db_manager.get_repo(ProductRepository, session)
            product = await product_repo.update(session, product_id, product_data)
            await session.commit()
            logger.info(f"Product was update: {product.id}")
            return product
    

    async def get_all_products(self) -> List[Product]:
        """Update product details."""
        async with self.db_manager.session_pool() as session:
            product_repo: ProductRepository = self.db_manager.get_repo(ProductRepository, session)
            products = await product_repo.get_multi(session)
            logger.info(f"Responce all products: {len(products)}")
            return products

    # ORDER