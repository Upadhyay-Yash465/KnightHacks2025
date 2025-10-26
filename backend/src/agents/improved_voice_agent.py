#!/usr/bin/env python3
"""
improved_voice_agent.py
Improved VoiceAgent with better error handling and fallbacks
"""

import os
import logging
import librosa
import numpy as np
import openai
from faster_whisper import WhisperModel


class ImprovedVoiceAgent:
    def __init__(self, model_size="base", openai_model="gpt-3.5-turbo"):
        """
        Initialize Whisper + OpenAI models with better error handling.
        """
        self.model = WhisperModel(f"systran/faster-whisper-{model_size}")
        self.openai_model = openai_model
        self.openai_api_key = os.getenv("OPENAI_API_KEY")

    def analyze(self, audio_path: str) -> dict:
        """
        Full pipeline with better error handling and fallbacks.
        """
        logging.info("🎧 Running Improved VoiceAgent pipeline...")

        # Step 1: Try transcription
        transcript = self._transcribe_with_fallback(audio_path)
        
        # Step 2: Analyze audio metrics
        audio_metrics = self._analyze_audio(audio_path)
        
        # Step 3: Get NLP feedback (only if we have a transcript)
        if transcript and transcript.strip():
            nlp_feedback = self._get_nlp_feedback(transcript)
        else:
            nlp_feedback = {
                "clarity": "N/A - No speech detected",
                "filler_words": 0,
                "feedback": "Please upload an audio file with clear speech for analysis."
            }

        return {
            "transcript": transcript,
            "metrics": audio_metrics,
            "clarity": nlp_feedback.get("clarity", "N/A"),
            "filler_words": nlp_feedback.get("filler_words", 0),
            "feedback": nlp_feedback.get("feedback", "No feedback available.")
        }

    def _transcribe_with_fallback(self, audio_path: str) -> str:
        """
        Transcribe with multiple fallback strategies.
        """
        logging.info("🗣️ Transcribing speech...")
        
        try:
            # Try primary transcription
            segments, info = self.model.transcribe(audio_path)
            transcript = " ".join([s.text.strip() for s in segments])
            
            if transcript and transcript.strip():
                logging.info(f"✅ Transcription successful: '{transcript[:50]}...'")
                return transcript
            else:
                logging.warning("⚠️ Empty transcript - trying fallback analysis")
                return self._analyze_audio_content(audio_path)
                
        except Exception as e:
            logging.error(f"❌ Transcription failed: {e}")
            return self._analyze_audio_content(audio_path)

    def _analyze_audio_content(self, audio_path: str) -> str:
        """
        Analyze audio content to provide meaningful feedback even without transcription.
        """
        try:
            y, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            
            # Analyze audio characteristics
            rms = np.mean(librosa.feature.rms(y=y))
            spectral_centroid = np.mean(librosa.feature.spectral_centroid(y=y, sr=sr))
            
            # Provide feedback based on audio characteristics
            if duration < 1:
                return "Audio too short for analysis. Please record at least 1 second of speech."
            elif rms < 0.01:
                return "Audio volume too low. Please speak louder or check your microphone."
            elif spectral_centroid < 1000:
                return "Audio appears to be low-frequency content (music/tone). Please record speech instead."
            else:
                return "Audio detected but no clear speech recognized. Please speak clearly into the microphone."
                
        except Exception as e:
            logging.error(f"❌ Audio analysis failed: {e}")
            return "Unable to analyze audio file. Please check file format and try again."

    def _analyze_audio(self, audio_path: str) -> dict:
        """
        Analyze pace, pitch, volume using Librosa with better error handling.
        """
        logging.info("🎵 Extracting audio features...")
        
        try:
            y, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            pitch = np.mean(librosa.yin(y, fmin=80, fmax=300))
            rms = np.mean(librosa.feature.rms(y=y))
            speech_rate = self._estimate_wpm(y, sr, duration)

            return {
                "duration_sec": round(float(duration), 2),
                "tempo_bpm": round(float(tempo), 2),
                "avg_pitch_hz": round(float(pitch), 2),
                "avg_volume_rms": round(float(rms), 4),
                "speech_rate_wpm": speech_rate
            }
        except Exception as e:
            logging.error(f"❌ Audio analysis failed: {e}")
            return {
                "duration_sec": 0,
                "tempo_bpm": 0,
                "avg_pitch_hz": 0,
                "avg_volume_rms": 0,
                "speech_rate_wpm": 0
            }

    def _estimate_wpm(self, y, sr, duration):
        """
        Rough words-per-minute estimation from tempo and energy.
        """
        try:
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            tempo_value = float(tempo) if hasattr(tempo, '__iter__') else tempo
            return round((tempo_value * 10) / (duration / 60), 1) if duration > 0 else 0
        except Exception:
            return 0

    def _get_nlp_feedback(self, transcript: str) -> dict:
        """
        Get NLP feedback with better error handling.
        """
        if not self.openai_api_key:
            logging.warning("⚠️ OPENAI_API_KEY missing — using basic analysis.")
            return self._basic_text_analysis(transcript)

        logging.info("💬 Generating language feedback via GPT...")
        
        try:
            client = openai.OpenAI(api_key=self.openai_api_key)
            response = client.chat.completions.create(
                model=self.openai_model,
                messages=[{"role": "system", "content": self._get_analysis_prompt(transcript)}],
                temperature=0.3
            )
            content = response.choices[0].message.content.strip()

            # Parse response
            import json
            try:
                feedback_data = json.loads(content)
            except json.JSONDecodeError:
                feedback_data = {"feedback": content}

            return feedback_data
        except Exception as e:
            logging.error(f"GPT feedback error: {e}")
            return self._basic_text_analysis(transcript)

    def _get_analysis_prompt(self, transcript: str) -> str:
        """Get the analysis prompt for OpenAI."""
        return (
            "You are an expert public speaking coach. Analyze the following transcript "
            "for filler words (like 'um', 'uh', 'like'), clarity, and fluency. "
            "Return ONLY a JSON object with fields: filler_words (number), clarity (1-10), and feedback (string).\n\n"
            f"Transcript:\n{transcript}"
        )

    def _basic_text_analysis(self, transcript: str) -> dict:
        """
        Basic text analysis without OpenAI API.
        """
        words = transcript.lower().split()
        
        # Count filler words
        filler_words = ['um', 'uh', 'like', 'you know', 'so', 'well', 'actually']
        filler_count = sum(1 for word in words if word in filler_words)
        
        # Basic clarity score based on length and filler words
        word_count = len(words)
        if word_count == 0:
            clarity = 0
        else:
            filler_ratio = filler_count / word_count
            clarity = max(1, min(10, round(10 - (filler_ratio * 20))))
        
        # Generate basic feedback
        if clarity >= 8:
            feedback = "Excellent clarity and fluency!"
        elif clarity >= 6:
            feedback = "Good speech with minor improvements needed."
        elif clarity >= 4:
            feedback = "Speech needs improvement in clarity and flow."
        else:
            feedback = "Focus on reducing filler words and speaking more clearly."
        
        return {
            "filler_words": filler_count,
            "clarity": clarity,
            "feedback": feedback
        }
