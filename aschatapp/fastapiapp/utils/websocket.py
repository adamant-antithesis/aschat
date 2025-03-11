import logging
import httpx
import json
from fastapi import WebSocket, WebSocketDisconnect, HTTPException
from datetime import datetime
from .producers import send_message_to_rabbitmq

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

active_connections = {}


def format_time(timestamp: str) -> str:
    return datetime.fromisoformat(timestamp).strftime('%Y-%m-%d %H:%M:%S')


async def get_chat_details(client: httpx.AsyncClient, chat_id: str, auth_headers: dict):
    # response = await client.get(f"http://django:8000/api/chats/{chat_id}/details/", headers=auth_headers)
    response = await client.get(f"https://44a2-188-163-20-93.ngrok-free.app/api/chats/{chat_id}/details/",
                                headers=auth_headers)
    return response


async def manage_websocket(websocket: WebSocket, chat_id: str, user_id: int, username: str, token: str):
    try:
        logger.info(f"Checking chat {chat_id} for user {user_id}")

        if not token.startswith('Bearer '):
            token = f"Bearer {token}"

        auth_headers = {"Authorization": token}

        async with httpx.AsyncClient() as client:
            response = await get_chat_details(client, chat_id, auth_headers)

            if response.status_code != 200:
                logger.error(f"Chat {chat_id} not found or access denied. Status code: {response.status_code}")
                await websocket.accept()
                await websocket.send_text(f"Error: You cannot access chat {chat_id}.")
                await websocket.close()
                return

            data = response.json()
            chat_history = data.get("messages", [])

            logger.info(f"Chat {chat_id} found, accepting WebSocket connection")
            await websocket.accept()

            for message in chat_history:
                message_time = format_time(message['created_at'])
                formatted_message = {
                    "username": message['user']['username'],
                    "content": f"[{message_time}] {message['content']}"
                }
                await websocket.send_text(json.dumps(formatted_message))

        if chat_id not in active_connections:
            active_connections[chat_id] = []
            logger.info(f"Created new connection list for chat {chat_id}")

        active_connections[chat_id].append(websocket)

        client_host = websocket.client.host
        logger.info(f"Client {client_host} (user_id {user_id}) connected to chat {chat_id}")

        join_message = {
            "username": "Connection",
            "content": f"{username} has joined the chat!"
        }
        for connection in active_connections[chat_id]:
            if connection != websocket:
                await connection.send_text(json.dumps(join_message))

        try:
            while True:
                message = await websocket.receive_text()
                logger.info(f"Message received in chat {chat_id}: {message}")

                async with httpx.AsyncClient() as client:
                    response = await get_chat_details(client, chat_id, auth_headers)

                if response.status_code != 200:
                    logger.warning(f"User {user_id} is no longer a member of chat {chat_id}. Disconnecting.")

                    if websocket in active_connections[chat_id]:
                        active_connections[chat_id].remove(websocket)

                    await websocket.send_text("You are no longer a member of this chat.")
                    await websocket.close()
                    return

                await send_message_to_rabbitmq(chat_id, user_id, message)

                message_time = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
                formatted_message = {
                    "username": username,
                    "content": f"[{message_time}] {message}"
                }

                await websocket.send_text(json.dumps(formatted_message))
                for connection in active_connections[chat_id]:
                    if connection != websocket:
                        await connection.send_text(json.dumps(formatted_message))

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
