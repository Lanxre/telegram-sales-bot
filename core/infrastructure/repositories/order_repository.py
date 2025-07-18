from typing import Any, Dict, List, Optional

from sqlalchemy import select, text, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.internal.enums import OrderStatus
from core.internal.models import OrderCreate, OrderUpdate

from ..database.models import Order
from .abstract_repository import SQLAlchemyRepository


class OrderRepository(SQLAlchemyRepository[Order, OrderCreate, OrderUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Order, session=session)

    async def get_all_orders_with_products(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[Order]:
        query = select(Order)

        if filters:
            query = self._apply_filters(query, filters)

        if order_by:
            query = query.order_by(text(order_by))

        query = (
            query.offset(skip)
            .limit(limit)
            .options(selectinload(Order.products), selectinload(Order.user))
        )

        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_with_products(self, order_id: int) -> Optional[Order]:
        query = (
            select(Order)
            .where(Order.id == order_id)
            .options(
                selectinload(Order.products),
                selectinload(Order.user),
                selectinload(Order.order_products),
            )
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

    async def update_status(self, id: int, order_status: OrderStatus) -> Optional[Order]:
        query = (
            update(Order)
            .where(Order.id == id)
            .values(status=order_status)
            .returning(Order)
        )

        result = await self.session.execute(query)
        await self.session.commit()
        return result.scalar_one()
        
