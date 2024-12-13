from backend.agent import agent_workflow

async def process_initial_search_query(
    model: str, prompt: str, category: str, user_id: int
):
    response = agent_workflow.invoke({"prompt": prompt, "category": category})

    print(response["steps"])

    tools_used = ["vector_search"]
    if response.get("perform_web_search", False):
        tools_used.append("web_search")

    return {
        "response": response["generation"] + f"\n\n### Tools used to generate response:\n\t{', '.join(tools_used)}",
        "tools_used": ", ".join(tools_used),
    }
