from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..utils.websocket import manage_websocket


router = APIRouter()


@router.websocket("/ws/chat")
async def websocket_endpoint(websocket: WebSocket):
    try:
        await manage_websocket(websocket)
    except WebSocketDisconnect:
        print("Client disconnected")
