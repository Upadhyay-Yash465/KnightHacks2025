#!/usr/bin/env python3
"""
multimodal_orchestrator.py
Enhanced orchestrator for Text/Audio/Visual analysis with summary
"""

import logging
import json
import time
from concurrent.futures import ThreadPoolExecutor
import asyncio

from .gemini_voice_agent import GeminiVoiceAgent as VoiceAgent
from .context_agent import ContextAgent
from .video_agent import VideoAgent


class MultimodalOrchestrator:
    def __init__(self):
        """
        Initialize all analysis agents for comprehensive multimodal analysis.
        """
        self.voice = VoiceAgent()
        self.context = ContextAgent()
        self.video = VideoAgent()
        
        logging.info("🎯 Multimodal Orchestrator initialized")

    async def run(self, audio_path: str = None, video_path: str = None) -> dict:
        """
        Run comprehensive multimodal analysis and return structured results.
        """
        start = time.time()
        logging.info("🚀 Starting Multimodal Analysis Pipeline...")

        # Handle audio analysis if audio is provided
        voice_result = {}
        context_result = {}
        
        if audio_path:
            # Run VoiceAgent first (needed for transcript)
            voice_result = await self._safe_run(self.voice.analyze, audio_path, name="VoiceAgent")
            
            # Run Context analysis
            context_result = await self._safe_run(
                self.context.analyze, voice_result.get("transcript", ""), name="ContextAgent"
            )
        else:
            logging.info("📝 No audio provided - skipping text analysis")

        # Handle video analysis if video is provided
        video_result = {}
        if video_path:
            video_result = await self._safe_run(self.video.analyze, video_path, name="VideoAgent")
        else:
            logging.info("🎬 No video provided - skipping visual analysis")

        # Structure the results according to the whiteboard format
        structured_result = self._structure_results(voice_result, context_result, video_result, audio_path, video_path)
        structured_result["execution_time_sec"] = round(time.time() - start, 2)

        logging.info(f"✅ Multimodal analysis completed in {structured_result['execution_time_sec']}s.")
        return structured_result

    async def _safe_run(self, func, *args, name="Agent", retries=2):
        """Async runner with retry & thread safety."""
        for attempt in range(1, retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args)
                else:
                    loop = asyncio.get_running_loop()
                    with ThreadPoolExecutor() as pool:
                        return await loop.run_in_executor(pool, func, *args)
            except Exception as e:
                logging.warning(f"⚠️ {name} failed (Attempt {attempt}): {e}")
                await asyncio.sleep(0.3)
        logging.error(f"❌ {name} failed all attempts.")
        return {"error": f"{name} unavailable."}

    def _structure_results(self, voice_result: dict, context_result: dict, video_result: dict, audio_path: str = None, video_path: str = None) -> dict:
        """
        Structure results according to the whiteboard format:
        - Text Analysis
        - Audio Analysis  
        - Visual Analysis
        - Summary with scoring
        """
        
        # Extract transcript and text analysis
        transcript = voice_result.get("transcript", "") if voice_result else ""
        
        # TEXT ANALYSIS
        text_analysis = {
            "transcript": transcript,
            "word_count": len(transcript.split()) if transcript else 0,
            "clarity_score": self._extract_score(context_result.get("clarity_score", 0)) if context_result else 0,
            "grammar_score": self._extract_score(context_result.get("grammar_score", 0)) if context_result else 0,
            "structure_score": self._extract_score(context_result.get("structure_score", 0)) if context_result else 0,
            "filler_words": voice_result.get("filler_words", 0) if voice_result else 0,
            "text_summary": context_result.get("summary", "No text analysis available") if context_result else "No audio provided",
            "suggestions": context_result.get("suggestions", [])
        }

        # AUDIO ANALYSIS - Use new detailed analysis structure from voice agent
        detailed_analysis = voice_result.get("detailed_analysis", {}) if voice_result else {}
        audio_metrics = voice_result.get("audio_metrics", {}) if voice_result else {}
        
        # Extract specific analysis from new structure
        pitch_analysis = detailed_analysis.get("pitch_analysis", {})
        tone_analysis = detailed_analysis.get("tone_analysis", {})
        speed_analysis = detailed_analysis.get("speed_analysis", {})
        prosody_analysis = detailed_analysis.get("prosody_analysis", {})
        
        audio_analysis = {
            "prosody": {
                "score": prosody_analysis.get("score", 5),
                "analysis": prosody_analysis.get("explanation", "No prosody analysis available")
            },
            "tone": {
                "score": tone_analysis.get("score", 5),
                "analysis": tone_analysis.get("explanation", "No tone analysis available")
            },
            "pitch": {
                "score": pitch_analysis.get("score", 5),
                "analysis": pitch_analysis.get("explanation", "No pitch analysis available")
            },
            "pace": {
                "score": speed_analysis.get("score", 5),
                "analysis": speed_analysis.get("explanation", "No speed analysis available")
            },
            "volume": {
                "score": tone_analysis.get("score", 5),  # Volume is part of tone analysis
                "analysis": tone_analysis.get("explanation", "No volume analysis available")
            }
        }

        # VISUAL ANALYSIS (if video provided)
        has_video = video_result and "note" not in video_result
        visual_analysis = {
            "facial_landmarks": {
                "detected": video_result.get("emotion", "Neutral") != "Neutral" if has_video else False,
                "analysis": f"Emotion: {video_result.get('emotion', 'N/A')}" if has_video else "No video provided"
            },
            "gestures": {
                "detected": video_result.get("gesture_frequency", "None") != "None" if has_video else False,
                "analysis": f"Gesture frequency: {video_result.get('gesture_frequency', 'N/A')}" if has_video else "No video provided"
            },
            "eye_contact": {
                "percentage": video_result.get("eye_contact", 0) if has_video else 0,
                "analysis": f"Eye contact: {video_result.get('eye_contact', 0):.1f}%" if has_video else "No video provided"
            },
            "confidence": {
                "score": video_result.get("confidence_score", 0) if has_video else 0,
                "analysis": f"Confidence level: {video_result.get('confidence_score', 0):.1f}/10" if has_video else "No video provided"
            }
        }

        # CALCULATE OVERALL SCORES
        text_score = (text_analysis["clarity_score"] + text_analysis["grammar_score"] + text_analysis["structure_score"]) / 3 if audio_path else 0
        audio_score = (audio_analysis["prosody"]["score"] + audio_analysis["tone"]["score"] +
                     audio_analysis["pitch"]["score"] + audio_analysis["pace"]["score"] +
                     audio_analysis["volume"]["score"]) / 5 if audio_path else 0
        visual_score = visual_analysis["confidence"]["score"] if has_video else 0

        # SUMMARY WITH SCORING
        overall_score = 0
        if audio_path and video_path:
            overall_score = (text_score + audio_score + visual_score) / 3
        elif audio_path:
            overall_score = (text_score + audio_score) / 2
        elif video_path:
            overall_score = visual_score
        summary = {
            "overall_score": round(overall_score, 1),
            "text_score": round(text_score, 1),
            "audio_score": round(audio_score, 1),
            "visual_score": round(visual_score, 1),
            "breakdown": {
                "text_performance": f"{text_score:.1f}/10 - Text clarity and structure",
                "audio_performance": f"{audio_score:.1f}/10 - Voice quality and delivery",
                "visual_performance": f"{visual_score:.1f}/10 - Non-verbal communication"
            },
            "recommendations": self._generate_recommendations(text_score, audio_score, visual_score),
            "strengths": self._identify_strengths(text_score, audio_score, visual_score),
            "improvement_areas": self._identify_improvements(text_score, audio_score, visual_score)
        }

        return {
            "text_analysis": text_analysis,
            "audio_analysis": audio_analysis,
            "visual_analysis": visual_analysis,
            "summary": summary,
            "execution_time_sec": 0  # Will be set by caller
        }

    def _extract_score(self, score_value) -> float:
        """Extract numeric score from various formats."""
        if isinstance(score_value, (int, float)):
            return float(score_value)
        elif isinstance(score_value, str):
            # Try to extract number from strings like "8/10" or "8.5"
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', score_value)
            return float(match.group(1)) if match else 0.0
        return 0.0
    
    def _extract_score_from_text(self, score_text) -> float:
        """Extract numeric score from text like '8/10'."""
        if isinstance(score_text, (int, float)):
            return float(score_text)
        elif isinstance(score_text, str):
            import re
            match = re.search(r'(\d+(?:\.\d+)?)', score_text)
            return float(match.group(1)) if match else 5.0
        return 5.0

    def _calculate_prosody_score(self, metrics: dict) -> float:
        """Calculate prosody score based on tempo and rhythm."""
        tempo = metrics.get("tempo_bpm", 0)
        if tempo > 0:
            return min(10, max(1, tempo / 20))  # Normalize tempo to 1-10 scale
        return 5.0  # Default middle score

    def _calculate_tone_score(self, metrics: dict) -> float:
        """Calculate tone score based on pitch characteristics."""
        pitch = metrics.get("avg_pitch_hz", 0)
        if 80 <= pitch <= 300:  # Normal human speech range
            return 8.0
        elif pitch > 0:
            return 6.0
        return 5.0

    def _calculate_pitch_score(self, metrics: dict) -> float:
        """Calculate pitch score."""
        pitch = metrics.get("avg_pitch_hz", 0)
        if 100 <= pitch <= 250:  # Optimal range
            return 9.0
        elif 80 <= pitch <= 300:  # Acceptable range
            return 7.0
        elif pitch > 0:
            return 5.0
        return 3.0

    def _calculate_pace_score(self, metrics: dict) -> float:
        """Calculate pace score based on speaking rate."""
        wpm = metrics.get("speech_rate_wpm", 0)
        if 120 <= wpm <= 180:  # Optimal speaking rate
            return 9.0
        elif 100 <= wpm <= 200:  # Good range
            return 7.0
        elif wpm > 0:
            return 5.0
        return 3.0

    def _calculate_volume_score(self, metrics: dict) -> float:
        """Calculate volume score."""
        volume = metrics.get("avg_volume_rms", 0)
        if 0.1 <= volume <= 0.8:  # Good volume range
            return 8.0
        elif volume > 0.8:  # Too loud
            return 6.0
        elif volume > 0.01:  # Too quiet
            return 4.0
        return 2.0

    def _generate_recommendations(self, text_score: float, audio_score: float, visual_score: float) -> list:
        """Generate personalized recommendations based on scores."""
        recommendations = []
        
        if text_score < 6:
            recommendations.append("Focus on improving speech clarity and reducing filler words")
        if audio_score < 6:
            recommendations.append("Work on voice projection and speaking pace")
        if visual_score < 6:
            recommendations.append("Practice maintaining eye contact and confident body language")
        
        if not recommendations:
            recommendations.append("Continue practicing to maintain your excellent performance")
            
        return recommendations

    def _identify_strengths(self, text_score: float, audio_score: float, visual_score: float) -> list:
        """Identify areas of strength."""
        strengths = []
        
        if text_score >= 8:
            strengths.append("Excellent speech clarity and structure")
        if audio_score >= 8:
            strengths.append("Strong voice quality and delivery")
        if visual_score >= 8:
            strengths.append("Confident non-verbal communication")
            
        if not strengths:
            strengths.append("Good foundation for improvement")
            
        return strengths

    def _identify_improvements(self, text_score: float, audio_score: float, visual_score: float) -> list:
        """Identify areas needing improvement."""
        improvements = []
        
        if text_score < 7:
            improvements.append("Speech clarity and grammar")
        if audio_score < 7:
            improvements.append("Voice projection and pace")
        if visual_score < 7:
            improvements.append("Eye contact and gestures")
            
        return improvements
