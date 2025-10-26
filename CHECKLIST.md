# Aesop AI - Pre-Launch Checklist

## Before First Run

### System Requirements
- [ ] Python 3.8+ installed (`python --version`)
- [ ] pip installed (`pip --version`)
- [ ] FFmpeg installed (`ffmpeg -version`)
- [ ] Modern browser (Chrome, Firefox, Edge, Safari)
- [ ] Webcam and microphone available

### Dependencies
- [ ] Run: `pip install -r requirements.txt`
- [ ] All packages installed without errors
- [ ] No version conflicts

### API Configuration
- [ ] Gemini API key obtained from https://makersuite.google.com/app/apikey
- [ ] Run: `cd backend && python setup.py`
- [ ] `.env` file created in `backend/` directory
- [ ] API key correctly set in `.env`

### Verification
- [ ] Run: `cd backend && python test_setup.py`
- [ ] All tests pass (imports, env, ffmpeg)
- [ ] No error messages

---

## First Launch

### Start Backend
- [ ] Open terminal/command prompt
- [ ] Navigate to project directory
- [ ] Run: `cd backend && python main.py`
- [ ] See "Uvicorn running on http://0.0.0.0:8000"
- [ ] No error messages in terminal
- [ ] Test: Open http://localhost:8000/health in browser
- [ ] See: `{"status": "healthy"}`

### Start Frontend
- [ ] Open second terminal/command prompt
- [ ] Navigate to project directory
- [ ] Run: `cd frontend && python -m http.server 8080`
- [ ] See "Serving HTTP on..."
- [ ] Open http://localhost:8080/record.html
- [ ] Page loads without errors

### Test Recording
- [ ] Click "Allow" for camera/microphone permissions
- [ ] See live video preview
- [ ] Click "Start Recording"
- [ ] See red recording indicator
- [ ] Click "Stop Recording"
- [ ] See recorded video playback
- [ ] Context input box appears

---

## First Analysis

### Upload Video
- [ ] Enter test context: "Practice presentation"
- [ ] Click "Upload and Get Feedback"
- [ ] See "Analyzing Your Speech" spinner
- [ ] Wait 30-60 seconds (first run downloads model)
- [ ] Backend terminal shows progress messages

### Check Results
- [ ] Transcription section populates with text
- [ ] Audio Analysis shows 4 scores (Prosody, Tone, Pitch, Speed)
- [ ] Visual Analysis shows emotion graph
- [ ] All scores are between 0-10
- [ ] No error messages

### Test Advice
- [ ] Click "Get Actionable Advice" on Transcription
- [ ] See advice popup with rewritten speech
- [ ] Click "Get Actionable Advice" on Audio Analysis  
- [ ] See vocal exercise recommendations
- [ ] Click "Get Actionable Advice" on Visual Analysis
- [ ] See facial expression tips

---

## Performance Check

### Expected Timings
- [ ] Backend startup: < 10 seconds
- [ ] First analysis: 30-60 seconds (includes model download)
- [ ] Subsequent analyses: 20-40 seconds
- [ ] Advice generation: 3-5 seconds each

### If Slower Than Expected
- [ ] Check internet connection (for Gemini API)
- [ ] Check CPU usage (should not max out)
- [ ] Try shorter video (15-20 seconds)
- [ ] Check terminal for error messages

---

## Troubleshooting Completed

If any issues occurred:
- [ ] Reviewed `TESTING.md` for solutions
- [ ] Checked all error messages in terminals
- [ ] Verified API key is correct
- [ ] Confirmed all dependencies installed
- [ ] Tried restarting backend/frontend
- [ ] Checked browser console (F12) for errors

---

## Ready for Demo

### Preparation
- [ ] Prepare 30-second test speech
- [ ] Good lighting setup
- [ ] Quiet environment
- [ ] Camera at eye level
- [ ] Test internet connection

### Demo Flow
- [ ] Start both servers
- [ ] Open frontend in browser
- [ ] Record practice speech
- [ ] Add meaningful context
- [ ] Upload and show analysis
- [ ] Request advice for each section
- [ ] Explain insights to audience

---

## Production Deployment (Optional)

If deploying to server:
- [ ] Set proper CORS origins in `backend/main.py`
- [ ] Use production ASGI server (Gunicorn + Uvicorn)
- [ ] Set up SSL/HTTPS
- [ ] Configure firewall rules
- [ ] Set up monitoring/logging
- [ ] Test on AMD cloud environment
- [ ] Perform load testing

---

## Documentation Review

- [ ] Read `README.md` - Project overview
- [ ] Read `QUICKSTART.md` - Fast setup
- [ ] Read `TESTING.md` - Comprehensive testing
- [ ] Read `IMPLEMENTATION_SUMMARY.md` - Technical details
- [ ] Read `backend/README.md` - API documentation

---

## Final Check

- [ ] Everything works end-to-end
- [ ] No console errors
- [ ] Results are accurate and helpful
- [ ] Performance is acceptable
- [ ] Ready to demo/present
- [ ] Backup plan if live demo fails (screenshots/video)

---

## Emergency Contacts

**If something goes wrong during demo:**
1. Have backup recorded demo video ready
2. Use screenshots of previous successful run
3. Explain architecture from `IMPLEMENTATION_SUMMARY.md`
4. Show code quality and documentation

---

**Status: Ready to Launch! 🚀**

Mark items as complete and you're good to go!

