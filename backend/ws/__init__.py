"""
WebSocket module
"""
from .manager import ConnectionManager

manager = ConnectionManager()

__all__ = ["manager", "ConnectionManager"]
