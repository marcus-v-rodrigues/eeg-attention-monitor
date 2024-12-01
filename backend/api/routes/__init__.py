"""
Rotas da API
"""
from api.routes.eeg import router as eeg_router
from api.routes.websocket import router as websocket_router
from api.routes.session import router as session_router

__all__ = ['eeg_router', 'websocket_router', 'session_router']