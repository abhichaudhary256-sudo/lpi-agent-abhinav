# LPI Agent — Level 3

## Overview

A simple AI agent that answers questions about the SMILE / LPI framework.
It fetches real data from an LPI MCP server, combines it, and generates a structured answer using a local LLM (Ollama). No frameworks. Single file.

## Project Versions

### 1. Basic Agent (agent.py)
- Simple version for evaluation
- Uses 2 LPI tools
- No external dependencies

### 2. Advanced Agent (advanced_agent.py)
- Uses MCP server
- Uses Ollama (local LLM)
- Dynamic tool selection
- More intelligent reasoning
---

## How It Works

```
Your question
     ↓
Select tools (keyword match)
     ↓
Call MCP tools → get data
     ↓
Send data + question to Ollama
     ↓
🧠 Reasoning / ✅ Answer / 📚 Sources
```

Tools used:
- `smile_overview` — always called
- `query_knowledge` — for how/what/why questions
- `get_case_studies` — when you ask about examples or cases

---

## Explainability

Every response has three parts:

| Section | What it shows |
|---|---|
| 🧠 Reasoning | How the agent used the data |
| ✅ Final Answer | Direct answer to your question |
| 📚 Sources | Which tools were used |

Tool selection is plain keyword matching — no hidden LLM logic.

---

## Setup

**1. MCP Server (Node.js)**
```bash
npm install
npm run build
```

**2. Ollama**

Download from [ollama.com](https://ollama.com), then:
```bash
ollama pull llama3
ollama serve
```

**3. Python**
```bash
pip install requests
```

---

## Run

```bash
python agent.py
```

Then type your question when prompted.

```
Ask your question: What is SMILE and show me a case study?

[Agent] Tools selected: ['smile_overview', 'get_case_studies']
[Agent] Calling smile_overview...
[Agent] Calling get_case_studies...
[Agent] Generating answer...

==============================
🤖 LPI AGENT RESPONSE
==============================

🧠 Reasoning ...
✅ Final Answer ...
📚 Sources ...
```

To switch models, edit the top of `agent.py`:
```python
OLLAMA_MODEL = "llama3"   # or mistral, phi3, gemma2...
```
