import subprocess
import json
import sys

MCP_COMMAND = ["node", "dist/src/index.js"]


def start_mcp():
    try:
        proc = subprocess.Popen(MCP_COMMAND, stdin=subprocess.PIPE, stdout=subprocess.PIPE, text=True)
    except FileNotFoundError:
        print("Hmm, can't find the MCP server. Is node installed and the project built?")
        sys.exit(1)

    # say hello to MCP
    proc.stdin.write(json.dumps({
        "jsonrpc": "2.0", "id": 1, "method": "initialize",
        "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "lpi-agent", "version": "1.0"}}
    }) + "\n")
    proc.stdin.flush()
    proc.stdout.readline()

    proc.stdin.write(json.dumps({"jsonrpc": "2.0", "method": "notifications/initialized"}) + "\n")
    proc.stdin.flush()

    return proc


def ask_tool(proc, tool_name, question, call_id):
    params = {"query": question} if tool_name == "query_knowledge" else {}

    proc.stdin.write(json.dumps({
        "jsonrpc": "2.0", "id": call_id, "method": "tools/call",
        "params": {"name": tool_name, "arguments": params}
    }) + "\n")
    proc.stdin.flush()

    try:
        reply = json.loads(proc.stdout.readline())
    except json.JSONDecodeError:
        print(f"  Got a weird response from {tool_name}, skipping it.")
        return None

    if "error" in reply:
        print(f"  {tool_name} ran into an issue: {reply['error']}")
        return None

    for block in reply.get("result", {}).get("content", []):
        if block.get("type") == "text":
            return block["text"]

    return None


def pick_tools(question):
    q = question.lower()
    tools = ["smile_overview"]  # always good to start with the basics

    if any(w in q for w in ["case", "example", "real", "industry"]):
        tools.append("get_case_studies")
    else:
        tools.append("query_knowledge")

    return tools


def main():
    print("Hey! LPI Agent here, ask me anything.\n")

    question = input("Your question: ").strip()
    if not question:
        print("You didn't type anything — try again!")
        sys.exit(1)

    tools = pick_tools(question)
    print(f"\nAlright, I'll use these tools: {tools}")

    proc = start_mcp()
    answers = {}

    try:
        print("\nLet me fetch that for you...\n")
        for i, tool in enumerate(tools):
            print(f"  Checking {tool}...")
            result = ask_tool(proc, tool, question, i + 2)
            if result:
                answers[tool] = result
                print(f"  Got it!")
            else:
                print(f"  Nothing came back from that one.")
    except Exception as e:
        print(f"Something went wrong mid-way: {e}")
    finally:
        proc.stdin.close()
        proc.wait()

    if not answers:
        print("\nSorry, none of the tools returned anything useful. Try rephrasing your question?")
        sys.exit(1)

    # put it all together
    everything   = " ".join(answers.values())
    word_count   = len(everything.split())

    print("\n" + "="*45)
    print("Here's what I found")
    print("="*45)

    print(f"\nI looked into this using {len(answers)} tools based on your question.")

    print("\nQuick summary:")
    print(f"  - Pulled {word_count} words worth of info")
    print(f"  - Sources: {' + '.join(answers.keys())}")
    print(f"  - Gist: {everything[:200]}...")

    print("\nFull details:")
    for tool, output in answers.items():
        print(f"\n[{tool}]\n{output}")
        print("-" * 40)

    print("\nTools I used:")
    for tool in answers:
        print(f"  • {tool}")

    print("\n" + "="*45)


if __name__ == "__main__":
    main()
