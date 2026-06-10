#!/usr/bin/env python3
"""Run retrieval + generation evaluation and save metrics.json."""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.evaluate import run_evaluation


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--retrieval-only", action="store_true")
    parser.add_argument("--gen-samples", type=int, default=20)
    args = parser.parse_args()

    metrics = run_evaluation(
        retrieval_only=args.retrieval_only,
        gen_samples=args.gen_samples,
    )
    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
