from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.core.vault import load_secrets_from_vault
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Cargar secretos de Vaultwarden PRIMERO
    await load_secrets_from_vault()

    # 2. Ahora que DATABASE_URL está en os.environ, crear tablas
    from app.database import create_tables
    await create_tables()

    logger.info("Application startup complete")
    yield

app = FastAPI(
    title="SentinelEdge API",
    version="0.1.0",
    lifespan=lifespan
)

from app.routers.agents   import router as agents_router
from app.routers.commands import router as commands_router
from app.routers.audit    import router as audit_router
from app.routers.inventory import router as inventory_router
app.include_router(inventory_router)

app.include_router(agents_router)
app.include_router(commands_router)
app.include_router(audit_router)

@app.get("/health")
async def health():
    return {"status": "healthy"}