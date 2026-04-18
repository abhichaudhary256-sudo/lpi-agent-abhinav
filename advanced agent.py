# Simple LPI Agent: input → tools → MCP → LLM → answer

import subprocess
import json
import requests

# ── CONFIG ─────────────────────────────────────────
MCP_COMMAND  = ["node", "dist/src/index.js"]
OLLAMA_URL   = "http://localhost:11434/api/generate"
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
            "clientInfo": {"name": "simple-agent", "version": "1.0"}
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

    try:
        proc.stdin.write(json.dumps(payload) + "\n")
        proc.stdin.flush()

        line = proc.stdout.readline()
        response = json.loads(line)

        if "error" in response:
            print(f"[MCP error] {tool_name}: {response['error']}")
            return None

        return response.get("result")

    except Exception as e:
        print(f"[Error] {tool_name}: {e}")
        return None

# ── TOOL SELECTION ─────────────────────────────────
def select_tools(question):
    q = question.lower()
    tools = ["smile_overview"]

    if any(w in q for w in ["case", "example", "study"]):
        tools.append("get_case_studies")

    if any(w in q for w in ["what", "how", "why", "explain"]):
        tools.append("query_knowledge")

    # Ensure at least 2 tools
    if len(tools) < 2:
        tools.append("query_knowledge")

    return tools

# ── OLLAMA REQUEST ─────────────────────────────────
def ask_ollama(question, context):
    prompt = f"""
You are an AI agent using LPI tools.

Use ONLY the context below.

Format:

🧠 Reasoning
Explain how you used tool data

✅ Final Answer
Clear answer

📚 Sources
Mention tool names

--- CONTEXT ---
{context}

--- QUESTION ---
{question}
"""
    try:
        res = requests.post(
            OLLAMA_URL,
            json={"model": OLLAMA_MODEL, "prompt": prompt, "stream": False},
            timeout=60
        )
        return res.json().get("response", "")
    except Exception as e:
        return f"[Ollama error] {e}"

# ── MAIN FLOW ──────────────────────────────────────
def main():
    question = input("Ask your question: ").strip()
    if not question:
        return

    tools = select_tools(question)
    print(f"\n[Agent] Tools selected: {tools}\n")

    proc = start_mcp()
    initialize_mcp(proc)

    context_parts = []

    for tool in tools:
        print(f"[Agent] Calling {tool}...")

        params = {"query": question} if tool == "query_knowledge" else {}
        result = call_tool(proc, tool, params)

        if result and "content" in result:
            for block in result["content"]:
                if block.get("type") == "text":
                    context_parts.append(f"[{tool}]\n{block['text']}")

    proc.stdin.close()
    proc.wait()

    if not context_parts:
        print("No data from tools.")
        return

    context = "\n\n".join(context_parts)

    print("\n[Agent] Generating answer...\n")
    answer = ask_ollama(question, context)

    print("\n==============================")
    print("🤖 LPI AGENT RESPONSE")
    print("==============================\n")
    print(answer)


if __name__ == "__main__":
    main()
