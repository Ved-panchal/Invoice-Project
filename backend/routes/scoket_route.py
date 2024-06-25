from fastapi import WebSocket, APIRouter, WebSocketDisconnect
from web_socket import socket_manager

socket_router = APIRouter()

@socket_router.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: str):
    await socket_manager.connect(websocket, user_id)
    try:
        while True:
            await websocket.receive_text()  # Keep the connection open and listen for incoming messages
    except WebSocketDisconnect:
        socket_manager.disconnect(user_id)