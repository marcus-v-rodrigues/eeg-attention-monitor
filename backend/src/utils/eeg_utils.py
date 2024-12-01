# src/utils/eeg_utils.py
"""
Funções utilitárias para processamento de EEG
"""
import numpy as np
from scipy import signal
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

async def validate_eeg_data(data: np.ndarray, sfreq: float, channel_names: List[str]) -> bool:
    """Versão assíncrona da validação de dados"""
    try:
        if data.ndim != 2:
            raise ValueError(f"Dados devem ter 2 dimensões, tem {data.ndim}")
            
        if data.shape[0] != len(channel_names):
            raise ValueError(
                f"Número de canais ({data.shape[0]}) não corresponde aos nomes ({len(channel_names)})"
            )
            
        if np.any(np.abs(data) > 500):
            logger.warning("Detectadas amplitudes anormalmente altas (>500 µV)")
            
        if not 100 <= sfreq <= 1000:
            raise ValueError(f"Frequência de amostragem inválida: {sfreq} Hz")
            
        return True
        
    except Exception as e:
        logger.error(f"Erro na validação: {str(e)}")
        return False

async def compute_band_power(data: np.ndarray, sfreq: float) -> Dict[str, np.ndarray]:
    """Versão assíncrona do cálculo de poder nas bandas"""
    try:
        # Ajusta nperseg para o tamanho do sinal
        nperseg = min(256, data.shape[1])
        freqs, psd = signal.welch(data, fs=sfreq, nperseg=nperseg)
        
        bands = {
            'delta': (0.5, 4),
            'theta': (4, 8),
            'alpha': (8, 13),
            'beta': (13, 30),
            'gamma': (30, 45)
        }
        
        powers = {}
        for band_name, (low, high) in bands.items():
            mask = (freqs >= low) & (freqs <= high)
            powers[band_name] = np.mean(psd[:, mask], axis=1)
        
        return powers
        
    except Exception as e:
        logger.error(f"Erro no cálculo de poder: {str(e)}")
        raise

async def compute_coherence(data: np.ndarray, sfreq: float) -> np.ndarray:
    """Versão assíncrona do cálculo de coerência"""
    try:
        n_channels = data.shape[0]
        coherence = np.zeros((n_channels, n_channels))
        
        for i in range(n_channels):
            for j in range(i+1, n_channels):
                f, Cxy = signal.coherence(data[i], data[j], fs=sfreq)
                mask = (f >= 8) & (f <= 13)
                coh = np.mean(Cxy[mask])
                coherence[i,j] = coh
                coherence[j,i] = coh
        
        return coherence
        
    except Exception as e:
        logger.error(f"Erro no cálculo de coerência: {str(e)}")
        raise