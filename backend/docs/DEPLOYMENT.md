# Deployment Guide

## Prerequisites

- Python 3.8-3.11 (required for MediaPipe compatibility)
- pip package manager
- Google API Key (for Gemini AI)
- OpenAI API Key (for OpenAI services)

## Local Development Setup

### 1. Clone and Navigate
```bash
cd ai-speech-coach-backend
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Environment Configuration
```bash
python scripts/setup_env.py
```

This will create `env/.env` with your API keys.

### 5. Run the Server
```bash
python main.py
```

The server will start on `http://localhost:8080`

## Production Deployment

### Using Docker

Create a `Dockerfile`:
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    libsndfile1 \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Expose port
EXPOSE 8080

# Run the application
CMD ["python", "main.py"]
```

Build and run:
```bash
docker build -t ai-speech-coach-backend .
docker run -p 8080:8080 --env-file env/.env ai-speech-coach-backend
```

### Using Gunicorn

Install Gunicorn:
```bash
pip install gunicorn
```

Run with Gunicorn:
```bash
gunicorn -w 4 -k uvicorn.workers.UvicornWorker src.api.main:app --bind 0.0.0.0:8080
```

### Environment Variables

Required environment variables:
```bash
GOOGLE_API_KEY=your_google_api_key
OPENAI_API_KEY=your_openai_api_key
LOG_LEVEL=INFO
```

## Monitoring and Logging

### Health Checks
- Endpoint: `GET /`
- Returns API status and health information

### Logs
- Application logs are written to stdout
- Use structured logging with colored output
- Log level can be controlled via `LOG_LEVEL` environment variable

### Performance Monitoring
- Execution time is included in analysis responses
- Monitor API response times and error rates

## Scaling Considerations

### Horizontal Scaling
- Stateless design allows for easy horizontal scaling
- Use load balancer to distribute requests
- Consider Redis for session management if needed

### Resource Requirements
- **CPU**: Moderate (AI processing is CPU-intensive)
- **Memory**: 2-4GB minimum (AI models require significant RAM)
- **Storage**: Minimal (temporary files are cleaned up)

### API Rate Limits
- Google Gemini API has rate limits
- OpenAI API has rate limits
- Implement rate limiting middleware if needed

## Security Considerations

### API Security
- Use HTTPS in production
- Implement API key authentication
- Add request rate limiting
- Validate file uploads (size, type, content)

### CORS Configuration
Update CORS settings in `src/api/main.py`:
```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://your-frontend-domain.com"],  # Replace with actual domain
    allow_credentials=True,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)
```

### File Upload Security
- Validate file types and sizes
- Scan uploaded files for malware
- Use temporary storage with automatic cleanup
- Implement file size limits

## Troubleshooting

### Common Issues

1. **MediaPipe Import Error**
   - Ensure Python version is 3.8-3.11
   - Reinstall MediaPipe: `pip uninstall mediapipe && pip install mediapipe`

2. **API Key Errors**
   - Verify API keys are set correctly in `env/.env`
   - Check API key permissions and quotas

3. **Port Already in Use**
   - Kill existing processes: `lsof -ti:8080 | xargs kill -9`
   - Use different port: `uvicorn.run(..., port=8081)`

4. **Memory Issues**
   - Increase system memory
   - Use smaller AI models
   - Implement request queuing

### Debug Mode
Run with debug logging:
```bash
LOG_LEVEL=DEBUG python main.py
```

### Testing
Run the test suite:
```bash
python test_reorganized.py
```
