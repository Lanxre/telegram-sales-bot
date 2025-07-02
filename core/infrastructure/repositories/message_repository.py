from sqlalchemy.ext.asyncio import AsyncSession

from core.internal.models import MessageCreate, MessageUpdate

from ..database.models import Message
from .abstract_repository import SQLAlchemyRepository


class MessageRepository(SQLAlchemyRepository[Message, MessageCreate, MessageUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Message, session=session)
