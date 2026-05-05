"""
Configuration for Chess Engine & Backend
"""
import os
from pathlib import Path

# Environment
DEBUG = os.getenv("DEBUG", "True").lower() == "true"
ENV = os.getenv("ENV", "development")

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./chess.db")

# Server
HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", 8000))
RELOAD = DEBUG

# Chess Engine
MAX_TRANSPOSITION_TABLE_SIZE = 1_000_000  # ~65 MB for 64-bit hashes
DEFAULT_AI_DEPTH = 5
MAX_AI_SEARCH_TIME = 3.0  # seconds per move
QUIESCENCE_DEPTH = 3

# Game
TIME_CONTROLS = {
    "blitz": 180,      # 3 min
    "rapid": 600,      # 10 min
    "classical": 3600, # 1 hour
}

# WebSocket
WS_HEARTBEAT_INTERVAL = 30  # seconds
WS_TIMEOUT = 60  # seconds

# ELO Ratings
ELO_K_FACTOR = 32
MIN_ELO = 400
MAX_ELO = 3000
