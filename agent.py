# LPI Smart Agent — Level 3 

import subprocess
import json
import requests

# ── CONFIG ─────────────────────────────────────────
MCP_COMMAND = ["node", "dist/src/index.js"]
OLLAMA_URL = "http://localhost:11434/api/generate"
OLLAMA_MODEL = "llama3"


# ── START MCP SERVER ───────────────────────────────
def start_mcp():
    return subprocess.Popen(
        MCP_COMMAND,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )


# ── INITIALIZE MCP ─────────────────────────────────
def initialize_mcp(proc):
    init_req = {
        "jsonrpc": "2.0",
        "id": 0,
        "method": "initialize",
        "params": {
            "protocolVersion": "2024-11-05",
            "capabilities": {},
            "clientInfo": {"name": "lpi-agent", "version": "1.0"}
        }
    }

    proc.stdin.write(json.dumps(init_req) + "\n")
    proc.stdin.flush()
    proc.stdout.readline()

    notif = {"jsonrpc": "2.0", "method": "notifications/initialized"}
    proc.stdin.write(json.dumps(notif) + "\n")
    proc.stdin.flush()


# ── CALL MCP TOOL ──────────────────────────────────
def call_tool(proc, tool_name, params=None):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": params or {}
        }
    }

    proc.stdin.write(json.dumps(payload) + "\n")
    proc.stdin.flush()

    response = json.loads(proc.stdout.readline())

    if "error" in response:
        print(f"[Error] {tool_name}: {response['error']}")
        return None

    return response.get("result")


# ── SMART TOOL SELECTION ───────────────────────────
def select_tools(question):
    q = question.lower()
    tools = []

    if any(w in q for w in ["case", "example", "industry"]):
        tools.append("get_case_studies")

    if any(w in q for w in ["what", "how", "why", "explain"]):
        tools.append("query_knowledge")

    if any(w in q for w in ["step", "process", "phase"]):
        tools.append("get_methodology_step")

    # Ensure at least 2 tools
    if len(tools) < 2:
        tools = ["get_case_studies", "query_knowledge"]

    return tools


# ── EXTRACT TEXT FROM MCP RESPONSE ─────────────────
def extract_text(result):
    texts = []

    if result and "content" in result:
        for block in result["content"]:
            if block.get("type") == "text":
                texts.append(block["text"])

    return "\n".join(texts)


# ── ASK OLLAMA ─────────────────────────────────────
def ask_ollama(question, context):
    context = context[:3000]  # prevent overload

    prompt = f"""
You are an AI agent using LPI tools.

Use ONLY the provided context.

Answer clearly.

Format:

🧠 Reasoning
Explain how tools were used

✅ Final Answer
Give structured explanation

📚 Sources
Mention tool names

--- CONTEXT ---
{context}

--- QUESTION ---
{question}
"""

    res = requests.post(
        OLLAMA_URL,
        json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
        timeout=60
    )

    return res.json().get("response", "")


# ── MAIN FLOW ──────────────────────────────────────
def main():
    print("🤖 LPI Smart Agent (Level 3 - PRO)\n")

    question = input("Enter your question: ").strip()
    if not question:
        print("⚠️ Enter a valid question")
        return

    print("\n[Agent] Analyzing query...\n")

    tools = select_tools(question)
    print(f"[Agent] Selected tools: {tools}\n")

    proc = start_mcp()
    initialize_mcp(proc)

    context_parts = []

    print("[Agent] Fetching real data from MCP...\n")

    for tool in tools:
        params = {"query": question} if tool == "query_knowledge" else {}

        result = call_tool(proc, tool, params)
        text = extract_text(result)

        if text:
            context_parts.append(f"[{tool}]\n{text}")

    proc.stdin.close()
    proc.wait()

    if not context_parts:
        print("❌ No data from tools")
        return

    context = "\n\n".join(context_parts)

    print("[Agent] Generating answer using LLM...\n")

    answer = ask_ollama(question, context)

    print("\n==============================")
    print("🤖 LPI AGENT RESPONSE")
    print("==============================\n")
    print(answer)


if __name__ == "__main__":
    main()
