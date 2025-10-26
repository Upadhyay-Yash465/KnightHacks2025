"""
config.py
Environment configuration loader for AI Speech Coach
"""

import os
from pathlib import Path
from dotenv import load_dotenv

def load_environment():
    """Load environment variables from .env file"""
    # Get the project root directory (go up from src/config to project root)
    project_root = Path(__file__).parent.parent.parent
    
    # Look for .env file in env directory
    env_file = project_root / "env" / ".env"
    
    if env_file.exists():
        load_dotenv(env_file)
        print(f"✅ Loaded environment from {env_file}")
    else:
        print(f"⚠️  No .env file found at {env_file}")
        print("   Run 'python scripts/setup_env.py' to create one")
    
    # Check if API keys are set
    google_key = os.getenv("GOOGLE_API_KEY")
    openai_key = os.getenv("OPENAI_API_KEY")
    
    if not google_key:
        print("❌ GOOGLE_API_KEY not set")
    else:
        print("✅ GOOGLE_API_KEY is set")
    
    if not openai_key:
        print("❌ OPENAI_API_KEY not set")
    else:
        print("✅ OPENAI_API_KEY is set")
    
    return {
        "google_api_key": google_key,
        "openai_api_key": openai_key,
        "log_level": os.getenv("LOG_LEVEL", "INFO")
    }

# Load environment on import
config = load_environment()
