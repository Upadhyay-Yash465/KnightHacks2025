import os
import json
import logging
import numpy as np
import librosa
from faster_whisper import WhisperModel
import google.generativeai as genai
from utils.logger import setup_logger

logger = setup_logger(__name__)

class GeminiVoiceAgent:
    """
    Advanced Voice Analysis Agent that provides specific, varied, and actionable feedback
    on Pitch, Tone, Speed, and Prosody with detailed rankings and explanations.
    """
    
    def __init__(self, model_size="base", gemini_model="gemini-2.5-flash"):
        self.model_size = model_size
        self.gemini_model = gemini_model
        
        # Initialize Whisper for transcription
        try:
            self.whisper_model = WhisperModel(model_size, device="cpu", compute_type="int8")
            logger.info(f"✅ Whisper model '{model_size}' loaded successfully")
        except Exception as e:
            logger.error(f"❌ Failed to load Whisper model: {e}")
            self.whisper_model = None
        
        # Configure Gemini
        try:
            genai.configure(api_key=os.getenv('GOOGLE_API_KEY'))
            logger.info(f"✅ Gemini API configured with model '{gemini_model}'")
        except Exception as e:
            logger.error(f"❌ Failed to configure Gemini API: {e}")

    def analyze(self, audio_path: str) -> dict:
        """
        Comprehensive voice analysis with specific rankings and explanations.
        """
        try:
            logger.info(f"🎤 Starting advanced voice analysis for: {audio_path}")
            
            # Step 1: Transcribe audio
            transcript = self._transcribe_audio(audio_path)
            logger.info(f"📝 Transcript: {transcript[:100]}..." if len(transcript) > 100 else f"📝 Transcript: {transcript}")
            
            # Step 2: Extract detailed audio metrics
            audio_metrics = self._extract_audio_metrics(audio_path)
            logger.info(f"📊 Audio metrics extracted: {len(audio_metrics)} parameters")
            
            # Step 3: Perform advanced voice analysis
            voice_analysis = self._perform_advanced_analysis(transcript, audio_metrics)
            
            # Step 4: Generate specific rankings and explanations
            ranked_analysis = self._generate_ranked_analysis(voice_analysis, audio_metrics)
            
            logger.info("✅ Advanced voice analysis completed successfully")
            return ranked_analysis
            
        except Exception as e:
            logger.error(f"❌ Voice analysis failed: {e}")
            return self._get_error_fallback(str(e))

    def _transcribe_audio(self, audio_path: str) -> str:
        """Transcribe audio using Whisper."""
        try:
            if not self.whisper_model:
                return "Transcription unavailable - Whisper model not loaded"
            
            segments, info = self.whisper_model.transcribe(audio_path, beam_size=5)
            transcript = " ".join([segment.text for segment in segments])
            
            if not transcript.strip():
                logger.warning("⚠️ Empty transcript - analyzing audio content")
                return "Audio appears to be low-frequency content (music/tone). Please record speech instead."
            
            return transcript.strip()
            
        except Exception as e:
            logger.error(f"❌ Transcription failed: {e}")
            return f"Transcription error: {str(e)}"

    def _extract_audio_metrics(self, audio_path: str) -> dict:
        """Extract comprehensive audio metrics using librosa."""
        try:
            logger.info(f"🎵 Loading audio file: {audio_path}")
            
            # Load audio file with better error handling
            try:
                y, sr = librosa.load(audio_path, sr=None)
                logger.info(f"✅ Audio loaded: {len(y)} samples at {sr}Hz")
            except Exception as load_error:
                logger.error(f"❌ Failed to load audio file: {load_error}")
                return self._get_default_audio_metrics()
            
            if len(y) == 0:
                logger.warning("⚠️ Audio file is empty")
                return self._get_default_audio_metrics()
            
            duration = len(y) / sr
            logger.info(f"📊 Audio duration: {duration:.2f} seconds")
            
            # Basic metrics with error handling
            try:
                rms = librosa.feature.rms(y=y)[0]
                avg_volume = float(np.mean(rms))
                volume_std = float(np.std(rms))
                logger.info(f"📊 Volume: {avg_volume:.4f} RMS, std: {volume_std:.4f}")
            except Exception as vol_error:
                logger.warning(f"⚠️ Volume analysis failed: {vol_error}")
                avg_volume = 0.0
                volume_std = 0.0
            
            # Pitch analysis with error handling
            try:
                pitches, magnitudes = librosa.piptrack(y=y, sr=sr, threshold=0.1)
                pitch_values = []
                for t in range(pitches.shape[1]):
                    index = magnitudes[:, t].argmax()
                    pitch = pitches[index, t]
                    if pitch > 0:
                        pitch_values.append(pitch)
                
                avg_pitch = float(np.mean(pitch_values)) if pitch_values else 0.0
                pitch_std = float(np.std(pitch_values)) if pitch_values else 0.0
                pitch_range = float(np.max(pitch_values) - np.min(pitch_values)) if len(pitch_values) > 1 else 0.0
                logger.info(f"📊 Pitch: {avg_pitch:.1f}Hz, std: {pitch_std:.1f}Hz, range: {pitch_range:.1f}Hz")
            except Exception as pitch_error:
                logger.warning(f"⚠️ Pitch analysis failed: {pitch_error}")
                avg_pitch = 0.0
                pitch_std = 0.0
                pitch_range = 0.0
                pitch_values = []
            
            # Tempo and rhythm with error handling
            try:
                tempo, beats = librosa.beat.beat_track(y=y, sr=sr)
                tempo = float(tempo)
                logger.info(f"📊 Tempo: {tempo:.1f} BPM")
            except Exception as tempo_error:
                logger.warning(f"⚠️ Tempo analysis failed: {tempo_error}")
                tempo = 0.0
            
            # Spectral features with error handling
            try:
                spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)[0]
                avg_spectral_centroid = float(np.mean(spectral_centroids))
                logger.info(f"📊 Spectral centroid: {avg_spectral_centroid:.1f}Hz")
            except Exception as spec_error:
                logger.warning(f"⚠️ Spectral analysis failed: {spec_error}")
                avg_spectral_centroid = 0.0
            
            # Zero crossing rate with error handling
            try:
                zcr = librosa.feature.zero_crossing_rate(y)[0]
                avg_zcr = float(np.mean(zcr))
                logger.info(f"📊 Zero crossing rate: {avg_zcr:.4f}")
            except Exception as zcr_error:
                logger.warning(f"⚠️ ZCR analysis failed: {zcr_error}")
                avg_zcr = 0.0
            
            # MFCC features with error handling
            try:
                mfccs = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=13)
                mfcc_mean = np.mean(mfccs, axis=1)
                logger.info(f"📊 MFCC features extracted: {len(mfcc_mean)} coefficients")
            except Exception as mfcc_error:
                logger.warning(f"⚠️ MFCC analysis failed: {mfcc_error}")
                mfcc_mean = np.zeros(13)
            
            metrics = {
                'duration_sec': float(duration),
                'avg_volume_rms': avg_volume,
                'volume_std': volume_std,
                'avg_pitch_hz': avg_pitch,
                'pitch_std': pitch_std,
                'pitch_range': pitch_range,
                'tempo_bpm': tempo,
                'avg_spectral_centroid': avg_spectral_centroid,
                'avg_zcr': avg_zcr,
                'mfcc_features': mfcc_mean.tolist(),
                'speech_rate_wpm': 0.0,  # Will be calculated later with transcript
                'pitch_values': pitch_values[:50] if pitch_values else [],
                'volume_values': rms[:50].tolist() if 'rms' in locals() else []
            }
            
            logger.info(f"✅ Audio metrics extracted successfully: {len(metrics)} parameters")
            return metrics
            
        except Exception as e:
            logger.error(f"❌ Audio metrics extraction failed: {str(e)}")
            logger.error(f"❌ Error type: {type(e).__name__}")
            return self._get_default_audio_metrics()
    
    def _get_default_audio_metrics(self) -> dict:
        """Return default audio metrics when extraction fails."""
        return {
            'duration_sec': 0.0,
            'avg_volume_rms': 0.0,
            'volume_std': 0.0,
            'avg_pitch_hz': 0.0,
            'pitch_std': 0.0,
            'pitch_range': 0.0,
            'tempo_bpm': 0.0,
            'avg_spectral_centroid': 0.0,
            'avg_zcr': 0.0,
            'mfcc_features': [],
            'speech_rate_wpm': 0.0,
            'pitch_values': [],
            'volume_values': []
        }

    def _perform_advanced_analysis(self, transcript: str, audio_metrics: dict) -> dict:
        """Perform advanced analysis using Gemini with specific focus on voice characteristics."""
        try:
            # Calculate speech rate
            if transcript and transcript != "Audio appears to be low-frequency content (music/tone). Please record speech instead.":
                words = transcript.split()
                word_count = len(words)
                duration = audio_metrics.get('duration_sec', 1)
                if duration > 0:
                    speech_rate = (word_count / duration) * 60  # words per minute
                else:
                    speech_rate = 0
                audio_metrics['speech_rate_wpm'] = speech_rate
            
            # Use Gemini for advanced analysis
            analysis = self._get_gemini_voice_analysis(transcript, audio_metrics)
            return analysis
            
        except Exception as e:
            logger.error(f"❌ Advanced analysis failed: {e}")
            return self._get_enhanced_fallback_analysis(transcript, audio_metrics, str(e))

    def _get_gemini_voice_analysis(self, transcript: str, audio_metrics: dict) -> dict:
        """Get advanced voice analysis from Gemini."""
        try:
            model = genai.GenerativeModel(self.gemini_model)
            prompt = self._create_advanced_voice_prompt(transcript, audio_metrics)
            
            max_retries = 3
            for attempt in range(max_retries):
                try:
                    response = model.generate_content(prompt)
                    content = response.text.strip()
                    
                    # Try to parse JSON response
                    try:
                        analysis_data = json.loads(content)
                        logger.info("✅ Gemini voice analysis successful")
                        return analysis_data
                    except json.JSONDecodeError:
                        logger.warning("⚠️ Gemini output not JSON — using enhanced fallback.")
                        return self._get_enhanced_fallback_analysis(transcript, audio_metrics, content)
                        
                except Exception as api_error:
                    logger.warning(f"⚠️ Gemini attempt {attempt + 1} failed: {api_error}")
                    if attempt == max_retries - 1:
                        raise api_error
                    import time
                    time.sleep(1)
                    
        except Exception as e:
            logger.error(f"❌ Gemini voice analysis failed: {e}")
            return self._get_enhanced_fallback_analysis(transcript, audio_metrics, str(e))

    def _create_advanced_voice_prompt(self, transcript: str, audio_metrics: dict) -> str:
        """Create advanced prompt for specific voice analysis."""
        return f"""You are an expert voice coach and speech analyst with 20+ years of experience. Analyze the following speech sample and provide SPECIFIC, VARIED, and ACTIONABLE feedback.

TRANSCRIPT: "{transcript}"

DETAILED AUDIO METRICS:
- Duration: {audio_metrics.get('duration_sec', 0):.2f} seconds
- Average Volume: {audio_metrics.get('avg_volume_rms', 0):.4f} RMS
- Volume Variation: {audio_metrics.get('volume_std', 0):.4f} (standard deviation)
- Average Pitch: {audio_metrics.get('avg_pitch_hz', 0):.1f} Hz
- Pitch Variation: {audio_metrics.get('pitch_std', 0):.1f} Hz (standard deviation)
- Pitch Range: {audio_metrics.get('pitch_range', 0):.1f} Hz
- Speech Rate: {audio_metrics.get('speech_rate_wpm', 0):.1f} words per minute
- Tempo: {audio_metrics.get('tempo_bpm', 0):.1f} BPM
- Spectral Centroid: {audio_metrics.get('avg_spectral_centroid', 0):.1f} Hz

CRITICAL REQUIREMENTS:
1. Analyze FOUR specific areas: PITCH, TONE, SPEED, and PROSODY
2. Rank each area from 1-10 with SPECIFIC explanations
3. Make rankings VARIED and REALISTIC based on actual metrics
4. Provide ACTIONABLE recommendations for each area
5. Explain WHY each ranking was given with specific evidence

Return ONLY valid JSON in this exact format:
{{
    "pitch_analysis": {{
        "score": <1-10 integer>,
        "ranking": "<Excellent/Good/Fair/Poor>",
        "explanation": "Specific explanation of why this score was given, referencing actual pitch metrics",
        "strengths": ["Specific pitch strengths observed"],
        "weaknesses": ["Specific pitch issues identified"],
        "recommendations": ["Specific actionable recommendations for pitch improvement"]
    }},
    "tone_analysis": {{
        "score": <1-10 integer>,
        "ranking": "<Excellent/Good/Fair/Poor>",
        "explanation": "Specific explanation of tone quality, referencing volume and pitch metrics",
        "strengths": ["Specific tone strengths observed"],
        "weaknesses": ["Specific tone issues identified"],
        "recommendations": ["Specific actionable recommendations for tone improvement"]
    }},
    "speed_analysis": {{
        "score": <1-10 integer>,
        "ranking": "<Excellent/Good/Fair/Poor>",
        "explanation": "Specific explanation of speaking pace, referencing WPM and tempo metrics",
        "strengths": ["Specific speed strengths observed"],
        "weaknesses": ["Specific speed issues identified"],
        "recommendations": ["Specific actionable recommendations for pace improvement"]
    }},
    "prosody_analysis": {{
        "score": <1-10 integer>,
        "ranking": "<Excellent/Good/Fair/Poor>",
        "explanation": "Specific explanation of rhythm, flow, and musicality, referencing tempo and variation metrics",
        "strengths": ["Specific prosody strengths observed"],
        "weaknesses": ["Specific prosody issues identified"],
        "recommendations": ["Specific actionable recommendations for prosody improvement"]
    }},
    "overall_assessment": {{
        "summary": "Comprehensive summary of voice performance",
        "primary_strength": "Main strength area",
        "primary_weakness": "Main area needing improvement",
        "next_steps": ["Top 3 specific next steps for improvement"]
    }}
}}

IMPORTANT: 
- Make rankings REALISTIC and VARIED based on actual metrics
- Provide SPECIFIC explanations referencing the data
- Give ACTIONABLE recommendations
- Avoid generic feedback - be specific and detailed
"""

    def _get_enhanced_fallback_analysis(self, transcript: str, audio_metrics: dict, error_msg: str = "") -> dict:
        """Enhanced fallback analysis with specific rankings based on actual metrics."""
        duration = audio_metrics.get('duration_sec', 0)
        volume = audio_metrics.get('avg_volume_rms', 0)
        pitch = audio_metrics.get('avg_pitch_hz', 0)
        pitch_std = audio_metrics.get('pitch_std', 0)
        pitch_range = audio_metrics.get('pitch_range', 0)
        speech_rate = audio_metrics.get('speech_rate_wpm', 0)
        tempo = audio_metrics.get('tempo_bpm', 0)
        volume_std = audio_metrics.get('volume_std', 0)
        
        # Calculate specific scores based on metrics
        pitch_score, pitch_explanation = self._analyze_pitch_specific(pitch, pitch_std, pitch_range)
        tone_score, tone_explanation = self._analyze_tone_specific(volume, volume_std, pitch)
        speed_score, speed_explanation = self._analyze_speed_specific(speech_rate, tempo, duration)
        prosody_score, prosody_explanation = self._analyze_prosody_specific(tempo, pitch_std, volume_std)
        
        return {
            "pitch_analysis": {
                "score": pitch_score,
                "ranking": self._get_ranking_label(pitch_score),
                "explanation": pitch_explanation,
                "strengths": self._get_pitch_strengths(pitch_score, pitch, pitch_range),
                "weaknesses": self._get_pitch_weaknesses(pitch_score, pitch, pitch_range),
                "recommendations": self._get_pitch_recommendations(pitch_score, pitch, pitch_range)
            },
            "tone_analysis": {
                "score": tone_score,
                "ranking": self._get_ranking_label(tone_score),
                "explanation": tone_explanation,
                "strengths": self._get_tone_strengths(tone_score, volume, pitch),
                "weaknesses": self._get_tone_weaknesses(tone_score, volume, pitch),
                "recommendations": self._get_tone_recommendations(tone_score, volume, pitch)
            },
            "speed_analysis": {
                "score": speed_score,
                "ranking": self._get_ranking_label(speed_score),
                "explanation": speed_explanation,
                "strengths": self._get_speed_strengths(speed_score, speech_rate),
                "weaknesses": self._get_speed_weaknesses(speed_score, speech_rate),
                "recommendations": self._get_speed_recommendations(speed_score, speech_rate)
            },
            "prosody_analysis": {
                "score": prosody_score,
                "ranking": self._get_ranking_label(prosody_score),
                "explanation": prosody_explanation,
                "strengths": self._get_prosody_strengths(prosody_score, tempo, pitch_std),
                "weaknesses": self._get_prosody_weaknesses(prosody_score, tempo, pitch_std),
                "recommendations": self._get_prosody_recommendations(prosody_score, tempo, pitch_std)
            },
            "overall_assessment": {
                "summary": f"Voice analysis completed with specific metrics: Pitch {pitch:.1f}Hz, Volume {volume:.3f}, Speed {speech_rate:.1f}WPM, Tempo {tempo:.1f}BPM",
                "primary_strength": self._get_primary_strength(pitch_score, tone_score, speed_score, prosody_score),
                "primary_weakness": self._get_primary_weakness(pitch_score, tone_score, speed_score, prosody_score),
                "next_steps": self._get_next_steps(pitch_score, tone_score, speed_score, prosody_score)
            }
        }

    def _analyze_pitch_specific(self, pitch: float, pitch_std: float, pitch_range: float) -> tuple:
        """Analyze pitch with specific scoring based on metrics."""
        if pitch < 50:
            return 3, f"Very low pitch ({pitch:.1f}Hz) indicates potential vocal strain or unclear speech. Pitch variation is {pitch_std:.1f}Hz, suggesting limited vocal range."
        elif pitch > 400:
            return 4, f"Very high pitch ({pitch:.1f}Hz) may sound strained or nervous. Pitch range of {pitch_range:.1f}Hz shows limited variation."
        elif 120 <= pitch <= 280:
            if pitch_range > 100:
                return 9, f"Excellent pitch range ({pitch:.1f}Hz average) with good variation ({pitch_range:.1f}Hz range). Pitch standard deviation of {pitch_std:.1f}Hz shows natural variation."
            else:
                return 7, f"Good pitch ({pitch:.1f}Hz) but limited range ({pitch_range:.1f}Hz). Pitch variation of {pitch_std:.1f}Hz is moderate."
        else:
            return 6, f"Moderate pitch ({pitch:.1f}Hz) with {pitch_range:.1f}Hz range. Pitch variation of {pitch_std:.1f}Hz suggests room for improvement."

    def _analyze_tone_specific(self, volume: float, volume_std: float, pitch: float) -> tuple:
        """Analyze tone with specific scoring based on metrics."""
        if volume < 0.01:
            return 2, f"Very quiet volume ({volume:.4f} RMS) makes speech hard to hear. Volume variation of {volume_std:.4f} is minimal."
        elif volume > 0.5:
            return 3, f"Very loud volume ({volume:.4f} RMS) may sound distorted. Volume variation of {volume_std:.4f} shows inconsistency."
        elif 0.1 <= volume <= 0.3:
            if volume_std < 0.05:
                return 8, f"Good consistent volume ({volume:.4f} RMS) with stable delivery. Volume variation of {volume_std:.4f} shows good control."
            else:
                return 6, f"Good volume level ({volume:.4f} RMS) but inconsistent delivery. Volume variation of {volume_std:.4f} needs improvement."
        else:
            return 5, f"Moderate volume ({volume:.4f} RMS) with {volume_std:.4f} variation. Consider adjusting volume for better projection."

    def _analyze_speed_specific(self, speech_rate: float, tempo: float, duration: float) -> tuple:
        """Analyze speed with specific scoring based on metrics."""
        if duration < 1:
            return 2, f"Recording too short ({duration:.1f}s) for accurate speed analysis. Speech rate of {speech_rate:.1f} WPM is unreliable."
        elif speech_rate < 60:
            return 4, f"Speaking too slowly ({speech_rate:.1f} WPM). Tempo of {tempo:.1f} BPM suggests sluggish delivery."
        elif speech_rate > 200:
            return 4, f"Speaking too quickly ({speech_rate:.1f} WPM). Tempo of {tempo:.1f} BPM indicates rushed delivery."
        elif 100 <= speech_rate <= 160:
            return 9, f"Excellent speaking pace ({speech_rate:.1f} WPM). Tempo of {tempo:.1f} BPM shows good rhythm and control."
        else:
            return 6, f"Moderate speaking pace ({speech_rate:.1f} WPM). Tempo of {tempo:.1f} BPM suggests room for pace optimization."

    def _analyze_prosody_specific(self, tempo: float, pitch_std: float, volume_std: float) -> tuple:
        """Analyze prosody with specific scoring based on metrics."""
        # Prosody is about rhythm, flow, and musicality
        rhythm_score = 5
        if 60 <= tempo <= 120:
            rhythm_score += 2
        elif tempo > 120:
            rhythm_score += 1
        
        variation_score = 5
        if pitch_std > 20:
            variation_score += 2
        elif pitch_std > 10:
            variation_score += 1
        
        if volume_std > 0.05:
            variation_score += 1
        
        prosody_score = min(10, (rhythm_score + variation_score) // 2)
        
        explanation = f"Prosody analysis: Tempo {tempo:.1f} BPM, pitch variation {pitch_std:.1f}Hz, volume variation {volume_std:.4f}. "
        if prosody_score >= 8:
            explanation += "Excellent rhythm and natural variation create engaging delivery."
        elif prosody_score >= 6:
            explanation += "Good rhythm with moderate variation shows developing prosody skills."
        else:
            explanation += "Limited rhythm and variation suggest need for prosody development."
        
        return prosody_score, explanation

    def _get_ranking_label(self, score: int) -> str:
        """Convert score to ranking label."""
        if score >= 9:
            return "Excellent"
        elif score >= 7:
            return "Good"
        elif score >= 5:
            return "Fair"
        else:
            return "Poor"

    def _get_pitch_strengths(self, score: int, pitch: float, pitch_range: float) -> list:
        """Get pitch-specific strengths."""
        strengths = []
        if score >= 7:
            strengths.append(f"Natural pitch range around {pitch:.1f}Hz")
            if pitch_range > 100:
                strengths.append(f"Excellent pitch variation ({pitch_range:.1f}Hz range)")
            strengths.append("Clear vocal projection")
        elif score >= 5:
            strengths.append("Basic pitch control")
            strengths.append("Audible speech")
        return strengths

    def _get_pitch_weaknesses(self, score: int, pitch: float, pitch_range: float) -> list:
        """Get pitch-specific weaknesses."""
        weaknesses = []
        if score < 6:
            if pitch < 100:
                weaknesses.append(f"Pitch too low ({pitch:.1f}Hz) - may sound unclear")
            elif pitch > 300:
                weaknesses.append(f"Pitch too high ({pitch:.1f}Hz) - may sound strained")
            if pitch_range < 50:
                weaknesses.append(f"Limited pitch range ({pitch_range:.1f}Hz) - sounds monotone")
        return weaknesses

    def _get_pitch_recommendations(self, score: int, pitch: float, pitch_range: float) -> list:
        """Get pitch-specific recommendations."""
        recommendations = []
        if score < 6:
            if pitch < 100:
                recommendations.append("Practice speaking in a higher pitch range (150-250Hz)")
                recommendations.append("Do vocal warm-up exercises to raise your natural pitch")
            elif pitch > 300:
                recommendations.append("Practice speaking in a lower pitch range (150-250Hz)")
                recommendations.append("Focus on relaxing your vocal cords")
            if pitch_range < 50:
                recommendations.append("Practice varying your pitch for emphasis")
                recommendations.append("Read aloud with different emotional tones")
        else:
            recommendations.append("Continue practicing to maintain your pitch control")
            recommendations.append("Experiment with pitch variation for different contexts")
        return recommendations

    def _get_tone_strengths(self, score: int, volume: float, pitch: float) -> list:
        """Get tone-specific strengths."""
        strengths = []
        if score >= 7:
            strengths.append(f"Good volume level ({volume:.3f} RMS)")
            strengths.append("Consistent vocal tone")
            strengths.append("Clear projection")
        elif score >= 5:
            strengths.append("Audible speech")
            strengths.append("Basic tone control")
        return strengths

    def _get_tone_weaknesses(self, score: int, volume: float, pitch: float) -> list:
        """Get tone-specific weaknesses."""
        weaknesses = []
        if score < 6:
            if volume < 0.05:
                weaknesses.append(f"Volume too quiet ({volume:.3f} RMS) - hard to hear")
            elif volume > 0.4:
                weaknesses.append(f"Volume too loud ({volume:.3f} RMS) - may sound harsh")
            weaknesses.append("Inconsistent tone delivery")
        return weaknesses

    def _get_tone_recommendations(self, score: int, volume: float, pitch: float) -> list:
        """Get tone-specific recommendations."""
        recommendations = []
        if score < 6:
            if volume < 0.05:
                recommendations.append("Practice projecting your voice louder")
                recommendations.append("Use diaphragmatic breathing for better volume control")
            elif volume > 0.4:
                recommendations.append("Practice speaking at a moderate volume")
                recommendations.append("Focus on vocal relaxation techniques")
            recommendations.append("Record yourself and adjust volume consistency")
        else:
            recommendations.append("Maintain your current tone quality")
            recommendations.append("Practice tone variation for different emotions")
        return recommendations

    def _get_speed_strengths(self, score: int, speech_rate: float) -> list:
        """Get speed-specific strengths."""
        strengths = []
        if score >= 7:
            strengths.append(f"Optimal speaking pace ({speech_rate:.1f} WPM)")
            strengths.append("Good rhythm and flow")
            strengths.append("Easy to follow")
        elif score >= 5:
            strengths.append("Consistent pace")
            strengths.append("Understandable speed")
        return strengths

    def _get_speed_weaknesses(self, score: int, speech_rate: float) -> list:
        """Get speed-specific weaknesses."""
        weaknesses = []
        if score < 6:
            if speech_rate < 80:
                weaknesses.append(f"Speaking too slowly ({speech_rate:.1f} WPM)")
            elif speech_rate > 180:
                weaknesses.append(f"Speaking too quickly ({speech_rate:.1f} WPM)")
            weaknesses.append("Inconsistent pacing")
        return weaknesses

    def _get_speed_recommendations(self, score: int, speech_rate: float) -> list:
        """Get speed-specific recommendations."""
        recommendations = []
        if score < 6:
            if speech_rate < 80:
                recommendations.append("Practice speaking faster (aim for 120-160 WPM)")
                recommendations.append("Use a metronome to practice consistent pacing")
            elif speech_rate > 180:
                recommendations.append("Practice speaking slower (aim for 120-160 WPM)")
                recommendations.append("Add strategic pauses between sentences")
            recommendations.append("Record yourself and count words per minute")
        else:
            recommendations.append("Maintain your current speaking pace")
            recommendations.append("Practice pace variation for emphasis")
        return recommendations

    def _get_prosody_strengths(self, score: int, tempo: float, pitch_std: float) -> list:
        """Get prosody-specific strengths."""
        strengths = []
        if score >= 7:
            strengths.append(f"Good rhythm (tempo {tempo:.1f} BPM)")
            strengths.append(f"Natural pitch variation ({pitch_std:.1f}Hz)")
            strengths.append("Engaging delivery")
        elif score >= 5:
            strengths.append("Basic rhythm")
            strengths.append("Some variation")
        return strengths

    def _get_prosody_weaknesses(self, score: int, tempo: float, pitch_std: float) -> list:
        """Get prosody-specific weaknesses."""
        weaknesses = []
        if score < 6:
            if tempo < 60:
                weaknesses.append(f"Slow rhythm (tempo {tempo:.1f} BPM)")
            elif tempo > 140:
                weaknesses.append(f"Fast rhythm (tempo {tempo:.1f} BPM)")
            if pitch_std < 10:
                weaknesses.append(f"Limited pitch variation ({pitch_std:.1f}Hz)")
            weaknesses.append("Monotone delivery")
        return weaknesses

    def _get_prosody_recommendations(self, score: int, tempo: float, pitch_std: float) -> list:
        """Get prosody-specific recommendations."""
        recommendations = []
        if score < 6:
            if tempo < 60:
                recommendations.append("Practice speaking with more energy and pace")
                recommendations.append("Use rhythmic exercises to improve tempo")
            elif tempo > 140:
                recommendations.append("Practice speaking more slowly and deliberately")
                recommendations.append("Focus on breathing and pacing")
            if pitch_std < 10:
                recommendations.append("Practice varying your pitch for emphasis")
                recommendations.append("Read poetry aloud with different tones")
            recommendations.append("Practice storytelling to improve rhythm")
        else:
            recommendations.append("Continue developing your prosody skills")
            recommendations.append("Practice with different types of content")
        return recommendations

    def _get_primary_strength(self, pitch_score: int, tone_score: int, speed_score: int, prosody_score: int) -> str:
        """Determine primary strength area."""
        scores = {"Pitch": pitch_score, "Tone": tone_score, "Speed": speed_score, "Prosody": prosody_score}
        best_area = max(scores, key=scores.get)
        return f"{best_area} (Score: {scores[best_area]}/10)"

    def _get_primary_weakness(self, pitch_score: int, tone_score: int, speed_score: int, prosody_score: int) -> str:
        """Determine primary weakness area."""
        scores = {"Pitch": pitch_score, "Tone": tone_score, "Speed": speed_score, "Prosody": prosody_score}
        worst_area = min(scores, key=scores.get)
        return f"{worst_area} (Score: {scores[worst_area]}/10)"

    def _get_next_steps(self, pitch_score: int, tone_score: int, speed_score: int, prosody_score: int) -> list:
        """Get top 3 next steps for improvement."""
        steps = []
        scores = {"Pitch": pitch_score, "Tone": tone_score, "Speed": speed_score, "Prosody": prosody_score}
        sorted_areas = sorted(scores.items(), key=lambda x: x[1])
        
        for area, score in sorted_areas[:3]:
            if score < 6:
                steps.append(f"Focus on improving {area} (current score: {score}/10)")
        
        if len(steps) < 3:
            steps.append("Continue practicing all areas to maintain improvement")
        
        return steps[:3]

    def _generate_ranked_analysis(self, voice_analysis: dict, audio_metrics: dict) -> dict:
        """Generate final ranked analysis with detailed explanations."""
        return {
            "transcript": voice_analysis.get("transcript", "No transcript available"),
            "word_count": len(voice_analysis.get("transcript", "").split()),
            "filler_words": voice_analysis.get("filler_words", 0),
            "detailed_analysis": voice_analysis,
            "audio_metrics": audio_metrics,
            "analysis_timestamp": str(np.datetime64('now'))
        }

    def _get_error_fallback(self, error_msg: str) -> dict:
        """Fallback for analysis errors."""
        return {
            "transcript": "Analysis failed",
            "word_count": 0,
            "filler_words": 0,
            "detailed_analysis": {
                "pitch_analysis": {"score": 0, "ranking": "Error", "explanation": f"Analysis failed: {error_msg}"},
                "tone_analysis": {"score": 0, "ranking": "Error", "explanation": f"Analysis failed: {error_msg}"},
                "speed_analysis": {"score": 0, "ranking": "Error", "explanation": f"Analysis failed: {error_msg}"},
                "prosody_analysis": {"score": 0, "ranking": "Error", "explanation": f"Analysis failed: {error_msg}"},
                "overall_assessment": {"summary": f"Analysis failed: {error_msg}"}
            },
            "audio_metrics": {},
            "analysis_timestamp": str(np.datetime64('now'))
        }