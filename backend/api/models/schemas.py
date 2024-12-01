from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime

class EEGDataPoint(BaseModel):
    """Dados EEG brutos recebidos"""
    timestamp: float = Field(..., description="Timestamp em segundos")
    channels: Dict[str, List[float]] = Field(..., description="Dados por canal")

class AttentionMetrics(BaseModel):
    """Métricas de atenção calculadas"""
    attention_score: float = Field(..., ge=0, le=1)
    eye_state: str = Field(..., pattern="^(open|closed)$")
    theta_beta_ratio: float
    engagement_index: float
    signal_quality: float = Field(..., ge=0, le=1)

class BandPowers(BaseModel):
    """Poder nas diferentes bandas de frequência"""
    delta: float = Field(..., ge=0)
    theta: float = Field(..., ge=0)
    alpha: float = Field(..., ge=0)
    beta: float = Field(..., ge=0) 
    gamma: float = Field(..., ge=0)

class ProcessedEEG(BaseModel):
    """Resultado do processamento EEG"""
    timestamp: float
    attention_metrics: AttentionMetrics
    band_powers: BandPowers
    channel_data: Dict[str, List[float]]  # Tornando obrigatório
    
    class Config:
        arbitrary_types_allowed = True  # Permite tipos personalizados como numpy.ndarray

class AnalysisRequest(BaseModel):
    """Requisição de análise histórica"""
    start_time: Optional[float] = None
    end_time: Optional[float] = None
    channels: Optional[List[str]] = None
    metrics: Optional[List[str]] = None

class AnalysisSummary(BaseModel):
    """Resumo da análise de dados"""
    mean_attention: float
    attention_variance: float
    dominant_eye_state: str
    band_power_trends: Dict[str, List[float]]
    quality_metrics: Dict[str, float]