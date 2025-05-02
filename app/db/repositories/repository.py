from typing import Generic, Type, TypeVar, Any, Optional, Sequence, cast, List
from pydantic import BaseModel

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, delete, Column, update

from app.schemas import Object_ID, PaginationBase

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


class BaseRepository(Repository[T]):

    def __init__(self, model: Type[T], session: AsyncSession):
        super().__init__(model, session)
        self.in_db_type: Optional[Type[BaseModel]] = None

    async def create_entity(self, entity_create: BaseModel) -> Optional[BaseModel]:
        """Создание сущности"""
        entity_db = await self.create(**entity_create.model_dump())
        return await self._convert_to_model(entity_db)

    async def get_as_model(self, object_id: Object_ID) -> Optional[BaseModel]:
        """Получение сущности с автоматическим преобразованием в выходную модель"""
        db_obj = await self.get_by_id(object_id.id)
        return await self._convert_to_model(db_obj)

    async def get_models(self, pagination: PaginationBase) -> List[BaseModel]:
        """Получение сущностей с автоматическим преобразованием в список выходных моделей"""
        db_objects = await self.get_multi(**pagination.model_dump())
        return await self._convert_to_list_model(db_objects)

    async def delete_model(self, object_id: Object_ID) -> bool:
        return await self.delete_by_id(object_id.id)

    async def update_model(
        self, object_id: Object_ID, object_update: BaseModel
    ) -> Optional[BaseModel]:
        object_db = await self.update(
            object_id=object_id.id, **object_update.model_dump(exclude_unset=True)
        )
        return await self._convert_to_model(object_db)

    async def _convert_to_model(self, db_obj: Optional[T]) -> Optional[BaseModel]:
        """Внутренний метод преобразования в выходную модель"""
        if db_obj is None or self.in_db_type is None:
            return None
        return self.in_db_type(**db_obj.__dict__)

    async def _convert_to_list_model(self, db_objects: Sequence[T]) -> List[BaseModel]:
        """Внутренний метод преобразования в список выходных моделей"""
        if db_objects is None or self.in_db_type is None:
            return list()
        return [await self._convert_to_model(db_obj) for db_obj in db_objects]

    async def get_by_field(
        self,
        field_name: str,
        field_value: Any,
        model_type: Optional[Type[BaseModel]] = None,
    ) -> Optional[BaseModel]:
        """
        Общий метод поиска по любому полю модели
        :param field_name: Название поля для поиска
        :param field_value: Значение для поиска
        :param model_type: Тип Pydantic модели для преобразования результата
        :return: Объект Pydantic модели или None
        """
        if not hasattr(self.model, field_name):
            raise ValueError(f"Model {self.model.__name__} has no field {field_name}")
        model_type = self.in_db_type if model_type is None else model_type
        if model_type is None:
            raise ValueError("No model_type provided and in_db_type not set")
        field = getattr(self.model, field_name)
        condition = (
            field.is_(field_value) if field_value is None else field == field_value
        )

        query = select(self.model).where(condition)
        result = await self.session.execute(query)
        db_obj = result.scalar_one_or_none()

        return model_type(**db_obj.__dict__)
