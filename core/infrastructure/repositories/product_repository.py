from sqlalchemy.ext.asyncio import AsyncSession

from core.internal.models import ProductCreate, ProductUpdate

from ..database.models import Product
from .abstract_repository import SQLAlchemyRepository

class ProductRepository(SQLAlchemyRepository[Product, ProductCreate, ProductUpdate]):
    def __init__(self, session: AsyncSession):
        super().__init__(model=Product, session=session)