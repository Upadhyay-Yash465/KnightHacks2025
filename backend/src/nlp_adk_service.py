"""
Google ADK NLP Service for Speech Analysis

This module provides NLP analysis of transcribed speech using Google's ADK (AI Development Kit)
to detect filler words, analyze clarity, and provide improvement suggestions.
"""

import asyncio
import logging
import re
import os
from typing import Dict, List, Optional, Tuple
import json

try:
    import google.generativeai as genai
    from google.generativeai.types import HarmCategory, HarmBlockThreshold
except ImportError:
    print("Warning: google-generativeai not installed. Run: pip install google-generativeai")
    genai = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class NLPAnalysisService:
    """
    Service for analyzing speech transcripts using Google ADK.
    
    Features:
    - Filler word detection and counting
    - Clarity scoring (1-10 scale)
    - Improvement suggestions
    - Structured JSON output
    """
    
    def __init__(self, api_key: Optional[str] = None):
        """
        Initialize the NLP analysis service.
        
        Args:
            api_key: Google ADK API key (can also be set via environment variable)
        """
        self.api_key = api_key
        self._model_loaded = False
        
        # Common filler words and phrases
        self.filler_patterns = [
            r'\bum\b', r'\buh\b', r'\blike\b', r'\byou know\b', r'\bso\b',
            r'\bwell\b', r'\bactually\b', r'\bbasically\b', r'\bliterally\b',
            r'\bkind of\b', r'\bsort of\b', r'\bI mean\b', r'\bright\b',
            r'\bokay\b', r'\bok\b', r'\byeah\b', r'\byep\b', r'\bnah\b',
            r'\banyway\b', r'\bso anyway\b', r'\buhm\b', r'\ber\b', r'\berm\b'
        ]
        
        # Compile regex patterns for efficiency
        self.compiled_patterns = [re.compile(pattern, re.IGNORECASE) for pattern in self.filler_patterns]
        
    async def _load_model(self) -> None:
        """
        Load the Google ADK model asynchronously.
        """
        if self._model_loaded:
            return
            
        if genai is None:
            raise ImportError("google-generativeai is not installed. Please install it with: pip install google-generativeai")
        
        # Configure API key
        if self.api_key:
            genai.configure(api_key=self.api_key)
        else:
            # Try to get from environment
            import os
            api_key = os.getenv('GOOGLE_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
            else:
                raise ValueError("Google API key not provided. Set GOOGLE_API_KEY environment variable or pass api_key parameter.")
        
        self._model_loaded = True
        logger.info("Google ADK model configured successfully")
    
    def _detect_filler_words(self, transcript: str) -> Dict:
        """
        Detect and count filler words in the transcript.
        
        Args:
            transcript: The text transcript to analyze
            
        Returns:
            Dictionary with filler word analysis
        """
        if not transcript.strip():
            return {
                "filler_count": 0,
                "filler_words": [],
                "filler_density": 0.0,
                "total_words": 0
            }
        
        # Split transcript into words
        words = transcript.lower().split()
        total_words = len(words)
        
        # Find filler words
        filler_words = []
        filler_count = 0
        
        for i, word in enumerate(words):
            for pattern in self.compiled_patterns:
                if pattern.search(word):
                    filler_words.append({
                        "word": word,
                        "position": i,
                        "context": " ".join(words[max(0, i-2):i+3])
                    })
                    filler_count += 1
                    break
        
        # Calculate filler density (fillers per 100 words)
        filler_density = (filler_count / total_words * 100) if total_words > 0 else 0.0
        
        return {
            "filler_count": filler_count,
            "filler_words": filler_words,
            "filler_density": round(filler_density, 2),
            "total_words": total_words
        }
    
    def _calculate_clarity_score(self, filler_analysis: Dict, transcript: str) -> float:
        """
        Calculate clarity score based on filler words and other factors.
        
        Args:
            filler_analysis: Results from filler word detection
            transcript: The original transcript
            
        Returns:
            Clarity score from 1-10
        """
        filler_density = filler_analysis["filler_density"]
        total_words = filler_analysis["total_words"]
        
        # Base score starts at 10
        score = 10.0
        
        # Deduct points for filler density
        if filler_density > 5:  # More than 5% fillers
            score -= min(4.0, filler_density * 0.4)
        elif filler_density > 2:  # More than 2% fillers
            score -= min(2.0, filler_density * 0.3)
        
        # Deduct points for very short or very long sentences
        sentences = re.split(r'[.!?]+', transcript)
        avg_sentence_length = sum(len(s.split()) for s in sentences if s.strip()) / len(sentences) if sentences else 0
        
        if avg_sentence_length < 5:  # Very short sentences
            score -= 1.0
        elif avg_sentence_length > 25:  # Very long sentences
            score -= 1.5
        
        # Bonus for good vocabulary diversity
        unique_words = len(set(transcript.lower().split()))
        if total_words > 0:
            vocabulary_diversity = unique_words / total_words
            if vocabulary_diversity > 0.7:
                score += 0.5
        
        # Ensure score is between 1 and 10
        return max(1.0, min(10.0, round(score, 1)))
    
    async def _generate_suggestions(self, transcript: str, filler_analysis: Dict, clarity_score: float) -> List[str]:
        """
        Generate improvement suggestions using Google ADK.
        
        Args:
            transcript: The transcript to analyze
            filler_analysis: Filler word analysis results
            clarity_score: Calculated clarity score
            
        Returns:
            List of improvement suggestions
        """
        try:
            # Check if API key is available
            if not self.api_key and not os.getenv('GOOGLE_API_KEY'):
                logger.warning("No Google API key found, using fallback suggestions")
                return self._get_fallback_suggestions(filler_analysis, clarity_score)
            
            await self._load_model()
            
            # Create analysis prompt
            prompt = f"""
            Analyze this speech transcript and provide 2-3 specific, actionable suggestions for improvement:
            
            Transcript: "{transcript}"
            
            Current Analysis:
            - Filler words found: {filler_analysis['filler_count']}
            - Filler density: {filler_analysis['filler_density']}%
            - Clarity score: {clarity_score}/10
            
            Please provide 2-3 concise, specific suggestions for improving speech clarity and reducing filler words.
            Focus on practical, actionable advice.
            
            Format your response as a JSON array of strings, like: ["suggestion1", "suggestion2", "suggestion3"]
            """
            
            # Generate suggestions using Google ADK
            # Try different model names for compatibility (updated to current models)
            model_names = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-flash-latest', 'gemini-1.5-flash', 'gemini-1.5-pro', 'gemini-pro']
            model = None
            
            for model_name in model_names:
                try:
                    model = genai.GenerativeModel(model_name)
                    logger.info(f"Using model: {model_name}")
                    break
                except Exception as e:
                    logger.warning(f"Model {model_name} not available: {str(e)}")
                    continue
            
            if model is None:
                logger.warning("No compatible Google ADK model found, using fallback suggestions")
                return self._get_fallback_suggestions(filler_analysis, clarity_score)
            
            # Run in thread pool to avoid blocking
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: model.generate_content(
                    prompt,
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
            )
            
            # Parse response
            suggestions_text = response.text.strip()
            
            # Try to extract JSON array
            try:
                # Look for JSON array in the response
                json_match = re.search(r'\[.*?\]', suggestions_text, re.DOTALL)
                if json_match:
                    suggestions = json.loads(json_match.group())
                else:
                    # Fallback: split by lines and clean up
                    suggestions = [s.strip().strip('"').strip("'") for s in suggestions_text.split('\n') if s.strip()]
                    suggestions = [s for s in suggestions if s and not s.startswith('[') and not s.startswith(']')]
            except (json.JSONDecodeError, AttributeError):
                # Fallback suggestions
                suggestions = [
                    "Practice pausing instead of using filler words",
                    "Slow down your speech pace for better clarity",
                    "Record yourself speaking to identify patterns"
                ]
            
            # Ensure we have 2-3 suggestions
            if len(suggestions) < 2:
                suggestions.extend([
                    "Practice speaking exercises to reduce filler words",
                    "Focus on clear articulation and pacing"
                ])
            
            return suggestions[:3]  # Return max 3 suggestions
            
        except Exception as e:
            logger.warning(f"Failed to generate AI suggestions: {str(e)}")
            # Return fallback suggestions
            return [
                "Practice pausing instead of using filler words",
                "Slow down your speech pace for better clarity",
                "Record yourself speaking to identify patterns"
            ]
    
    def _get_fallback_suggestions(self, filler_analysis: Dict, clarity_score: float) -> List[str]:
        """
        Generate fallback suggestions when Google ADK is not available.
        
        Args:
            filler_analysis: Filler word analysis results
            clarity_score: Calculated clarity score
            
        Returns:
            List of fallback suggestions
        """
        suggestions = []
        
        # Base suggestions based on filler count
        if filler_analysis['filler_count'] > 5:
            suggestions.append("Practice pausing instead of using filler words like 'um' and 'uh'")
            suggestions.append("Record yourself speaking to identify filler word patterns")
        elif filler_analysis['filler_count'] > 2:
            suggestions.append("Focus on reducing filler words by speaking more deliberately")
        
        # Suggestions based on clarity score
        if clarity_score < 6:
            suggestions.append("Slow down your speech pace for better clarity")
            suggestions.append("Practice speaking exercises to improve articulation")
        elif clarity_score < 8:
            suggestions.append("Work on maintaining consistent pacing throughout your speech")
        
        # Ensure we have at least 2-3 suggestions
        if len(suggestions) < 2:
            suggestions.extend([
                "Practice speaking exercises to reduce filler words",
                "Focus on clear articulation and pacing"
            ])
        
        return suggestions[:3]  # Return max 3 suggestions
    
    def _generate_summary(self, filler_analysis: Dict, clarity_score: float) -> str:
        """
        Generate a summary based on the analysis results.
        
        Args:
            filler_analysis: Filler word analysis results
            clarity_score: Calculated clarity score
            
        Returns:
            Summary string
        """
        filler_count = filler_analysis["filler_count"]
        filler_density = filler_analysis["filler_density"]
        
        if clarity_score >= 9:
            return "Excellent clarity with minimal filler usage."
        elif clarity_score >= 7:
            return "Good clarity with some filler words that can be reduced."
        elif clarity_score >= 5:
            return "Moderate clarity, consider reducing filler words and improving pacing."
        else:
            return "Clarity needs improvement. Focus on reducing filler words and speaking more deliberately."
    
    async def analyze_transcript(self, transcript: str) -> Dict:
        """
        Analyze a speech transcript and return structured feedback.
        
        Args:
            transcript: The text transcript to analyze
            
        Returns:
            Dictionary containing:
            - filler_count: Number of filler words found
            - clarity_score: Score from 1-10
            - suggestions: List of improvement suggestions
            - summary: Brief summary of the analysis
        """
        if not transcript or not transcript.strip():
            return {
                "filler_count": 0,
                "clarity_score": 0.0,
                "suggestions": ["Please provide a valid transcript for analysis"],
                "summary": "No transcript provided for analysis",
                "success": False
            }
        
        logger.info("Analyzing transcript for speech clarity...")
        
        try:
            # Detect filler words
            filler_analysis = self._detect_filler_words(transcript)
            
            # Calculate clarity score
            clarity_score = self._calculate_clarity_score(filler_analysis, transcript)
            
            # Generate suggestions using Google ADK
            suggestions = await self._generate_suggestions(transcript, filler_analysis, clarity_score)
            
            # Generate summary
            summary = self._generate_summary(filler_analysis, clarity_score)
            
            result = {
                "filler_count": filler_analysis["filler_count"],
                "clarity_score": clarity_score,
                "suggestions": suggestions,
                "summary": summary,
                "filler_density": filler_analysis["filler_density"],
                "total_words": filler_analysis["total_words"],
                "filler_words": filler_analysis["filler_words"],
                "success": True
            }
            
            logger.info(f"Analysis completed - Score: {clarity_score}, Fillers: {filler_analysis['filler_count']}")
            return result
            
        except Exception as e:
            logger.error(f"Analysis failed: {str(e)}")
            return {
                "filler_count": 0,
                "clarity_score": 0.0,
                "suggestions": ["Analysis failed due to technical error"],
                "summary": "Unable to analyze transcript",
                "success": False,
                "error": str(e)
            }


# Global service instance for caching
_nlp_service: Optional[NLPAnalysisService] = None


async def get_nlp_service(api_key: Optional[str] = None) -> NLPAnalysisService:
    """
    Get or create the global NLP service instance.
    
    Args:
        api_key: Google API key (optional)
        
    Returns:
        NLPAnalysisService instance
    """
    global _nlp_service
    if _nlp_service is None:
        _nlp_service = NLPAnalysisService(api_key)
    return _nlp_service


async def analyze_transcript(transcript: str, api_key: Optional[str] = None) -> Dict:
    """
    Convenience function to analyze a transcript using the global service.
    
    Args:
        transcript: The text transcript to analyze
        api_key: Google API key (optional)
        
    Returns:
        Analysis results dictionary
    """
    service = await get_nlp_service(api_key)
    return await service.analyze_transcript(transcript)


# Test block for standalone testing
if __name__ == "__main__":
    async def test_nlp_analysis():
        """Test the NLP analysis service with sample transcripts."""
        print("Testing Google ADK NLP Analysis Service...")
        
        # Create a test service
        service = NLPAnalysisService()
        
        # Test transcripts
        test_transcripts = [
            "So, um, I think that, like, the main point is that, you know, we should probably, uh, consider the options.",
            "The presentation was excellent. We achieved all our goals and exceeded expectations.",
            "Well, basically, I mean, it's like, you know, sort of complicated, right? So anyway, um, what do you think?"
        ]
        
        for i, transcript in enumerate(test_transcripts, 1):
            print(f"\n=== Test Transcript {i} ===")
            print(f"Text: {transcript}")
            
            try:
                result = await service.analyze_transcript(transcript)
                
                print(f"\nAnalysis Results:")
                print(f"Success: {result['success']}")
                print(f"Filler count: {result['filler_count']}")
                print(f"Clarity score: {result['clarity_score']}/10")
                print(f"Filler density: {result['filler_density']}%")
                print(f"Total words: {result['total_words']}")
                print(f"Summary: {result['summary']}")
                print(f"Suggestions:")
                for j, suggestion in enumerate(result['suggestions'], 1):
                    print(f"  {j}. {suggestion}")
                
                if result.get('filler_words'):
                    print(f"Filler words found:")
                    for filler in result['filler_words'][:5]:  # Show first 5
                        print(f"  - '{filler['word']}' at position {filler['position']}")
                
            except Exception as e:
                print(f"Analysis failed: {str(e)}")
        
        print("\n=== Service Info ===")
        print(f"Model loaded: {service._model_loaded}")
        print(f"API configured: {service.api_key is not None}")
    
    # Run the test
    asyncio.run(test_nlp_analysis())
