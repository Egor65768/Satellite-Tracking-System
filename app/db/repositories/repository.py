from typing import Generic, Type, TypeVar, Any, Optional, Sequence

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column

T = TypeVar("T", bound="Base")


class Repository(Generic[T]):

    def __init__(self, model: Type[T], session: AsyncSession):
        self.model = model
        self.session = session

    async def create(self, **kwargs) -> Optional[T]:
        try:
            db_object = self.model(**kwargs)
            self.session.add(db_object)
            await self.session.flush()
            await self.session.refresh(db_object)
            return db_object
        except SQLAlchemyError:
            await self.session.rollback()
            return None

    async def get_by_id(self, object_id: Any) -> Optional[T]:
        if not isinstance(self.model.id, Column):
            raise TypeError("Model id is not a SQLAlchemy Column")
        query = select(self.model).where(self.model.id == object_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_by_id(self, object_id: Any) -> bool:
        if not isinstance(self.model.id, Column):
            raise TypeError("Model id is not a SQLAlchemy Column")
        query = delete(self.model).where(self.model.id == object_id)
        result = await self.session.execute(query)
        return result.rowcount() > 0

    async def get_multi(self, limit: int = 10, offset: int = 0) -> Sequence[T]:
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()
