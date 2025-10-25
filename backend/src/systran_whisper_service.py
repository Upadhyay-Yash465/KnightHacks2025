"""
SYSTRAN Faster-Whisper Service for Speech-to-Text Transcription

This module provides async-friendly speech transcription using SYSTRAN's Faster-Whisper model.
It caches the model for efficiency and returns structured transcript data with timestamps.
"""

import asyncio
import logging
from typing import Dict, List, Optional, Tuple
from pathlib import Path
import time

try:
    from faster_whisper import WhisperModel
except ImportError:
    print("Warning: faster_whisper not installed. Run: pip install faster-whisper")
    WhisperModel = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class SystranWhisperService:
    """
    Service for transcribing audio files using SYSTRAN Faster-Whisper model.
    
    Features:
    - Model caching for efficiency
    - Async-friendly operations
    - Structured output with timestamps
    - Support for various audio formats
    """
    
    def __init__(self, model_name: str = "systran/faster-whisper-base"):
        """
        Initialize the Whisper service with model caching.
        
        Args:
            model_name: The SYSTRAN Faster-Whisper model to use
        """
        self.model_name = model_name
        self._model: Optional[WhisperModel] = None
        self._model_loaded = False
        
    async def _load_model(self) -> None:
        """
        Load the Whisper model asynchronously.
        Caches the model for subsequent calls.
        """
        if self._model_loaded:
            return
            
        if WhisperModel is None:
            raise ImportError("faster_whisper is not installed. Please install it with: pip install faster-whisper")
        
        logger.info(f"Loading SYSTRAN Faster-Whisper model: {self.model_name}")
        
        # Run model loading in thread pool to avoid blocking
        loop = asyncio.get_event_loop()
        self._model = await loop.run_in_executor(
            None, 
            lambda: WhisperModel(self.model_name, device="cpu", compute_type="int8")
        )
        
        self._model_loaded = True
        logger.info("Model loaded successfully")
    
    async def transcribe_audio(self, file_path: str) -> Dict:
        """
        Transcribe an audio file and return structured results.
        
        Args:
            file_path: Path to the audio file to transcribe
            
        Returns:
            Dictionary containing:
            - transcript: Full text transcription
            - segments: List of segments with timestamps
            - language: Detected language
            - duration: Audio duration in seconds
            - confidence: Average confidence score
        """
        # Validate file path
        if not Path(file_path).exists():
            raise FileNotFoundError(f"Audio file not found: {file_path}")
        
        # Load model if not already loaded
        await self._load_model()
        
        logger.info(f"Transcribing audio file: {file_path}")
        start_time = time.time()
        
        try:
            # Run transcription in thread pool
            loop = asyncio.get_event_loop()
            segments, info = await loop.run_in_executor(
                None,
                lambda: self._model.transcribe(
                    file_path,
                    beam_size=5,
                    word_timestamps=True,
                    vad_filter=True,
                    vad_parameters=dict(min_silence_duration_ms=500)
                )
            )
            
            # Process segments into structured format
            processed_segments = []
            full_transcript = ""
            total_confidence = 0
            segment_count = 0
            
            for segment in segments:
                segment_data = {
                    "start": round(segment.start, 2),
                    "end": round(segment.end, 2),
                    "text": segment.text.strip(),
                    "confidence": round(segment.avg_logprob, 3) if hasattr(segment, 'avg_logprob') else 0.0
                }
                
                # Add word-level timestamps if available
                if hasattr(segment, 'words') and segment.words:
                    segment_data["words"] = [
                        {
                            "word": word.word,
                            "start": round(word.start, 2),
                            "end": round(word.end, 2),
                            "confidence": round(word.probability, 3) if hasattr(word, 'probability') else 0.0
                        }
                        for word in segment.words
                    ]
                
                processed_segments.append(segment_data)
                full_transcript += segment.text.strip() + " "
                total_confidence += segment_data["confidence"]
                segment_count += 1
            
            # Calculate average confidence
            avg_confidence = round(total_confidence / segment_count, 3) if segment_count > 0 else 0.0
            
            # Calculate duration
            duration = round(info.duration, 2) if hasattr(info, 'duration') else 0.0
            
            transcription_time = round(time.time() - start_time, 2)
            
            result = {
                "transcript": full_transcript.strip(),
                "segments": processed_segments,
                "language": info.language if hasattr(info, 'language') else "unknown",
                "language_probability": round(info.language_probability, 3) if hasattr(info, 'language_probability') else 0.0,
                "duration": duration,
                "confidence": avg_confidence,
                "transcription_time": transcription_time,
                "model_used": self.model_name,
                "success": True
            }
            
            logger.info(f"Transcription completed in {transcription_time}s")
            return result
            
        except Exception as e:
            logger.error(f"Transcription failed: {str(e)}")
            return {
                "transcript": "",
                "segments": [],
                "language": "unknown",
                "language_probability": 0.0,
                "duration": 0.0,
                "confidence": 0.0,
                "transcription_time": 0.0,
                "model_used": self.model_name,
                "success": False,
                "error": str(e)
            }
    
    def get_model_info(self) -> Dict:
        """
        Get information about the loaded model.
        
        Returns:
            Dictionary with model information
        """
        return {
            "model_name": self.model_name,
            "model_loaded": self._model_loaded,
            "model_type": "SYSTRAN Faster-Whisper"
        }


# Global service instance for caching
_whisper_service: Optional[SystranWhisperService] = None


async def get_whisper_service() -> SystranWhisperService:
    """
    Get or create the global Whisper service instance.
    
    Returns:
        SystranWhisperService instance
    """
    global _whisper_service
    if _whisper_service is None:
        _whisper_service = SystranWhisperService()
    return _whisper_service


async def transcribe_audio(file_path: str) -> Dict:
    """
    Convenience function to transcribe audio using the global service.
    
    Args:
        file_path: Path to the audio file
        
    Returns:
        Transcription results dictionary
    """
    service = await get_whisper_service()
    return await service.transcribe_audio(file_path)


# Test block for standalone testing
if __name__ == "__main__":
    async def test_transcription():
        """Test the transcription service with a sample audio file."""
        print("Testing SYSTRAN Faster-Whisper Service...")
        
        # Create a test service
        service = SystranWhisperService()
        
        # Test with a sample audio file (you'll need to provide a real file)
        test_file = "sample_audio.wav"  # Replace with actual audio file path
        
        if Path(test_file).exists():
            print(f"Transcribing: {test_file}")
            result = await service.transcribe_audio(test_file)
            
            print("\n=== Transcription Results ===")
            print(f"Success: {result['success']}")
            print(f"Language: {result['language']} (confidence: {result['language_probability']})")
            print(f"Duration: {result['duration']}s")
            print(f"Transcription time: {result['transcription_time']}s")
            print(f"Average confidence: {result['confidence']}")
            print(f"\nTranscript:\n{result['transcript']}")
            
            if result['segments']:
                print(f"\nSegments ({len(result['segments'])}):")
                for i, segment in enumerate(result['segments'][:3]):  # Show first 3 segments
                    print(f"  {i+1}. [{segment['start']}s - {segment['end']}s] {segment['text']}")
        else:
            print(f"Test file not found: {test_file}")
            print("Please provide a valid audio file path for testing.")
        
        print("\nModel info:", service.get_model_info())
    
    # Run the test
    asyncio.run(test_transcription())
