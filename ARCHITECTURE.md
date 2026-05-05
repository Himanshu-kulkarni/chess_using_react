# Architecture & Design

## System Overview

```
┌─────────────────┐                    ┌──────────────────┐
│   React Client  │                    │   Mobile Client  │
│  (SPA + WebGL)  │ ◄───── HTTP ─────► │   (Future)       │
└────────┬────────┘                    └──────────────────┘
         │
         │ REST + WebSocket
         ▼
┌──────────────────────────────────────────────────────────┐
│          FastAPI Backend (Python)                        │
├──────────────────────────────────────────────────────────┤
│ ┌──────────────────────────────────────────────────────┐ │
│ │  API Routes  │ WebSocket │ Game Manager │ Auth       │ │
│ └──────────────────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────────────────┐ │
│ │  Chess Engine (Pure Python)                         │ │
│ │  ├─ Board Representation                            │ │
│ │  ├─ Move Generation                                 │ │
│ │  ├─ Iterative Deepening Search                      │ │
│ │  ├─ Transposition Tables                            │ │
│ │  └─ Position Evaluation                             │ │
│ └──────────────────────────────────────────────────────┘ │
│ ┌──────────────────────────────────────────────────────┐ │
│ │  Database Layer (SQLAlchemy ORM)                    │ │
│ │  ├─ Player Management                               │ │
│ │  ├─ Game History                                    │ │
│ │  ├─ Rating Tracking                                 │ │
│ │  └─ Game Analysis                                   │ │
│ └──────────────────────────────────────────────────────┘ │
└──────────────────────────────────────────────────────────┘
         ▲
         │ SQL
         ▼
┌──────────────────────────┐
│   SQLite / PostgreSQL    │
└──────────────────────────┘
```

## Chess Engine Architecture

### Board Representation
- **8x8 Squares Array**: Simple, cache-friendly
- **Piece Encoding**: 3-bit encoding (color + type)
- **Move Validation**: Efficient legal move generation

```python
# Board Layout
board.squares = [0] * 64  # 0-indexed, bottom-left = 56 (a1)
# Piece: (color << 3) | piece_type
# Color: 0=WHITE, 1=BLACK
# Type: PAWN=1, KNIGHT=2, BISHOP=3, ROOK=4, QUEEN=5, KING=6
```

### Move Generation
1. **Pseudo-legal moves**: All possible moves ignoring check
2. **Legal filtering**: Remove moves that leave king in check
3. **Special moves**: Castling, en passant, promotion

### Search Algorithm

```
Iterative Deepening
├─ Depth 1
│  └─ Alpha-Beta Pruning
│     ├─ Transposition Table Lookup
│     ├─ Move Ordering
│     └─ Quiescence Search
├─ Depth 2
│  └─ ...
└─ Depth N (until time runs out)
```

### Transposition Tables
- **Zobrist Hashing**: 64-bit hash per position
- **Collision Rate**: < 0.01% in practice
- **Storage**: Up to 1M positions (~65 MB)
- **Entry Format**: (depth, score, flag, best_move)

```python
class TranspositionEntry:
    EXACT = 0          # Score is exact
    LOWER_BOUND = 1    # Score is at least this value
    UPPER_BOUND = 2    # Score is at most this value
```

### Evaluation Function
```
Score = Material + PST + Mobility + Pawn Structure + King Safety

Where:
- Material: Piece values (P=100, N=320, B=330, R=500, Q=900)
- PST: Piece-square table bonuses
- Mobility: Bonus for having many legal moves
- Pawn Structure: Penalties for doubled/isolated pawns
- King Safety: Bonus for castling rights, penalty for center exposure
```

### Quiescence Search
- **Purpose**: Solve horizon effect (captures beyond search horizon)
- **Depth Limit**: 3 plies from leaf nodes
- **Moves Considered**: Captures + checks only
- **Recursion**: Until no tactical moves available

## API Design

### REST Architecture
```
GET    /health                           # Health check
GET    /api/games/{id}                   # Get game state
POST   /api/games/create                 # Create new game
POST   /api/games/{id}/move              # Make move
POST   /api/games/{id}/resign            # Resign
POST   /api/games/{id}/draw              # Offer/accept draw
GET    /api/games/{id}/legal-moves       # Get legal moves

GET    /api/players/{username}           # Get profile
POST   /api/players/register             # Register
GET    /api/players/{username}/stats     # Get stats

POST   /api/multiplayer/room/create      # Create room
POST   /api/multiplayer/room/{code}/join # Join room
GET    /api/multiplayer/rooms/public     # List rooms

POST   /api/analysis/{id}/analyze        # Analyze game
GET    /api/analysis/{id}/best-moves     # Get best moves
```

### Request/Response Format
```json
// Move Request
{
  "from_square": "e2",
  "to_square": "e4",
  "promotion": "queen",
  "player": "alice"
}

// Game Response
{
  "game_id": "abc123",
  "white_player": "alice",
  "black_player": "bob",
  "fen": "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1",
  "moves": ["e2e4"],
  "white_time": 599000,
  "black_time": 600000,
  "is_finished": false,
  "result": null,
  "current_turn": "black"
}
```

