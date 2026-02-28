from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker
import os

Base = declarative_base()

def get_engine():
    database_url = os.environ.get("DATABASE_URL", "")
    return create_async_engine(database_url, echo=False)

async def get_db():
    engine = get_engine()
    async_session = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session

async def create_tables():
    from app.models.agent import Agent
    from app.models.command import Command
    from app.models.tenant import Tenant
    from app.models.audit import AuditLog
    from app.models.inventory import AgentInventory
    engine = get_engine()
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)