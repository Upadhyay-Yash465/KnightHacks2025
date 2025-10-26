# Aesop AI - Public Speaking Coach

An AI-powered public speaking coach that provides real-time feedback on speech quality, voice characteristics, and emotional expression.

## Project Structure

```
KnightHacks2025/
├── backend/                # FastAPI backend
│   ├── main.py            # Main FastAPI application
│   ├── agents/            # Data and Action agents
│   │   ├── transcriber.py      # Speech transcription + quality
│   │   ├── voice_analyzer.py   # Voice metrics analysis
│   │   ├── emotion_analyzer.py # Facial emotion detection
│   │   └── action_agent.py     # Advice generation
│   ├── utils/             # Utilities
│   │   └── video_utils.py      # Video/audio processing
│   ├── setup.py           # Setup script
│   └── README.md          # Backend documentation
├── frontend/              # HTML/JS frontend
│   ├── index.html         # Entry point
│   ├── record.html        # Recording interface
│   ├── record-script.js   # Recording logic
│   └── styles.css         # Styles
└── requirements.txt       # Python dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install FFmpeg

- **macOS**: `brew install ffmpeg`
- **Ubuntu**: `sudo apt-get install ffmpeg`
- **Windows**: Download from https://ffmpeg.org/

### 3. Setup Backend

```bash
cd backend
python setup.py
```

This will prompt you for your Gemini API key. Get one from: https://makersuite.google.com/app/apikey

### 4. Run Backend Server

```bash
python main.py
```

Server runs on `http://localhost:8000`

### 5. Open Frontend

Open `frontend/record.html` in your browser, or use a local server:

```bash
cd frontend
python -m http.server 8080
```

Then visit `http://localhost:8080/record.html`

## Features

- **Transcription Analysis**: Converts speech to text and scores quality (0-10)
- **Voice Analysis**: Analyzes pitch, volume, speed, and prosody (0-10 each)
- **Emotion Analysis**: Tracks facial emotions throughout the speech
- **Actionable Advice**: Generates personalized coaching for each analysis type

## API Endpoints

- `POST /analyze` - Analyzes video and returns all metrics
- `POST /actionable-advice` - Generates specific improvement advice
- `GET /health` - Health check

## Tech Stack

- **Backend**: FastAPI, faster-whisper, librosa, OpenCV, Gemini API
- **Frontend**: Vanilla HTML/CSS/JavaScript
- **AI**: Google Gemini for emotion detection and advice generation

## Development Notes

- First run downloads Whisper model (~150MB)
- Uses CPU by default (AMD-friendly)
- Temporary files auto-cleaned after processing
- CORS enabled for local development
