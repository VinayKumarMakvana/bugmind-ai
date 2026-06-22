import chromadb
import uuid
import os

# Initialize local ChromaDB client (stores in memory or local disk)
chroma_client = chromadb.PersistentClient(path="./chroma_db")
collection = chroma_client.get_or_create_collection(name="bugmind_code_chunks")

def store_chunks(repo_id, chunks):
    """Store chunks in ChromaDB with metadata linking to repo_id."""
    documents = []
    metadatas = []
    ids = []
    
    for i, chunk in enumerate(chunks):
        documents.append(chunk["content"])
        metadata = chunk["metadata"]
        metadata["repo_id"] = repo_id
        metadatas.append(metadata)
        ids.append(f"{repo_id}_{uuid.uuid4()}")
        
    if documents:
        collection.upsert(
            documents=documents,
            metadatas=metadatas,
            ids=ids
        )
    print(f"Stored {len(documents)} chunks in ChromaDB for repo {repo_id}")

def retrieve_context(repo_id, query, n_results=3):
    """Retrieve the most relevant code chunks for a given query."""
    try:
        results = collection.query(
            query_texts=[query],
            n_results=n_results,
            where={"repo_id": repo_id}
        )
        if results and results.get("documents") and len(results["documents"]) > 0:
            return results["documents"][0]
    except Exception as e:
        print(f"RAG Retrieval failed: {e}")
        
    return []
