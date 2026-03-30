import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer
import os

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "chroma_db")

_model = None
_client = None
_collection = None

def _get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def _get_collection():
    global _client, _collection
    if _collection is None:
        os.makedirs(DB_PATH, exist_ok=True)
        _client = chromadb.PersistentClient(path=DB_PATH)
        _collection = _client.get_or_create_collection(
            name="legal_docs",
            metadata={"hnsw:space": "cosine"}
        )
    return _collection

def add_document(chunks: list[dict], doc_id: str):
    """Embed and store document chunks."""
    collection = _get_collection()
    model = _get_model()
    texts = [c["text"] for c in chunks]
    embeddings = model.encode(texts, show_progress_bar=False).tolist()
    ids = [f"{doc_id}__chunk_{i}" for i in range(len(chunks))]
    metadatas = [{"source": c["source"], "page": c["page"], "doc_id": doc_id} for c in chunks]
    collection.add(documents=texts, embeddings=embeddings, ids=ids, metadatas=metadatas)

def search(query: str, n_results: int = 6, doc_ids: list[str] | None = None) -> list[dict]:
    """Retrieve top-k chunks for a query, optionally filtered by doc_ids."""
    collection = _get_collection()
    model = _get_model()
    query_embedding = model.encode([query], show_progress_bar=False).tolist()
    where = {"doc_id": {"$in": doc_ids}} if doc_ids else None
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=n_results,
        where=where,
        include=["documents", "metadatas", "distances"]
    )
    chunks = []
    for doc, meta, dist in zip(results["documents"][0], results["metadatas"][0], results["distances"][0]):
        chunks.append({"text": doc, "source": meta["source"], "page": meta["page"], "score": 1 - dist})
    return chunks

def list_documents() -> list[str]:
    """Return unique doc_ids in the store."""
    collection = _get_collection()
    result = collection.get(include=["metadatas"])
    ids = set()
    for meta in result["metadatas"]:
        ids.add(meta["doc_id"])
    return sorted(ids)

def delete_document(doc_id: str):
    """Delete all chunks for a doc_id."""
    collection = _get_collection()
    result = collection.get(where={"doc_id": doc_id}, include=[])
    if result["ids"]:
        collection.delete(ids=result["ids"])

def document_exists(doc_id: str) -> bool:
    collection = _get_collection()
    result = collection.get(where={"doc_id": doc_id}, include=[], limit=1)
    return len(result["ids"]) > 0
