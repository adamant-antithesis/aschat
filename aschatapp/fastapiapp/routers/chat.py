import logging

import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer

from ..utils.auth import get_user_from_django
from ..utils.websocket import manage_websocket


router = APIRouter()


django_api_url = "http://django:8000/api/"

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


@router.get("/chats")
async def get_chats():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{django_api_url}chats/")

    if response.status_code == 200:
        return response.json()

    raise HTTPException(status_code=400, detail="Unable to fetch chats")


@router.get("/chats/{chat_id}")
async def get_chat(chat_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{django_api_url}chats/{chat_id}/")

    if response.status_code == 200:
        return response.json()

    raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found")


@router.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    token = websocket.headers.get("Authorization")

    logging.info(f"Received WebSocket connection request for chat {chat_id} from {websocket.client.host}")

    if token is None:
        logging.error("No Authorization token provided")
        await websocket.close(code=4000)
        return

    try:
        user_data = await get_user_from_django(token)
        logging.info(f"User authenticated, user_id: {user_data['id']}")

        await manage_websocket(websocket, chat_id, user_id=user_data['id'], username=user_data['username'])
    except WebSocketDisconnect:
        logging.info(f"Client disconnected from chat {chat_id}")
        logging.info(f"Client data: {token}")
    except HTTPException as e:
        logging.error(f"Authentication error: {e.detail}")
        await websocket.close(code=4000)
