import logging
import httpx
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from datetime import datetime
from .producers import send_message_to_rabbitmq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

active_connections = {}


def format_time(timestamp: str) -> str:
    return datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')


async def manage_websocket(websocket: WebSocket, chat_id: str, user_id: int, username: str):
    try:
        logger.info(f"Checking chat {chat_id} for user {user_id}")

        async with httpx.AsyncClient() as client:
            response = await client.get(f"http://django:8000/api/chats/{chat_id}/")

            if response.status_code != 200:
                logger.error(f"Chat {chat_id} not found in Django. Status code: {response.status_code}")
                await websocket.accept()
                await websocket.send_text(f"Error: Chat with ID {chat_id} does not exist.")
                await websocket.close()
                return

            logger.info(f"Chat {chat_id} found, accepting WebSocket connection")
            await websocket.accept()

            history_response = await client.get(f"http://django:8000/api/chats/{chat_id}/messages/")
            if history_response.status_code == 200:
                chat_history = history_response.json()
                for message in chat_history:
                    message_time = format_time(message['created_at'])
                    formatted_message = f"{message['user']['username']} [{message_time}]: {message['content']}"
                    await websocket.send_text(formatted_message)

        if chat_id not in active_connections:
            active_connections[chat_id] = []
            logger.info(f"Created new connection list for chat {chat_id}")

        active_connections[chat_id].append(websocket)

        client_host = websocket.client.host
        logger.info(f"Client {client_host} (user_id {user_id}) connected to chat {chat_id}")

        join_message = f"{username} has joined the chat!"
        for connection in active_connections[chat_id]:
            if connection != websocket:
                await connection.send_text(join_message)

        try:
            while True:
                message = await websocket.receive_text()
                logger.info(f"Message received in chat {chat_id}: {message}")

                await send_message_to_rabbitmq(chat_id, user_id, message)

                message_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                formatted_message = f"{username} [{message_time}]: {message}"

                await websocket.send_text(formatted_message)
                for connection in active_connections[chat_id]:
                    if connection != websocket:
                        await connection.send_text(formatted_message)

        except WebSocketDisconnect:
            if websocket in active_connections[chat_id]:
                active_connections[chat_id].remove(websocket)

            logger.info(f"WebSocket connection for chat {chat_id} closed.")

            if not active_connections[chat_id]:
                del active_connections[chat_id]
                logger.info(f"Chat {chat_id} is now empty, removed from active connections.")
            try:
                await websocket.close()
            except RuntimeError:
                logger.warning(f"WebSocket already closed for chat {chat_id}")

    except HTTPException as e:
        logger.error(f"HTTP error during WebSocket connection: {e.detail}")
        await websocket.close(code=4000)
