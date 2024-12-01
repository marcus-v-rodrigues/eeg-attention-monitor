"""
Utilitários para preparação de dados para visualização
"""
from typing import Dict, List, Any
import numpy as np

def prepare_eeg_visualization(data: np.ndarray, sfreq: float = 128.0) -> Dict[str, Any]:
    """
    Prepara dados EEG para visualização no frontend
    
    Args:
        data: Array com dados EEG (channels x samples)
        sfreq: Frequência de amostragem
        
    Returns:
        Dicionário com dados formatados para visualização
    """
    return {
        'data': data.tolist(),
        'timepoints': (np.arange(data.shape[1]) / sfreq).tolist(),
        'sampling_rate': sfreq
    }

def prepare_band_powers_visualization(powers: Dict[str, float]) -> Dict[str, Any]:
    """
    Prepara dados de poder das bandas para visualização
    
    Args:
        powers: Dicionário com poder em cada banda
        
    Returns:
        Dicionário formatado para visualização
    """
    return {
        'labels': list(powers.keys()),
        'values': list(powers.values()),
        'colors': {
            'delta': '#1f77b4',
            'theta': '#ff7f0e',
            'alpha': '#2ca02c',
            'beta': '#d62728',
            'gamma': '#9467bd'
        }
    }

def prepare_attention_metrics_visualization(metrics: Dict[str, float]) -> Dict[str, Any]:
    """
    Prepara métricas de atenção para visualização
    
    Args:
        metrics: Dicionário com métricas
        
    Returns:
        Dicionário formatado para visualização
    """
    return {
        'attention_score': metrics.get('attention_score', 0),
        'eye_state': metrics.get('eye_state', 'unknown'),
        'engagement_index': metrics.get('engagement_index', 0),
        'signal_quality': metrics.get('signal_quality', 0)
    }