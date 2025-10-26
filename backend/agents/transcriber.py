"""
Transcriber Agent - Uses faster-whisper for transcription and analyzes speech quality.
"""
from faster_whisper import WhisperModel
import re
from typing import Dict


class TranscriberAgent:
    """
    Transcribes speech and assigns quality scores based on:
    - Clarity (filler words, articulation)
    - Content (coherence, structure)
    - Argumentation (logical flow)
    """
    
    def __init__(self, model_size: str = "base"):
        """
        Initialize the Whisper model.
        Args:
            model_size: Model size (tiny, base, small, medium, large)
        """
        # Use CPU for AMD compatibility
        self.model = WhisperModel(model_size, device="cpu", compute_type="int8")
        
        # Common filler words
        self.filler_words = {
            'um', 'uh', 'like', 'you know', 'so', 'basically', 'actually',
            'literally', 'kind of', 'sort of', 'i mean', 'right', 'okay'
        }
    
    def transcribe(self, audio_path: str) -> Dict:
        """
        Transcribe audio and analyze quality.
        
        Returns:
            {
                "text": str,
                "quality_score": float (0-10)
            }
        """
        # Transcribe
        segments, info = self.model.transcribe(audio_path, beam_size=5)
        
        # Collect all text
        full_text = ""
        for segment in segments:
            full_text += segment.text + " "
        
        full_text = full_text.strip()
        
        if not full_text:
            return {
                "text": "[No speech detected]",
                "quality_score": 0.0
            }
        
        # Analyze quality
        quality_score = self._analyze_speech_quality(full_text)
        
        return {
            "text": full_text,
            "quality_score": quality_score
        }
    
    def _analyze_speech_quality(self, text: str) -> float:
        """
        Analyze speech quality based on multiple factors.
        Returns score 0-10.
        """
        text_lower = text.lower()
        words = text_lower.split()
        
        if len(words) < 5:
            return 3.0  # Too short
        
        # Factor 1: Clarity (filler word ratio)
        filler_count = 0
        for filler in self.filler_words:
            filler_count += text_lower.count(filler)
        
        filler_ratio = filler_count / len(words)
        clarity_score = max(0, 10 - (filler_ratio * 50))  # Penalize fillers
        
        # Factor 2: Content structure (sentence count and variety)
        sentences = [s.strip() for s in re.split(r'[.!?]+', text) if s.strip()]
        sentence_count = len(sentences)
        
        if sentence_count == 0:
            structure_score = 2.0
        else:
            avg_sentence_length = len(words) / sentence_count
            # Good speeches have 10-20 words per sentence
            if 10 <= avg_sentence_length <= 20:
                structure_score = 10.0
            elif 8 <= avg_sentence_length <= 25:
                structure_score = 8.0
            else:
                structure_score = 6.0
        
        # Factor 3: Vocabulary richness (unique words ratio)
        unique_words = set(words)
        vocab_ratio = len(unique_words) / len(words)
        vocab_score = min(10, vocab_ratio * 20)  # Higher ratio = richer vocabulary
        
        # Factor 4: Coherence (check for repeated phrases - indicates planning)
        # Penalize excessive repetition
        word_counts = {}
        for word in words:
            if len(word) > 4:  # Only count meaningful words
                word_counts[word] = word_counts.get(word, 0) + 1
        
        repetition_penalty = 0
        for count in word_counts.values():
            if count > 5:  # Word repeated more than 5 times
                repetition_penalty += 0.5
        
        coherence_score = max(0, 10 - repetition_penalty)
        
        # Weighted average
        quality_score = (
            clarity_score * 0.35 +      # Clarity is most important
            structure_score * 0.25 +     # Structure matters
            vocab_score * 0.20 +         # Vocabulary richness
            coherence_score * 0.20       # Coherence
        )
        
        # Clamp to 0-10
        return max(0.0, min(10.0, quality_score))


