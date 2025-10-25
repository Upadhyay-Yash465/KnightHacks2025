#!/bin/bash

# Start script for Public Speaking Coach
# Starts both backend and frontend

echo "🚀 Starting Public Speaking Coach..."

# Check if backend is running
if ! curl -s http://localhost:8000/health > /dev/null; then
    echo "📡 Starting backend..."
    cd backend
    python3 main.py &
    BACKEND_PID=$!
    cd ..
    sleep 3
else
    echo "✅ Backend already running"
fi

# Check if frontend exists
if [ -d "frontend" ]; then
    echo "🎨 Starting frontend..."
    cd frontend
    
    # Install dependencies if needed
    if [ ! -d "node_modules" ]; then
        echo "📦 Installing frontend dependencies..."
        npm install
    fi
    
    npm run dev &
    FRONTEND_PID=$!
    cd ..
    
    echo ""
    echo "✅ Public Speaking Coach is running!"
    echo ""
    echo "🌐 Frontend: http://localhost:3000"
    echo "📡 Backend:  http://localhost:8000"
    echo ""
    echo "Press Ctrl+C to stop both servers"
    
    # Wait for interrupt
    wait $BACKEND_PID $FRONTEND_PID
else
    echo "⚠️  Frontend directory not found"
    echo "📡 Backend is running at http://localhost:8000"
fi

