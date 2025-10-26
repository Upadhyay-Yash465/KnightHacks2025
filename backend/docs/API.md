# API Documentation

## Overview

The AI Speech Coach Backend provides a RESTful API for multimodal speech analysis using AI-powered agents.

## Base URL

```
http://localhost:8080
```

## Endpoints

### Health Check

**GET** `/`

Returns the API status and health information.

**Response:**
```json
{
  "status": "✅ API is live",
  "message": "AI Speech Coach backend running."
}
```

### Analyze Speech

**POST** `/analyze`

Accepts audio and/or video files for comprehensive speech analysis.

**Parameters:**
- `audio` (file, optional): Audio file (WAV, MP3, etc.)
- `video` (file, optional): Video file (MP4, AVI, etc.)

**Note:** At least one file (audio or video) must be provided.

**Response:**
```json
{
  "text_analysis": {
    "transcript": "string",
    "word_count": 0,
    "clarity_score": 0.0,
    "grammar_score": 0.0,
    "structure_score": 0.0,
    "filler_words": 0,
    "text_summary": "string",
    "suggestions": []
  },
  "audio_analysis": {
    "prosody": {
      "score": 0.0,
      "analysis": "string"
    },
    "tone": {
      "score": 0.0,
      "analysis": "string"
    },
    "pitch": {
      "score": 0.0,
      "analysis": "string"
    },
    "pace": {
      "score": 0.0,
      "analysis": "string"
    },
    "volume": {
      "score": 0.0,
      "analysis": "string"
    }
  },
  "visual_analysis": {
    "facial_landmarks": {
      "detected": false,
      "analysis": "string"
    },
    "gestures": {
      "detected": false,
      "analysis": "string"
    },
    "eye_contact": {
      "percentage": 0.0,
      "analysis": "string"
    },
    "confidence": {
      "score": 0.0,
      "analysis": "string"
    }
  },
  "summary": {
    "overall_score": 0.0,
    "text_score": 0.0,
    "audio_score": 0.0,
    "visual_score": 0.0,
    "summary": "string"
  },
  "execution_time_sec": 0.0
}
```

## Error Responses

### 400 Bad Request
```json
{
  "detail": "No audio or video file provided"
}
```

### 500 Internal Server Error
```json
{
  "detail": "Analysis failed: [error message]"
}
```

## Example Usage

### cURL
```bash
# Health check
curl http://localhost:8080/

# Analyze audio file
curl -X POST -F "audio=@speech.wav" http://localhost:8080/analyze

# Analyze video file
curl -X POST -F "video=@speech.mp4" http://localhost:8080/analyze

# Analyze both audio and video
curl -X POST -F "audio=@speech.wav" -F "video=@speech.mp4" http://localhost:8080/analyze
```

### Python
```python
import requests

# Health check
response = requests.get('http://localhost:8080/')
print(response.json())

# Analyze audio file
with open('speech.wav', 'rb') as f:
    files = {'audio': ('speech.wav', f, 'audio/wav')}
    response = requests.post('http://localhost:8080/analyze', files=files)
    result = response.json()
    print(f"Overall Score: {result['summary']['overall_score']}")
```

### JavaScript
```javascript
// Health check
fetch('http://localhost:8080/')
  .then(response => response.json())
  .then(data => console.log(data));

// Analyze audio file
const formData = new FormData();
formData.append('audio', audioFile);

fetch('http://localhost:8080/analyze', {
  method: 'POST',
  body: formData
})
.then(response => response.json())
.then(result => console.log('Overall Score:', result.summary.overall_score));
```

## Interactive Documentation

Visit `http://localhost:8080/docs` for interactive API documentation powered by Swagger UI.
