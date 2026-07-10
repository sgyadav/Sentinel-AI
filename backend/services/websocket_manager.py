"""Real-time WebSocket management and broadcasting"""

import logging
import json
from typing import Dict, List, Set
from fastapi import WebSocket

logger = logging.getLogger(__name__)


class ConnectionManager:
    """Manage WebSocket connections and broadcast"""
    
    def __init__(self):
        """Initialize connection manager"""
        self.active_connections: Dict[str, List[WebSocket]] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str = None):
        """Accept a WebSocket connection"""
        await websocket.accept()
        
        # Use random ID if not provided
        if not client_id:
            client_id = f"client_{id(websocket)}"
        
        if client_id not in self.active_connections:
            self.active_connections[client_id] = []
        
        self.active_connections[client_id].append(websocket)
        logger.info(f"Client connected: {client_id}")
        
        return client_id
    
    def disconnect(self, client_id: str, websocket: WebSocket):
        """Remove a client connection"""
        if client_id in self.active_connections:
            self.active_connections[client_id].remove(websocket)
            if not self.active_connections[client_id]:
                del self.active_connections[client_id]
        
        logger.info(f"Client disconnected: {client_id}")
    
    async def broadcast(self, message: Dict):
        """Broadcast message to all connected clients"""
        disconnected_clients = []
        
        for client_id, connections in self.active_connections.items():
            for connection in connections[:]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send to {client_id}: {e}")
                    disconnected_clients.append((client_id, connection))
        
        # Cleanup disconnected clients
        for client_id, connection in disconnected_clients:
            self.disconnect(client_id, connection)
    
    async def send_personal_message(self, message: Dict, client_id: str):
        """Send message to specific client"""
        if client_id in self.active_connections:
            for connection in self.active_connections[client_id]:
                try:
                    await connection.send_json(message)
                except Exception as e:
                    logger.error(f"Failed to send to {client_id}: {e}")
    
    async def broadcast_threat(self, threat: Dict, threat_level: int):
        """Broadcast threat alert to all clients"""
        message = {
            "type": "threat_alert",
            "threat_level": threat_level,  # 1-5: Low to Critical
            "threat": threat,
            "timestamp": threat.get("timestamp")
        }
        
        await self.broadcast(message)
    
    async def broadcast_device_status(self, device_data: Dict):
        """Broadcast device status update"""
        message = {
            "type": "device_update",
            "device": device_data
        }
        
        await self.broadcast(message)
    
    async def broadcast_incident(self, incident: Dict):
        """Broadcast incident alert"""
        message = {
            "type": "incident",
            "incident": incident
        }
        
        await self.broadcast(message)
    
    async def broadcast_dashboard_update(self, dashboard_data: Dict):
        """Broadcast dashboard statistics update"""
        message = {
            "type": "dashboard_update",
            "data": dashboard_data
        }
        
        await self.broadcast(message)
    
    async def broadcast_telemetry_update(self, telemetry: Dict):
        """Broadcast device telemetry update"""
        message = {
            "type": "telemetry_update",
            "telemetry": telemetry
        }
        
        await self.broadcast(message)
    
    def get_connection_count(self) -> int:
        """Get total number of connected clients"""
        return sum(len(conns) for conns in self.active_connections.values())
    
    def get_connected_clients(self) -> List[str]:
        """Get list of connected client IDs"""
        return list(self.active_connections.keys())


# Global connection manager instance
manager = ConnectionManager()
