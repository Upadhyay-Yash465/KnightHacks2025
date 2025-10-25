"""
Orchestrator Agent - Main agent that coordinates all analysis components
"""
import sys
import os

# Add backend directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent.tools.voice_agent import analyze_voice
from agent.tools.transcript_agent import analyze_transcript_local
from agent.tools.body_agent import analyze_body
from services.systran_whisper_service import transcribe_audio
import json


class OrchestratorAgent:
    """
    Orchestrator Agent that manages:
    - Context (Gemini)
    - Voice (Transcriber, Suggestor, Pitch/Pace/Volume Analyzer with Librosa, Cross-checker with Gemini)
    - Video (Facial-emotion recognition with Cloud Vision API, Hand-gesture analyzer with MediaPipe)
    """
    
    def __init__(self):
        self.context_data = {}
        self.voice_results = {}
        self.video_results = {}
    
    def analyze(self, audio_path=None, video_path=None, transcript=None):
        """
        Main analysis function that orchestrates all components
        
        Args:
            audio_path: Path to audio file
            video_path: Path to video file  
            transcript: Pre-generated transcript (optional)
        
        Returns:
            dict: Complete analysis results
        """
        results = {
            "context": {},
            "voice": {},
            "video": {},
            "summary": {}
        }
        
        # Phase 1: Extract Transcript if not provided
        if not transcript and audio_path:
            print("📝 Transcribing audio...")
            transcript_data = transcribe_audio(audio_path)
            transcript = transcript_data.get("transcript", "")
            results["context"]["transcript"] = transcript
        
        # Phase 2: Voice Analysis Branch
        if audio_path:
            print("🎤 Analyzing voice...")
            results["voice"] = self._analyze_voice_branch(audio_path, transcript)
        
        # Phase 3: Video Analysis Branch  
        if video_path:
            print("🎥 Analyzing video...")
            results["video"] = self._analyze_video_branch(video_path)
        
        # Phase 4: Context Analysis with Gemini
        if transcript:
            print("🧠 Analyzing context with Gemini...")
            results["context"] = self._analyze_context_with_gemini(transcript)
        
        # Phase 5: Generate TTS Summary
        print("📊 Generating summary...")
        results["summary"] = self._generate_summary(results)
        
        return results
    
    def _analyze_voice_branch(self, audio_path, transcript):
        """
        Voice branch analysis includes:
        - Transcriber (already done)
        - Suggestor
        - Pitch, Pace, Volume Analyzer (Librosa)
        - Cross-checker (Gemini/Grammarly)
        """
        voice_results = {}
        
        # Pitch, Pace, Volume Analysis with Librosa
        try:
            voice_analysis = analyze_voice(audio_path)
            voice_results.update(voice_analysis)
        except Exception as e:
            print(f"Error in voice analysis: {e}")
            voice_results["error"] = str(e)
        
        # Cross-checker: Transcript analysis for suggestions
        if transcript:
            try:
                transcript_analysis = analyze_transcript_local(transcript)
                voice_results["transcript_analysis"] = transcript_analysis
            except Exception as e:
                print(f"Error in transcript analysis: {e}")
        
        return voice_results
    
    def _analyze_video_branch(self, video_path):
        """
        Video branch analysis includes:
        - Facial-emotion recognition (Cloud Vision API)
        - Hand-gesture analyzer (MediaPipe)
        """
        video_results = {}
        
        # Body language analysis (lightweight alternative to MediaPipe)
        try:
            body_analysis = analyze_body(video_path)
            video_results.update(body_analysis)
        except Exception as e:
            print(f"Error in body analysis: {e}")
            video_results["error"] = str(e)
        
        # TODO: Add Cloud Vision API for facial emotion recognition
        # TODO: Add MediaPipe for hand gesture analysis
        
        return video_results
    
    def _analyze_context_with_gemini(self, transcript):
        """
        Context analysis using Gemini
        """
        context_results = {
            "transcript": transcript,
            "word_count": len(transcript.split()),
            "estimated_duration": len(transcript.split()) / 2.5  # ~150 WPM average
        }
        
        # TODO: Add Gemini API calls for advanced context analysis
        # This would provide insights on content quality, structure, etc.
        
        return context_results
    
    def _generate_summary(self, all_results):
        """
        Generate final TTS Summary combining all analysis results
        """
        summary = {
            "overall_score": 0,
            "key_metrics": {},
            "strengths": [],
            "areas_for_improvement": [],
            "recommendations": []
        }
        
        # Calculate overall score from voice analysis
        if "voice" in all_results and all_results["voice"]:
            voice = all_results["voice"]
            
            # Extract metrics
            clarity_score = voice.get("transcript_analysis", {}).get("clarity_score", 8) if "transcript_analysis" in voice else 8
            duration_sec = voice.get("duration_sec", 30)
            volume_rms = voice.get("volume_rms", 0.02)
            
            # Calculate WPM from transcript
            transcript = all_results.get("context", {}).get("transcript", "")
            word_count = len(transcript.split()) if transcript else 0
            wpm = round((word_count / duration_sec * 60) if duration_sec > 0 else 140)
            
            # Normalize scores
            clarity_percent = min(100, clarity_score * 10)
            # WPM: ideal is 140-160, we'll score based on that
            pace_score = min(100, max(0, wpm))
            confidence_score = min(10, volume_rms * 500)
            
            summary["key_metrics"] = {
                "clarity": int(clarity_percent),
                "pace": int(wpm),  # Return actual WPM
                "confidence": round(confidence_score, 1)
            }
            
            # Calculate overall score (average of normalized metrics)
            clarity_weight = clarity_percent
            pace_weight = pace_score  # Direct WPM score
            confidence_weight = confidence_score * 10
            overall = (clarity_weight + pace_weight + confidence_weight) / 3
            summary["overall_score"] = int(overall)
            
            # Extract strengths
            if voice.get("emotion") == "confident":
                summary["strengths"].append("Confident and clear delivery")
            if volume_rms > 0.03:
                summary["strengths"].append("Strong vocal projection")
            if clarity_score >= 8:
                summary["strengths"].append("Clear pronunciation throughout")
            if 140 <= wpm <= 160:
                summary["strengths"].append("Optimal speaking pace")
            
            # Extract areas for improvement
            filler_count = voice.get("transcript_analysis", {}).get("filler_count", 0) if "transcript_analysis" in voice else 0
            if filler_count > 3:
                summary["areas_for_improvement"].append("Reduce filler words for clearer communication")
            if volume_rms < 0.02:
                summary["areas_for_improvement"].append("Increase vocal volume for better engagement")
            if wpm < 120:
                summary["areas_for_improvement"].append("Increase speaking pace for better engagement")
            elif wpm > 180:
                summary["areas_for_improvement"].append("Slow down slightly for clearer communication")
        
        # Add video analysis feedback
        if "video" in all_results and all_results["video"]:
            video = all_results["video"]
            body_feedback = video.get("body_feedback", "")
            
            if "Good" in body_feedback:
                summary["strengths"].append(body_feedback)
            else:
                summary["areas_for_improvement"].append(body_feedback)
        
        # Default values if no analysis
        if not summary["strengths"]:
            summary["strengths"] = ["Good overall presentation"]
        if not summary["areas_for_improvement"]:
            summary["areas_for_improvement"] = ["Continue practicing to improve"]
        
        return summary


def run_orchestrator(audio_path=None, video_path=None, transcript=None):
    """
    Convenience function to run the orchestrator agent
    """
    agent = OrchestratorAgent()
    return agent.analyze(audio_path=audio_path, video_path=video_path, transcript=transcript)

