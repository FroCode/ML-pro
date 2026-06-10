"""Embed chunks and persist them in ChromaDB."""
from __future__ import annotations

import json
from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions
from tqdm import tqdm

from src.config import (
    CHROMA_PATH,
    CHUNKS_FILE,
    COLLECTION_NAME,
    EMBEDDING_MODEL,
)


def load_chunks(path: Path = CHUNKS_FILE) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def get_collection(reset: bool = False):
    CHROMA_PATH.mkdir(parents=True, exist_ok=True)
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    ef = embedding_functions.SentenceTransformerEmbeddingFunction(
        model_name=EMBEDDING_MODEL
    )
    if reset:
        try:
            client.delete_collection(COLLECTION_NAME)
        except Exception:
            pass
    return client.get_or_create_collection(
        name=COLLECTION_NAME,
        embedding_function=ef,
        metadata={"hnsw:space": "cosine"},
    )


def build_index(chunks: list[dict] | None = None, *, reset: bool = True, batch_size: int = 128) -> dict:
    chunks = chunks or load_chunks()
    if not chunks:
        raise FileNotFoundError(f"No chunks found at {CHUNKS_FILE}. Run ingest first.")

    collection = get_collection(reset=reset)
    ids = [c["id"] for c in chunks]
    documents = [c["text"] for c in chunks]
    metadatas = [
        {
            "doc_id": c["doc_id"],
            "chunk_id": str(c["chunk_id"]),
            "question": c["question"][:500],
            "source": (c.get("source") or "")[:500],
        }
        for c in chunks
    ]

    for i in tqdm(range(0, len(ids), batch_size), desc="Indexing"):
        collection.add(
            ids=ids[i : i + batch_size],
            documents=documents[i : i + batch_size],
            metadatas=metadatas[i : i + batch_size],
        )

    return {"indexed_chunks": len(ids), "collection": COLLECTION_NAME, "path": str(CHROMA_PATH)}


if __name__ == "__main__":
    print(build_index())
