# Phase 1: Basics & Hand-written Agent (Week 1-4)

## Goal
Understand LLM API, Function Calling, and ReAct pattern by writing everything from scratch.

## Scripts

| File | Week | What you learn |
|------|------|---------------|
| `01_hello_agent.py` | W1 | First API call, token usage, system prompt |
| `02_chat_loop.py` | W2 | Multi-turn conversation, context window |
| `03_function_call.py` | W2 | Tool use via Function Calling |
| `04_react_agent.py` | W3 | ReAct loop: Reason -> Act -> Observe -> repeat |
| `05_file_assistant.py` | W4 | Complete project: an Agent that can read/write files |

## How to run

```bash
# 1. Install dependencies (from project root)
pip install anthropic python-dotenv

# 2. Configure API key
cp .env.example .env
# Edit .env and fill in your LLM_API_KEY

# 3. Run
python phase1/01_hello_agent.py
```

## Key concepts

- **System prompt**: Instructions given to the model at the start of every conversation
- **Token**: The basic unit of text that LLMs process (roughly 1 token = 0.75 English words or 0.5 Chinese characters)
- **Temperature**: Controls randomness (0 = deterministic, 1 = creative)
- **Function Calling**: A structured way for the model to request tool execution
