"""
WebSocket functionality for real-time communication
"""

import asyncio
import json
import logging
from typing import Set, Dict, Any
from fastapi import WebSocket, WebSocketDisconnect

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manages WebSocket connections and broadcasting"""
    
    def __init__(self):
        # Active connections
        self.active_connections: Set[WebSocket] = set()
        self._lock = asyncio.Lock()
    
    async def connect(self, websocket: WebSocket) -> None:
        """Accept a new WebSocket connection"""
        await websocket.accept()
        async with self._lock:
            self.active_connections.add(websocket)
        logger.info(f"Client connected. Total clients: {len(self.active_connections)}")
    
    def disconnect(self, websocket: WebSocket) -> None:
        """Remove a WebSocket connection"""
        self.active_connections.discard(websocket)
        logger.info(f"Client disconnected. Total clients: {len(self.active_connections)}")
    
    async def send_personal_message(self, message: str, websocket: WebSocket) -> None:
        """Send message to a specific WebSocket connection"""
        try:
            await websocket.send_text(message)
        except Exception as e:
            logger.error(f"Error sending personal message: {e}")
            self.disconnect(websocket)
    
    async def broadcast(self, message: str) -> None:
        """Broadcast message to all connected clients"""
        if not self.active_connections:
            return
        
        # Create a copy of connections to avoid modification during iteration
        connections_to_remove = set()
        
        for connection in self.active_connections.copy():
            try:
                await connection.send_text(message)
            except Exception as e:
                logger.error(f"Error broadcasting to client: {e}")
                connections_to_remove.add(connection)
        
        # Remove failed connections
        for connection in connections_to_remove:
            self.disconnect(connection)
    
    def get_client_count(self) -> int:
        """Return number of connected clients"""
        return len(self.active_connections)


# Global connection manager instance
manager = ConnectionManager()


async def websocket_endpoint(websocket: WebSocket) -> None:
    """WebSocket endpoint handler"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive by listening for messages
            data = await websocket.receive_text()
            # For now, we don't handle incoming messages from clients
            # but we could add message handling here if needed
            logger.debug(f"Received message from client: {data}")
    except WebSocketDisconnect:
        manager.disconnect(websocket)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
        manager.disconnect(websocket)
