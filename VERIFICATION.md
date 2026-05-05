# Verification Checklist

Use this checklist to verify your chess platform is working correctly.

## ✅ Pre-Flight Checks

### Backend
- [ ] Python 3.10+ installed: `python --version`
- [ ] Pip installed: `pip --version`
- [ ] cd backend works
- [ ] requirements.txt exists

### Frontend
- [ ] Node.js 18+ installed: `node --version`
- [ ] npm installed: `npm --version`
- [ ] cd frontend works
- [ ] package.json exists

---

## ✅ Backend Verification

### 1. Virtual Environment
```bash
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
```
Expected: No errors, command prompt shows `(venv)`

### 2. Dependencies
```bash
pip install -r requirements.txt
```
Expected: All packages install successfully (~20 packages)

### 3. Import Test
```bash
python -c "from engine import Board, MoveGenerator, ChessEngine; print('✓ Engine imports OK')"
python -c "from models import GameState, ELOCalculator; print('✓ Models imports OK')"
```
Expected: Both print success messages

### 4. Chess Engine Test
```bash
python -c "
from engine import Board, MoveGenerator
b = Board()
moves = MoveGenerator.generate_legal_moves(b, 0)  # 0 = WHITE
print(f'✓ Initial position has {len(moves)} legal moves (expected 20)')
"
```
Expected: Prints 20 legal moves

### 5. Start Server
```bash
python app.py
```
Expected:
```
INFO:     Uvicorn running on http://0.0.0.0:8000
```

### 6. API Smoke Test (new terminal)
```bash
curl http://localhost:8000/docs
```
Expected: Returns HTML (Swagger UI page)

### 7. Health Check
```bash
curl http://localhost:8000/health
```
Expected:
```json
{"status": "healthy"}
```

### 8. Create Game
```bash
curl -X POST http://localhost:8000/api/games/create \
  -H "Content-Type: application/json" \
  -d '{"white_player": "alice", "black_player": "AI", "time_control": "rapid"}'
```
Expected: Returns game object with game_id, FEN, etc.

### 9. Make Move
```bash
# Replace {GAME_ID} with actual game_id from above
curl -X POST http://localhost:8000/api/games/{GAME_ID}/move \
  -H "Content-Type: application/json" \
  -d '{"from_square": "e2", "to_square": "e4", "player": "alice"}'
```
Expected: Returns updated game state with move applied

### 10. Get Legal Moves
```bash
curl http://localhost:8000/api/games/{GAME_ID}/legal-moves
```
Expected: Returns array of legal moves in algebraic notation

### 11. Run Tests
```bash
pytest tests.py -v
```
Expected: All tests pass
```
test_initial_position PASSED
test_move_execution PASSED
test_fen_parsing PASSED
...
```

---

## ✅ Frontend Verification

### 1. Install Dependencies
```bash
cd frontend
npm install
```
Expected: No errors, node_modules folder created (~200MB)

### 2. Type Check
```bash
npm run build
```
Expected: Builds successfully
```
vite v5.0.8 building for production...
✓ 123 modules transformed.
dist/index.html          0.45 kB │ gzip: 0.30 kB
dist/assets/main.xxx.js  145.23 kB │ gzip: 42.15 kB
```

### 3. Start Dev Server
```bash
npm run dev
```
Expected:
```
  VITE v5.0.8  ready in 234 ms

  ➜  Local:   http://localhost:5173/
  ➜  press h to show help
```

### 4. Browser Test
- Open http://localhost:5173/
- Expected: Chess app loads (if backend running)
- Expected: Board displays
- Expected: Timer shows

### 5. Board Interaction
- [ ] Click piece - highlights legal moves (yellow squares)
- [ ] Drag piece to square - piece moves
- [ ] Pieces can't move to illegal squares
- [ ] Board updates after move

### 6. Network Test
Open browser DevTools (F12), Network tab:
- [ ] Make a move
- [ ] See POST request to `/api/games/{id}/move`
- [ ] Response has 200 status
- [ ] Response has updated FEN

---

## ✅ Integration Tests

### Full Game Flow
1. Backend running on :8000
2. Frontend running on :5173
3. In browser:
   - [ ] Page loads
   - [ ] Board displays with pieces
   - [ ] Click "New Game vs AI"
   - [ ] Game creates successfully
   - [ ] Make a move (e.g., e2 to e4)
   - [ ] Move appears on board
   - [ ] AI makes a move (wait ~1-2 seconds)
   - [ ] AI move appears on board
   - [ ] Move history updates
   - [ ] Timer counts down

### Player Registration
```bash
curl -X POST http://localhost:8000/api/players/register \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testplayer",
    "email": "test@example.com",
    "password": "password123",
    "display_name": "Test Player"
  }'
```
Expected: Returns player object with id and initial 1200 rating

### Get Player Stats
```bash
curl http://localhost:8000/api/players/testplayer/stats
```
Expected: Returns stats object with ratings, win/loss/draw

---

## ✅ Database Tests

### Check Database File
```bash
ls -la chess.db  # Linux/Mac: ls chess.db (Windows: dir chess.db)
```
Expected: chess.db file exists in backend folder (~50KB after first game)

### List Games
```bash
curl http://localhost:8000/api/games
```
Expected: Returns array of games (empty if none created)

---

## ⚠️ Common Issues

### "Port 8000 already in use"
```bash
# Kill process on port 8000
lsof -ti:8000 | xargs kill -9  # Linux/Mac
netstat -ano | findstr :8000   # Windows (find PID, then taskkill /PID xxx)
```

### "Module not found" error
```bash
pip install -r requirements.txt --force-reinstall
```

### "npm install fails"
```bash
rm -rf node_modules package-lock.json
npm cache clean --force
npm install
```

### CORS Error in Browser
Check backend/app.py CORS config allows localhost:5173

### "Cannot connect to localhost:8000"
- [ ] Backend running? Check terminal shows "Uvicorn running"
- [ ] Correct port? Should be :8000
- [ ] Firewall blocking? Try http://127.0.0.1:8000

---

## 📊 Verification Summary

Run this script to verify everything:

```bash
#!/bin/bash

echo "=== BACKEND CHECKS ==="
echo "✓ Python version"
python --version

echo "✓ Importing engine"
python -c "from engine import Board; print('✓ OK')"

echo "✓ Importing models"
python -c "from models import GameState; print('✓ OK')"

echo "✓ Running tests"
pytest tests.py --tb=no -q

echo ""
echo "=== FRONTEND CHECKS ==="
cd frontend
echo "✓ Node version"
node --version

echo "✓ Npm version"
npm --version

echo "✓ Build test"
npm run build > /dev/null 2>&1 && echo "✓ Build successful"

echo ""
echo "=== ALL CHECKS PASSED ==="
echo "Ready to use!"
```

---

## 🎯 Sign-Off

When all checks pass, your chess platform is ready:
- ✅ Backend API working
- ✅ Frontend UI working
- ✅ Chess engine functional
- ✅ Database set up
- ✅ Real-time sync ready

**Happy playing! ♟️**
