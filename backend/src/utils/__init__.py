"""
Utilitários para processamento e análise de EEG
"""

from .eeg_utils import (
    validate_eeg_data,
    compute_band_power,
    compute_coherence
)

from .visualization import (
    prepare_eeg_visualization,
    prepare_band_powers_visualization,
    prepare_attention_metrics_visualization
)

__all__ = [
    'validate_eeg_data',
    'compute_band_power',
    'compute_coherence',
    'prepare_eeg_visualization',
    'prepare_band_powers_visualization',
    'prepare_attention_metrics_visualization'
]