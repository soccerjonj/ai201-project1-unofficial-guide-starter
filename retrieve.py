"""
Milestone 4 — Embedding + vector store + retrieval.

Pipeline (matches planning.md Architecture, stages 3-4):
  build_index()  - embed every chunk from chunks.json with all-MiniLM-L6-v2
                   and store it in ChromaDB together with its metadata
  retrieve(q, k) - embed a query and return the top-k nearest chunks
                   (text + metadata + distance score)

Run once to build the store:   python retrieve.py --build
Then query from the CLI:        python retrieve.py "is lincoln park worth it?"
"""

import json
import sys
from pathlib import Path

import chromadb
from sentence_transformers import SentenceTransformer

CHUNKS_FILE = Path("chunks.json")
DB_DIR = "chroma_db"                  # gitignored; ChromaDB persists here
COLLECTION_NAME = "unofficial_guide"
EMBED_MODEL_NAME = "all-MiniLM-L6-v2"  # from planning.md Retrieval Approach
TOP_K = 7                              # from planning.md (brief suggests trying 4-5 too)

# Load the embedding model once and reuse it (loading is the slow part).
_model = None


def get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        _model = SentenceTransformer(EMBED_MODEL_NAME)
    return _model


def get_collection():
    """
    Open (or create) the ChromaDB collection.

    - PersistentClient writes the index to DB_DIR on disk, so we only have to
      embed once; later runs reopen the same store.
    - hnsw:space="cosine" makes ChromaDB report *cosine distance* (0 = identical,
      ~1 = unrelated). The brief's 0.6-0.7 "weak match" thresholds assume cosine.
    """
    client = chromadb.PersistentClient(path=DB_DIR)
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"hnsw:space": "cosine"},
    )


def build_index() -> None:
    """Embed all chunks and (re)load them into ChromaDB with metadata."""
    chunks = json.loads(CHUNKS_FILE.read_text(encoding="utf-8"))
    print(f"Loaded {len(chunks)} chunks from {CHUNKS_FILE}")

    # Start clean so re-running never double-inserts the same ids.
    client = chromadb.PersistentClient(path=DB_DIR)
    try:
        client.delete_collection(COLLECTION_NAME)
    except Exception:
        pass
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME, metadata={"hnsw:space": "cosine"}
    )

    texts = [c["text"] for c in chunks]
    print(f"Embedding {len(texts)} chunks with {EMBED_MODEL_NAME} ...")
    embeddings = get_model().encode(
        texts, batch_size=64, show_progress_bar=True
    ).tolist()

    # ChromaDB stores four parallel lists: id, vector, raw text, metadata.
    collection.add(
        ids=[c["id"] for c in chunks],
        embeddings=embeddings,
        documents=texts,
        metadatas=[c["metadata"] for c in chunks],
    )
    print(f"Stored {collection.count()} chunks in ChromaDB ('{COLLECTION_NAME}').")


def retrieve(query: str, k: int = TOP_K) -> list[dict]:
    """
    Embed `query` and return the k nearest chunks.

    Each result is {text, metadata, distance}. Lower distance = more similar.
    """
    collection = get_collection()
    query_embedding = get_model().encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_embedding,
        n_results=k,
        include=["documents", "metadatas", "distances"],
    )
    # query() returns lists-of-lists (one row per query); we sent one query.
    return [
        {"text": doc, "metadata": meta, "distance": dist}
        for doc, meta, dist in zip(
            results["documents"][0],
            results["metadatas"][0],
            results["distances"][0],
        )
    ]


if __name__ == "__main__":
    args = sys.argv[1:]
    if "--build" in args:
        build_index()
    elif args:
        query = " ".join(args)
        print(f"\nQuery: {query!r}\n" + "=" * 64)
        for hit in retrieve(query):
            m = hit["metadata"]
            print(f"\n(distance {hit['distance']:.3f})  "
                  f"{m['source']} | {m['filename']} #{m['chunk_index']}")
            print(hit["text"])
    else:
        print("Usage:\n  python retrieve.py --build        # build the vector store\n"
              "  python retrieve.py <your question>  # retrieve top chunks")
