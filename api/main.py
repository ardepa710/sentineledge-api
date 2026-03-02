from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from app.core.vault import load_secrets_from_vault
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await load_secrets_from_vault()
    from app.database import create_tables
    await create_tables()
    logger.info("Application startup complete")
    yield

app = FastAPI(
    title="SentinelEdge API",
    version="0.1.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "https://*.vercel.app"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

from app.routers.agents    import router as agents_router
from app.routers.commands  import router as commands_router
from app.routers.audit     import router as audit_router
from app.routers.inventory import router as inventory_router

app.include_router(inventory_router)
app.include_router(agents_router)
app.include_router(commands_router)
app.include_router(audit_router)

@app.get("/health")
async def health():
    return {"status": "healthy"}