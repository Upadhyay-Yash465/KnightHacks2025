"""
vision_service.py
Provides basic visual metrics using OpenCV + MediaPipe.
"""

import cv2
import mediapipe as mp
import logging


class VisionService:
    def __init__(self):
        self.mp_face = mp.solutions.face_detection.FaceDetection(min_detection_confidence=0.5)
        self.mp_hands = mp.solutions.hands.Hands(static_image_mode=False, max_num_hands=2)

    def analyze_video(self, video_path: str) -> dict:
        """Compute rough confidence and gesture metrics."""
        try:
            cap = cv2.VideoCapture(video_path)
            total, faces, hands = 0, 0, 0

            while True:
                ok, frame = cap.read()
                if not ok:
                    break
                total += 1
                rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                if self.mp_face.process(rgb).detections:
                    faces += 1
                if self.mp_hands.process(rgb).multi_hand_landmarks:
                    hands += 1
            cap.release()

            eye_contact = round((faces / total) * 100, 2) if total else 0
            gesture_rate = round((hands / total) * 100, 2) if total else 0
            confidence = min(10, round(eye_contact / 10 + (gesture_rate / 25), 1))

            return {
                "eye_contact": eye_contact,
                "gesture_rate": gesture_rate,
                "confidence_score": confidence,
                "summary": (
                    f"Eye contact: {eye_contact}%, gestures: {gesture_rate}%, "
                    f"estimated confidence: {confidence}/10."
                )
            }
        except Exception as e:
            logging.error(f"VisionService error: {e}")
            return {"error": str(e)}
