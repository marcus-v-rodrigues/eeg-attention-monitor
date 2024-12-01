import pytest
from fastapi.testclient import TestClient
from api.main import app
from api.core.application import app, get_state
from api.core.config import settings

client = TestClient(app)

def test_root():
    """Testa endpoint raiz"""
    response = client.get(settings.API_V1_STR + "/")
    assert response.status_code == 200

def test_process_eeg(sample_eeg_data):
    """Testa endpoint de processamento"""
    try:
        response = client.post(
            f"{settings.API_V1_STR}/eeg/process",
            json=sample_eeg_data
        )
        
        assert response.status_code == 200
        data = response.json()
        
        # Verifica se todos os campos necessários estão presentes
        assert "timestamp" in data
        assert "attention_metrics" in data
        assert "band_powers" in data
        assert "channel_data" in data
        
        # Verifica se band_powers tem os valores corretos
        assert all(isinstance(v, float) for v in data["band_powers"].values())
        assert all(v >= 0 for v in data["band_powers"].values())
        
    except Exception as e:
        pytest.fail(f"Teste falhou com erro: {str(e)}")

@pytest.mark.asyncio
async def test_get_analysis(sample_eeg_data):
    """Testa endpoint de análise"""
    # Usar o estado global do app
    app.state.global_state.add_data(sample_eeg_data)
    
    params = {
        "start_time": 1234567890.0,
        "end_time": 1234567900.0
    }
    
    response = client.get(f"{settings.API_V1_STR}/eeg/analysis", params=params)
    assert response.status_code == 200

@pytest.mark.asyncio
async def test_websocket_connection(client):
    """Testa conexão WebSocket"""
    with client.websocket_connect(f"{settings.API_V1_STR}/ws/stream") as websocket:
        assert websocket is not None

@pytest.mark.asyncio
async def test_session_controls(client):
    """Testa controles de sessão"""
    response = client.post(f"{settings.API_V1_STR}/session/start")
    assert response.status_code == 200