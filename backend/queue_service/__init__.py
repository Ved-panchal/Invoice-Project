from .client import RemoteProcessClient
from web_socket import socket_manager

queue_manager = RemoteProcessClient(socket_manager)