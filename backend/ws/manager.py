"""
WebSocket connection manager for real-time multiplayer
"""
from typing import Set, Dict
from fastapi import WebSocket

class ConnectionManager:
    """Manage WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: Dict[str, Set[WebSocket]] = {}  # game_id -> connections
    
    async def connect(self, game_id: str, websocket: WebSocket):
        """Accept new connection"""
        await websocket.accept()
        if game_id not in self.active_connections:
            self.active_connections[game_id] = set()
        self.active_connections[game_id].add(websocket)
    
    def disconnect(self, game_id: str, websocket: WebSocket):
        """Remove connection"""
        if game_id in self.active_connections:
            self.active_connections[game_id].discard(websocket)
            if not self.active_connections[game_id]:
                del self.active_connections[game_id]
    
    async def broadcast(self, game_id: str, message: dict):
        """Broadcast message to all clients in game"""
        if game_id in self.active_connections:
            for connection in self.active_connections[game_id]:
                try:
                    await connection.send_json(message)
                except:
                    pass
    
    async def send_personal(self, websocket: WebSocket, message: dict):
        """Send message to specific client"""
        try:
            await websocket.send_json(message)
        except:
            pass
