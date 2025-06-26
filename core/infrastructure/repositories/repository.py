from sqlalchemy.ext.asyncio import AsyncSession

from ..database.models import User
from core.internal.models import UserCreate, UserUpdate
from .abstract_repository import SQLAlchemyRepository


class UserRepository(SQLAlchemyRepository[User, UserCreate, UserUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=User)
