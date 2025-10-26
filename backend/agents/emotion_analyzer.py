"""
Emotion Analyzer Agent - Uses Gemini Vision API for facial emotion detection.
"""
import os
import google.generativeai as genai
from PIL import Image
import numpy as np
from typing import List, Dict
import json


class EmotionAnalyzerAgent:
    """
    Analyzes facial emotions throughout a speech using Gemini Vision.
    Tracks: Happy, Angry, Disgust, Fear, Surprise, Sad, Neutral
    """
    
    def __init__(self, api_key: str = None):
        """
        Initialize Gemini API.
        """
        if api_key is None:
            api_key = os.getenv("GEMINI_API_KEY")
        
        if not api_key:
            raise ValueError("GEMINI_API_KEY not provided")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-2.5-flash')
    
    def analyze(self, frames: List[tuple]) -> Dict:
        """
        Analyze emotions and gestures from video frames.
        
        Args:
            frames: List of (timestamp_str, frame_image) tuples
        
        Returns:
            {
                "timeline": [
                    {
                        "time": "0:05",
                        "Happy": 80,
                        "Angry": 0,
                        "Disgust": 0,
                        "Fear": 5,
                        "Surprise": 10,
                        "Sad": 0,
                        "Neutral": 5,
                        "dominant": "Happy"
                    },
                    ...
                ],
                "overall_rating": 8.4,
                "gesture_rating": 7.9,
                "gesture_description": "Natural and purposeful"
            }
        """
        timeline = []
        gesture_scores = []
        
        for timestamp, frame in frames:
            emotion_data, gesture_score = self._analyze_frame(frame, timestamp)
            timeline.append(emotion_data)
            gesture_scores.append(gesture_score)
        
        # Calculate overall rating
        overall_rating = self._calculate_overall_rating(timeline)
        
        # Calculate gesture rating and description
        gesture_rating = sum(gesture_scores) / len(gesture_scores) if gesture_scores else 5.0
        gesture_description = self._get_gesture_description(gesture_rating)
        
        return {
            "timeline": timeline,
            "overall_rating": overall_rating,
            "gesture_rating": gesture_rating,
            "gesture_description": gesture_description
        }
    
    def _analyze_frame(self, frame: np.ndarray, timestamp: str) -> tuple:
        """
        Analyze emotions and gestures in a single frame using Gemini Vision.
        Returns: (emotion_dict, gesture_score)
        """
        # Convert numpy array to PIL Image
        pil_image = Image.fromarray(frame)
        
        # Create prompt for Gemini
        prompt = """Analyze the facial expression and body language in this image.
Respond ONLY with valid JSON in this exact format (no markdown, no extra text):
{
  "Happy": 0,
  "Angry": 0,
  "Disgust": 0,
  "Fear": 0,
  "Surprise": 0,
  "Sad": 0,
  "Neutral": 0,
  "gesture_score": 7.5
}

Emotion values should sum to approximately 100. The gesture_score (0-10) rates body language, hand gestures, and posture quality for public speaking."""
        
        try:
            # Generate response
            response = self.model.generate_content([prompt, pil_image])
            
            # Parse response
            response_text = response.text.strip()
            
            # Remove markdown code blocks if present
            if response_text.startswith("```"):
                response_text = response_text.split("```")[1]
                if response_text.startswith("json"):
                    response_text = response_text[4:].strip()
            
            data = json.loads(response_text)
            
            # Extract gesture score
            gesture_score = float(data.get("gesture_score", 5.0))
            
            # Validate emotions
            required_emotions = ["Happy", "Angry", "Disgust", "Fear", "Surprise", "Sad", "Neutral"]
            emotions = {}
            for emotion in required_emotions:
                emotions[emotion] = data.get(emotion, 0)
            
            # Find dominant emotion
            dominant = max(emotions, key=emotions.get)
            
            # Add metadata
            emotions["time"] = timestamp
            emotions["dominant"] = dominant
            
            return emotions, gesture_score
            
        except Exception as e:
            print(f"Error analyzing frame at {timestamp}: {e}")
            # Return neutral emotions and average gesture score on error
            return {
                "time": timestamp,
                "Happy": 0,
                "Angry": 0,
                "Disgust": 0,
                "Fear": 0,
                "Surprise": 0,
                "Sad": 0,
                "Neutral": 100,
                "dominant": "Neutral"
            }, 5.0
    
    def _calculate_overall_rating(self, timeline: List[Dict]) -> float:
        """
        Calculate overall emotion rating (0-10) based on:
        - Emotional variety (good speakers show range)
        - Positive emotion ratio
        - Appropriate emotion changes
        """
        if not timeline:
            return 5.0
        
        # Count dominant emotions
        emotion_counts = {}
        positive_emotions = ['Happy', 'Surprise']
        negative_emotions = ['Angry', 'Disgust', 'Fear', 'Sad']
        
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        
        for entry in timeline:
            dominant = entry.get('dominant', 'Neutral')
            emotion_counts[dominant] = emotion_counts.get(dominant, 0) + 1
            
            if dominant in positive_emotions:
                positive_count += 1
            elif dominant in negative_emotions:
                negative_count += 1
            else:
                neutral_count += 1
        
        total = len(timeline)
        
        # Factor 1: Emotional variety (3-5 different emotions = good)
        variety_score = min(10, len(emotion_counts) * 2)
        
        # Factor 2: Positive ratio (60-80% positive = good)
        positive_ratio = positive_count / total
        if 0.4 <= positive_ratio <= 0.7:
            positivity_score = 10.0
        elif 0.3 <= positive_ratio < 0.4 or 0.7 < positive_ratio <= 0.8:
            positivity_score = 8.0
        else:
            positivity_score = 6.0
        
        # Factor 3: Not too much negativity
        negative_ratio = negative_count / total
        if negative_ratio > 0.5:
            negativity_penalty = 3.0
        elif negative_ratio > 0.3:
            negativity_penalty = 1.5
        else:
            negativity_penalty = 0
        
        # Factor 4: Some neutral is okay (shows control)
        neutral_ratio = neutral_count / total
        if 0.1 <= neutral_ratio <= 0.3:
            neutral_score = 10.0
        else:
            neutral_score = 7.0
        
        # Calculate final score
        overall = (
            variety_score * 0.25 +
            positivity_score * 0.35 +
            neutral_score * 0.15 +
            (10 - negativity_penalty) * 0.25
        )
        
        return max(0.0, min(10.0, overall))
    
    def _get_gesture_description(self, rating: float) -> str:
        """
        Get a text description of gesture quality based on rating.
        """
        if rating >= 9.0:
            return "Exceptional and highly engaging"
        elif rating >= 8.0:
            return "Very effective and natural"
        elif rating >= 7.0:
            return "Natural and purposeful"
        elif rating >= 6.0:
            return "Generally appropriate"
        elif rating >= 5.0:
            return "Adequate with room for improvement"
        else:
            return "Needs significant improvement"


