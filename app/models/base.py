from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Type, TypeVar, Union
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import TIMESTAMP, Column, Integer, String, DateTime, Boolean
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm import Session
from app.database.base import Base

#Define base model with common columns created_at and updated_at

class Base(Base):
    __abstract__ = True
    reated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc)
    )
    updated_at = Column(
        TIMESTAMP(timezone=True),
        nullable=False,
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )

    @declared_attr
    def __tablename__(cls) -> str:
        return cls.__name__.lower()