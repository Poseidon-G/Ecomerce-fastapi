# app/database/connection.py
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from app.core.config import settings
from sqlalchemy.ext.declarative import declarative_base
from app.models import *

# Create async engine with explicit asyncpg driver
engine = create_async_engine(
    settings.DATABASE_URL.replace('postgresql://', 'postgresql+asyncpg://'),
    echo=settings.DEBUG,
    future=True
)

Base = declarative_base()

# Create async session factory
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()