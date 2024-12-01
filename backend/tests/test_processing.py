from typing import Dict, List
import logging
import pytest
import numpy as np
from src.attention_bci import AttentionBCI
from src.signal_processor import EEGProcessor, SignalConfig

@pytest.mark.asyncio
async def test_eeg_processor(processor, sample_eeg_data):
    """Testa processador EEG"""
    # Converte dados para formato numpy
    data = np.array([sample_eeg_data["channels"][ch] for ch in processor.config.channels])
    
    # Testa processamento
    processed = await processor.process_async(data)
    assert processed.shape == data.shape
    
    # Testa checagem de qualidade
    quality = await processor.check_quality_async(processed)
    assert isinstance(quality, dict)
    assert "amplitude_ok" in quality
    assert "variance_ok" in quality
    assert "line_noise_ok" in quality

@pytest.mark.asyncio
async def test_band_power_calculation(processor, sample_eeg_data):
    """Testa cálculo de poder das bandas"""
    data = np.array([sample_eeg_data["channels"][ch] for ch in processor.config.channels])
    powers = await processor.compute_band_power(data)
    
    assert isinstance(powers, dict)
    assert all(band in powers for band in ['delta', 'theta', 'alpha', 'beta', 'gamma'])
    assert all(isinstance(power, np.ndarray) for power in powers.values())

@pytest.mark.asyncio
async def test_attention_bci(bci, sample_eeg_data):
    """Testa sistema BCI"""
    # Converte dados para numpy array
    data = np.array([sample_eeg_data["channels"][ch] for ch in bci.config.channels])
    
    # Processa dados
    processed = await bci.processor.process_async(data)
    
    # Agora testa o processamento
    features = await bci.process_epoch(processed)
    
    assert isinstance(features, dict)
    assert "attention_metrics" in features
    assert "features" in features
    assert "band_powers" in features["features"]
    assert "quality" in features

@pytest.mark.asyncio
async def test_signal_processing_pipeline(processor, bci, sample_eeg_data):
    """Testa pipeline completo de processamento"""
    # Processa dados brutos
    data = np.array([sample_eeg_data["channels"][ch] for ch in processor.config.channels])
    processed = await processor.process_async(data)
    
    # Verifica conectividade
    connectivity = await processor.compute_connectivity(processed)
    assert connectivity.shape == (len(processor.config.channels), len(processor.config.channels))
    
    # Verifica bandas de frequência
    band_powers = await processor.get_band_power(processed)
    assert all(band in band_powers for band in ['delta', 'theta', 'alpha', 'beta', 'gamma'])