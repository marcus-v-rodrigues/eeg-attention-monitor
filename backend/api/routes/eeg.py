from fastapi import APIRouter, HTTPException, WebSocket, Depends
from fastapi.websockets import WebSocketDisconnect
from typing import Dict, Optional
from datetime import datetime
from ..models.schemas import EEGDataPoint, ProcessedEEG
from ..core.state import GlobalState
from ..core.application import get_state
import numpy as np
import logging
import asyncio

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/process")
async def process_eeg(data: EEGDataPoint):
    """Processa dados EEG"""
    try:
        state = get_state()
        raw_result = await state.process_data(data.model_dump())
        
        # Converte arrays NumPy para floats simples
        processed_result = {
            'timestamp': raw_result['timestamp'],
            'attention_metrics': raw_result['attention_metrics'],
            'band_powers': {
                band: float(power[0]) if isinstance(power, np.ndarray) else float(power)
                for band, power in raw_result['band_powers'].items()
            },
            'channel_data': data.channels  # Adiciona os dados dos canais
        }
        
        # Envia dados processados para clientes WebSocket
        await state.broadcast({
            'type': 'new_data',
            'data': processed_result
        })
        
        return ProcessedEEG(**processed_result)
        
    except Exception as e:
        logger.error(f"Erro no processamento: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/analysis")
async def get_analysis(
    start_time: Optional[float] = None,
    end_time: Optional[float] = None,
    state: GlobalState = Depends(get_state)
):
    """
    Retorna análise dos dados históricos
    
    Args:
        start_time: Timestamp inicial
        end_time: Timestamp final
        state: Estado global da aplicação
    """
    try:
        # Obtém dados do período
        recent_data = await state.get_recent_data(
            seconds=(end_time or datetime.now().timestamp()) - (start_time or 0)
        )
        
        if not recent_data:
            raise HTTPException(
                status_code=404,
                detail="Nenhum dado encontrado para o período"
            )
        
        # Calcula estatísticas
        stats = state.get_processing_stats()
        
        return {
            'data': recent_data,
            'stats': stats
        }
        
    except Exception as e:
        logger.error(f"Erro na análise: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@router.websocket("/stream")
async def websocket_endpoint(
    websocket: WebSocket,
    state: GlobalState = Depends(get_state)
):
    """
    Endpoint WebSocket para streaming de dados
    
    Args:
        websocket: Conexão WebSocket
        state: Estado global da aplicação
    """
    await state.add_client(websocket)
    
    try:
        while True:
            # Recebe dados do cliente
            data = await websocket.receive_json()
            
            # Valida dados
            eeg_data = EEGDataPoint(**data)
            
            # Processa usando o state
            # Em api/routes/eeg.py
            result = await state.process_data(data.model_dump())
            
            # Resultado já foi adicionado ao buffer pelo process_data
            
            # Envia resultado processado
            await websocket.send_json(result)
            
            # Pequena pausa para não sobrecarregar
            await asyncio.sleep(0.01)
            
    except WebSocketDisconnect:
        state.remove_client(websocket)
        logger.info("Cliente WebSocket desconectado")
        
    except Exception as e:
        logger.error(f"Erro no WebSocket: {str(e)}")
        state.remove_client(websocket)
        # Não re-levanta a exceção para não quebrar o socket

# Rotas adicionais para controle de sessão

@router.post("/session/start")
async def start_session(
    state: GlobalState = Depends(get_state)
):
    """Inicia gravação de sessão"""
    try:
        await state.start_recording()
        return {"message": "Gravação iniciada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/stop")
async def stop_session(
    state: GlobalState = Depends(get_state)
):
    """Para gravação de sessão"""
    try:
        await state.stop_recording()
        return {
            "message": "Gravação finalizada",
            "samples": len(state.session_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/save")
async def save_session(
    filename: str,
    state: GlobalState = Depends(get_state)
):
    """Salva sessão em arquivo"""
    try:
        await state.save_session(filename)
        return {"message": f"Sessão salva em {filename}"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/session/load")
async def load_session(
    filename: str,
    state: GlobalState = Depends(get_state)
):
    """Carrega sessão de arquivo"""
    try:
        await state.load_session(filename)
        return {
            "message": f"Sessão carregada de {filename}",
            "samples": len(state.session_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))