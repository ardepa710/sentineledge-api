from fastapi import FastAPI, Request
from contextlib import asynccontextmanager
from app.database import engine, Base
from app.models import Agent, Tenant, Command
from app.routers.agents import router as agents_router
from app.routers.commands import router as commands_router
from fastapi.responses import JSONResponse
import traceback



@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    await engine.dispose()

app = FastAPI(
    title="SentinelEdge API",
    description="API para gestión de agentes MSP",
    version="0.1.0",
    lifespan=lifespan
)


app.include_router(agents_router)
app.include_router(commands_router)


# después de crear el app, agrega:
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    error_detail = traceback.format_exc()
    print(f"ERROR COMPLETO:\n{error_detail}")
    return JSONResponse(
        status_code=500,
        content={"detail": str(exc), "traceback": error_detail}
    )

@app.get("/")
async def root():
    return {"status": "ok", "message": "SentinelEdge API funcionando"}

@app.get("/health")
async def health():
    return {"status": "healthy"}