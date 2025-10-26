"""
orchestrator_agent.py
Final orchestration layer integrating:
- VoiceAgent (Whisper + GPT)
- ContextAgent (Gemini 2.5 Flash / 2.0 fallback)
- VideoAgent (Gemini multimodal / MediaPipe fallback)

Performs adaptive reasoning and dynamic weighting to produce unified feedback.
"""

import asyncio
import logging
import json
import time
from concurrent.futures import ThreadPoolExecutor

from .gemini_voice_agent import GeminiVoiceAgent as VoiceAgent
from .context_agent import ContextAgent
from .video_agent import VideoAgent


class OrchestratorAgent:
    """
    The brain of the AI Speech Coach.
    Coordinates all sub-agents, merges insights, and computes confidence metrics.
    """

    def __init__(self):
        self.voice = VoiceAgent()
        self.context = ContextAgent()
        self.video = VideoAgent()

        logging.basicConfig(
            level=logging.INFO,
            format="%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%H:%M:%S"
        )

    # -------------------------------
    # Main Runner
    # -------------------------------
    async def run(self, audio_path: str, video_path: str = None) -> dict:
        start = time.time()
        logging.info("🚀 Starting Orchestrator pipeline...")

        # Run VoiceAgent first (needed for transcript)
        voice_result = await self._safe_run(self.voice.analyze, audio_path, name="VoiceAgent")

        # Run Context + Video concurrently
        context_task = asyncio.create_task(
            self._safe_run(self.context.analyze, voice_result.get("transcript", ""), name="ContextAgent")
        )

        video_task = (
            asyncio.create_task(self._safe_run(self.video.analyze, video_path, name="VideoAgent"))
            if video_path else None
        )

        context_result = await context_task
        video_result = await video_task if video_task else {"note": "No video provided"}

        combined = self._combine_results(voice_result, context_result, video_result)
        combined["execution_time_sec"] = round(time.time() - start, 2)

        logging.info(f"✅ Orchestration completed in {combined['execution_time_sec']}s.")
        return combined

    # -------------------------------
    # Safe Runner with Retry
    # -------------------------------
    async def _safe_run(self, func, *args, name="Agent", retries=2):
        """Async runner with retry & thread safety."""
        for attempt in range(1, retries + 1):
            try:
                if asyncio.iscoroutinefunction(func):
                    return await func(*args)
                else:
                    loop = asyncio.get_running_loop()
                    with ThreadPoolExecutor() as pool:
                        return await loop.run_in_executor(pool, func, *args)
            except Exception as e:
                logging.warning(f"⚠️ {name} failed (Attempt {attempt}): {e}")
                await asyncio.sleep(0.3)
        logging.error(f"❌ {name} failed all attempts.")
        return {"error": f"{name} unavailable."}

    # -------------------------------
    # Merge All Results
    # -------------------------------
    def _combine_results(self, voice, context, video):
        """Blend agent data into a unified performance report."""
        clarity = context.get("clarity_score", 0)
        grammar = context.get("grammar_score", 0)
        structure = context.get("structure_score", 0)
        vocal_clarity = voice.get("clarity", 0)
        filler_penalty = voice.get("filler_words", 0)
        confidence = video.get("confidence_score", 7.0)

        # Dynamic weighting: balance verbal + nonverbal
        final_score = round(
            ((clarity + grammar + structure) / 3 * 0.5)
            + (confidence * 0.3)
            + ((10 - min(filler_penalty, 10)) * 0.2),
            2
        )

        # Create overall feedback summary
        summary = self._generate_summary(voice, context, video, final_score)

        return {
            "voice": voice,
            "context": context,
            "video": video,
            "final_score": final_score,
            "summary": summary,
            "weighted_breakdown": {
                "verbal_score": round((clarity + grammar + structure) / 3, 2),
                "nonverbal_score": confidence,
                "filler_penalty": filler_penalty,
            }
        }

    # -------------------------------
    # Summary Generator
    # -------------------------------
    def _generate_summary(self, voice, context, video, final_score):
        """Generate a human-style summary using aggregated signals."""
        emotion = video.get("emotion", "Neutral")
        clarity = context.get("clarity_score", "N/A")
        eye_contact = video.get("eye_contact", "N/A")
        filler_words = voice.get("filler_words", 0)

        tone_feedback = (
            "Excellent clarity and structure!" if final_score > 8
            else "Good clarity, moderate confidence."
            if final_score > 6
            else "Needs more focus and fluency practice."
        )

        return (
            f"🗣️ Clarity: {clarity}/10 | Filler Words: {filler_words}\n"
            f"🎥 Confidence: {video.get('confidence_score', 'N/A')}/10 | Eye Contact: {eye_contact}%\n"
            f"🙂 Emotion: {emotion}\n\n"
            f"💡 Overall Feedback: {tone_feedback}\n"
            f"🏁 Composite Score: {final_score}/10"
        )


# -------------------------------
# Local Test
# -------------------------------
if __name__ == "__main__":
    import asyncio

    orchestrator = OrchestratorAgent()
    result = asyncio.run(orchestrator.run("sample_audio.wav", "sample_video.mp4"))
    print(json.dumps(result, indent=2))
