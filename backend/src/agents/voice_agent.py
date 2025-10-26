"""
voice_agent.py
Advanced VoiceAgent — performs:
  • Speech transcription (Faster-Whisper)
  • Acoustic feature extraction (Librosa)
  • NLP clarity & filler analysis (Gemini 2.5 Flash → GPT fallback)
  • Context-aware coaching suggestions

Output JSON is frontend-ready for word highlighting and tooltips.
"""

import os
import json
import logging
import numpy as np
import librosa
from faster_whisper import WhisperModel
import openai
import google.generativeai as genai

from utils.logger import setup_logger
logger = setup_logger(__name__)


class VoiceAgent:
    """Central component for voice + transcript analysis."""

    def __init__(self,
                 whisper_model="base",
                 nlp_primary="gemini-2.5-flash",
                 nlp_fallback="gpt-4-turbo"):
        # === Whisper ===
        logger.info("🔧 Initializing Faster-Whisper model...")
        self.whisper = WhisperModel(f"systran/faster-whisper-{whisper_model}")

        # === NLP models ===
        self.primary_model = nlp_primary
        self.fallback_model = nlp_fallback
        self.google_api = os.getenv("GOOGLE_API_KEY")
        self.openai_api = os.getenv("OPENAI_API_KEY")

        if self.google_api:
            genai.configure(api_key=self.google_api)
        if self.openai_api:
            openai.api_key = self.openai_api

    # ------------------------------------------------------------------
    # Public entry point
    # ------------------------------------------------------------------
    def analyze(self, audio_path: str) -> dict:
        """Full pipeline for voice + transcript analysis."""
        logger.info("🎧 VoiceAgent: starting full analysis...")

        transcript = self._transcribe(audio_path)
        audio_metrics = self._analyze_audio(audio_path)
        nlp_feedback = self._analyze_text(transcript)

        # Enhance feedback with contextual filler suggestions
        enriched_feedback = self._contextualize_feedback(nlp_feedback)

        result = {
            "transcript": transcript,
            "metrics": audio_metrics,
            "clarity_score": enriched_feedback.get("clarity_score", "N/A"),
            "filler_words": enriched_feedback.get("filler_words", []),
            "suggestions": enriched_feedback.get("suggestions", []),
            "feedback": enriched_feedback.get("feedback", "Analysis complete.")
        }

        logger.info("✅ VoiceAgent: analysis finished successfully.")
        return result

    # ------------------------------------------------------------------
    # 1️⃣  Transcription
    # ------------------------------------------------------------------
    def _transcribe(self, audio_path: str) -> str:
        """Run SYSTRAN Faster-Whisper transcription."""
        try:
            logger.info("🗣️  Transcribing audio...")
            segments, _ = self.whisper.transcribe(audio_path)
            transcript = " ".join([s.text.strip() for s in segments])
            logger.info("✅ Transcription complete.")
            return transcript
        except Exception as e:
            logger.error(f"❌ Whisper transcription failed: {e}")
            return ""

    # ------------------------------------------------------------------
    # 2️⃣  Acoustic metrics
    # ------------------------------------------------------------------
    def _analyze_audio(self, audio_path: str) -> dict:
        """Analyze audio tempo, pitch, and loudness."""
        try:
            logger.info("🎵 Extracting acoustic metrics...")
            y, sr = librosa.load(audio_path, sr=None)
            duration = librosa.get_duration(y=y, sr=sr)
            tempo, _ = librosa.beat.beat_track(y=y, sr=sr)
            pitch = float(np.mean(librosa.yin(y, fmin=80, fmax=300)))
            rms = float(np.mean(librosa.feature.rms(y=y)))
            speech_rate = round((tempo * 10) / (duration / 60), 1) if duration else 0

            return {
                "duration_sec": round(duration, 2),
                "tempo_bpm": round(tempo, 2),
                "avg_pitch_hz": round(pitch, 2),
                "avg_volume_rms": round(rms, 4),
                "speech_rate_wpm": speech_rate
            }
        except Exception as e:
            logger.error(f"❌ Audio analysis failed: {e}")
            return {"error": str(e)}

    # ------------------------------------------------------------------
    # 3️⃣  NLP analysis (Gemini 2.5 → GPT fallback)
    # ------------------------------------------------------------------
    def _analyze_text(self, transcript: str) -> dict:
        """Run NLP evaluation using Gemini 2.5 Flash (fallback GPT)."""
        if not transcript.strip():
            return {"error": "Empty transcript"}

        prompt = (
    "You are an expert speech coach. Analyze the transcript below and identify **all issues** "
    "affecting clarity, fluency, or filler-word overuse. "
    "List **each distinct issue separately** with its explanation and a fix suggestion. "
    "Return a JSON in this format:\n"
    "{"
    '"clarity_score": <1–10>, '
    '"filler_words": <count>, '
    '"issues": ['
    ' {"type": "Filler Word", "example": "uh", "suggestion": "Pause briefly instead"}, '
    ' {"type": "Grammar", "example": "He go", "suggestion": "He goes"} '
    '], '
    '"summary": "Overall clarity feedback."'
    "}\n\n"
    f"Transcript:\n{transcript}"
)


        # --- Gemini 2.5 Flash ---
        if self.google_api:
            try:
                model = genai.GenerativeModel(self.primary_model)
                response = model.generate_content(prompt)
                raw = response.text.strip()
                return json.loads(raw) if raw.startswith("{") else {"feedback": raw}
            except Exception as e:
                logger.warning(f"⚠️ Gemini NLP failed, switching to GPT: {e}")

        # --- GPT fallback ---
        try:
            response = openai.ChatCompletion.create(
                model=self.fallback_model,
                messages=[{"role": "system", "content": prompt}],
                temperature=0.3
            )
            raw = response.choices[0].message.content.strip()
            return json.loads(raw) if raw.startswith("{") else {"feedback": raw}
        except Exception as e:
            logger.error(f"❌ Both NLP models failed: {e}")
            return {"feedback": "NLP analysis unavailable."}

    # ------------------------------------------------------------------
    # 4️⃣  Contextual filler-word suggestions
    # ------------------------------------------------------------------
    def _contextualize_feedback(self, base_feedback: dict) -> dict:
        """Adds contextual coaching tips for detected filler words."""
        fillers = base_feedback.get("filler_words", [])
        tips = []

        for w in fillers:
            tip = self._context_tip(w)
            tips.append({"word": w, "suggestion": tip})

        base_feedback["suggestions"] = tips
        return base_feedback

    def _context_tip(self, word: str) -> str:
        """Context-aware coaching dictionary."""
        guide = {
            "like": "Use a brief pause instead of 'like' to sound more confident.",
            "you know": "Avoid 'you know' — it signals uncertainty.",
            "literally": "Reserve 'literally' for factual emphasis only.",
            "so": "Try starting directly; 'so' can weaken openings.",
            "um": "Replace 'um' with a pause — silence shows control.",
            "actually": "Remove 'actually' unless contrasting a misconception."
        }
        return guide.get(word.lower(), "Be concise for clarity and flow.")
