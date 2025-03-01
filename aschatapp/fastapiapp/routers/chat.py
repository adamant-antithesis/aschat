import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from ..utils.websocket import manage_websocket


router = APIRouter()


django_api_url = "http://django:8000/api/"


@router.get("/chats")
async def get_chats():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{django_api_url}chats/")

    if response.status_code == 200:
        return response.json()

    raise HTTPException(status_code=400, detail="Unable to fetch chats")


@router.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    try:
        await manage_websocket(websocket, chat_id)
    except WebSocketDisconnect:
        print(f"Client disconnected from chat {chat_id}")
