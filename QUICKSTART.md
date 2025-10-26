# Aesop AI - Quick Start Guide

## 60-Second Setup

### 1. Install Dependencies (30 seconds)
```bash
pip install -r requirements.txt
brew install ffmpeg  # macOS (or apt-get install ffmpeg on Linux)
```

### 2. Configure API Key (15 seconds)
```bash
cd backend
python setup.py
# Enter your Gemini API key when prompted
# Get key from: https://makersuite.google.com/app/apikey
```

### 3. Start Everything (15 seconds)
```bash
cd ..
./start.sh  # or start.bat on Windows
```

That's it! Open http://localhost:8080/record.html

---

## Manual Start (If Scripts Don't Work)

### Terminal 1 - Backend:
```bash
cd backend
python main.py
```

### Terminal 2 - Frontend:
```bash
cd frontend
python -m http.server 8080
```

Open: http://localhost:8080/record.html

---

## First Use

1. **Allow camera/mic** when prompted
2. **Record a test speech** (15-30 seconds)
3. **Add context** (optional): "Practice presentation about technology"
4. **Click "Upload and Get Feedback"**
5. **Wait 30-60 seconds** (first run downloads AI model)
6. **View results** in 3 sections
7. **Click "Get Actionable Advice"** on any section

---

## Troubleshooting

### Backend won't start?
```bash
cd backend
python test_setup.py  # Diagnoses issues
```

### First analysis is slow?
- **Normal!** Downloads Whisper model (~150MB) once
- Subsequent analyses: 20-40 seconds

### Camera not working?
- Check browser permissions
- Try different browser
- Use Chrome/Edge for best compatibility

### API errors?
- Verify `GEMINI_API_KEY` in `backend/.env`
- Check API quota at https://makersuite.google.com

---

## What Each Part Does

### Frontend (record.html)
- Records video using your webcam
- Uploads to backend
- Displays analysis results
- Requests personalized advice

### Backend (/analyze)
- **Transcriber**: Speech → Text + Quality Score
- **Voice Analyzer**: Pitch, Volume, Speed, Prosody scores
- **Emotion Analyzer**: Facial expression timeline

### Backend (/actionable-advice)
- **Action Agent**: Generates personalized coaching

---

## File Locations

```
KnightHacks2025/
├── backend/
│   ├── main.py              ← Start here
│   ├── .env                 ← Your API key goes here
│   └── agents/              ← AI analysis code
├── frontend/
│   └── record.html          ← Open this in browser
├── start.sh / start.bat     ← One-click start
└── README.md                ← Full documentation
```

---

## Testing Commands

**Health check:**
```bash
curl http://localhost:8000/health
```

**API docs:**
Open http://localhost:8000/docs

---

## Common First-Time Issues

❌ **"Module not found"**  
✅ Run: `pip install -r requirements.txt`

❌ **"ffmpeg not found"**  
✅ Install: `brew install ffmpeg` (macOS) or `apt-get install ffmpeg` (Linux)

❌ **"GEMINI_API_KEY not found"**  
✅ Run: `cd backend && python setup.py`

❌ **"Connection refused"**  
✅ Make sure backend is running: `cd backend && python main.py`

---

## Need More Help?

- **Setup Issues**: Read `TESTING.md`
- **API Details**: Read `backend/README.md`
- **Complete Docs**: Read `README.md`
- **Implementation**: Read `IMPLEMENTATION_SUMMARY.md`

---

## Expected Results

**Good Setup:**
- Backend starts in ~5 seconds
- Frontend loads immediately  
- First analysis: 30-60 seconds
- Later analyses: 20-40 seconds
- All 3 feedback sections populate
- Advice generates in 3-5 seconds

**If something's different, check `TESTING.md`**

---

## Quick Commands Reference

```bash
# Setup
pip install -r requirements.txt
cd backend && python setup.py

# Start (Easy Way)
./start.sh

# Start (Manual)
cd backend && python main.py          # Terminal 1
cd frontend && python -m http.server 8080  # Terminal 2

# Test
cd backend && python test_setup.py    # Verify setup
curl http://localhost:8000/health     # Check backend

# Stop
Ctrl+C in both terminals
```

---

**You're ready to go! Record your first speech and see the magic happen! 🎤🎯**

