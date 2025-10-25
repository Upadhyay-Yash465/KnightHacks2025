from agent.tools.voice_agent import analyze_voice
from agent.tools.transcript_agent import analyze_transcript_local
from agent.tools.body_agent import analyze_body

def run_agents(audio_path=None, video_path=None, transcript=None) -> dict:
    results = {}

    if audio_path:
        results["voice"] = analyze_voice(audio_path)
    if transcript:
        results["transcript"] = analyze_transcript_local(transcript)
    if video_path:
        results["body"] = analyze_body(video_path)

    return results