## Real-time Multiplayer

### WebSocket Protocol
```
Client → Server:
  { "type": "move", "move": "e2e4" }
  { "type": "resign" }
  { "type": "draw_offer" }

Server → Client:
  { "type": "move_made", "move": "e2e4", "game_state": {...} }
  { "type": "game_ended", "result": "white_win" }
  { "type": "draw_offered", "by_player": "alice" }
```

### Connection Management
- **Heartbeat**: Every 30 seconds
- **Timeout**: 60 seconds of inactivity
- **Broadcast**: All clients in game room receive updates
- **Error Recovery**: Automatic reconnect with state sync

## Database Schema

### Players
```sql
CREATE TABLE players (
  id INTEGER PRIMARY KEY,
  username TEXT UNIQUE NOT NULL,
  email TEXT UNIQUE NOT NULL,
  password_hash TEXT NOT NULL,
  standard_rating INTEGER DEFAULT 1200,
  blitz_rating INTEGER DEFAULT 1200,
  rapid_rating INTEGER DEFAULT 1200,
  total_games INTEGER DEFAULT 0,
  wins INTEGER DEFAULT 0,
  losses INTEGER DEFAULT 0,
  draws INTEGER DEFAULT 0,
  created_at TIMESTAMP DEFAULT NOW(),
  last_online TIMESTAMP
);
```

### Games
```sql
CREATE TABLE games (
  id INTEGER PRIMARY KEY,
  white_player_id INTEGER FOREIGN KEY,
  black_player_id INTEGER FOREIGN KEY,
  status ENUM ('pending', 'in_progress', 'completed'),
  result ENUM ('white_win', 'black_win', 'draw'),
  time_control ENUM ('blitz', 'rapid', 'classical'),
  fen TEXT,
  pgn TEXT,
  moves TEXT,
  created_at TIMESTAMP,
  completed_at TIMESTAMP
);
```

### Rating History
```sql
CREATE TABLE rating_history (
  id INTEGER PRIMARY KEY,
  player_id INTEGER FOREIGN KEY,
  game_id INTEGER FOREIGN KEY,
  old_rating INTEGER,
  new_rating INTEGER,
  rating_change INTEGER,
  time_control ENUM ('blitz', 'rapid', 'classical'),
  created_at TIMESTAMP
);
```

## Frontend Architecture

### Component Hierarchy
```
App
├─ Navbar
├─ Router
│  ├─ HomePage
│  ├─ GamePage
│  │  ├─ Board (drag-drop logic)
│  │  ├─ GameTimer
│  │  ├─ MoveList
│  │  ├─ GameAnalysis
│  │  └─ GameControls
│  ├─ MultiplayerPage
│  └─ ProfilePage
└─ Footer
```

### State Management
- **Zustand** for global state (optional)
- **React Hooks** for local state
- **Context API** for theme/auth

### Rendering Pipeline
1. **FEN to Visual**: Parse FEN → create square grid
2. **Move Handling**: Click/drag detection → validate → animate
3. **Board Update**: Receive updated FEN → re-render with animation
4. **Performance**: Memoize expensive calculations

### CSS Approach
- **Tailwind CSS** for utility classes
- **CSS Modules** for component-specific styles
- **Framer Motion** for animations
- **Responsive Design**: Mobile-first

## Performance Optimizations

### Backend
1. **Move Generation**: Cache legal moves between turns
2. **Evaluation Caching**: Transposition tables (Zobrist hashing)
3. **Database Indexing**: Index on (player_id, created_at)
4. **Connection Pooling**: SQLAlchemy connection pool

### Frontend
1. **Code Splitting**: Lazy load pages
2. **Memoization**: useMemo for expensive calculations
3. **Virtual Scrolling**: For long move lists
4. **Image Optimization**: SVG pieces, no rasterization
5. **Caching**: HTTP cache headers for static assets

## Scalability Considerations

### Horizontal Scaling
- **Load Balancer**: Distribute requests
- **Session Persistence**: WebSocket sticky sessions
- **Shared Transposition Cache**: Redis for multi-instance
- **Database Replication**: Master-slave setup

### Vertical Scaling
- **Increase Search Depth**: Faster hardware
- **Larger TT**: More memory for position cache
- **Thread Pooling**: Parallel move evaluation (future)

## Testing Strategy

### Unit Tests
- Move generation edge cases
- Evaluation correctness
- ELO calculation

### Integration Tests
- Game flow (create, move, resign)
- Multiplayer synchronization
- Rating updates

### Performance Tests
- NPS benchmarking
- WebSocket latency
- Database query times

## Security Considerations

1. **Input Validation**: All moves verified server-side
2. **Authentication**: JWT tokens (future)
3. **Rate Limiting**: Prevent move spam
4. **SQL Injection Prevention**: SQLAlchemy ORM
5. **CORS**: Restrict to allowed origins
6. **HTTPS**: Required in production

## Deployment

### Docker
```dockerfile
# Backend Dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0"]
```

### Docker Compose
```yaml
services:
  backend:
    build: ./backend
    ports:
      - "8000:8000"
  frontend:
    build: ./frontend
    ports:
      - "5173:5173"
  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: chess
```
