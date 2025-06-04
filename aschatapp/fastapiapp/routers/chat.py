import httpx
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from fastapi.security import OAuth2PasswordBearer

from ..config import DJANGO_API_URL
from ..utils.auth import get_user_from_token
from ..utils.websocket import manage_websocket
from ..utils.logging_config import get_logger


router = APIRouter()

logger = get_logger(__name__)

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/token")


@router.get("/chats")
async def get_chats():
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DJANGO_API_URL}chats/")

    if response.status_code == 200:
        return response.json()

    raise HTTPException(status_code=400, detail="Unable to fetch chats")


@router.get("/chats/{chat_id}")
async def get_chat(chat_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"{DJANGO_API_URL}chats/{chat_id}/")

    if response.status_code == 200:
        return response.json()

    raise HTTPException(status_code=404, detail=f"Chat with ID {chat_id} not found")


@router.websocket("/ws/chat/{chat_id}")
async def websocket_endpoint(websocket: WebSocket, chat_id: str):
    logger.info(
        f"Received WebSocket connection request for chat {chat_id} from {websocket.client.host}"
    )

    token = websocket.headers.get("Authorization")
    if not token:
        token = websocket.query_params.get("token")
        if not token:
            logger.error("No Authorization token provided in headers or query params")
            await websocket.send_text("Error: No token provided")
            await websocket.close(code=4000)
            return

    try:
        user_data = await get_user_from_token(token)
        logger.info(f"User authenticated, user_id: {user_data['id']}")
        await manage_websocket(
            websocket,
            chat_id,
            user_id=user_data["id"],
            username=user_data.get("username", ""),
            token=token,
        )
    except WebSocketDisconnect:
        logger.info(f"Client disconnected from chat {chat_id}")
        logger.info(f"Client data: {token}")
    except HTTPException as e:
        logger.error(f"Authentication error: {e.detail}")
        await websocket.close(code=4000)
