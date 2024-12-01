"""
API FastAPI para Sistema BCI

Este módulo fornece endpoints REST e WebSocket para interação
com o sistema BCI de detecção de estados de atenção.
"""

from fastapi import FastAPI
from .core.config import settings
from .core.state import GlobalState
from .models.schemas import (
    EEGDataPoint,
    BandPowers,
    AttentionMetrics,
    ProcessedEEG,
    AnalysisRequest,
    AnalysisSummary
)

__version__ = '0.1.0'

def create_app() -> FastAPI:
    """
    Cria e configura a aplicação FastAPI
    
    Returns:
        FastAPI: Aplicação configurada
    """
    app = FastAPI(
        title=settings.PROJECT_NAME,
        description="API para Sistema BCI de Detecção de Atenção",
        version=__version__,
        openapi_url=f"{settings.API_V1_STR}/openapi.json"
    )
    
    return app

__all__ = [
    'create_app',
    'settings',
    'GlobalState',
    'EEGDataPoint',
    'BandPowers',
    'AttentionMetrics',
    'ProcessedEEG',
    'AnalysisRequest',
    'AnalysisSummary'
]