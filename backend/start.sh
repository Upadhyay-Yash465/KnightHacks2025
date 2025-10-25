#!/bin/bash

# Quick start script for Public Speaking Coach Backend

echo "🚀 Starting Public Speaking Coach Backend..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "⚠️  .env file not found. Copying from env.example..."
    cp env.example .env
    echo "✅ Please edit .env with your configuration"
fi

# Check if Firebase key exists
if [ ! -f firebase-key.json ]; then
    echo "⚠️  firebase-key.json not found!"
    echo "Please download your Firebase service account key and save it as firebase-key.json"
    exit 1
fi

# Create uploads directory
mkdir -p uploads

# Run the server
echo "🎤 Starting FastAPI server..."
python main.py

