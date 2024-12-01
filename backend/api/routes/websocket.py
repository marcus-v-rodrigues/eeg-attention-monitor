from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from typing import List
from ..core.state import GlobalState
from ..core.application import get_state
import asyncio

router = APIRouter()

@router.websocket("/stream")
async def websocket_endpoint(websocket: WebSocket):
    state = get_state()
    data_loader = state.data_loader

    await websocket.accept()
    print("connection open")
    
    try:
        while True:
            data = data_loader.get_next_sample()
            result = await state.process_data(data)
            await websocket.send_json(result)
            await asyncio.sleep(1/128)
            
    except WebSocketDisconnect:
        print("connection closed")
    except Exception as e:
        print(f"Erro no WebSocket: {str(e)}")
        try:
            await websocket.close()
        except:
            pass