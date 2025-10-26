"""
nlp_service.py
Provides text-level language analysis and clarity scoring using Gemini or OpenAI.
"""

import os
import json
import logging
import openai
import google.generativeai as genai


class NLPService:
    def __init__(self,
                 primary_model="gemini-2.5-flash",
                 fallback_model="gpt-4-turbo"):
        self.primary_model = primary_model
        self.fallback_model = fallback_model
        self.google_api_key = os.getenv("GOOGLE_API_KEY")
        self.openai_key = os.getenv("OPENAI_API_KEY")

        if self.google_api_key:
            genai.configure(api_key=self.google_api_key)
        if self.openai_key:
            self.openai_client = openai.OpenAI(api_key=self.openai_key)

    def analyze_text(self, transcript: str) -> dict:
        """Run clarity and filler-word detection."""
        if not transcript.strip():
            return {"error": "Empty transcript"}

        try:
            return self._analyze_with_gemini(transcript)
        except Exception as e:
            logging.error(f"⚠️ Gemini NLP failed: {e}")
            return self._analyze_with_openai(transcript)

    def _analyze_with_gemini(self, transcript):
        model = genai.GenerativeModel(self.primary_model)
        prompt = (
            "Analyze this transcript for filler words, clarity, and structure. "
            "Return valid JSON with fields: clarity_score, filler_words, feedback."
            f"\nTranscript:\n{transcript}"
        )
        response = model.generate_content(prompt)
        text = response.text.strip()
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            return {"feedback": text}

    def _analyze_with_openai(self, transcript):
        prompt = (
            "You are an expert speaking coach. Analyze filler words and clarity. "
            "Return JSON: clarity_score, filler_words, feedback.\n\n"
            f"{transcript}"
        )
        response = self.openai_client.chat.completions.create(
            model=self.fallback_model,
            messages=[{"role": "system", "content": prompt}],
            temperature=0.3
        )
        content = response.choices[0].message.content.strip()
        try:
            return json.loads(content)
        except Exception:
            return {"feedback": content}
