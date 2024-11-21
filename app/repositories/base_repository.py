from typing import TypeVar, Generic, Dict, Any, Optional, List
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, asc, desc, func
from sqlalchemy.exc import SQLAlchemyError
from fastapi import HTTPException
from app.models.base import Base

T = TypeVar("T", bound=Base)

class BaseRepository(Generic[T]):
    def __init__(self, db: AsyncSession):
        self.db = db
        self.model = self.__orig_bases__[0].__args__[0]

    async def _build_query(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        order: str = "asc",
        skip: int = 0,
        limit: Optional[int] = None
    ):
        stmt = select(self.model)

        if filters:
            for key, value in filters.items():
                if hasattr(self.model, key):
                    column = getattr(self.model, key)
                    if isinstance(value, list):
                        stmt = stmt.where(column.in_(value))
                    else:
                        stmt = stmt.where(column == value)

        if sort_by and hasattr(self.model, sort_by):
            sort_column = getattr(self.model, sort_by)
            stmt = stmt.order_by(desc(sort_column) if order == "desc" else asc(sort_column))

        if skip:
            stmt = stmt.offset(skip)
        if limit:
            stmt = stmt.limit(limit)

        return stmt

    async def create(self, obj_in: Dict[str, Any]) -> T:
        try:
            db_obj = self.model(**obj_in)
            self.db.add(db_obj)
            await self.db.flush()
            await self.db.commit()
            await self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def get(self, id: Any) -> Optional[T]:
        stmt = select(self.model).where(self.model.id == id)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_by_field(self, field: str, value: Any) -> Optional[T]:
        if not hasattr(self.model, field):
            return None
        column = getattr(self.model, field)
        stmt = select(self.model).where(column == value)
        result = await self.db.execute(stmt)
        return result.scalars().first()

    async def get_all(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        order: str = "asc",
        skip: int = 0,
        limit: Optional[int] = None
    ) -> List[T]:
        stmt = await self._build_query(filters, sort_by, order, skip, limit)
        result = await self.db.execute(stmt)
        return result.scalars().all()

    async def update(self, db_obj: T, obj_in: Dict[str, Any]) -> T:
        for key, value in obj_in.items():
            if hasattr(db_obj, key):
                setattr(db_obj, key, value)
        self.db.add(db_obj)
        try:
            await self.db.commit()
            await self.db.refresh(db_obj)
            return db_obj
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    async def delete(self, db_obj: T) -> None:
        try:
            await self.db.delete(db_obj)
            await self.db.commit()
        except SQLAlchemyError as e:
            await self.db.rollback()
            raise HTTPException(status_code=400, detail=str(e))