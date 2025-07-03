from typing import Optional

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from core.internal.models import (
    ShopCardCreate,
    ShopCardItemCreate,
    ShopCardItemUpdate,
    ShopCardUpdate,
)

from ..database.models import ShopCard, ShopCardItem
from .abstract_repository import SQLAlchemyRepository


class ShopCardRepository(
    SQLAlchemyRepository[ShopCard, ShopCardCreate, ShopCardUpdate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(model=ShopCard, session=session)

    async def get_active_card(self, user_id: int) -> Optional[ShopCard]:
        query = (
            select(ShopCard)
            .where((ShopCard.user_id == user_id))
            .order_by(ShopCard.created_at.desc())
            .limit(1)
        )

        result = await self.session.execute(query)
        return result.scalars().first()

    async def get_active_card_with_items(self, user_id: int) -> Optional[ShopCard]:
        query = (
            select(ShopCard)
            .where((ShopCard.user_id == user_id))
            .options(selectinload(ShopCard.items).selectinload(ShopCardItem.product))
            .order_by(ShopCard.created_at.desc())
            .limit(1)
        )

        result = await self.session.execute(query)
        return result.scalars().first()


class ShopCardItemRepository(
    SQLAlchemyRepository[ShopCardItem, ShopCardItemCreate, ShopCardItemUpdate]
):
    def __init__(self, session: AsyncSession):
        super().__init__(model=ShopCardItem, session=session)

    async def get_by_product(
        self, card_id: int, product_id: int
    ) -> Optional[ShopCardItem]:
        query = select(ShopCardItem).where(
            (ShopCardItem.shop_card_id == card_id)
            & (ShopCardItem.product_id == product_id)
        )

        result = await self.session.execute(query)
        return result.scalars().first()
