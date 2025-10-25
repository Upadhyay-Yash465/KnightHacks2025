"""
Quick start script for using AMD Cloud Agent in Jupyter Notebook or Python.
Run this in a Jupyter cell or as a standalone script.
"""

import asyncio
from agent.main_agent import run_agent, get_agent
from agent.tools.adk_nlp_tool import analyze_transcript_with_adk
from utils.firebase_utils import initialize_firebase, save_to_firestore


def quick_analysis(transcript: str):
    """Quick analysis without async."""
    return analyze_transcript_with_adk(transcript)


async def analyze_with_agent(transcript: str, user_id: str = "notebook_user"):
    """Run full agent analysis and save to Firestore."""
    # Run AMD Agent
    result = await run_agent(transcript, tool_name="adk_nlp_analysis")
    
    # Save to Firestore
    firestore_id = save_to_firestore(transcript, result, user_id)
    
    return {
        **result,
        "firestore_id": firestore_id
    }


async def batch_analyze(transcripts: list):
    """Analyze multiple transcripts."""
    results = []
    for text in transcripts:
        result = await run_agent(text, tool_name="adk_nlp_analysis")
        results.append({
            "transcript": text[:50] + "..." if len(text) > 50 else text,
            "filler_count": result['filler_count'],
            "clarity_score": result['clarity_score'],
            "summary": result['summary']
        })
    return results


if __name__ == "__main__":
    # Initialize Firebase
    initialize_firebase()
    
    # Example usage
    sample = "Um, so I think that, like, you know, public speaking is really important."
    
    # Quick analysis
    print("Quick Analysis:")
    quick_result = quick_analysis(sample)
    print(f"Fillers: {quick_result['filler_count']}, Score: {quick_result['clarity_score']}/10")
    
    # Full agent analysis
    print("\nAMD Agent Analysis:")
    result = asyncio.run(analyze_with_agent(sample))
    print(f"Fillers: {result['filler_count']}, Score: {result['clarity_score']}/10")
    print(f"Firestore ID: {result['firestore_id']}")

