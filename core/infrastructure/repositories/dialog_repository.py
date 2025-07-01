from sqlalchemy.ext.asyncio import AsyncSession

from core.internal.models import DialogCreate, DialogUpdate

from ..database.models import Dialog
from .abstract_repository import SQLAlchemyRepository

class DialogRepository(SQLAlchemyRepository[Dialog, DialogCreate, DialogUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Dialog, session=session)