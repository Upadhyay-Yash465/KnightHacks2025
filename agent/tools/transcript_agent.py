def analyze_transcript_local(transcript: str) -> dict:
    """
    Detect filler words and analyze transcript quality.
    Uses simple text analysis without external APIs.
    """
    if not transcript:
        return {
            "filler_count": 0,
            "clarity_score": 0,
            "suggestions": [],
            "summary": "No transcript available"
        }
    
    filler_words = ["um", "uh", "like", "you know", "so", "actually", "basically"]
    filler_count = sum(transcript.lower().count(f) for f in filler_words)
    
    # Calculate clarity score based on filler word count
    word_count = len(transcript.split())
    filler_ratio = filler_count / word_count if word_count > 0 else 0
    clarity_score = max(0, min(10, 10 - (filler_ratio * 20)))
    
    # Generate suggestions
    suggestions = []
    if filler_count > 3:
        suggestions.append("Reduce filler words for clearer communication")
    if word_count < 50:
        suggestions.append("Expand your speech with more detail")
    
    return {
        "filler_count": filler_count,
        "clarity_score": round(clarity_score, 1),
        "suggestions": suggestions,
        "summary": f"Transcript analyzed: {word_count} words, {filler_count} filler words detected"
    }
