import cv2
import numpy as np

def analyze_body(video_path: str) -> dict:
    """
    Lightweight body-language analyzer (works without mediapipe).
    Evaluates lighting, motion, and overall presence.
    """
    cap = cv2.VideoCapture(video_path)
    frame_count = 0
    brightness_values = []
    motion_score = 0
    prev_gray = None

    while True:
        ret, frame = cap.read()
        if not ret:
            break
        frame_count += 1

        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness_values.append(np.mean(gray))

        if prev_gray is not None:
            diff = cv2.absdiff(gray, prev_gray)
            motion_score += np.sum(diff > 25)
        prev_gray = gray

    cap.release()

    avg_brightness = np.mean(brightness_values) if brightness_values else 0
    avg_motion = motion_score / (frame_count or 1)

    feedback = []
    if avg_brightness < 80:
        feedback.append("Lighting seems dim — face the camera or add more light.")
    if avg_motion < 50000:
        feedback.append("Use more hand gestures or movement for engagement.")
    else:
        feedback.append("Good physical energy and presence!")

    return {
        "frames_analyzed": frame_count,
        "avg_brightness": round(avg_brightness, 2),
        "avg_motion_score": round(avg_motion, 2),
        "body_feedback": " ".join(feedback)
    }
