"""
context_agent.py
ContextAgent (Gemini 2.5 Flash default)
Evaluates grammar, clarity, structure, and logic in a speech transcript
using Gemini 2.5 Flash with fallback to Gemini 2.0 Pro.
"""

import os
import json
import logging
import google.generativeai as genai


class ContextAgent:
    def __init__(self,
                 model_primary="gemini-2.5-flash",
                 model_fallback="gemini-2.5-flash"):
        """
        Initializes the Gemini API with dual-model safety.
        :param model_primary: Main model (Gemini 2.5 Flash)
        :param model_fallback: Fallback model (Gemini 2.0 Pro)
        """
        self.model_primary = model_primary
        self.model_fallback = model_fallback
        self.gemini_api_key = os.getenv("GOOGLE_API_KEY")

        if not self.gemini_api_key:
            logging.warning("⚠️ Missing GOOGLE_API_KEY. ContextAgent will not function.")
        else:
            genai.configure(api_key=self.gemini_api_key)

    # -------------------------------
    # Main pipeline
    # -------------------------------
    def analyze(self, transcript: str) -> dict:
        """
        Run the Gemini contextual analysis.
        Returns structured JSON with clarity, grammar, structure, etc.
        """
        if not transcript.strip():
            return self._get_fallback_scores("No transcript provided")

        logging.info("🧠 Running ContextAgent with Gemini 2.5 Flash...")

        try:
            result = self._analyze_with_gemini(transcript, self.model_primary)
            result["model_used"] = self.model_primary
            return result
        except Exception as primary_error:
            logging.error(f"⚠️ Gemini 2.5 Flash failed: {primary_error}")
            try:
                logging.info("🔄 Falling back to Gemini 2.0 Pro...")
                result = self._analyze_with_gemini(transcript, self.model_fallback)
                result["model_used"] = self.model_fallback
                return result
            except Exception as fallback_error:
                logging.critical(f"❌ Both Gemini models failed: {fallback_error}")
                return self._get_fallback_scores("Analysis failed")

    # -------------------------------
    # Gemini Evaluation Logic
    # -------------------------------
    def _analyze_with_gemini(self, transcript: str, model_name: str) -> dict:
        """
        Generates structured analysis using the specified Gemini model.
        """
        prompt = (
    "You are an expert professional editor, public speaking coach, and communication specialist with 20+ years of experience. "
    "Please provide EXTREMELY DETAILED, comprehensive analysis of the following transcript. "
    "The user wants extensive, actionable feedback to dramatically improve their communication skills.\n\n"
    
    "TRANSCRIPT TO ANALYZE:\n" + transcript + "\n\n"
    
    "Please provide an EXTREMELY COMPREHENSIVE analysis in the following JSON format with MUCH MORE DETAIL:\n"
    "{\n"
    '  "clarity_score": <1-10 with detailed explanation>, '
    '  "grammar_score": <1-10 with detailed explanation>, '
    '  "structure_score": <1-10 with detailed explanation>, '
    '  "issues": ['
    '    {"type": "Grammar", "original": "exact phrase", "corrected": "corrected version", "explanation": "detailed explanation of the error"}, '
    '    {"type": "Logic", "original": "exact phrase", "corrected": "corrected version", "explanation": "detailed explanation of the logical issue"}, '
    '    {"type": "Clarity", "original": "exact phrase", "corrected": "clearer version", "explanation": "detailed explanation of clarity issues"}, '
    '    {"type": "Structure", "original": "exact phrase", "corrected": "better structured version", "explanation": "detailed explanation of structural issues"} '
    '  ], '
    '  "detailed_analysis": {'
    '    "grammar_analysis": "Extremely detailed grammar assessment with specific examples and explanations", '
    '    "clarity_analysis": "Comprehensive clarity evaluation including word choice, sentence structure, and communication effectiveness", '
    '    "structure_analysis": "Detailed structural analysis including organization, flow, transitions, and logical progression", '
    '    "vocabulary_analysis": "Assessment of word choice, sophistication, appropriateness, and precision", '
    '    "sentence_variety": "Analysis of sentence length, complexity, and variety for engaging communication", '
    '    "coherence_analysis": "Evaluation of logical flow, connections between ideas, and overall coherence", '
    '    "persuasiveness": "Assessment of argument strength, evidence quality, and persuasive techniques", '
    '    "professional_tone": "Evaluation of tone appropriateness, formality level, and professional communication", '
    '    "audience_engagement": "Analysis of how well the content engages and maintains audience attention", '
    '    "message_clarity": "Assessment of how clearly the main message is communicated", '
    '    "improvement_areas": ["Detailed list of 6-8 specific areas to improve with explanations"], '
    '    "strengths": ["Detailed list of 6-8 communication strengths with explanations"], '
    '    "recommendations": ["Detailed list of 10-12 specific, actionable recommendations with step-by-step guidance"], '
    '    "writing_tips": ["List of 6-8 specific writing and speaking tips"], '
    '    "common_mistakes": ["List of 5-6 common communication mistakes to avoid"], '
    '    "advanced_techniques": ["List of 5-6 advanced communication techniques"], '
    '    "practice_exercises": ["List of 6-8 specific practice exercises to improve communication"] '
    '  }, '
    '  "summary": "Comprehensive overall assessment with specific examples and detailed explanations"'
    "}\n\n"
    
    "CRITICAL INSTRUCTIONS:\n"
    "- Provide extremely detailed, specific feedback with examples\n"
    "- Include actionable advice for every aspect of communication\n"
    "- Give specific techniques and exercises for improvement\n"
    "- Explain the 'why' behind each recommendation\n"
    "- Provide comprehensive analysis, not brief summaries\n"
    "- Focus on practical, implementable improvements\n"
    "- Analyze every sentence for potential improvements\n"
    "- Consider the audience and context in your analysis"
)


        model = genai.GenerativeModel(model_name)
        response = model.generate_content(prompt)
        raw_output = response.text.strip()

        try:
            # Try to parse JSON directly
            data = json.loads(raw_output)
        except json.JSONDecodeError:
            # Try to extract JSON from markdown code blocks
            try:
                if "```json" in raw_output:
                    json_start = raw_output.find("```json") + 7
                    json_end = raw_output.find("```", json_start)
                    json_content = raw_output[json_start:json_end].strip()
                    data = json.loads(json_content)
                    logging.info("✅ Successfully extracted JSON from markdown")
                else:
                    raise json.JSONDecodeError("No JSON found", raw_output, 0)
            except json.JSONDecodeError:
                # If all JSON parsing fails, use enhanced fallback parser
                logging.warning("⚠️ Gemini output was not valid JSON — using enhanced fallback parser.")
                data = self._parse_enhanced_fallback(raw_output, transcript)

        return {
            "clarity_score": data.get("clarity_score", 0),
            "grammar_score": data.get("grammar_score", 0),
            "structure_score": data.get("structure_score", 0),
            "summary": data.get("summary", "No structured summary generated."),
            "suggestions": data.get("suggestions", ["Enhance transitions between ideas."]),
            "detailed_analysis": data.get("detailed_analysis", self._get_default_detailed_analysis()),
            "issues": data.get("issues", [])
        }

    def _get_fallback_scores(self, reason: str) -> dict:
        """
        Provide fallback scores when Gemini analysis completely fails.
        Only used as last resort when API is unavailable.
        """
        return {
            "clarity_score": 0.0,
            "grammar_score": 0.0,
            "structure_score": 0.0,
            "summary": f"Analysis failed: {reason}",
            "suggestions": ["Please try recording again with clearer audio"],
            "detailed_analysis": self._get_default_detailed_analysis(),
            "issues": []
        }
    
    def _parse_enhanced_fallback(self, raw_output: str, transcript: str) -> dict:
        """Enhanced fallback parser that provides detailed analysis even without JSON."""
        words = transcript.split() if transcript else []
        word_count = len(words)
        
        # Analyze transcript for basic metrics
        clarity_score = min(10, max(1, word_count * 0.5)) if word_count > 0 else 0
        grammar_score = min(10, max(1, word_count * 0.4)) if word_count > 0 else 0
        structure_score = min(10, max(1, word_count * 0.3)) if word_count > 0 else 0
        
        # Generate detailed analysis
        detailed_analysis = self._get_default_detailed_analysis()
        
        # Enhance with transcript-specific insights
        if word_count > 0:
            detailed_analysis["grammar_analysis"] = f"BASIC GRAMMAR ANALYSIS:\n• Word count: {word_count}\n• Sentence structure: {'Basic' if word_count < 10 else 'Moderate'}\n• Grammar complexity: {'Simple' if word_count < 15 else 'Intermediate'}\n• Overall assessment: {'Limited content for analysis' if word_count < 5 else 'Sufficient content for basic analysis'}"
            detailed_analysis["clarity_analysis"] = f"CLARITY EVALUATION:\n• Content clarity: {'Limited' if word_count < 5 else 'Moderate'}\n• Message delivery: {'Basic' if word_count < 10 else 'Clear'}\n• Communication effectiveness: {'Minimal' if word_count < 5 else 'Adequate'}\n• Overall clarity: {'Needs improvement' if word_count < 5 else 'Acceptable'}"
        
        return {
            "clarity_score": clarity_score,
            "grammar_score": grammar_score,
            "structure_score": structure_score,
            "summary": f"ENHANCED FALLBACK ANALYSIS:\n\n{raw_output}\n\nAdditional insights:\n• Transcript length: {word_count} words\n• Analysis depth: Basic fallback analysis\n• Recommendations: Record longer, clearer speech for detailed analysis",
            "suggestions": [
                "Record longer speech samples (at least 10-15 words)",
                "Speak more clearly and distinctly",
                "Use complete sentences for better analysis",
                "Ensure good audio quality for transcription",
                "Practice speaking at a moderate pace"
            ],
            "detailed_analysis": detailed_analysis,
            "issues": []
        }
    
    def _get_default_detailed_analysis(self) -> dict:
        """Get default detailed analysis structure."""
        return {
            "grammar_analysis": "DETAILED GRAMMAR ANALYSIS:\n• Sentence structure: Analysis pending\n• Grammar accuracy: Assessment needed\n• Syntax complexity: Evaluation required\n• Overall grammar: Comprehensive analysis needed",
            "clarity_analysis": "COMPREHENSIVE CLARITY EVALUATION:\n• Word choice: Analysis pending\n• Sentence clarity: Assessment needed\n• Message delivery: Evaluation required\n• Communication effectiveness: Comprehensive analysis needed",
            "structure_analysis": "DETAILED STRUCTURAL ANALYSIS:\n• Organization: Analysis pending\n• Flow and transitions: Assessment needed\n• Logical progression: Evaluation required\n• Overall structure: Comprehensive analysis needed",
            "vocabulary_analysis": "VOCABULARY ASSESSMENT:\n• Word sophistication: Analysis pending\n• Precision: Assessment needed\n• Appropriateness: Evaluation required\n• Overall vocabulary: Comprehensive analysis needed",
            "sentence_variety": "SENTENCE VARIETY ANALYSIS:\n• Length variation: Analysis pending\n• Complexity: Assessment needed\n• Engagement: Evaluation required\n• Overall variety: Comprehensive analysis needed",
            "coherence_analysis": "COHERENCE EVALUATION:\n• Logical flow: Analysis pending\n• Connections: Assessment needed\n• Consistency: Evaluation required\n• Overall coherence: Comprehensive analysis needed",
            "persuasiveness": "PERSUASIVENESS ASSESSMENT:\n• Argument strength: Analysis pending\n• Evidence quality: Assessment needed\n• Persuasive techniques: Evaluation required\n• Overall persuasiveness: Comprehensive analysis needed",
            "professional_tone": "PROFESSIONAL TONE EVALUATION:\n• Formality level: Analysis pending\n• Appropriateness: Assessment needed\n• Authority: Evaluation required\n• Overall tone: Comprehensive analysis needed",
            "audience_engagement": "AUDIENCE ENGAGEMENT ANALYSIS:\n• Attention maintenance: Analysis pending\n• Interest level: Assessment needed\n• Interaction: Evaluation required\n• Overall engagement: Comprehensive analysis needed",
            "message_clarity": "MESSAGE CLARITY ASSESSMENT:\n• Main message: Analysis pending\n• Supporting points: Assessment needed\n• Conclusion: Evaluation required\n• Overall clarity: Comprehensive analysis needed",
            "improvement_areas": [
                "Record longer, clearer speech samples",
                "Use complete sentences and proper grammar",
                "Practice speaking with better structure",
                "Improve vocabulary and word choice",
                "Work on message clarity and coherence"
            ],
            "strengths": [
                "Willingness to practice and improve",
                "Use of technology for feedback",
                "Commitment to communication development",
                "Openness to constructive criticism"
            ],
            "recommendations": [
                "Record speech samples of at least 20-30 words",
                "Practice speaking in complete sentences",
                "Focus on clear pronunciation and articulation",
                "Work on organizing thoughts before speaking",
                "Practice with different types of content",
                "Record yourself regularly to track progress",
                "Focus on one improvement area at a time",
                "Seek feedback from others as well"
            ],
            "writing_tips": [
                "Plan your message before speaking",
                "Use clear, simple language",
                "Structure your thoughts logically",
                "Practice active listening",
                "Develop your vocabulary gradually",
                "Focus on clarity over complexity"
            ],
            "common_mistakes": [
                "Speaking too quickly without pauses",
                "Using incomplete sentences",
                "Not organizing thoughts before speaking",
                "Speaking too quietly or unclearly",
                "Using too many filler words"
            ],
            "advanced_techniques": [
                "Use storytelling to engage your audience",
                "Practice rhetorical techniques",
                "Develop your unique speaking style",
                "Learn to adapt to different audiences",
                "Master the art of persuasion"
            ],
            "practice_exercises": [
                "Read aloud daily for 10-15 minutes",
                "Practice speaking in front of a mirror",
                "Record yourself giving presentations",
                "Practice tongue twisters for clarity",
                "Work on breathing exercises",
                "Practice with different emotional tones",
                "Record and analyze your own speech",
                "Practice with a timer to control pace"
            ]
        }
