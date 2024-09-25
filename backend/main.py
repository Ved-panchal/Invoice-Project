from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pika.exceptions import AMQPConnectionError
import ssl

from routes.test_route import test_router
from routes.scoket_route import socket_router
from routes.login_route import login_router
from routes.api_route import api_router

from logger import logger

# Create fastapi object
app = FastAPI()

# Disable SSL certificate verification
ssl._create_default_https_context = ssl._create_unverified_context

# Static file hosting
app.mount("/static", StaticFiles(directory="static"), name="static")

# Include routers
app.include_router(router=test_router)
app.include_router(router=socket_router)
app.include_router(router=login_router)
app.include_router(router=api_router)

# Allow cross origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://85.13.195.92:5173", "http://192.168.10.205:5173", "http://localhost:5173", "http://0.0.0.0:5173"],
    # allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

if __name__ == "__main__":
    try:
        import uvicorn
        uvicorn.run(app, host="0.0.0.0", port=5500)
    except KeyboardInterrupt:
        logger.error("Shut down server by keyboard.")
        print("keyboard interrupted.")