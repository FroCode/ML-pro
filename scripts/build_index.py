#!/usr/bin/env python3
"""Full pipeline: ingest MedQuAD → chunk → embed → ChromaDB index."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.embed_index import build_index
from src.ingest import run_ingest


def main() -> None:
    parser = argparse.ArgumentParser(description="Build MedAssist Local vector index")
    parser.add_argument("--max-records", type=int, default=None, help="Limit MedQuAD records (0 = all)")
    parser.add_argument("--no-reset", action="store_true", help="Append to existing index")
    args = parser.parse_args()

    ingest_kwargs = {}
    if args.max_records is not None:
        ingest_kwargs["max_records"] = args.max_records

    print("Step 1/2 — Ingesting MedQuAD…")
    ingest_stats = run_ingest(**ingest_kwargs)
    print(json.dumps(ingest_stats, indent=2))

    print("\nStep 2/2 — Building ChromaDB index…")
    index_stats = build_index(reset=not args.no_reset)
    print(json.dumps(index_stats, indent=2))
    print("\nDone. Run: streamlit run app/streamlit_app.py")


if __name__ == "__main__":
    main()
