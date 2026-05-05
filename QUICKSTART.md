# Quick Start Guide

## 🚀 Getting Started

### Prerequisites
- Python 3.10+
- Node.js 18+
- Git

## Backend Setup

### 1. Clone & Navigate
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```

### 2. Install Dependencies
```bash
pip install -r requirements.txt
```

### 3. Start Server
```bash
python app.py
```

Server runs on `http://localhost:8000`

**API Documentation**: `http://localhost:8000/docs`

## Frontend Setup

### 1. Navigate & Install
```bash
cd frontend
npm install
```

### 2. Start Dev Server
```bash
npm run dev
```

App runs on `http://localhost:5173`

## Quick Test

### 1. Create a Game
```bash
curl -X POST http://localhost:8000/api/games/create \
  -H "Content-Type: application/json" \
  -d '{
    "white_player": "alice",
    "black_player": "AI",
    "time_control": "rapid",
    "ai_difficulty": "medium"
  }'
```

Response:
```json
{
  "game_id": "abc123",
  "white_player": "alice",
  "black_player": "AI",
  "fen": "rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1",
  "moves": [],
  "white_time": 600000,
  "black_time": 600000,
  ...
}
```

### 2. Make a Move
```bash
curl -X POST http://localhost:8000/api/games/abc123/move \
  -H "Content-Type: application/json" \
  -d '{
    "from_square": "e2",
    "to_square": "e4",
    "player": "alice"
  }'
```

### 3. Get Legal Moves
```bash
curl http://localhost:8000/api/games/abc123/legal-moves
```

## 🎮 In-Game Features

### Board
- **Click**: Select piece, then click destination
- **Drag**: Drag piece to destination
- **Hover**: See legal moves highlighted in yellow
- **Last Move**: Highlighted in light yellow

### Move History
- **Click Move**: Navigate to that position (replay)
- **Algebraic Notation**: Standard chess notation

### Timer
- **Color-Coded**: Green (plenty) → Red (critical)
- **Active Timer**: Bold and scaled up
- **Auto-Update**: Every 100ms

### Game Controls
- **Resign**: Concede the game
- **Draw Offer**: Offer draw to opponent
- **Undo**: Take back last move

## 📊 API Examples

### Register Player
```bash
curl -X POST http://localhost:8000/api/players/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "alice",
    "email": "alice@example.com",
    "password": "secure_password",
    "display_name": "Alice"
  }'
```

### Get Player Stats
```bash
curl http://localhost:8000/api/players/alice/stats
```

### Create Multiplayer Room
```bash
curl -X POST http://localhost:8000/api/multiplayer/room/create \
  -H "Content-Type: application/json" \
  -d '{
    "creator": "alice",
    "time_control": "rapid",
    "is_private": false
  }'
```

### Join Room
```bash
curl -X POST http://localhost:8000/api/multiplayer/room/ABC123/join \
  -H "Content-Type: application/json" \
  -d '{
    "player": "bob"
  }'
```

## 🧪 Testing

### Run Unit Tests
```bash
cd backend
pytest tests.py -v
```

### Test Coverage
```bash
pytest tests.py --cov=engine --cov=models
```

## 🔧 Configuration

### Backend `.env`
```env
DEBUG=True
DATABASE_URL=sqlite:///./chess.db
HOST=0.0.0.0
PORT=8000
MAX_TRANSPOSITION_TABLE_SIZE=1000000
DEFAULT_AI_DEPTH=5
MAX_AI_SEARCH_TIME=3.0
```

### Difficulty Levels
- **Easy**: Depth 3, random from top 6 moves (55% chance)
- **Medium**: Depth 5, full alpha-beta
- **Hard**: Depth 7, optimized search

## 📈 Performance Tuning

### Increase Engine Strength
```python
# In backend/models/game.py
depth_map = {
    "easy": 5,      # was 3
    "medium": 7,    # was 5
    "hard": 9,      # was 7
}
```

### Larger Transposition Table
```env
MAX_TRANSPOSITION_TABLE_SIZE=5000000  # was 1M, now 5M
```

### Database Optimization
```bash
# Create index on common queries
sqlite3 chess.db "CREATE INDEX idx_games_players ON games(white_player_id, black_player_id);"
```

## 🐛 Debugging

### Enable Debug Logging
```env
DEBUG=True
LOG_LEVEL=DEBUG
```

### Check Engine Stats
```bash
# After making a move, check:
curl http://localhost:8000/api/games/abc123/status
```

Response includes:
```json
{
  "game_id": "abc123",
  "is_finished": false,
  "white_time": 598000,
  "black_time": 600000,
  "move_count": 1
}
```

### Browser DevTools
1. Open Chrome DevTools (F12)
2. Network tab: Monitor API requests
3. Console: Check for JavaScript errors
4. Performance: Measure rendering time

## 🚢 Deployment

### Docker Setup
```bash
docker-compose up
```

Starts:
- Backend on port 8000
- Frontend on port 5173
- PostgreSQL on port 5432

### Production Checklist
- [ ] Set `DEBUG=False`
- [ ] Change database to PostgreSQL
- [ ] Set secure CORS origins
- [ ] Enable HTTPS
- [ ] Set up authentication
- [ ] Configure rate limiting
- [ ] Set up monitoring/logging

## 📚 Architecture

See [ARCHITECTURE.md](ARCHITECTURE.md) for detailed system design.

## 🆘 Troubleshooting

### Port Already in Use
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9

# Kill process on port 5173
lsof -ti:5173 | xargs kill -9
```

### Database Locked
```bash
# Delete and recreate
rm chess.db
# Restart server
```

### Module Not Found
```bash
# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### CORS Error
Check `app.py` CORS configuration. Add frontend URL:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    ...
)
```

## 📞 Support

For issues or questions:
1. Check logs: `backend/app.py` and browser console
2. Review [ARCHITECTURE.md](ARCHITECTURE.md)
3. Run tests: `pytest tests.py -v`

## 📝 Next Steps

- [ ] Add authentication system
- [ ] Implement opening book
- [ ] Add spectator mode
- [ ] Create tournament system
- [ ] Mobile app support
- [ ] Lichess API integration

---

**Happy Playing! ♟️**
