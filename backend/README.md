# Public Speaking Coach - Backend API

A FastAPI backend for the Public Speaking Coach application, powered by AMD Cloud Agents, Google ADK, SYSTRAN Faster-Whisper, and Firebase.

## 🚀 Features

- **Audio Transcription**: Uses SYSTRAN Faster-Whisper for fast, accurate speech-to-text
- **NLP Analysis**: Google ADK-powered analysis for speech clarity, filler detection, and improvement suggestions
- **AMD Cloud Agents**: Orchestrates AI analysis via AMD Cloud Agents framework
- **Firebase Integration**: Stores transcripts and analysis results in Firestore, uploads audio to Firebase Storage
- **RESTful API**: Clean FastAPI endpoints for frontend integration

## 📁 Project Structure

```
backend/
├── main.py                          # FastAPI application entry point
├── amd.yaml                         # AMD Cloud Agent configuration
├── requirements.txt                 # Python dependencies
├── .env.example                     # Environment variables template
├── services/
│   ├── systran_whisper_service.py  # Faster-Whisper transcription service
│   └── nlp_adk_service.py          # (Future) Google ADK service
├── agent/
│   ├── main_agent.py               # AMD Cloud Agent implementation
│   └── tools/
│       └── adk_nlp_tool.py         # Google ADK NLP analysis tool
└── utils/
    └── firebase_utils.py           # Firebase operations (Firestore & Storage)
```

## 🛠️ Setup

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Firebase

1. Download your Firebase service account key and save it as `firebase-key.json` in the `backend/` directory
2. Update `.env` with your Firebase Storage bucket name

### 3. Configure Environment Variables

```bash
cp .env.example .env
# Edit .env with your configuration
```

### 4. Run the Server

```bash
python main.py
# Or with uvicorn directly:
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 📡 API Endpoints

### `GET /`
Health check and API information

### `POST /upload`
Upload audio file to Firebase Storage
- **Input**: Multipart file upload
- **Returns**: Firebase URL

### `POST /analyze`
Full analysis workflow: transcribe → analyze → save
- **Input**: Audio file + user_id (optional)
- **Returns**: Transcript + filler count + clarity score + suggestions + summary

### `POST /analyze-text`
Analyze text directly without audio
- **Input**: JSON with transcript and user_id
- **Returns**: Analysis results

### `GET /history/{user_id}`
Get analysis history for a user
- **Parameters**: user_id, limit (optional)
- **Returns**: List of historical analysis records

### `GET /health`
Health check endpoint

## 🔧 Configuration

### Whisper Model Options

Set `WHISPER_MODEL_SIZE` in `.env`:
- `tiny` - Fastest, least accurate
- `base` - Good balance (default)
- `small` - Better accuracy
- `medium` - High accuracy
- `large` - Best accuracy, slowest

### Device Configuration

Set `WHISPER_DEVICE` in `.env`:
- `cpu` - Default, works everywhere
- `cuda` - For GPU acceleration (if available)

## 🚢 Deployment to Google Cloud Run

### 1. Build Docker Image

```bash
docker build -t public-speaking-coach-backend .
```

### 2. Deploy to Cloud Run

```bash
gcloud run deploy public-speaking-coach-backend \
  --image gcr.io/YOUR_PROJECT/public-speaking-coach-backend \
  --platform managed \
  --region us-central1 \
  --allow-unauthenticated \
  --memory 4Gi \
  --cpu 2 \
  --timeout 300
```

### 3. Set Environment Variables

```bash
gcloud run services update public-speaking-coach-backend \
  --set-env-vars WHISPER_MODEL_SIZE=base,FIREBASE_STORAGE_BUCKET=your-bucket
```

## 🧪 Testing

### Test with curl

```bash
# Analyze audio file
curl -X POST "http://localhost:8000/analyze" \
  -F "file=@audio_sample.wav" \
  -F "user_id=test_user"

# Analyze text
curl -X POST "http://localhost:8000/analyze-text" \
  -H "Content-Type: application/json" \
  -d '{"transcript": "Um, so I think that, like, you know, this is great!", "user_id": "test_user"}'
```

## 📊 Response Format

```json
{
  "transcript": "Full transcribed text...",
  "filler_count": 3,
  "clarity_score": 8.5,
  "suggestions": [
    "Consider pausing instead of using filler words for better flow.",
    "Break down longer sentences for improved clarity."
  ],
  "summary": "Excellent speech clarity with minimal filler usage.",
  "firestore_id": "document-id-here"
}
```

## 🔐 Security Notes

- Configure CORS origins appropriately for production
- Use Firebase Security Rules to protect Firestore data
- Store Firebase credentials securely (never commit `firebase-key.json`)
- Use environment variables for all sensitive configuration

## 🤝 Contributing

This backend is part of the Public Speaking Coach application built for AMD KnightHacks.

## 📝 License

Proprietary - AMD KnightHacks Project

