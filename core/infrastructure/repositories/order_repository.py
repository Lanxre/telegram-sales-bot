from typing import Optional, List
from sqlalchemy import select
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession

from core.internal.models import OrderCreate, OrderUpdate

from ..database.models import Order
from .abstract_repository import SQLAlchemyRepository


class OrderRepository(SQLAlchemyRepository[Order, OrderCreate, OrderUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Order, session=session)

    async def get_with_products(self, order_id: int) -> Optional[Order]:
        query = (
            select(Order)
            .where(Order.id == order_id)
            .options(selectinload(Order.products), selectinload(Order.user))
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_by_user(self, user_id: int) -> List[Order]:
        query = (
            select(Order)
            .where(Order.user_id == user_id)
            .options(selectinload(Order.products))
            .order_by(Order.created_at.desc())
        )

        result = await self.session.execute(query)
        return result.scalars().all()
