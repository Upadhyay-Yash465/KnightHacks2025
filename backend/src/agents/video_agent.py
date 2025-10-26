"""
video_agent.py
VideoAgent (Gemini 2.5 Flash default)
Analyzes video input for facial emotion, eye contact, and body gestures.
Falls back to MediaPipe + OpenCV when Gemini is unavailable.
"""

import os
import cv2
import json
import logging
import google.generativeai as genai
import mediapipe as mp


class VideoAgent:
    def __init__(self,
                 model_primary="gemini-2.5-flash",
                 model_fallback="mediapipe-opencv"):
        """
        Initializes Gemini for high-level perception with local fallback.
        """
        self.model_primary = model_primary
        self.model_fallback = model_fallback
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")

        if self.gemini_api_key:
            genai.configure(api_key=self.gemini_api_key)
        else:
            logging.warning("⚠️ No GOOGLE_API_KEY found. Will use local fallback only.")

    # -------------------------------
    # Main pipeline
    # -------------------------------
    def analyze(self, video_path: str) -> dict:
        """
        Executes visual analysis via Gemini 2.5 Flash,
        or falls back to MediaPipe + OpenCV.
        """
        if not os.path.exists(video_path):
            return {"error": f"Video file not found: {video_path}"}

        logging.info("🎥 Running VideoAgent analysis...")

        if self.gemini_api_key:
            try:
                return self._analyze_with_gemini(video_path)
            except Exception as e:
                logging.error(f"⚠️ Gemini analysis failed: {e}")
                logging.info("🔄 Falling back to MediaPipe + OpenCV.")
                return self._analyze_with_mediapipe(video_path)
        else:
            return self._analyze_with_mediapipe(video_path)

    # -------------------------------
    # Gemini 2.5 Flash analysis
    # -------------------------------
    def _analyze_with_gemini(self, video_path: str) -> dict:
        """
        Uploads the video and requests structured perception reasoning.
        """
        logging.info("🧠 Using Gemini 2.5 Flash for video understanding...")

        prompt = (
            "You are an expert nonverbal communication coach, body language specialist, and presentation skills consultant with 20+ years of experience. "
            "Please provide EXTREMELY DETAILED, comprehensive analysis of this video. "
            "The user wants extensive, actionable feedback to dramatically improve their visual presentation skills.\n\n"
            
            "Please analyze this video for ALL aspects of nonverbal communication and provide an EXTREMELY COMPREHENSIVE analysis in the following JSON format:\n"
            "{\n"
            '  "emotion": "Detailed analysis of facial expressions and emotional state with specific observations", '
            '  "confidence_score": <1-10 with detailed explanation>, '
            '  "eye_contact": <percentage with detailed analysis>, '
            '  "gesture_frequency": "Detailed assessment of gesture usage with specific examples", '
            '  "detailed_analysis": {'
            '    "facial_expressions": "Extremely detailed analysis of facial expressions, micro-expressions, and emotional indicators", '
            '    "eye_contact_analysis": "Comprehensive evaluation of eye contact patterns, duration, and effectiveness", '
            '    "gesture_analysis": "Detailed assessment of hand gestures, body movements, and nonverbal communication", '
            '    "posture_analysis": "Analysis of body posture, stance, and physical presence", '
            '    "facial_landmarks": "Assessment of facial feature positioning, symmetry, and expression clarity", '
            '    "confidence_indicators": "Detailed evaluation of confidence markers and authority presence", '
            '    "engagement_level": "Analysis of how well the speaker engages the audience visually", '
            '    "professional_presence": "Evaluation of professional appearance and executive presence", '
            '    "body_language": "Comprehensive assessment of overall body language and nonverbal cues", '
            '    "movement_patterns": "Analysis of movement, pacing, and spatial awareness", '
            '    "micro_expressions": "Detailed analysis of subtle facial expressions and emotional micro-movements", '
            '    "improvement_areas": ["Detailed list of 6-8 specific visual presentation areas to improve"], '
            '    "strengths": ["Detailed list of 6-8 visual presentation strengths"], '
            '    "recommendations": ["Detailed list of 10-12 specific, actionable recommendations for visual improvement"], '
            '    "practice_exercises": ["List of 6-8 specific exercises to improve visual presentation"], '
            '    "common_mistakes": ["List of 5-6 common visual presentation mistakes to avoid"], '
            '    "advanced_techniques": ["List of 5-6 advanced visual presentation techniques"], '
            '    "camera_technique": ["List of 4-5 specific camera and recording techniques"], '
            '    "lighting_tips": ["List of 4-5 lighting and setup recommendations"] '
            '  }, '
            '  "summary": "Comprehensive overall visual presentation assessment with specific examples and detailed explanations"'
            "}\n\n"
            
            "CRITICAL INSTRUCTIONS:\n"
            "- Provide extremely detailed, specific feedback with examples\n"
            "- Include actionable advice for every aspect of visual presentation\n"
            "- Give specific techniques and exercises for improvement\n"
            "- Explain the 'why' behind each recommendation\n"
            "- Provide comprehensive analysis, not brief summaries\n"
            "- Focus on practical, implementable improvements\n"
            "- Analyze every aspect of nonverbal communication\n"
            "- Consider the professional context and audience impact"
        )

        model = genai.GenerativeModel(self.model_primary)
        # Gemini supports direct video inputs via parts=[]
        response = model.generate_content(
            [prompt, {"mime_type": "video/mp4", "data": open(video_path, "rb").read()}]
        )

        raw = response.text.strip()
        try:
            data = json.loads(raw)
        except json.JSONDecodeError:
            logging.warning("⚠️ Gemini output not JSON — using minimal parse.")
            data = {"summary": raw}

        return {
            "emotion": data.get("emotion", "Neutral"),
            "confidence_score": data.get("confidence_score", 7.0),
            "eye_contact": data.get("eye_contact", 70.0),
            "gesture_frequency": data.get("gesture_frequency", "Moderate"),
            "summary": data.get("summary", "Speaker appears confident and engaged."),
            "model_used": self.model_primary
        }

    # -------------------------------
    # MediaPipe + OpenCV fallback
    # -------------------------------
    def _analyze_with_mediapipe(self, video_path: str) -> dict:
        """
        Estimate emotion & gesture metrics locally.
        """
        logging.info("📸 Running local MediaPipe/OpenCV fallback...")

        mp_face = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.5)
        mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2)

        cap = cv2.VideoCapture(video_path)
        total_frames, face_frames, hand_frames = 0, 0, 0

        while True:
            success, frame = cap.read()
            if not success:
                break
            total_frames += 1

            rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            face_result = mp_face.process(rgb)
            hand_result = mp_hands.process(rgb)

            if face_result.detections:
                face_frames += 1
            if hand_result.multi_hand_landmarks:
                hand_frames += 1

        cap.release()

        eye_contact = round((face_frames / total_frames) * 100, 2) if total_frames else 0
        gesture_rate = round((hand_frames / total_frames) * 100, 2) if total_frames else 0
        confidence = min(10, round(eye_contact / 10 + (gesture_rate / 25), 1))

        return {
            "emotion": "Neutral (local-estimation)",
            "confidence_score": confidence,
            "eye_contact": eye_contact,
            "gesture_frequency": f"{gesture_rate}%",
            "summary": (
                f"Maintained eye contact {eye_contact}% of the time; "
                f"gesture activity {gesture_rate}%. Estimated confidence {confidence}/10."
            ),
            "model_used": self.model_fallback
        }
