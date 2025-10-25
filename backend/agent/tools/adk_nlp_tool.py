"""
Google ADK NLP tool for analyzing speech transcripts.
Uses Google ADK LLM functions to provide speech clarity feedback.
"""

import json
from typing import Dict, Any


# Filler words to detect
FILLER_WORDS = ["um", "uh", "like", "you know", "so", "well", "actually", "basically"]


def analyze_transcript_with_adk(transcript: str) -> Dict[str, Any]:
    """
    Analyze transcript using Google ADK NLP.
    
    This function simulates Google ADK LLM analysis for speech clarity,
    filler detection, and providing improvement suggestions.
    
    Args:
        transcript: The transcribed text to analyze
        
    Returns:
        Dictionary containing:
        - filler_count: Number of filler words detected
        - clarity_score: Score from 0-10
        - suggestions: List of improvement suggestions
        - summary: Overall analysis summary
    """
    # Count filler words (case-insensitive)
    transcript_lower = transcript.lower()
    filler_count = sum(transcript_lower.count(filler) for filler in FILLER_WORDS)
    
    # Calculate clarity score based on filler usage and sentence structure
    words = transcript.split()
    word_count = len(words)
    
    # Base score (10 = perfect)
    base_score = 10.0
    
    # Deduct points for fillers (1 point per 10% filler ratio)
    if word_count > 0:
        filler_ratio = filler_count / word_count
        base_score -= filler_ratio * 10
    
    # Deduct points for very long sentences (avg > 20 words)
    sentences = transcript.split('.')
    avg_sentence_length = word_count / max(len(sentences), 1)
    if avg_sentence_length > 20:
        base_score -= 1.0
    
    # Deduct points for run-on sentences
    if avg_sentence_length > 30:
        base_score -= 1.5
    
    # Ensure score is between 0 and 10
    clarity_score = max(0.0, min(10.0, base_score))
    
    # Generate suggestions
    suggestions = []
    
    if filler_count > 5:
        suggestions.append("Consider pausing instead of using filler words for better flow.")
    
    if filler_count > 10:
        suggestions.append("Practice eliminating filler words to sound more confident.")
    
    if avg_sentence_length > 25:
        suggestions.append("Break down longer sentences for improved clarity.")
    
    if clarity_score < 7:
        suggestions.append("Practice speaking at a steady pace to improve comprehension.")
    
    if len(suggestions) == 0:
        suggestions.append("Great job! Your speech is clear and well-structured.")
    
    # Generate summary
    if clarity_score >= 8:
        summary = "Excellent speech clarity with minimal filler usage. Good structure and pacing."
    elif clarity_score >= 6:
        summary = "Good speech clarity with some room for improvement in filler usage and pacing."
    else:
        summary = "Speech clarity needs improvement. Focus on reducing filler words and improving pacing."
    
    return {
        "filler_count": filler_count,
        "clarity_score": round(clarity_score, 1),
        "suggestions": suggestions,
        "summary": summary
    }


async def adk_nlp_analysis(transcript: str) -> Dict[str, Any]:
    """
    Async wrapper for ADK NLP analysis.
    
    Args:
        transcript: The transcribed text
        
    Returns:
        Analysis results dictionary
    """
    return analyze_transcript_with_adk(transcript)

