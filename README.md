# LPI Agent — Level 3

A simple agent that answers your questions about the SMILE / LPI framework.
It calls real LPI MCP tools, combines what they return, and gives you a clear cited answer. No frameworks. Single file.

---

## How It Works

```
Your question
     ↓
Pick tools (keyword match)
     ↓
Call real MCP tools → get data
     ↓
Combine + summarize results
     ↓
🧠 Reasoning / ✅ Answer / 📚 Sources
```

Tools used:

| Tool | When it's called |
|---|---|
| `smile_overview` | Always — good baseline for any question |
| `get_case_studies` | When you ask about examples, cases, or real-world use |
| `query_knowledge` | Everything else — how, what, why questions |

---

## Explainability

Every response has three parts:

| Section | What it shows |
|---|---|
| 🧠 Reasoning | How many tools were used and why |
| ✅ Combined Answer | Full output from each tool, clearly labelled |
| 📚 Sources | Exact tool names and how much data each returned |

Tool selection is plain keyword matching — no hidden logic, no black box.

---

## Setup

**1. MCP Server (Node.js)**
```bash
npm install
npm run build
```

**2. Python**
```bash
# No extra packages needed — uses stdlib only
python agent.py
```

---

## Run

```bash
python agent.py
```

Then type your question when prompted:

```
Hey! LPI Agent here, ask me anything.

Your question: What is SMILE and show me a case study?

[Agent] Tools selected: ['smile_overview', 'get_case_studies']

  Checking smile_overview...
  ✓ Got it!
  Checking get_case_studies...
  ✓ Got it!

=============================================
Here's what I found
=============================================

🧠 Reasoning:
Queried 2 LPI tools to answer: 'What is SMILE and show me a case study?'

✅ Combined Answer:
  - Pulled 284 words across 2 tools
  - Sources: smile_overview + get_case_studies
  - Gist: SMILE stands for...

📚 Tools Used:
  • smile_overview
  • get_case_studies
```

---

## Error Handling

| Situation | What happens |
|---|---|
| Empty question | Tells you to try again |
| MCP server not found | Tells you to check node / build |
| Bad response from tool | Skips that tool, continues |
| No data from any tool | Exits cleanly with a helpful message |
| Unexpected crash | Caught — MCP process still cleaned up |

---

## Requirements

- Python 3.7+
- Node.js
- LPI MCP server built at `dist/src/index.js`

---

## Submission

Built for **Track A — Level 3**.

- ✅ Accepts user input
- ✅ Calls at least 2 real LPI tools via MCP
- ✅ Combines and summarizes results
- ✅ Cites every tool used with full output shown
