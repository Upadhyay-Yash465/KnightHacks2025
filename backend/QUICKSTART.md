# Quick Start Guide

Get the Public Speaking Coach backend running in 5 minutes!

## 🚀 Prerequisites

- Python 3.11+
- Firebase account with a project
- pip (Python package manager)

## 📦 Step 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## 🔑 Step 2: Firebase Setup

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Create a new project or select existing one
3. Go to Project Settings → Service Accounts
4. Click "Generate New Private Key"
5. Save the downloaded JSON file as `firebase-key.json` in the `backend/` directory
6. Note your Firebase Storage bucket name (found in Storage section)

## ⚙️ Step 3: Configure Environment

```bash
cp env.example .env
```

Edit `.env` and set:
- `FIREBASE_STORAGE_BUCKET` to your Firebase Storage bucket name
- Keep other settings as defaults for now

## 🎤 Step 4: Start the Server

```bash
python main.py
```

Or use the start script:
```bash
./start.sh
```

The server will start on `http://localhost:8000`

## 🧪 Step 5: Test the API

In a new terminal:

```bash
python test_api.py
```

Or manually test with curl:

```bash
# Analyze text
curl -X POST "http://localhost:8000/analyze-text" \
  -H "Content-Type: application/json" \
  -d '{
    "transcript": "Um, so I think this is great!",
    "user_id": "test_user"
  }'
```

## 📱 Expected Response

```json
{
  "transcript": "Um, so I think this is great!",
  "filler_count": 2,
  "clarity_score": 8.5,
  "suggestions": ["Consider pausing instead of using filler words..."],
  "summary": "Good speech clarity with some room for improvement...",
  "firestore_id": "abc123..."
}
```

## 🐳 Docker Alternative

If you prefer Docker:

```bash
docker-compose up
```

## 🔍 Verify Installation

Visit http://localhost:8000 in your browser to see the API documentation.

## ❓ Troubleshooting

### Error: "No module named 'faster_whisper'"
```bash
pip install faster-whisper
```

### Error: "firebase-key.json not found"
- Make sure you downloaded the Firebase service account key
- Verify it's named exactly `firebase-key.json`
- Check it's in the `backend/` directory

### Error: "No transcript generated"
- Try a longer audio file (> 3 seconds)
- Ensure audio format is supported (wav, mp3, m4a, flac)
- Check that the audio is audible and clear

## 🎯 Next Steps

- Explore the API docs at http://localhost:8000/docs
- Test audio upload with `/analyze` endpoint
- View analysis history with `/history/{user_id}`
- Integrate with your frontend!

