import pytest
from fastapi.testclient import TestClient
import numpy as np
from api.main import app
from api.core.config import settings
from api.core.state import GlobalState
from src.signal_processor import EEGProcessor, SignalConfig
from src.attention_bci import AttentionBCI, BCIConfig

@pytest.fixture(autouse=True)
def setup_app():
    """Configura o app para testes"""
    app.state.api_v1_str = settings.API_V1_STR
    app.state.global_state = GlobalState()
    
@pytest.fixture
def client():
    """Fixture para cliente de teste"""
    return TestClient(app)

@pytest.fixture
def global_state():
    return GlobalState()

@pytest.fixture
def get_state_override(global_state):
    def _get_state():
        return global_state
    return _get_state

@pytest.fixture(autouse=True)
def override_get_state(monkeypatch, get_state_override):
    """Substitui a função get_state para usar o estado de teste"""
    from api.routes import eeg
    monkeypatch.setattr(eeg, "get_state", get_state_override)

@pytest.fixture
def sample_eeg_data():
    """Fixture para dados EEG de exemplo"""
    channels = ['AF3', 'F7', 'F3', 'FC5', 'T7', 'P7', 'O1',
                'O2', 'P8', 'T8', 'FC6', 'F4', 'F8', 'AF4']
    
    # Gera 1 segundo de dados (128 amostras) para cada canal
    data = {
        "timestamp": 1234567890.0,
        "channels": {
            ch: (np.sin(2 * np.pi * 10 * np.linspace(0, 1, 128)) + 
                 np.random.normal(0, 0.1, 128)).tolist()
            for ch in channels
        }
    }
    return data

@pytest.fixture
def processor():
    """Fixture para processador EEG"""
    config = SignalConfig(sfreq=128.0)
    return EEGProcessor(config)

@pytest.fixture
def bci():
    """Fixture para sistema BCI"""
    config = BCIConfig(sfreq=128.0)
    return AttentionBCI(config)

@pytest.fixture
async def sample_processed_data(sample_eeg_data, processor):
    """Fixture para dados processados"""
    # Converte dados para formato numpy
    data = np.array([sample_eeg_data["channels"][ch] for ch in processor.config.channels])
    
    # Processa dados
    return await processor.process_async(data)