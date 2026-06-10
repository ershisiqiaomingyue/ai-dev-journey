# phase1/01_hello_agent.py
#
# What:   First LLM API call - send a message, print the reply and token usage.
# Run:    python phase1/01_hello_agent.py
# Before: 1. Copy .env.example to .env
#         2. Fill in your LLM_API_KEY in .env
#         3. pip install anthropic python-dotenv

import os
import sys
from pathlib import Path

from dotenv import load_dotenv
import anthropic

# --- Load config ---
# .env is at project root, this script is in phase1/
env_path = Path(__file__).resolve().parent.parent / ".env"
load_dotenv(env_path)

api_key = os.getenv("LLM_API_KEY")
base_url = os.getenv("LLM_BASE_URL", "https://api.anthropic.com")
model = os.getenv("LLM_MODEL", "claude-sonnet-4-20250514")

if not api_key or api_key == "your-api-key-here":
    print("[ERROR] LLM_API_KEY not set.")
    print("  Please edit the .env file and fill in your actual API Key.")
    print("  File location:", env_path)
    sys.exit(1)

# --- Create client ---
client = anthropic.Anthropic(api_key=api_key, base_url=base_url)

# --- Send request ---
try:
    response = client.messages.create(
        model=model,
        max_tokens=1024,
        system="You are a helpful AI assistant. Reply in Chinese.",
        messages=[
            {"role": "user", "content": "Hello! Please introduce yourself briefly and tell me what you can do."},
        ],
    )
except anthropic.AuthenticationError:
    print("[ERROR] Authentication failed - API Key is invalid.")
    print("  Please check your LLM_API_KEY in .env")
    sys.exit(1)
except anthropic.APIConnectionError as e:
    print(f"[ERROR] Connection failed - cannot reach {base_url}")
    print(f"  Details: {e}")
    sys.exit(1)

# --- Print result ---
reply = response.content[0].text
usage = response.usage

print("=" * 50)
print("Model reply:")
print("-" * 50)
print(reply)
print("=" * 50)
print("Token usage:")
print(f"  Input tokens:  {usage.input_tokens}")
print(f"  Output tokens: {usage.output_tokens}")
print(f"  Total tokens:  {usage.input_tokens + usage.output_tokens}")
print("=" * 50)
