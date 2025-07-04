from contextlib import asynccontextmanager
from typing import AsyncIterator, List, Optional

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from core.infrastructure.database import DatabaseManager
from core.infrastructure.database.models import Order
from core.infrastructure.repositories import OrderRepository, ProductRepository
from core.internal.enums import OrderStatus
from core.internal.models import OrderCreate, OrderUpdate
from logger import LoggerBuilder

logger = LoggerBuilder("OrderService - Service").add_stream_handler().build()


class OrderService:
    def __init__(self, db_manager: DatabaseManager):
        self._db_manager = db_manager

    @property
    def db_manager(self) -> DatabaseManager:
        return self._db_manager

    @asynccontextmanager
    async def _get_session(self) -> AsyncIterator[AsyncSession]:
        async with self.db_manager.get_db_session() as session:
            try:
                yield session
            except SQLAlchemyError:
                raise
            except Exception:
                raise

    async def create_order(self, order_data: OrderCreate) -> Order:
        async with self._get_session() as session:
            product_repo = self.db_manager.get_repo(ProductRepository, session)
            products = [await product_repo.get(p.id) for p in order_data.products]
            order = Order(
                user_id=order_data.user_id,
                total_price=order_data.total_price,
                total_count=order_data.total_count,
                delivery_address=order_data.delivery_address,
                order_note=order_data.order_note,
                status=order_data.status,
                products=products
            )

            session.add(order)
            await session.commit()
            return order

    async def get_order(self, order_id: int) -> Optional[Order]:
        async with self._get_session() as session:
            repo = self.db_manager.get_repo(OrderRepository, session)
            return await repo.get_with_products(order_id)

    async def get_user_orders(self, user_id: int) -> List[Order]:
        async with self._get_session() as session:
            repo = self.db_manager.get_repo(OrderRepository, session)
            return await repo.get_by_user(user_id)

    async def cancel_order(self, order_id: int) -> bool:
        await self.update_order(order_id, OrderUpdate(status=OrderStatus.PENDING))

    async def update_order(
        self, order_id: int, update_data: OrderUpdate
    ) -> Optional[Order]:
        async with self._get_session() as session:
            repo = self.db_manager.get_repo(OrderRepository, session)
            return await repo.update(order_id, update_data)
