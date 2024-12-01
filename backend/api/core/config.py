from pydantic_settings import BaseSettings
from pydantic import ConfigDict
from typing import List
import os

class Settings(BaseSettings):
    """Configurações da API"""
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "EEG Analysis API"
    VERSION: str = "0.1.0"
    # Configurações CORS
    BACKEND_CORS_ORIGINS: List[str] = ["http://localhost", "http://localhost:3000"]
    
    # Configurações EEG
    SAMPLING_RATE: float = 128.0
    BUFFER_SIZE: int = 1000  # ~7.8 segundos @ 128Hz
    DEFAULT_CHANNELS: List[str] = [
        'AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1',
        'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4'
    ]
    
    # Configurações processamento
    PROCESS_BATCH_SIZE: int = 128  # 1 segundo de dados
    MIN_SIGNAL_QUALITY: float = 0.5
    
    model_config = ConfigDict(
        case_sensitive=True,
        env_file='.env',
        env_file_encoding='utf-8',
        extra='ignore'
    )

settings = Settings()