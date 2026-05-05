"""
Starter script - Initialize and run the chess platform
"""
import os
import sys
import subprocess
import platform

def print_header(text):
    print("\n" + "=" * 60)
    print(f"  {text}")
    print("=" * 60 + "\n")

def main():
    print_header("♟️  CHESS PLATFORM - STARTER SCRIPT")
    
    # Detect OS
    system = platform.system()
    is_windows = system == "Windows"
    
    # Backend setup
    print_header("1️⃣  BACKEND SETUP")
    os.chdir("backend")
    
    # Create venv
    venv_path = "venv"
    if not os.path.exists(venv_path):
        print("📦 Creating virtual environment...")
        subprocess.run([sys.executable, "-m", "venv", venv_path])
    else:
        print("✅ Virtual environment already exists")
    
    # Activate venv and install
    activate_cmd = os.path.join(venv_path, "Scripts", "activate") if is_windows else f"source {venv_path}/bin/activate"
    
    print("📥 Installing backend dependencies...")
    pip_cmd = os.path.join(venv_path, "Scripts", "pip") if is_windows else f"{venv_path}/bin/pip"
    subprocess.run([pip_cmd, "install", "-q", "-r", "requirements.txt"])
    print("✅ Backend dependencies installed")
    
    # Frontend setup
    print_header("2️⃣  FRONTEND SETUP")
    os.chdir("../frontend")
    
    if not os.path.exists("node_modules"):
        print("📥 Installing frontend dependencies...")
        subprocess.run(["npm", "install", "-q"])
        print("✅ Frontend dependencies installed")
    else:
        print("✅ Node modules already exist")
    
    # Show next steps
    print_header("✨ SETUP COMPLETE!")
    print("""
    🚀 NEXT STEPS:

    Terminal 1 - Start Backend:
    ┌─────────────────────────────────────────┐
    │ cd backend                              │
    │ source venv/bin/activate  # Windows:    │
    │ venv\\Scripts\\activate                   │
    │ python app.py                           │
    │                                         │
    │ Server: http://localhost:8000           │
    │ Docs:   http://localhost:8000/docs      │
    └─────────────────────────────────────────┘

    Terminal 2 - Start Frontend:
    ┌─────────────────────────────────────────┐
    │ cd frontend                             │
    │ npm run dev                             │
    │                                         │
    │ App: http://localhost:5173              │
    └─────────────────────────────────────────┘

    Terminal 3 - Run Tests:
    ┌─────────────────────────────────────────┐
    │ cd backend                              │
    │ pytest tests.py -v                      │
    └─────────────────────────────────────────┘

    📚 Documentation:
    ├─ README.md                - Overview
    ├─ QUICKSTART.md            - Quick guide
    ├─ ARCHITECTURE.md          - System design
    └─ IMPLEMENTATION_SUMMARY   - What's built

    🎮 Quick Test:
    curl -X POST http://localhost:8000/api/games/create \\
      -H "Content-Type: application/json" \\
      -d '{"white_player": "alice", "black_player": "AI", "time_control": "rapid"}'

    🌟 Enjoy your production-grade chess platform!
    """)

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        sys.exit(1)
