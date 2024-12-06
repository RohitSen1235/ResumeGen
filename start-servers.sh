#!/bin/bash

echo "Starting FastAPI backend server..."
cd backend
python3 -m uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

echo "Starting Vue.js frontend server..."
cd ../frontend
npm run dev &
FRONTEND_PID=$!

echo "Both servers are starting up..."
echo "Backend running on http://localhost:8000"
echo "Frontend running on http://localhost:5173"

# Wait for either process to exit
wait -n $BACKEND_PID $FRONTEND_PID

# Kill both processes on exit
trap "kill $BACKEND_PID $FRONTEND_PID 2>/dev/null" EXIT

# Exit with status of process that exited first
exit $?
