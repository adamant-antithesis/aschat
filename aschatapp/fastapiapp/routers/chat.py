from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from ..utils.websocket import manage_websocket


router = APIRouter()


@router.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    try:
        await manage_websocket(websocket, chat_id)
    except WebSocketDisconnect:
        print(f"Client disconnected from chat {chat_id}")
