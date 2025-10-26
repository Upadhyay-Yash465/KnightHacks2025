# AI Speech Coach Backend

A clean, organized backend for AI-powered speech analysis with multimodal capabilities.

## Project Structure

```
ai-speech-coach-backend/
├── src/                          # Source code
│   ├── api/                      # API layer
│   │   ├── __init__.py
│   │   ├── main.py              # FastAPI application
│   │   └── routes.py            # API routes
│   ├── agents/                   # AI analysis agents
│   │   ├── __init__.py
│   │   ├── context_agent.py     # Text analysis
│   │   ├── gemini_voice_agent.py # Voice analysis
│   │   ├── multimodal_orchestrator.py # Main orchestrator
│   │   └── video_agent.py       # Video analysis
│   ├── services/                 # Core services
│   │   ├── __init__.py
│   │   ├── audio_service.py     # Audio processing
│   │   ├── nlp_service.py       # NLP processing
│   │   ├── vision_service.py    # Video processing
│   │   └── whisper_service.py   # Speech transcription
│   ├── utils/                    # Utilities
│   │   ├── __init__.py
│   │   └── logger.py            # Logging utilities
│   └── config/                   # Configuration
│       ├── __init__.py
│       └── settings.py          # Environment settings
├── tests/                        # Test files
│   ├── __init__.py
│   ├── test_api.py
│   ├── test_agents.py
│   └── test_services.py
├── scripts/                      # Utility scripts
│   ├── setup_env.py
│   ├── server_manager.py
│   └── create_test_audio.py
├── docs/                         # Documentation
│   ├── README.md
│   ├── API.md
│   └── DEPLOYMENT.md
├── env/                          # Environment files
│   ├── .env.example
│   └── .env
├── requirements.txt              # Dependencies
└── main.py                       # Entry point
```

## Features

- **Multimodal Analysis**: Text, Audio, and Visual analysis
- **Real AI Integration**: Uses Gemini API for comprehensive analysis
- **Structured Output**: Returns organized JSON with scores and feedback
- **File Upload Support**: Handles audio and video file uploads
- **Error Handling**: Robust error handling and fallbacks

## Quick Start

1. Install dependencies: `pip install -r requirements.txt`
2. Set up environment: `python scripts/setup_env.py`
3. Run the server: `python main.py`

## API Endpoints

- `GET /` - Health check
- `POST /analyze` - Main analysis endpoint (accepts audio/video files)
