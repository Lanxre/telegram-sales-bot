from abc import ABC, abstractmethod
from typing import Any, Generic, List, Optional, TypeVar

from sqlalchemy import delete, select, update
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession

ModelType = TypeVar("ModelType")
CreateSchemaType = TypeVar("CreateSchemaType")
UpdateSchemaType = TypeVar("UpdateSchemaType")


class AbstractRepository(ABC, Generic[ModelType, CreateSchemaType, UpdateSchemaType]):
    @abstractmethod
    async def create(
        self, session: AsyncSession, obj_in: CreateSchemaType
    ) -> ModelType:
        pass

    @abstractmethod
    async def get(self, session: AsyncSession, id: Any) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def get_multi(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        pass

    @abstractmethod
    async def update(
        self, session: AsyncSession, id: Any, obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        pass

    @abstractmethod
    async def delete(self, session: AsyncSession, id: Any) -> bool:
        pass


class SQLAlchemyRepository(
    AbstractRepository[ModelType, CreateSchemaType, UpdateSchemaType]
):
    def __init__(self, model: type[ModelType]):
        self.model = model

    async def create(
        self, session: AsyncSession, obj_in: CreateSchemaType
    ) -> ModelType:
        db_obj = self.model(**obj_in.model_dump(exclude_unset=True))
        session.add(db_obj)
        await session.flush()
        await session.refresh(db_obj)
        return db_obj

    async def get(self, session: AsyncSession, id: Any) -> Optional[ModelType]:
        query = select(self.model).where(self.model.id == id)
        result = await session.execute(query)
        try:
            return result.scalar_one()
        except NoResultFound:
            return None

    async def get_multi(
        self, session: AsyncSession, skip: int = 0, limit: int = 100
    ) -> List[ModelType]:
        query = select(self.model).offset(skip).limit(limit)
        result = await session.execute(query)
        return result.scalars().all()

    async def update(
        self, session: AsyncSession, id: Any, obj_in: UpdateSchemaType
    ) -> Optional[ModelType]:
        query = (
            update(self.model)
            .where(self.model.id == id)
            .values(obj_in.model_dump(exclude_unset=True))
        )
        result = await session.execute(query)
        if result.rowcount == 0:
            return None
        await session.commit()
        return await self.get(session, id)

    async def delete(self, session: AsyncSession, id: Any) -> bool:
        query = delete(self.model).where(self.model.id == id)
        result = await session.execute(query)
        await session.commit()
        return result.rowcount > 0