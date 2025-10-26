#!/usr/bin/env python3
"""
update_openai_key.py
Quick script to update just the OpenAI API key
"""

import os
from pathlib import Path

def update_openai_key():
    """Update OpenAI API key in .env file"""
    env_file = Path(".env")
    
    if not env_file.exists():
        print("❌ .env file not found!")
        return
    
    print("🔑 OpenAI API Key Update")
    print("=" * 30)
    print("Get your API key from: https://platform.openai.com/api-keys")
    
    new_key = input("\nEnter your OpenAI API key: ").strip()
    
    if not new_key or len(new_key) < 10:
        print("❌ Invalid API key")
        return
    
    # Read current .env file
    with open(env_file, 'r') as f:
        lines = f.readlines()
    
    # Update OpenAI key line
    updated_lines = []
    for line in lines:
        if line.startswith("OPENAI_API_KEY="):
            updated_lines.append(f"OPENAI_API_KEY={new_key}\n")
        else:
            updated_lines.append(line)
    
    # Write back to file
    with open(env_file, 'w') as f:
        f.writelines(updated_lines)
    
    print("✅ OpenAI API key updated successfully!")
    print("\n🚀 You can now run: python main.py")

if __name__ == "__main__":
    update_openai_key()
