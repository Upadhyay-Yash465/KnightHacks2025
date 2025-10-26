"""
Voice Analyzer Agent - Uses librosa for voice quality analysis.
"""
import librosa
import numpy as np
from typing import Dict


class VoiceAnalyzerAgent:
    """
    Analyzes voice quality metrics:
    - Pitch variation (0-10)
    - Volume consistency (0-10)
    - Speech rate/speed (0-10)
    - Prosody/intonation (0-10)
    """
    
    def __init__(self):
        pass
    
    def analyze(self, audio_path: str) -> Dict:
        """
        Analyze voice characteristics from audio file.
        
        Returns:
            {
                "pitch": float (0-10),
                "volume": float (0-10),
                "speed": float (0-10),
                "prosody": float (0-10)
            }
        """
        # Load audio
        y, sr = librosa.load(audio_path, sr=None)
        
        # Analyze each metric
        pitch_score = self._analyze_pitch(y, sr)
        volume_score = self._analyze_volume(y, sr)
        speed_score = self._analyze_speed(y, sr)
        prosody_score = self._analyze_prosody(y, sr)
        
        return {
            "pitch": pitch_score,
            "volume": volume_score,
            "speed": speed_score,
            "prosody": prosody_score
        }
    
    def _analyze_pitch(self, y: np.ndarray, sr: int) -> float:
        """
        Analyze pitch variation. Good speakers vary pitch appropriately.
        Returns score 0-10.
        """
        # Extract pitch using YIN algorithm
        f0 = librosa.yin(y, fmin=50, fmax=400, sr=sr)
        
        # Remove zero/nan values (silence)
        f0_valid = f0[~np.isnan(f0) & (f0 > 0)]
        
        if len(f0_valid) < 10:
            return 5.0  # Not enough data
        
        # Calculate pitch variation (standard deviation)
        pitch_std = np.std(f0_valid)
        pitch_mean = np.mean(f0_valid)
        
        # Coefficient of variation (normalized std dev)
        if pitch_mean > 0:
            cv = pitch_std / pitch_mean
        else:
            cv = 0
        
        # Good pitch variation: CV between 0.1 and 0.3
        if 0.1 <= cv <= 0.3:
            score = 10.0
        elif 0.05 <= cv < 0.1 or 0.3 < cv <= 0.4:
            score = 8.0
        elif cv < 0.05:
            score = 5.0  # Monotone
        else:
            score = 6.0  # Too much variation
        
        return score
    
    def _analyze_volume(self, y: np.ndarray, sr: int) -> float:
        """
        Analyze volume consistency. Good speakers maintain steady volume.
        Returns score 0-10.
        """
        # Calculate RMS energy in windows
        frame_length = 2048
        hop_length = 512
        rms = librosa.feature.rms(y=y, frame_length=frame_length, hop_length=hop_length)[0]
        
        # Remove very quiet sections (silence)
        rms_valid = rms[rms > np.percentile(rms, 10)]
        
        if len(rms_valid) < 5:
            return 5.0
        
        # Calculate consistency (lower std = more consistent)
        rms_std = np.std(rms_valid)
        rms_mean = np.mean(rms_valid)
        
        if rms_mean > 0:
            cv = rms_std / rms_mean
        else:
            cv = 1.0
        
        # Good volume consistency: CV < 0.3
        if cv < 0.2:
            score = 10.0
        elif cv < 0.3:
            score = 8.5
        elif cv < 0.4:
            score = 7.0
        elif cv < 0.5:
            score = 6.0
        else:
            score = 5.0  # Inconsistent volume
        
        return score
    
    def _analyze_speed(self, y: np.ndarray, sr: int) -> float:
        """
        Analyze speech rate/speed. Optimal speed is around 140-160 words per minute.
        Returns score 0-10.
        """
        # Estimate speech rate using zero crossing rate and energy
        duration = len(y) / sr
        
        if duration < 1:
            return 5.0
        
        # Detect onset events (syllables/words)
        onset_env = librosa.onset.onset_strength(y=y, sr=sr)
        onsets = librosa.onset.onset_detect(onset_envelope=onset_env, sr=sr)
        
        # Estimate syllables per second
        syllables_per_second = len(onsets) / duration
        
        # Convert to words per minute (roughly 1.5 syllables per word)
        words_per_minute = (syllables_per_second * 60) / 1.5
        
        # Optimal range: 120-180 WPM
        if 130 <= words_per_minute <= 170:
            score = 10.0
        elif 110 <= words_per_minute < 130 or 170 < words_per_minute <= 190:
            score = 8.0
        elif 90 <= words_per_minute < 110 or 190 < words_per_minute <= 210:
            score = 6.5
        elif words_per_minute < 90:
            score = 5.0  # Too slow
        else:
            score = 5.5  # Too fast
        
        return score
    
    def _analyze_prosody(self, y: np.ndarray, sr: int) -> float:
        """
        Analyze prosody/intonation patterns. Good prosody = varied pitch + rhythm.
        Returns score 0-10.
        """
        # Prosody combines pitch variation and rhythm
        
        # 1. Pitch contour variation
        f0 = librosa.yin(y, fmin=50, fmax=400, sr=sr)
        f0_valid = f0[~np.isnan(f0) & (f0 > 0)]
        
        if len(f0_valid) < 10:
            return 5.0
        
        # Calculate pitch range
        pitch_range = np.ptp(f0_valid)  # Peak-to-peak
        pitch_mean = np.mean(f0_valid)
        
        if pitch_mean > 0:
            pitch_range_ratio = pitch_range / pitch_mean
        else:
            pitch_range_ratio = 0
        
        # 2. Rhythm variation (tempo)
        tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
        
        # Good prosody: moderate pitch range and clear rhythm
        pitch_component = min(10, pitch_range_ratio * 15)  # Good range: 0.3-0.7
        
        # Tempo consistency indicates good rhythm
        if 80 <= tempo <= 180:
            rhythm_component = 10.0
        else:
            rhythm_component = 7.0
        
        # Combine scores
        prosody_score = (pitch_component * 0.6 + rhythm_component * 0.4)
        
        return max(0.0, min(10.0, prosody_score))


