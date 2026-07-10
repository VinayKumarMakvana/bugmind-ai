from __future__ import annotations

import logging
import uuid
from typing import Any, Dict, List

import chromadb
from chromadb.api.models.Collection import Collection


logger = logging.getLogger(__name__)

# =========================================================
# CONFIG
# =========================================================

CHROMA_DB_PATH = "./chroma_db"

COLLECTION_NAME = "bugmind_code_chunks"

DEFAULT_TOP_K = 5


# =========================================================
# CHROMA CLIENT
# =========================================================

client = chromadb.PersistentClient(
    path=CHROMA_DB_PATH
)

collection: Collection = client.get_or_create_collection(
    name=COLLECTION_NAME
)


# =========================================================
# CREATE DOCUMENT ID
# =========================================================

def generate_chunk_id(
    repo_id: str,
) -> str:

    return f"{repo_id}_{uuid.uuid4()}"


# =========================================================
# VALIDATE CHUNK
# =========================================================

def validate_chunk(
    chunk: Dict[str, Any],
) -> bool:

    if "content" not in chunk:
        return False

    if "metadata" not in chunk:
        return False

    if not chunk["content"].strip():
        return False

    return True

# =========================================================
# STORE CHUNKS
# =========================================================

def store_chunks(
    repo_id: str,
    chunks: List[Dict[str, Any]],
) -> int:
    """
    Store AST chunks into ChromaDB.

    Returns:
        Number of stored chunks.
    """

    documents: List[str] = []
    metadatas: List[Dict[str, Any]] = []
    ids: List[str] = []

    for chunk in chunks:

        if not validate_chunk(chunk):
            continue

        metadata = dict(chunk["metadata"])

        metadata["repo_id"] = repo_id

        documents.append(chunk["content"])

        metadatas.append(metadata)

        ids.append(
            generate_chunk_id(repo_id)
        )

    if not documents:

        logger.warning(
            "No valid chunks found for %s",
            repo_id,
        )

        return 0

    try:

        collection.upsert(
            ids=ids,
            documents=documents,
            metadatas=metadatas,
        )

        logger.info(
            "%s chunks stored successfully.",
            len(documents),
        )

        return len(documents)

    except Exception:

        logger.exception(
            "Failed to store chunks."
        )

        return 0


# =========================================================
# DELETE REPOSITORY CHUNKS
# =========================================================

def delete_repository(
    repo_id: str,
) -> None:
    """
    Remove all chunks for a repository.
    """

    try:

        collection.delete(
            where={
                "repo_id": repo_id
            }
        )

        logger.info(
            "Repository %s deleted.",
            repo_id,
        )

    except Exception:

        logger.exception(
            "Unable to delete repository."
        )


# =========================================================
# REINDEX REPOSITORY
# =========================================================

def reindex_repository(
    repo_id: str,
    chunks: List[Dict[str, Any]],
) -> int:
    """
    Delete old chunks and insert new ones.
    """

    delete_repository(repo_id)

    return store_chunks(
        repo_id,
        chunks,
    )

# =========================================================
# RETRIEVE CONTEXT
# =========================================================

def retrieve_context(
    repo_id: str,
    query: str,
    n_results: int = DEFAULT_TOP_K,
) -> List[str]:
    """
    Retrieve the most relevant code chunks for the query.
    """

    try:

        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where={
                "repo_id": repo_id,
            },
        )

    except Exception:

        logger.exception(
            "Context retrieval failed."
        )

        return []

    if not results:
        return []

    documents = results.get(
        "documents",
        [],
    )

    if not documents:
        return []

    if not documents[0]:
        return []

    unique = []

    visited = set()

    for document in documents[0]:

        if not document:
            continue

        if document in visited:
            continue

        visited.add(document)

        unique.append(document)

    return unique


# =========================================================
# FORMAT CONTEXT
# =========================================================

def format_context(
    contexts: List[str],
    max_characters: int = 12000,
) -> List[str]:
    """
    Limit context size before sending to the LLM.
    """

    output = []

    total = 0

    for context in contexts:

        size = len(context)

        if total + size > max_characters:
            break

        output.append(context)

        total += size

    return output


# =========================================================
# SEARCH REPOSITORY
# =========================================================

def search_repository(
    repo_id: str,
    query: str,
    n_results: int = DEFAULT_TOP_K,
) -> List[str]:
    """
    Retrieve and format repository context.
    """

    contexts = retrieve_context(
        repo_id=repo_id,
        query=query,
        n_results=n_results,
    )

    return format_context(contexts)


# =========================================================
# COLLECTION INFO
# =========================================================

def collection_info() -> Dict[str, Any]:
    """
    Returns collection metadata.
    """

    try:

        count = collection.count()

        return {
            "collection": COLLECTION_NAME,
            "documents": count,
        }

    except Exception:

        logger.exception(
            "Unable to read collection info."
        )

        return {
            "collection": COLLECTION_NAME,
            "documents": 0,
        }


# =========================================================
# CLEAR COLLECTION
# =========================================================

def clear_collection() -> bool:
    """
    Delete all indexed documents.
    """

    try:

        client.delete_collection(
            COLLECTION_NAME
        )

        client.get_or_create_collection(
            name=COLLECTION_NAME
        )

        logger.info(
            "Collection cleared successfully."
        )

        return True

    except Exception:

        logger.exception(
            "Unable to clear collection."
        )

        return False


# =========================================================
# EXPORTS
# =========================================================

__all__ = [

    "store_chunks",

    "retrieve_context",

    "search_repository",

    "delete_repository",

    "reindex_repository",

    "collection_info",

    "clear_collection",

]