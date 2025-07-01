from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.internal.models import DialogCreate, DialogUpdate

from ..database.models import Dialog
from .abstract_repository import SQLAlchemyRepository

class DialogRepository(SQLAlchemyRepository[Dialog, DialogCreate, DialogUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Dialog, session=session)
    
    async def find_dialog_between_users(self, user1_id: int, user2_id: int) -> Optional[Dialog]:
        """Find dialog between two users (in any order)."""
        query = select(self.model).where(
            (
                (self.model.user1_id == user1_id) & 
                (self.model.user2_id == user2_id)
            ) | (
                (self.model.user1_id == user2_id) & 
                (self.model.user2_id == user1_id)
            )
        )
        result = await self.session.execute(query)
        return result.scalars().first()