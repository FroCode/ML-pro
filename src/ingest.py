"""Download MedQuAD and build chunked JSONL for indexing."""
from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd
from datasets import load_dataset
from tqdm import tqdm

from src.config import (
    CHUNK_OVERLAP,
    CHUNK_SIZE,
    CHUNKS_FILE,
    DATA_PROCESSED,
    DATA_RAW,
    DEMO_DOCS_PER_PATTERN,
    DEMO_TOPIC_PATTERNS,
    MAX_RECORDS,
    RANDOM_SEED,
    TEST_SIZE,
    TEST_SPLIT_FILE,
)


def _clean(text: str) -> str:
    text = re.sub(r"<[^>]+>", " ", text or "")
    text = re.sub(r"\s+", " ", text).strip()
    return text


def _word_chunks(text: str, size: int, overlap: int) -> list[str]:
    words = text.split()
    if not words:
        return []
    if len(words) <= size:
        return [" ".join(words)]
    chunks: list[str] = []
    start = 0
    while start < len(words):
        end = min(start + size, len(words))
        chunks.append(" ".join(words[start:end]))
        if end == len(words):
            break
        start = max(end - overlap, start + 1)
    return chunks


def _select_demo_records(df: pd.DataFrame) -> pd.DataFrame:
    """Always index presentation demo topics, even if outside the random sample."""
    picked: list[pd.DataFrame] = []
    for primary, secondary in DEMO_TOPIC_PATTERNS:
        mask = (
            df["question"].str.contains(primary, case=False, na=False)
            | df["answer"].str.contains(primary, case=False, na=False)
        )
        if secondary:
            mask &= (
                df["question"].str.contains(secondary, case=False, na=False)
                | df["answer"].str.contains(secondary, case=False, na=False)
            )
        hits = df[mask].head(DEMO_DOCS_PER_PATTERN)
        if not hits.empty:
            picked.append(hits)
    if not picked:
        return df.iloc[0:0]
    return pd.concat(picked).drop_duplicates(subset=["question"]).reset_index(drop=True)


def load_medquad(max_records: int = MAX_RECORDS) -> pd.DataFrame:
    DATA_RAW.mkdir(parents=True, exist_ok=True)
    cache = DATA_RAW / "medquad.parquet"
    if cache.exists():
        full = pd.read_parquet(cache)
    else:
        ds = load_dataset("lavita/MedQuAD", split="train")
        full = ds.to_pandas()
        full.to_parquet(cache, index=False)

    full["question"] = full["question"].map(_clean)
    full["answer"] = full["answer"].map(_clean)
    if "source" not in full.columns:
        full["source"] = ""
    full["source"] = full["source"].astype(str).map(_clean)
    full = full[full["answer"].str.len() > 20].reset_index(drop=True)

    demo = _select_demo_records(full)
    demo_questions = set(demo["question"])

    if max_records and max_records > 0:
        pool = full[~full["question"].isin(demo_questions)]
        n_sample = max(max_records - len(demo), 0)
        sample = pool.sample(n=min(n_sample, len(pool)), random_state=RANDOM_SEED)
        df = pd.concat([demo, sample], ignore_index=True)
    else:
        df = full

    df = df.reset_index(drop=True)
    df["doc_id"] = [f"doc_{i}" for i in range(len(df))]
    return df


def build_chunks(df: pd.DataFrame) -> tuple[list[dict], list[dict]]:
    """Index all documents; hold out test questions for evaluation."""
    test_df = df.sample(n=min(TEST_SIZE, len(df)), random_state=RANDOM_SEED).reset_index(drop=True)

    chunks: list[dict] = []
    for _, row in tqdm(df.iterrows(), total=len(df), desc="Chunking"):
        body = f"Question: {row['question']}\nAnswer: {row['answer']}"
        for chunk_i, piece in enumerate(_word_chunks(body, CHUNK_SIZE, CHUNK_OVERLAP)):
            chunks.append(
                {
                    "id": f"{row['doc_id']}_chunk_{chunk_i}",
                    "doc_id": row["doc_id"],
                    "chunk_id": chunk_i,
                    "text": piece,
                    "question": row["question"],
                    "answer": row["answer"],
                    "source": row.get("source", ""),
                }
            )

    test_records = [
        {
            "doc_id": row["doc_id"],
            "question": row["question"],
            "answer": row["answer"],
            "source": row.get("source", ""),
        }
        for _, row in test_df.iterrows()
    ]
    return chunks, test_records


def save_jsonl(rows: list[dict], path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8") as f:
        for row in rows:
            f.write(json.dumps(row, ensure_ascii=False) + "\n")


def run_ingest(max_records: int = MAX_RECORDS) -> dict:
    df = load_medquad(max_records)
    chunks, test_records = build_chunks(df)
    save_jsonl(chunks, CHUNKS_FILE)
    save_jsonl(test_records, TEST_SPLIT_FILE)
    return {
        "records": len(df),
        "chunks": len(chunks),
        "test_size": len(test_records),
        "avg_chunk_words": sum(len(c["text"].split()) for c in chunks) / max(len(chunks), 1),
    }


if __name__ == "__main__":
    print(run_ingest())
