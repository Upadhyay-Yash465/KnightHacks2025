"""
AMD Cloud Agent main implementation.
Orchestrates ADK NLP analysis using AMD Cloud Agents framework.
"""

from typing import Dict, Any
import asyncio
from agent.tools.adk_nlp_tool import adk_nlp_analysis


class AMDAgent:
    """
    AMD Cloud Agent wrapper for running NLP analysis.
    This class manages the agent lifecycle and tool execution.
    """
    
    def __init__(self):
        """Initialize the AMD Agent."""
        self.tools = {
            "adk_nlp_analysis": adk_nlp_analysis
        }
    
    async def run_analysis(self, transcript: str) -> Dict[str, Any]:
        """
        Run NLP analysis on transcript using ADK tools.
        
        Args:
            transcript: The transcribed text to analyze
            
        Returns:
            Analysis results dictionary
        """
        # Execute the ADK NLP analysis tool
        result = await self.tools["adk_nlp_analysis"](transcript)
        
        return result


# Global agent instance
_agent_instance = None


def get_agent() -> AMDAgent:
    """Get or create the global AMD agent instance."""
    global _agent_instance
    
    if _agent_instance is None:
        _agent_instance = AMDAgent()
    
    return _agent_instance


async def run_agent(input_data: str, tool_name: str = "adk_nlp_analysis") -> Dict[str, Any]:
    """
    Run the AMD agent with specified input and tool.
    
    Args:
        input_data: Input data (transcript text)
        tool_name: Name of the tool to execute
        
    Returns:
        Tool execution results
    """
    agent = get_agent()
    
    if tool_name == "adk_nlp_analysis":
        return await agent.run_analysis(input_data)
    else:
        raise ValueError(f"Unknown tool: {tool_name}")

