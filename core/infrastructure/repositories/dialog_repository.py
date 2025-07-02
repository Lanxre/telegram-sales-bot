from typing import List, Optional

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from core.internal.models import DialogCreate, DialogUpdate

from ..database.models import Dialog
from .abstract_repository import SQLAlchemyRepository


class DialogRepository(SQLAlchemyRepository[Dialog, DialogCreate, DialogUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Dialog, session=session)

    async def find_dialog_between_users(
        self, user1_id: int, user2_id: int
    ) -> Optional[Dialog]:
        """Find dialog between two users (in any order)."""
        query = select(self.model).where(
            ((self.model.user1_id == user1_id) & (self.model.user2_id == user2_id))
            | ((self.model.user1_id == user2_id) & (self.model.user2_id == user1_id))
        )
        result = await self.session.execute(query)
        return result.scalars().first()

    async def count_unread_dialogs(self, admin_id: int) -> int:
        query = select(func.count(Dialog.id)).where(
            (Dialog.user2_id == admin_id) & (Dialog.is_read == 0)
        )
        result = await self.session.execute(query)
        return result.scalar() or 0

    async def get_unread_dialogs(self, admin_id: int, limit: Optional[int] = 10, offset: Optional[int] = 0) -> List[Dialog]:
        query = (
            select(Dialog)
            .where(
                (Dialog.user2_id == admin_id) & (Dialog.is_read == 0)
            )
            .order_by(Dialog.updated_at.desc())
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)
        return result.scalars().all()
