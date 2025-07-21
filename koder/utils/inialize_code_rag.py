"""Initialize the code repository and vector store."""

import os

from coderag import Repository, ChromaDBStore
from watchfiles import watch

from dotenv import load_dotenv

load_dotenv()

# Use a mutable container to hold the shared Repository instance and avoid 'global'
_repo_container: dict[str, Repository | None] = {"instance": None}


def initialize_code_rag() -> None:
    """Initialize the code repository and vector store."""
    code_repo_path = os.getcwd()
    vector_store_path = os.path.join(code_repo_path, "vector_db")

    # Initialize vector store
    vector_store = ChromaDBStore(
        collection_name="my_repo", persist_directory=vector_store_path
    )

    # Initialize repository handler (store in container)
    _repo_container["instance"] = Repository(
        repo_path=code_repo_path, vector_store=vector_store, use_code_summaries=True
    )

    # Initialize the repository
    stats = _repo_container["instance"].index()
    print(f"Indexed {stats['total_chunks']} chunks from {stats['indexed_files']} files")
    print(f"Vector store path: {vector_store_path}")

    # Start watching for file changes in the *same* thread
    _watch_repository_for_changes(code_repo_path, _repo_container["instance"])


def _watch_repository_for_changes(repo_path: str, repo: Repository) -> None:
    """Watch *repo_path* for file changes using *watchfiles* and re-index when they occur."""

    print("👀  Starting watchfiles-based file watcher …")

    for changes in watch(repo_path):
        # *changes* is a set of (Change, path) tuples
        relevant = [p for _, p in changes if "/vector_db" not in p]

        if not relevant:
            continue  # Only vector store files changed → ignore

        print(f"🔄  Detected {len(relevant)} change(s) – re-indexing …")
        stats = repo.index()
        print(
            f"✅  Re-indexed {stats['total_chunks']} chunks from {stats['indexed_files']} files"
        )


# Public accessor for other modules
def get_repository() -> Repository | None:
    """Return the shared Repository instance, or None if not yet initialized."""
    return _repo_container["instance"]


if __name__ == "__main__":
    initialize_code_rag()
