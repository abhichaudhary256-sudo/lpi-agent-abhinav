# LPI Smart Agent — Level 3
def get_case_studies(query):
    return f"Case Study: Real-world implementation of '{query}' showing practical applications."

def query_knowledge(query):
    return f"Knowledge: Core concepts and explanation of '{query}' based on LPI methodology."

def analyze_query(query):
    query = query.lower()

    tools = []

    if any(word in query for word in ["case", "example", "industry", "application"]):
        tools.append("get_case_studies")

    if any(word in query for word in ["what", "how", "why", "explain", "define"]):
        tools.append("query_knowledge")

    # Ensure at least 2 tools are always used
    if len(tools) < 2:
        tools = ["get_case_studies", "query_knowledge"]

    return tools

def process_results(query, results):
    reasoning = f"The query '{query}' was analyzed using multiple tools to ensure both practical and conceptual understanding."

    final_answer = "\n".join(results)

    sources = "\n".join([f"- {tool}" for tool in results.keys()])

    return reasoning, final_answer, sources

def main():
    print("🤖 LPI Smart Agent (Level 3 - Enhanced)\n")

    user_input = input("Enter your question: ").strip()

    if not user_input:
        print("⚠️ Please enter a valid question.")
        return

    print("\n[Agent] Analyzing query...\n")

    selected_tools = analyze_query(user_input)

    print(f"[Agent] Selected tools: {selected_tools}\n")

    results = {}

    print("[Agent] Fetching data...\n")

    for tool in selected_tools:
        if tool == "get_case_studies":
            results["get_case_studies"] = get_case_studies(user_input)

        elif tool == "query_knowledge":
            results["query_knowledge"] = query_knowledge(user_input)

    print("[Agent] Processing results...\n")

    reasoning = f"The agent used {len(selected_tools)} tools to answer the query."

    final_answer = "\n\n".join(results.values())

    sources = "\n".join([f"- {tool}" for tool in results.keys()])

    print("\n==============================")
    print("🤖 LPI AGENT RESPONSE")
    print("==============================\n")

    print("🧠 Reasoning:")
    print(reasoning)

    print("\n✅ Final Answer:")
    print(final_answer)

    print("\n📚 Sources:")
    print(sources)


if __name__ == "__main__":
    main()
