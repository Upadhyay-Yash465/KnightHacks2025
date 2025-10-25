# Frontend-Backend Integration Guide

## 🎯 Quick Start

### 1. Backend Setup
```bash
cd backend
python main.py
```
Backend runs on: `http://localhost:8000`

### 2. Frontend Setup
```bash
cd frontend
npm install
npm run dev
```
Frontend runs on: `http://localhost:3000`

## 🔗 API Integration

### Endpoints Used by Frontend

| Frontend Method | Backend Endpoint | Purpose |
|----------------|------------------|---------|
| `POST /analyze` | `POST /analyze` | Upload audio and get analysis |
| `POST /analyze-text` | `POST /analyze-text` | Analyze text directly |
| `GET /history/:id` | `GET /history/{user_id}` | Get user history |

### API Response Format

The frontend expects this response from `/analyze`:

```json
{
  "transcript": "Full transcribed text...",
  "filler_count": 3,
  "clarity_score": 8.5,
  "suggestions": [
    "Consider pausing instead of using filler words..."
  ],
  "summary": "Good speech clarity...",
  "firestore_id": "doc-id"
}
```

## 🚀 Running Both Together

### Option 1: Separate Terminals
```bash
# Terminal 1 - Backend
cd backend
python main.py

# Terminal 2 - Frontend
cd frontend
npm run dev
```

### Option 2: Concurrent (requires npm install -g concurrently)
```bash
npm install -g concurrently
concurrently "cd backend && python main.py" "cd frontend && npm run dev"
```

## 📁 File Structure

```
amd-knighthacks/
├── backend/                 # FastAPI backend
│   ├── main.py            # API endpoints
│   ├── agent/             # AMD Cloud Agent
│   ├── services/          # Transcription service
│   └── utils/             # Firebase utilities
│
└── frontend/              # React frontend
    ├── src/
    │   ├── components/
    │   │   └── Recorder.jsx      # Audio recording
    │   └── pages/
    │       ├── Home.jsx           # Landing page
    │       ├── Record.jsx          # Recording page
    │       └── Report.jsx          # Results page
    └── vite.config.js
```

## 🔧 Configuration

### Backend CORS
Already configured in `backend/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

### Frontend API URL
Set in `frontend/.env`:
```
VITE_API_BASE_URL=http://localhost:8000
```

Change to production URL when deploying:
```
VITE_API_BASE_URL=https://your-cloud-run-url.run.app
```

## 🧪 Testing Integration

### 1. Test Backend API
```bash
cd backend
python test_api.py
```

### 2. Test Frontend
1. Start both servers
2. Open http://localhost:3000
3. Record audio
4. Check backend logs for upload

## 📊 Data Flow

```
Frontend (React)
    ↓
Recorder Component
    ↓
POST /analyze with audio file
    ↓
Backend (FastAPI)
    ↓
SYSTRAN Faster-Whisper (transcription)
    ↓
AMD Cloud Agent + Google ADK (analysis)
    ↓
Firebase Firestore (storage)
    ↓
JSON Response
    ↓
Frontend Report Component
```

## 🐛 Troubleshooting

### CORS Errors
- Ensure backend CORS allows `http://localhost:3000`
- Check browser console for specific errors

### Audio Upload Fails
- Check backend logs
- Verify Firebase credentials
- Ensure audio format is supported (webm, wav, mp3)

### Build Issues
```bash
cd frontend
rm -rf node_modules package-lock.json
npm install
npm run dev
```

## 🚢 Deployment

### Backend to Google Cloud Run
```bash
cd backend
gcloud run deploy public-speaking-coach-backend \
  --source . \
  --platform managed \
  --region us-central1
```

### Frontend to Vercel/Netlify
```bash
cd frontend
npm run build
# Deploy dist/ folder
```

Update `VITE_API_BASE_URL` to production backend URL.

## 📝 Environment Variables

### Backend (.env)
```
FIREBASE_KEY_PATH=firebase-key.json
FIREBASE_STORAGE_BUCKET=your-project.appspot.com
WHISPER_MODEL_SIZE=base
WHISPER_DEVICE=cpu
```

### Frontend (.env)
```
VITE_API_BASE_URL=http://localhost:8000
```

