import logging
from fastapi import WebSocket, WebSocketDisconnect


active_connections = {}


async def manage_websocket(websocket: WebSocket, chat_id: str):
    await websocket.accept()

    if chat_id not in active_connections:
        active_connections[chat_id] = []

    active_connections[chat_id].append(websocket)

    try:
        while True:
            message = await websocket.receive_text()

            for connection in active_connections[chat_id]:
                if connection != websocket:
                    await connection.send_text(f"Message from chat {chat_id}: {message}")
    except WebSocketDisconnect:
        active_connections[chat_id].remove(websocket)
        await websocket.close()
        logging.info(f"WebSocket connection for chat {chat_id} closed.")
        if not active_connections[chat_id]:
            del active_connections[chat_id]
