# LPI Smart Agent — Level 3

import subprocess
import json

MCP_COMMAND = ["node", "dist/src/index.js"]


def start_mcp():
    return subprocess.Popen(
        MCP_COMMAND,
        stdin=subprocess.PIPE,
        stdout=subprocess.PIPE,
        stderr=subprocess.DEVNULL,
        text=True
    )


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

    proc.stdin.write(json.dumps({
        "jsonrpc": "2.0",
        "method": "notifications/initialized"
    }) + "\n")
    proc.stdin.flush()


def call_tool(proc, tool_name, args=None):
    payload = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "tools/call",
        "params": {
            "name": tool_name,
            "arguments": args or {}
        }
    }

    try:
        proc.stdin.write(json.dumps(payload) + "\n")
        proc.stdin.flush()
        response = json.loads(proc.stdout.readline())
        return response.get("result", {})
    except Exception as e:
        print(f"⚠️ Error calling {tool_name}: {e}")
        return None


def main():
    print("🤖 LPI MCP Agent\n")

    try:
        question = input("Enter your question: ").strip()
        if not question:
            raise ValueError("Empty input")
    except Exception as e:
        print(f"⚠️ Error: {e}")
        return

    proc = start_mcp()
    initialize_mcp(proc)

    tools = ["smile_overview", "query_knowledge"]

    print(f"\n[Agent] Using tools: {tools}\n")

    results = []

    for tool in tools:
        print(f"[Agent] Calling {tool}...")
        params = {"query": question} if tool == "query_knowledge" else {}

        res = call_tool(proc, tool, params)

        if res and "content" in res:
            for block in res["content"]:
                if block.get("type") == "text":
                    results.append(block["text"])

    proc.stdin.close()
    proc.wait()

    if not results:
        print("⚠️ No data received from tools")
        return

    print("\n==============================")
    print("🤖 LPI AGENT RESPONSE")
    print("==============================\n")

    print("🧠 Reasoning:")
    print("Used smile_overview and query_knowledge tools from LPI MCP server.\n")

    print("✅ Final Answer:")
    for r in results:
        print("-", r[:200], "...")

    print("\n📚 Sources:")
    print("- smile_overview")
    print("- query_knowledge")


if __name__ == "__main__":
    main()
