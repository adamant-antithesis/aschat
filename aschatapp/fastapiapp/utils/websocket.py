import logging
from fastapi import WebSocket, WebSocketDisconnect
import httpx

active_connections = {}


async def manage_websocket(websocket: WebSocket, chat_id: str):
    async with httpx.AsyncClient() as client:
        response = await client.get(f"http://django:8000/api/chats/{chat_id}/")

    if response.status_code != 200:
        try:
            await websocket.accept()
            await websocket.send_text(f"Error: Chat with ID {chat_id} does not exist.")
        except Exception as e:
            logging.error(f"Error sending message to WebSocket: {e}")
        finally:
            await websocket.close()
            logging.error(f"Attempt to connect to non-existent chat {chat_id} by client {websocket.client.host}")
        return

    await websocket.accept()

    if chat_id not in active_connections:
        active_connections[chat_id] = []
        logging.info(f"Created new connection list for chat {chat_id}")

    active_connections[chat_id].append(websocket)

    client_host = websocket.client.host
    logging.info(f"Client {client_host} connected to chat {chat_id}")

    try:
        while True:
            message = await websocket.receive_text()
            logging.info(f"Message received in chat {chat_id}: {message}")

            for connection in active_connections[chat_id]:
                if connection != websocket:
                    await connection.send_text(f"Message from chat {chat_id}: {message}")
    except WebSocketDisconnect:
        if websocket in active_connections[chat_id]:
            active_connections[chat_id].remove(websocket)

        logging.info(f"WebSocket connection for chat {chat_id} closed.")

        if not active_connections[chat_id]:
            del active_connections[chat_id]
            logging.info(f"Chat {chat_id} is now empty, removed from active connections.")
        try:
            await websocket.close()
        except RuntimeError:
            logging.warning(f"WebSocket already closed for chat {chat_id}")
