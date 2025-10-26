# Testing Aesop AI

This guide will help you test the complete system after setup.

## Pre-Testing Checklist

1. ✅ Dependencies installed: `pip install -r requirements.txt`
2. ✅ FFmpeg installed: `ffmpeg -version` works
3. ✅ Gemini API key configured in `backend/.env`
4. ✅ Backend running: `python backend/main.py`
5. ✅ Frontend accessible: Open `frontend/record.html`

## Quick Test Procedure

### Test 1: Backend Health Check

```bash
curl http://localhost:8000/health
```

Expected response:
```json
{"status": "healthy", "message": "Aesop AI Backend is running"}
```

### Test 2: Record a Test Speech

1. Open `http://localhost:8080/record.html` (or open file directly)
2. Allow camera and microphone access
3. Click "Start Recording"
4. Speak for 10-15 seconds (test speech):
   ```
   "Hello everyone. Today I want to talk about the importance of clear 
   communication. When we speak clearly and confidently, our message 
   resonates with our audience. Let's make every word count."
   ```
5. Click "Stop Recording"
6. The video should appear in the playback area

### Test 3: Add Context (Optional)

In the context box, enter something like:
```
This is a practice speech about communication skills for a business presentation.
```

### Test 4: Upload and Analyze

1. Click "Upload and Get Feedback"
2. You should see the "Analyzing Your Speech" spinner
3. Wait 30-60 seconds (first run downloads Whisper model)
4. Results should appear in three sections:
   - **Transcription**: Your speech text
   - **Audio Analysis**: Scores for prosody, tone, pitch, speed
   - **Visual Analysis**: Emotion timeline graph

### Test 5: Get Actionable Advice

For each section, click "Get Actionable Advice":

1. **Transcription Advice**: Should provide a rewritten version of your speech
2. **Voice Advice**: Should suggest vocal exercises
3. **Emotion Advice**: Should suggest facial expression exercises

## Troubleshooting

### Backend Won't Start

```bash
cd backend
python test_setup.py
```

This will diagnose setup issues.

### Video Upload Fails

- Check browser console (F12) for errors
- Verify backend is running on port 8000
- Check CORS is enabled (should be by default)

### Analysis Takes Too Long

- First run: Normal (downloading Whisper model ~150MB)
- Subsequent runs: Should take 20-60 seconds depending on video length
- Check terminal for progress messages

### Emotion Analysis Fails

- Verify `GEMINI_API_KEY` is set correctly
- Check API key has quota remaining
- Ensure frames are being extracted (check terminal logs)

### Audio Extraction Fails

- Verify FFmpeg is installed: `ffmpeg -version`
- Check video file is valid (try playing it)
- Ensure video has audio track

## Expected Performance

- **Transcription**: ~5-10 seconds for 30s video
- **Voice Analysis**: ~3-5 seconds
- **Emotion Analysis**: ~10-20 seconds (depends on API latency)
- **Total Analysis Time**: 20-40 seconds for typical speech

## Test Videos

For consistent testing, use videos with:
- Clear audio
- Visible face
- 30-60 second duration
- Good lighting
- Frontal camera angle

## API Testing (Advanced)

### Test /analyze endpoint directly

```bash
curl -X POST http://localhost:8000/analyze \
  -F "video=@test_video.webm" \
  -F "context=Test speech about technology"
```

### Test /actionable-advice endpoint

```bash
curl -X POST http://localhost:8000/actionable-advice \
  -H "Content-Type: application/json" \
  -d '{
    "agent_type": "transcriber",
    "analysis_data": {...},
    "context": "business presentation"
  }'
```

## Success Criteria

✅ Backend starts without errors  
✅ Frontend loads and camera works  
✅ Video records successfully  
✅ Analysis completes in under 60 seconds  
✅ All three analysis sections populate  
✅ Actionable advice generates for all three types  
✅ Results are accurate and relevant  

## Common Issues

**Issue**: Camera not detected  
**Solution**: Check browser permissions, try different browser

**Issue**: Whisper model download fails  
**Solution**: Check internet connection, run `backend/test_setup.py`

**Issue**: Gemini API quota exceeded  
**Solution**: Wait for quota reset or use different API key

**Issue**: Memory errors  
**Solution**: Reduce video length, close other applications

## Next Steps

Once testing is complete:
- Test with various speech types (formal, casual, technical)
- Test with different video lengths
- Test edge cases (no audio, no face visible)
- Performance test with longer videos

## AMD Cloud Deployment

For AMD cloud deployment:
- Ensure CPU-only mode is configured (default)
- May need to install additional codecs for video processing
- Test thoroughly on target environment before production use

