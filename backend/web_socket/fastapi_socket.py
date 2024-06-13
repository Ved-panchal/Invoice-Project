from fastapi import WebSocket
from typing import List, Dict

class SocketConnectionManager:
    def __init__(self):
        self.active_connections: Dict[str, WebSocket] = {}

    async def connect(self, websocket: WebSocket, user_id: str):
        await websocket.accept()
        self.active_connections[user_id] = websocket

    def disconnect(self, user_id: str):
        if user_id in self.active_connections:
            del self.active_connections[user_id]

    async def send_message(self, message: str, user_id: str):
        # print(f'Sending message: {message}')
        # print(f'user_id1: {user_id}')
        websocket = self.active_connections.get(user_id)
        # print(f'user_id2: {user_id}')
        if websocket:
            await websocket.send_text(message)
        # print("Message sent")

    async def broadcast(self, message: str):
        for websocket in self.active_connections.values():
            await websocket.send_text(message)
