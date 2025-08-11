"""
This module contains functions to construct queries for the main agent.
"""
from koder.tools.search import search_similar_code

## add context to the user prompt
def construct_query(user_prompt: str) -> str:
    """
    Construct a query for main agent by adding context to the user prompt.
    """
    # coderag
    try:
        results = search_similar_code(user_prompt) or []
    except Exception:
        results = []

    def _truncate(text: str, max_len: int = 400) -> str:
        text = str(text).strip().replace("\n", " ")
        return text if len(text) <= max_len else text[: max_len - 1] + "…"

    if isinstance(results, (list, tuple)) and results:
        formatted_results = "\n".join(
            f"- {_truncate(item)}" for item in list(results)[:5]
        )
    else:
        formatted_results = "- No additional context found."

    constructed_query = (
        f"User request: {user_prompt.strip()}\n\n"
        f"Relevant context:\n{formatted_results}"
    )
    return constructed_query
