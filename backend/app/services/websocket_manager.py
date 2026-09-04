import asyncio
import json
from typing import List
from fastapi import WebSocket
from app.logger import logger


class ConnectionManager:
    """
    Manages WebSocket connections for the real-time dashboard.
    Provides async and sync broadcast capabilities safely.
    """
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
        self.loop = None

    def set_loop(self, loop):
        """
        Store the main event loop so that background threads can
        safely schedule async broadcasts.
        """
        self.loop = loop

    def add_connection(self, websocket: WebSocket):
        self.active_connections.append(websocket)
        logger.info(f"WebSocket client authenticated and connected. Total clients: {len(self.active_connections)}")

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            self.active_connections.remove(websocket)
            logger.info(f"WebSocket client disconnected. Total clients: {len(self.active_connections)}")

    async def broadcast(self, message: dict):
        """
        Asynchronously broadcast a JSON message to all connected clients.
        Removes any clients that fail to receive the message (e.g., dropped connection).
        """
        if not self.active_connections:
            return

        text_data = json.dumps(message)
        dead_connections = []
        
        for connection in self.active_connections:
            try:
                await connection.send_text(text_data)
            except Exception as e:
                logger.error(f"Failed to send message to websocket client: {e}")
                dead_connections.append(connection)
        
        for dead in dead_connections:
            self.disconnect(dead)

    def broadcast_sync(self, message: dict):
        """
        Safely broadcast from a synchronous context (e.g. a background thread).
        """
        if self.loop and self.loop.is_running():
            try:
                asyncio.run_coroutine_threadsafe(self.broadcast(message), self.loop)
            except Exception as e:
                logger.error(f"Failed to schedule websocket broadcast: {e}")

ws_manager = ConnectionManager()
