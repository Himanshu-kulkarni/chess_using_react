"""
FastAPI application - Main entry point
"""
from fastapi import FastAPI, HTTPException, WebSocket, Depends
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import uvicorn

from config import HOST, PORT, RELOAD, DATABASE_URL
from models import init_db, get_session
from routes import games, players, multiplayer, analysis

# ═════════════════════════════════════════════════════════════════
# LIFECYCLE
# ═════════════════════════════════════════════════════════════════

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan"""
    # Startup
    print("🚀 Starting Chess Engine API...")
    engine = init_db(DATABASE_URL)
    app.state.engine = engine
    print("✅ Database initialized")
    
    yield
    
    # Shutdown
    print("🛑 Shutting down...")

# ═════════════════════════════════════════════════════════════════
# APP SETUP
# ═════════════════════════════════════════════════════════════════

app = FastAPI(
    title="Chess Platform API",
    description="Production-grade chess backend with AI engine",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, restrict this
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ═════════════════════════════════════════════════════════════════
# ROUTES
# ═════════════════════════════════════════════════════════════════

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "chess-engine-api"}

@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Chess Platform API",
        "version": "1.0.0",
        "docs": "/docs",
    }

# Include route modules
app.include_router(games.router, prefix="/api/games", tags=["games"])
app.include_router(players.router, prefix="/api/players", tags=["players"])
app.include_router(multiplayer.router, prefix="/api/multiplayer", tags=["multiplayer"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])

# ═════════════════════════════════════════════════════════════════
# MAIN
# ═════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    uvicorn.run(
        "app:app",
        host=HOST,
        port=PORT,
        reload=RELOAD,
    )
