from fastapi import FastAPI, WebSocket, WebSocketDisconnect
import asyncio
import datetime

app = FastAPI()

# Placeholder for the function to store data in the database
async def store_data_in_database(data):
    print(f"Storing data: {data}")
    # Implement your database storing logic here
    await asyncio.sleep(2)  # Simulate database storage delay

async def generate_data(websocket: WebSocket):
    try:
        for i in range(1, 11):
            data = {"value": i, "timestamp": datetime.datetime.now().isoformat()}
            await websocket.send_json(data)
            await store_data_in_database(data)
            await asyncio.sleep(3)
    except WebSocketDisconnect:
        print("Client disconnected. Continuing to store data in database.")
        for i in range(i, 11):
            data = {"value": i, "timestamp": datetime.datetime.now().isoformat()}
            await store_data_in_database(data)
            await asyncio.sleep(3)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    await generate_data(websocket)


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=5500)
