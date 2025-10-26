"""
Action Agent - Generates actionable advice based on analysis results using Gemini.
"""
import os
import json
import google.generativeai as genai
from typing import Dict, Any


class ActionAgent:
    """
    Generates specific, actionable advice based on Data Agent analysis.
    - Transcriber: Rewritten speech with improvements
    - Voice: Vocal exercises
    - Emotion: Facial/eye exercises
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini API for generating advice.
        """
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not provided")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def generate_advice(self, agent_type: str, analysis_data: Dict, context: str = "") -> Dict:
        """
        Generate actionable advice based on agent type and analysis.
        
        Args:
            agent_type: 'transcriber', 'voice', or 'emotion'
            analysis_data: Full analysis results from all agents
            context: User-provided speech context
        
        Returns:
            {"advice": str}
        """
        if agent_type == "transcriber":
            return self._generate_transcriber_advice(analysis_data, context)
        elif agent_type == "voice":
            return self._generate_voice_advice(analysis_data)
        elif agent_type == "emotion":
            return self._generate_emotion_advice(analysis_data)
        else:
            return {"advice": "Unknown agent type"}
    
    def _generate_transcriber_advice(self, analysis_data: Dict, context: str) -> Dict:
        """
        Generate improved speech rewrite based on transcription.
        """
        transcription = analysis_data.get('transcription', {})
        original_text = transcription.get('text', '')
        quality_score = transcription.get('quality_score', 0)
        
        prompt = f"""You are an expert speech coach. A speaker gave the following speech:

ORIGINAL SPEECH:
{original_text}

QUALITY SCORE: {quality_score}/10

SPEECH CONTEXT: {context if context else "General public speaking"}

Please provide:
1. A rewritten version of their speech that improves clarity, structure, and argumentation while maintaining their core message and intent.
2. 2-3 specific tips on what was changed and why.

Make the rewrite natural and conversational, not overly formal unless the context demands it."""

        try:
            response = self.model.generate_content(prompt)
            advice = response.text.strip()
            
            return {"advice": advice}
        except Exception as e:
            return {"advice": f"Error generating advice: {str(e)}"}
    
    def _generate_voice_advice(self, analysis_data: Dict) -> Dict:
        """
        Generate vocal exercises based on voice analysis.
        """
        voice = analysis_data.get('voice', {})
        pitch = voice.get('pitch', 5)
        volume = voice.get('volume', 5)
        speed = voice.get('speed', 5)
        prosody = voice.get('prosody', 5)
        
        prompt = f"""You are an expert voice coach. A speaker's voice has been analyzed with these scores (0-10 scale):

- Pitch Variation: {pitch}/10
- Volume Consistency: {volume}/10
- Speech Speed: {speed}/10
- Prosody (Intonation): {prosody}/10

Based on these scores, provide:
1. Identification of the 1-2 weakest areas
2. 3-4 specific vocal exercises to improve those areas
3. Practical tips they can apply immediately in their next speech

Be specific and actionable. Focus on exercises they can do daily."""

        try:
            response = self.model.generate_content(prompt)
            advice = response.text.strip()
            
            return {"advice": advice}
        except Exception as e:
            return {"advice": f"Error generating advice: {str(e)}"}
    
    def _generate_emotion_advice(self, analysis_data: Dict) -> Dict:
        """
        Generate facial expression exercises and breakdown based on emotion analysis.
        """
        emotions = analysis_data.get('emotions', {})
        timeline = emotions.get('timeline', [])
        overall_rating = emotions.get('overall_rating', 5)
        gesture_rating = emotions.get('gesture_rating', 5)
        
        # Analyze emotion patterns
        if timeline:
            dominant_emotions = [entry.get('dominant', 'Neutral') for entry in timeline]
            emotion_summary = ', '.join(dominant_emotions)
        else:
            emotion_summary = "No emotion data available"
        
        # Generate actionable advice
        advice_prompt = f"""You are an expert in nonverbal communication and facial expressions for public speaking.

A speaker's facial emotions throughout their speech showed this pattern:
{emotion_summary}

Overall Emotional Expression Rating: {overall_rating}/10
Gesture and Body Language Rating: {gesture_rating}/10

Based on this analysis, provide:
1. Assessment of their emotional expression (what's working, what needs work)
2. 3-4 specific exercises to improve facial expressions and eye contact
3. Tips for projecting appropriate emotions during speeches
4. Advice on maintaining engagement through facial cues

Be specific and practical. Include exercises they can practice in front of a mirror."""

        try:
            response = self.model.generate_content(advice_prompt)
            advice = response.text.strip()
            
            # Generate breakdown analysis
            breakdown = self._generate_emotion_breakdown(analysis_data)
            
            return {
                "advice": advice,
                "breakdown": breakdown
            }
        except Exception as e:
            return {"advice": f"Error generating advice: {str(e)}", "breakdown": {}}
    
    def _generate_emotion_breakdown(self, analysis_data: Dict) -> Dict:
        """
        Generate detailed breakdown of emotional expression analysis.
        """
        emotions = analysis_data.get('emotions', {})
        timeline = emotions.get('timeline', [])
        overall_rating = emotions.get('overall_rating', 5)
        gesture_rating = emotions.get('gesture_rating', 5)
        
        # Analyze emotion patterns
        if timeline:
            dominant_emotions = [entry.get('dominant', 'Neutral') for entry in timeline]
            emotion_counts = {}
            for emotion in dominant_emotions:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        else:
            emotion_counts = {}
        
        breakdown_prompt = f"""You are an expert in nonverbal communication for public speaking.

Analyze this speaker's performance:
- Overall Emotional Expression: {overall_rating}/10
- Gesture/Body Language: {gesture_rating}/10
- Emotion patterns: {emotion_counts}

Provide 4 brief analyses (2-3 sentences each) in this EXACT JSON format:
{{
  "emotional_range": "Analysis of their emotional variety and transitions",
  "gesture_effectiveness": "Analysis of their hand gestures and body language",
  "facial_expressions": "Analysis of their facial expressions and eye contact",
  "overall_impact": "Overall assessment of their nonverbal communication impact"
}}

Be specific, constructive, and professional. Focus on what they did well and areas for improvement."""

        try:
            response = self.model.generate_content(breakdown_prompt)
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:].strip()
            
            breakdown = json.loads(response_text)
            
            return {
                "emotional_range": breakdown.get("emotional_range", "Analysis not available"),
                "gesture_effectiveness": breakdown.get("gesture_effectiveness", "Analysis not available"),
                "facial_expressions": breakdown.get("facial_expressions", "Analysis not available"),
                "overall_impact": breakdown.get("overall_impact", "Analysis not available")
            }
        except Exception as e:
            print(f"Error generating breakdown: {e}")
            return {
                "emotional_range": "Your emotional expression analysis is being processed.",
                "gesture_effectiveness": "Your gesture analysis is being processed.",
                "facial_expressions": "Your facial expression analysis is being processed.",
                "overall_impact": "Your overall impact analysis is being processed."
            }


