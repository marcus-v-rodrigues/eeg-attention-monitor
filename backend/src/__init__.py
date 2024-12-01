"""
Sistema BCI para Detecção de Estados de Atenção

Este pacote implementa um sistema BCI (Brain-Computer Interface) para detecção 
de estados de atenção usando EEG adaptado para streaming de dados.
"""

from .attention_bci import AttentionBCI
from .data_loader import EEGDataLoader
from .feature_extractor import EEGFeatureExtractor
from .signal_processor import EEGProcessor, SignalConfig
from . import utils

__version__ = '0.2.0'
__author__ = 'Seu Nome'
__email__ = 'seu.email@dominio.com'

# Configurações padrão
DEFAULT_CONFIG = {
    'sfreq': 128.0,  # Frequência de amostragem
    'channels': [    # Canais EEG padrão
        'AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1',
        'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4'
    ],
    'buffer_size': 1000,  # Tamanho do buffer (~7.8s @ 128Hz)
    'freq_bands': {  # Bandas de frequência
        'delta': (0.5, 4),
        'theta': (4, 8),
        'alpha': (8, 13),
        'beta': (13, 30),
        'gamma': (30, 45)
    }
}