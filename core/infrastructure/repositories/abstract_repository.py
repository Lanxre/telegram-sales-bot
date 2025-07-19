from abc import ABC, abstractmethod
from typing import Any, Dict, Generic, List, Optional, TypeVar

from pydantic import BaseModel as PydanticBaseModel
from sqlalchemy import Select, delete, select, text, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

from core.infrastructure.database.models import BaseModel

ModelType = TypeVar("ModelType", bound=BaseModel)
CreateSchemaType = TypeVar("CreateSchemaType", bound=PydanticBaseModel)
UpdateSchemaType = TypeVar("UpdateSchemaType", bound=PydanticBaseModel)


class AbstractRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    @abstractmethod
    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        raise NotImplementedError

    @abstractmethod
    async def get(self, id: Any) -> Optional[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def get_multi(self, skip: int = 0, limit: int = 100) -> List[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def update(self, id: Any, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        raise NotImplementedError

    @abstractmethod
    async def delete(self, id: Any) -> bool:
        raise NotImplementedError


class SQLAlchemyRepository(
    AbstractRepository[ModelType, CreateSchemaType, UpdateSchemaType]
):
    def __init__(self, model: type[ModelType], session: AsyncSession):
        self._model = model
        self._session = session

    @property
    def model(self) -> type[ModelType]:
        return self._model

    @property
    def session(self) -> AsyncSession:
        return self._session

    def _apply_filters(self, query: Select, filters: Dict[str, Any]) -> Select:
        for field, value in filters.items():
            query = query.where(getattr(self.model, field) == value)
        return query

    async def create(self, obj_in: CreateSchemaType) -> ModelType:
        db_obj = self.model(**obj_in.model_dump(exclude_unset=True))
        self.session.add(db_obj)
        await self.session.flush()
        await self.session.refresh(db_obj)
        return db_obj

    async def get(self, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        try:
            return result.scalar_one()
        except NoResultFound:
            return None

    async def get_multi(
        self,
        *,
        skip: int = 0,
        limit: int = 100,
        filters: Optional[Dict[str, Any]] = None,
        order_by: Optional[str] = None,
    ) -> List[ModelType]:
        query = select(self.model)

        if filters:
            query = self._apply_filters(query, filters)

        if order_by:
            query = query.order_by(text(order_by))

        query = query.offset(skip).limit(limit)

        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, id: Any, obj_in: UpdateSchemaType) -> Optional[ModelType]:
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(**obj_in.model_dump(exclude_unset=True))
            .returning(self.model)
        )

        result = await self.session.execute(query)
        await self.session.commit()

        try:
            return result.scalar_one()
        except NoResultFound:
            return None

    async def delete(self, id: Any) -> bool:
        query = delete(self.model).where(self.model.id == id)
        result = await self.session.execute(query)
        await self.session.commit()
        return result.rowcount > 0
