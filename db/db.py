from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from core.config import settings

db_url = f"postgresql+asyncpg://{settings.db.username}:{settings.db.password}@{settings.db.host}:{settings.db.port}/{settings.db.name}"

engine = create_async_engine(db_url, echo=True)

new_session = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_session() -> AsyncSession:
    async with new_session() as session:
        yield session