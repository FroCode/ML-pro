"""Retrieval-Augmented Generation pipeline."""
from __future__ import annotations

import time
from dataclasses import dataclass, field

from src.config import (
    OLLAMA_MODEL,
    SIMILARITY_THRESHOLD,
    SYSTEM_PROMPT,
    TOP_K,
)
from src.embed_index import get_collection
from src import ollama_client


@dataclass
class RetrievedChunk:
    text: str
    doc_id: str
    chunk_id: str
    score: float
    source: str = ""
    question: str = ""


@dataclass
class RAGResponse:
    question: str
    answer: str
    chunks: list[RetrievedChunk] = field(default_factory=list)
    latency_sec: float = 0.0
    retrieval_sec: float = 0.0
    generation_sec: float = 0.0
    used_ollama: bool = False
    model: str = OLLAMA_MODEL


def retrieve(question: str, top_k: int = TOP_K) -> list[RetrievedChunk]:
    collection = get_collection(reset=False)
    result = collection.query(query_texts=[question], n_results=top_k)
    chunks: list[RetrievedChunk] = []
    if not result["documents"] or not result["documents"][0]:
        return chunks

    for doc, meta, dist in zip(
        result["documents"][0],
        result["metadatas"][0],
        result["distances"][0],
    ):
        score = 1.0 - float(dist)  # cosine distance → similarity
        if score < SIMILARITY_THRESHOLD:
            continue
        chunks.append(
            RetrievedChunk(
                text=doc,
                doc_id=meta.get("doc_id", ""),
                chunk_id=meta.get("chunk_id", ""),
                score=round(score, 4),
                source=meta.get("source", ""),
                question=meta.get("question", ""),
            )
        )
    return chunks


def _format_context(chunks: list[RetrievedChunk]) -> str:
    parts = []
    for i, c in enumerate(chunks, 1):
        parts.append(
            f"[Source {i}] (score: {c.score:.2f}, doc: {c.doc_id})\n{c.text}"
        )
    return "\n\n".join(parts)


def _build_prompt(question: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return (
            f"{SYSTEM_PROMPT}\n\n"
            "CONTEXT:\nNo relevant passages were retrieved.\n\n"
            f"QUESTION: {question}\n\nANSWER:"
        )
    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"CONTEXT:\n{_format_context(chunks)}\n\n"
        f"QUESTION: {question}\n\nANSWER:"
    )


def _fallback_answer(question: str, chunks: list[RetrievedChunk]) -> str:
    if not chunks:
        return (
            "I don't have enough information in my sources to answer that question. "
            "(Ollama is not running — start it with `ollama serve` and pull a model.)"
        )
    best = chunks[0]
    return (
        f"Based on the most relevant source (score {best.score:.2f}):\n\n"
        f"{best.text}\n\n"
        f"— Extractive fallback (Ollama unavailable). Source: {best.doc_id}"
    )


def ask(question: str, top_k: int = TOP_K, use_ollama: bool | None = None) -> RAGResponse:
    t0 = time.perf_counter()
    chunks = retrieve(question, top_k=top_k)
    t1 = time.perf_counter()

    prompt = _build_prompt(question, chunks)
    used_ollama = False
    gen_sec = 0.0

    if use_ollama is None:
        use_ollama = ollama_client.is_available()

    if use_ollama and chunks:
        try:
            answer, gen_sec = ollama_client.generate(prompt)
            used_ollama = True
        except Exception:
            answer = _fallback_answer(question, chunks)
    else:
        answer = _fallback_answer(question, chunks)

    total = time.perf_counter() - t0
    return RAGResponse(
        question=question,
        answer=answer,
        chunks=chunks,
        latency_sec=round(total, 3),
        retrieval_sec=round(t1 - t0, 3),
        generation_sec=round(gen_sec, 3),
        used_ollama=used_ollama,
    )


if __name__ == "__main__":
    import sys

    q = sys.argv[1] if len(sys.argv) > 1 else "What are the symptoms of diabetes?"
    resp = ask(q)
    print(f"Q: {resp.question}\n")
    print(f"A: {resp.answer}\n")
    print(f"Chunks: {len(resp.chunks)} | Latency: {resp.latency_sec}s | Ollama: {resp.used_ollama}")
