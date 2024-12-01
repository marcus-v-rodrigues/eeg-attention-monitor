from fastapi import APIRouter, HTTPException, Depends
from typing import Dict
from ..core.state import GlobalState

router = APIRouter()

def get_state():
    """Dependency injection para GlobalState"""
    return GlobalState()

@router.post("/start")
async def start_session(state: GlobalState = Depends(get_state)):
    """Inicia gravação de sessão"""
    try:
        state.is_recording = True
        return {"message": "Gravação iniciada"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/stop")
async def stop_session(state: GlobalState = Depends(get_state)):
    """Para gravação de sessão"""
    try:
        state.is_recording = False
        return {
            "message": "Gravação finalizada",
            "samples": len(state.session_data)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/save")
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

@router.post("/load")
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