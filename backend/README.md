# Aesop AI Backend

Simple, efficient backend for AI-powered public speaking analysis.

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r ../requirements.txt
   ```

2. **Set up environment variables:**
   ```bash
   cp .env.example .env
   # Edit .env and add your GEMINI_API_KEY
   ```

3. **Install ffmpeg (required for audio extraction):**
   - macOS: `brew install ffmpeg`
   - Ubuntu: `sudo apt-get install ffmpeg`
   - Windows: Download from https://ffmpeg.org/

## Running the Server

```bash
cd backend
python main.py
```

The server will start on `http://localhost:8000`

## API Endpoints

### POST /analyze
Analyzes a video and returns transcription, voice, and emotion analysis.

**Request:**
- `video`: Video file (multipart/form-data)
- `context`: Optional speech context (string)

**Response:**
```json
{
  "transcription": {
    "text": "...",
    "quality_score": 7.5
  },
  "voice": {
    "pitch": 8.2,
    "volume": 7.8,
    "speed": 7.9,
    "prosody": 8.5
  },
  "emotions": {
    "timeline": [...],
    "overall_rating": 8.4
  }
}
```

### POST /actionable-advice
Generates specific advice based on analysis results.

**Request:**
```json
{
  "agent_type": "transcriber|voice|emotion",
  "analysis_data": {...},
  "context": "optional context"
}
```

**Response:**
```json
{
  "advice": "Detailed actionable advice..."
}
```

## Architecture

- **Data Agents (DA):** Analyze speech quality
  - `transcriber.py`: Speech-to-text + quality scoring
  - `voice_analyzer.py`: Pitch, volume, speed, prosody analysis
  - `emotion_analyzer.py`: Facial emotion tracking
  
- **Action Agent (AA):** Generates improvement advice
  - `action_agent.py`: Personalized coaching based on DA results

- **Utilities:**
  - `video_utils.py`: Video/audio processing

## Notes

- First run downloads Whisper model (~150MB)
- Uses CPU by default (AMD-friendly)
- Temporary files are cleaned up automatically

