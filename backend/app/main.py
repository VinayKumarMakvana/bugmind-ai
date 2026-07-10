from contextlib import asynccontextmanager
import asyncio

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .core.config import settings
from .core.events import event_manager

from .api.v1 import (
    auth,
    webhooks,
    repos,
    chat,
    stream,
    analyze,
    execute,
)


# =========================================================
# APPLICATION LIFECYCLE
# =========================================================

@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Application startup & shutdown.
    """

    event_manager.set_loop(
        asyncio.get_running_loop()
    )

    yield

    # Future cleanup
    # await close_database()
    # await close_chromadb()


# =========================================================
# FASTAPI
# =========================================================

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)


# =========================================================
# ROUTES
# =========================================================

API = settings.API_V1_STR

app.include_router(
    auth.router,
    prefix=f"{API}/auth",
    tags=["Authentication"],
)

app.include_router(
    webhooks.router,
    prefix=f"{API}/webhooks",
    tags=["Webhooks"],
)

app.include_router(
    repos.router,
    prefix=f"{API}/repos",
    tags=["Repositories"],
)

app.include_router(
    chat.router,
    prefix=f"{API}/chat",
    tags=["AI Chat"],
)

app.include_router(
    stream.router,
    prefix=f"{API}/stream",
    tags=["Streaming"],
)

app.include_router(
    analyze.router,
    prefix=f"{API}/analyze",
    tags=["Analysis"],
)

app.include_router(
    execute.router,
    prefix=f"{API}/execute",
    tags=["Execution"],
)


# =========================================================
# ROOT
# =========================================================

@app.get("/", tags=["Root"])
async def root():
    return {
        "project": settings.PROJECT_NAME,
        "status": "running",
        "version": "1.0.0",
        "message": "Welcome to BugMind AI API",
    }


# =========================================================
# HEALTH CHECK
# =========================================================

@app.get("/health", tags=["Health"])
async def health():

    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
    }