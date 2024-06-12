from fastapi import FastAPI, WebSocket
from pymongo import MongoClient
import asyncio
from bson import ObjectId
from decouple import config

# Mongo variables
uri = config("MONGO_URI")
db_name = config("MONGO_DB_NAME")
user_pdf_mapping_collection_name = config("USER_PDF_COLLECTION_NAME")

mongo_client = MongoClient(uri)
db = mongo_client[db_name]
user_pdf_mapping_collection = db[user_pdf_mapping_collection_name]

app = FastAPI()

# WebSocket connection manager
class ConnectionManager:
    def __init__(self):
        self.active_connections = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def notify_changes(self, message: str):
        for connection in self.active_connections:
            await connection.send_text(message)

manager = ConnectionManager()

# WebSocket endpoint to watch for changes
@app.websocket("/ws/{user_id}")
async def websocket_endpoint(websocket: WebSocket, user_id: int):
    await manager.connect(websocket)
    try:
        # Create a change stream outside the while loop
        change_stream = user_pdf_mapping_collection.watch()

        while True:
            # Get the next change event
            change = change_stream.next()

            # Process the change event
            if change["fullDocument"]["userId"] == user_id:
                # Notify the frontend about the change
                await manager.notify_changes(str(change))

    except Exception as e:
        print("WebSocket Error:", e)
        manager.disconnect(websocket)

