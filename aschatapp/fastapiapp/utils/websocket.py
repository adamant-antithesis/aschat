from fastapi import WebSocket, WebSocketDisconnect
import logging

active_connections = []


async def manage_websocket(websocket: WebSocket):
    await websocket.accept()
    active_connections.append(websocket)

    try:
        while True:
            message = await websocket.receive_text()

            for connection in active_connections:
                if connection != websocket:
                    await connection.send_text(f"Message: {message}")
    except WebSocketDisconnect:
        active_connections.remove(websocket)
        await websocket.close()
        logging.info("WebSocket connection closed.")
