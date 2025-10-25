# Running Public Speaking Coach on Jupyter Notebook with AMD Cloud Agents

## 📓 Quick Start

### Option 1: Open Existing Notebook
```bash
cd backend
jupyter notebook Public_Speaking_Coach_AMD_Agent.ipynb
```

### Option  Penal 2: Create New Notebook
1. Start Jupyter: `jupyter notebook`
2. Create new Python 3 notebook
3. Copy cells from examples below

## 🔧 Setup in Notebook

### Cell 1: Install Dependencies
```python
!pip install fastapi uvicorn faster-whisper firebase-admin aiofiles python-multipart pydantic
```

### Cell 2: Imports
```python
import os
import asyncio
from typing import Dict, Any

# AMD Cloud Agent
from agent.main_agent import run_agent, get_agent
from agent.tools.adk_nlp_tool import analyze_transcript_with_adk

# Firebase
from utils.firebase_utils import initialize_firebase, save_to_firestore

print("✅ Imports successful!")
```

### Cell 3: Initialize
```python
# Initialize Firebase
initialize_firebase()

# Get AMD Agent
agent = get_agent()
print(f"✅ Agent ready! Tools: {list(agent.tools.keys())}")
```

## 🎯 Usage Examples

### Quick Analysis
```python
# Simple analysis
transcript = "Um, so I think that, like, you know, this is great!"
result = await run_agent(transcript, tool_name="adk_nlp_analysis")

print(f"Filler Count: {result['filler_count']}")
print(f"Clarity Score: {result['clarity_score']}/10")
```

### Save to Firestore
```python
async def analyze_and_save(text: str, user_id: str = "notebook_user"):
    result = await run_agent(text, tool_name="adk_nlp_analysis")
    firestore_id = save_to_firestore(text, result, user_id)
    return {**result, "firestore_id": firestore_id}

# Use it
full_result = await analyze_and_save(transcript)
print(f"Saved with ID: {full_result['firestore_id']}")
```

### Batch Processing
```python
transcripts = [
    "Um, so this is great!",
    "Clear communication is essential.",
    "Like, you know, practice makes perfect."
]

async def batch_analyze(texts):
    results = []
    for text in texts:
        result = await run_agent(text, tool_name="adk_nlp_analysis")
        results.append(result)
    return results

results = await batch_analyze(transcripts)
for i, r in enumerate(results):
    print(f"Speech {i+1}: {r['clarity_score']}/10")
```

## 🚀 AMD Cloud Agent Integration

### Direct Tool Access
```python
# Use ADK NLP tool directly
from agent.tools.adk_nlp_tool import analyze_transcript_with_adk

result = analyze_transcript_with_adk("Your transcript here")
print(result)
```

### Agent API
```python
# Use full agent framework
agent = get_agent()

# Run analysis
transcript = "Um, so I think..."
result = await agent.run_analysis(transcript)

print(result)
```

## 📊 Visualizations

### Clarity Score Bar
```python
def show_score(score):
    filled = int(score)
    return "█" * filled + "░" * (10 - filled)

result = await run_agent(transcript, tool_name="adk_nlp_analysis")
print(f"Clarity: [{show_score(result['clarity_score'])}] {result['clarity_score']}/10")
```

### Filler Word Analysis
```python
from agent.tools.adk_nlp_tool import FILLER_WORDS

transcript = "Um, so I think that, like, you know..."
lower = transcript.lower()

for filler in FILLER_WORDS:
    count = lower.count(filler)
    if count > 0:
        print(f"{filler}: {count}")
```

## 🎨 Custom Analysis

### Create Custom Analyzer
```python
async def custom_analysis(text: str):
    # Get ADK analysis
    adk_result = await run_agent(text, tool_name="adk_nlp_analysis")
    
    # Add custom metrics
    word_count = len(text.split())
    char_count = len(text)
    
    return {
        **adk_result,
        "word_count": word_count,
        "char_count": char_count,
        "avg_word_length": char_count / word_count if word_count > 0 else 0
    }

result = await custom_analysis(transcript)
print(result)
```

## 🔗 Integration with FastAPI

### Run Backend from Notebook
```python
import subprocess
import time

# Start FastAPI server
server = subprocess.Popen(['python', 'main.py'])

# Wait for server to start
time.sleep(3)

# Test API
import requests
response = requests.get('http://localhost:8000/health')
print(response.json())
```

## 📝 Tips

1. **Use async/await**: Always use `await` when calling agent functions
2. **Firebase credentials**: Make sure `firebase-key.json` is in the backend directory
3. **Environment variables**: Set `.env` file if needed
4. **Kernel restart**: Restart kernel if imports fail
5. **Error handling**: Wrap in try/except for production code

## 🐛 Troubleshooting

### Import Errors
```python
# Add backend to path
import sys
sys.path.append('/path/to/backend')
```

### Firebase Not Initialized
```python
# Explicit initialization
from utils.firebase_utils import initialize_firebase
initialize_firebase()
```

### Agent Not Found
```python
# Import directly
from agent.tools.adk_nlp_tool import analyze_transcript_with_adk
result = analyze_transcript_with_adk(text)
```

## 📚 Next Steps

- Deploy to AMD Cloud: See `amd.yaml` configuration
- Extend analysis: Add custom NLP tools
- Create visualizations: Use matplotlib for charts
- Export results: Save to CSV/JSON

## 🤝 Support

See `README.md` for full documentation and API reference.

