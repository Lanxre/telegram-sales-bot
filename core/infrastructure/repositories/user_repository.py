from typing import Any, Optional

from sqlalchemy import select
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from core.internal.models import UserCreate, UserUpdate

from ..database.models import User
from .abstract_repository import ModelType, SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=User)

    async def get(self, session: AsyncSession, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.telegram_id == id)
        result = await session.execute(query)
        try:
            return result.scalar_one()
        except NoResultFound:
            return None
