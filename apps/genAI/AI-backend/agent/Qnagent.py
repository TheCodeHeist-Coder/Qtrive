from utils.llm import Google_llm
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage


search = TavilySearch(
    max_results=5
)


def chat(user_query: str):

    # Decide whether web search is required
    router_prompt = f"""
You are a query classifier.

Decide whether the user query requires a web search.

Return ONLY one word:

SEARCH
or
NO_SEARCH

Use SEARCH for:
- Latest information
- Current news
- Current events
- Recent prices
- Current weather
- Recent updates
- Information that may have changed recently

Use NO_SEARCH for:
- Normal conversation
- General knowledge
- Explanations
- Coding questions
- Greetings
- Questions that can be answered from your existing knowledge

User Query:
{user_query}
"""

    decision_response = Google_llm.invoke(
        [HumanMessage(content=router_prompt)]
    )

    # Gemini content can be string OR list
    decision_content = decision_response.content

    if isinstance(decision_content, list):
        decision = ""

        for item in decision_content:
            if isinstance(item, dict):
                decision += item.get("text", "")
            else:
                decision += str(item)

        decision = decision.strip().upper()

    else:
        decision = str(decision_content).strip().upper()


    # Web search required
    if decision == "SEARCH":

        search_result = search.invoke({
            "query": user_query
        })

        prompt = f"""
Answer the user's question using the web search results.

User Question:
{user_query}

Web Search Results:
{search_result}

Rules:
- Give an accurate answer.
- Use the search results as your source.
- If the search results do not contain enough information, say so.
"""

        response = Google_llm.invoke(
            [HumanMessage(content=prompt)]
        )

        return response.content


    # Normal question
    response = Google_llm.invoke([
        HumanMessage(content=user_query)
    ])

    return response.content