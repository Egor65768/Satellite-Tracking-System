from typing import Generic, Type, TypeVar, Any, Optional, Sequence, cast

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, update

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
        id_column = cast(Column, self.model.id)
        query = select(self.model).where(id_column == object_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def delete_by_id(self, object_id: Any) -> bool:
        id_column = cast(Column, self.model.id)
        query = delete(self.model).where(id_column == object_id)
        result = await self.session.execute(query)
        number_lines_removed: int = result.rowcount  # type: ignore[attr-defined]
        return number_lines_removed > 0

    async def get_multi(self, limit: int = 10, offset: int = 0) -> Sequence[T]:
        query = select(self.model).offset(offset).limit(limit)
        result = await self.session.execute(query)
        return result.scalars().all()

    async def update(self, object_id: Any, **kwargs) -> Optional[T]:
        try:
            id_column = cast(Column, self.model.id)
            query = update(self.model).where(id_column == object_id).values(**kwargs)
            await self.session.execute(query)
            return await self.get_by_id(object_id)
        except SQLAlchemyError:
            if self.session.in_transaction():
                await self.session.rollback()
            return None
