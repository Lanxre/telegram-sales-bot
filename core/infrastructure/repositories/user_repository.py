from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from core.internal.models import UserCreate, UserUpdate

from ..database.models import User
from .abstract_repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=User, session=session)

    async def get(self, id: Any) -> Optional[User]:
        query = select(self.model).where(self.model.telegram_id == id)
        result = await self.session.execute(query)
        try:
            return result.scalar_one()
        except NoResultFound:
            return None
