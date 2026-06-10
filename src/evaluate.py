"""Evaluate retrieval and generation quality on held-out MedQuAD questions."""
from __future__ import annotations

import json
import time
from pathlib import Path

from rouge_score import rouge_scorer
from tqdm import tqdm

from src.config import (
    EVAL_TOP_K,
    METRICS_FILE,
    RESULTS_DIR,
    TEST_SPLIT_FILE,
)
from src.embed_index import get_collection
from src import ollama_client
from src.rag import ask


def load_test_split(path: Path = TEST_SPLIT_FILE) -> list[dict]:
    rows: list[dict] = []
    with path.open(encoding="utf-8") as f:
        for line in f:
            rows.append(json.loads(line))
    return rows


def recall_at_k(relevant_doc_id: str, retrieved_doc_ids: list[str], k: int) -> float:
    return 1.0 if relevant_doc_id in retrieved_doc_ids[:k] else 0.0


def reciprocal_rank(relevant_doc_id: str, retrieved_doc_ids: list[str]) -> float:
    for i, doc_id in enumerate(retrieved_doc_ids, 1):
        if doc_id == relevant_doc_id:
            return 1.0 / i
    return 0.0


def evaluate_retrieval(test_rows: list[dict], top_k: int = EVAL_TOP_K) -> dict:
    collection = get_collection(reset=False)
    recalls, mrrs, latencies = [], [], []

    for row in tqdm(test_rows, desc="Retrieval eval"):
        t0 = time.perf_counter()
        result = collection.query(query_texts=[row["question"]], n_results=top_k)
        latencies.append(time.perf_counter() - t0)
        doc_ids = [m.get("doc_id", "") for m in result["metadatas"][0]]
        recalls.append(recall_at_k(row["doc_id"], doc_ids, top_k))
        mrrs.append(reciprocal_rank(row["doc_id"], doc_ids))

    return {
        f"recall@{top_k}": round(sum(recalls) / max(len(recalls), 1), 4),
        "mrr": round(sum(mrrs) / max(len(mrrs), 1), 4),
        "retrieval_latency_mean_sec": round(sum(latencies) / max(len(latencies), 1), 4),
        "retrieval_latency_p95_sec": round(sorted(latencies)[int(0.95 * len(latencies))], 4)
        if latencies
        else 0.0,
        "n_samples": len(test_rows),
    }


def evaluate_generation(test_rows: list[dict], max_samples: int = 20) -> dict:
    subset = test_rows[:max_samples]
    scorer = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)
    rouge_scores, latencies = [], []
    ollama_ok = ollama_client.is_available()

    for row in tqdm(subset, desc="Generation eval"):
        resp = ask(row["question"])
        latencies.append(resp.latency_sec)
        scores = scorer.score(row["answer"], resp.answer)
        rouge_scores.append(scores["rougeL"].fmeasure)

    return {
        "rouge_l": round(sum(rouge_scores) / max(len(rouge_scores), 1), 4),
        "generation_latency_mean_sec": round(sum(latencies) / max(len(latencies), 1), 4),
        "generation_latency_p95_sec": round(sorted(latencies)[int(0.95 * len(latencies))], 4)
        if latencies
        else 0.0,
        "n_samples": len(subset),
        "ollama_used": ollama_ok,
    }


def run_evaluation(
    *,
    retrieval_only: bool = False,
    gen_samples: int = 20,
) -> dict:
    test_rows = load_test_split()
    if not test_rows:
        raise FileNotFoundError(f"No test split at {TEST_SPLIT_FILE}. Run ingest first.")

    metrics = {
        "retrieval": evaluate_retrieval(test_rows),
    }
    if not retrieval_only:
        metrics["generation"] = evaluate_generation(test_rows, max_samples=gen_samples)

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    METRICS_FILE.write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    return metrics


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--retrieval-only", action="store_true")
    parser.add_argument("--gen-samples", type=int, default=20)
    args = parser.parse_args()
    print(json.dumps(run_evaluation(retrieval_only=args.retrieval_only, gen_samples=args.gen_samples), indent=2))
