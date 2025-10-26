#!/bin/bash

# Aesop AI - Quick Start Script

echo "=================================="
echo "Starting Aesop AI"
echo "=================================="

# Check if running from correct directory
if [ ! -d "backend" ] || [ ! -d "frontend" ]; then
    echo "Error: Please run this script from the project root directory"
    exit 1
fi

# Start backend server
echo ""
echo "Starting backend server on http://localhost:8000"
cd backend
python main.py &
BACKEND_PID=$!

# Wait a bit for backend to start
sleep 3

# Start frontend server
echo ""
echo "Starting frontend server on http://localhost:8080"
cd ../frontend
python -m http.server 8080 &
FRONTEND_PID=$!

echo ""
echo "=================================="
echo "✅ Aesop AI is running!"
echo "=================================="
echo ""
echo "Backend:  http://localhost:8000"
echo "Frontend: http://localhost:8080/record.html"
echo ""
echo "Press Ctrl+C to stop both servers"
echo "=================================="

# Wait for Ctrl+C
trap "echo ''; echo 'Stopping servers...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# Keep script running
wait

