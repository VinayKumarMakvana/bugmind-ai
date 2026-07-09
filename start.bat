@echo off
echo Starting BugMind AI locally...

echo Starting Backend API...
start cmd /k "cd backend && py -m pip install -r requirements.txt && py -m uvicorn app.main:app --reload --host 127.0.0.1 --port 8000"

echo Starting Frontend...
start cmd /k "cd frontend && npm install && npm run dev"

echo Done! BugMind AI is starting up. 
echo API: http://127.0.0.1:8000
echo Web: http://localhost:3000
