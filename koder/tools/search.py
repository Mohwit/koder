"""Search for similar code in the codebase."""

from dotenv import load_dotenv

from koder.utils.inialize_code_rag import get_repository

load_dotenv()


def search_similar_code(query):
    """
    Search for similar code in the codebase using vector similarity.

    Args:
        query (str): The search query describing what to find

    Returns:
        list: Search results from the vector database
    """
    repo = get_repository()
    if repo is None:
        raise RuntimeError(
            "Repository has not been initialized yet."
            "Call initialize_code_rag() first."
        )

    results = repo.search(query, top_k=5)

    return results
