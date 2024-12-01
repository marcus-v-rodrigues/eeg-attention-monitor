from asyncio.log import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from .core.config import settings
from .core.application import app
from .routes import eeg_router, websocket_router, session_router
import logging

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app_: FastAPI):
    # Startup
    logger.info("Iniciando API...")
    yield
    # Shutdown
    logger.info("Finalizando API...")

# Adiciona CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Adiciona rotas
app.include_router(eeg_router, prefix=f"{settings.API_V1_STR}/eeg", tags=["eeg"])
app.include_router(websocket_router, prefix=f"{settings.API_V1_STR}/ws", tags=["websocket"])
app.include_router(session_router, prefix=f"{settings.API_V1_STR}/session", tags=["session"])

@app.get(f"{settings.API_V1_STR}/")
async def root():
    return {
        "status": "online",
        "version": settings.VERSION
    }