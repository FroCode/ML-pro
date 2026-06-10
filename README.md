# MedAssist Local

Private healthcare Q&A assistant using **Local LLM + RAG** (Retrieval-Augmented Generation).

- **LLM:** [Ollama](https://ollama.com/) (Llama 3.2 / Mistral)
- **Embeddings:** `sentence-transformers/all-MiniLM-L6-v2`
- **Vector DB:** ChromaDB
- **Dataset:** [MedQuAD](https://huggingface.co/datasets/lavita/MedQuAD) (NIH medical Q&A)
- **UI:** Streamlit

> **Disclaimer:** Informational use only. Not medical advice.

## Quick start

### 1. Prerequisites

- Python 3.10+
- [Ollama](https://ollama.com/download) installed and running

```bash
ollama serve
ollama pull llama3.2
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Build the index

```bash
python scripts/build_index.py
```

This downloads MedQuAD (cached in `data/raw/`), chunks it, embeds it, and stores vectors in `chroma_db/`.

Options:

```bash
python scripts/build_index.py --max-records 1000   # faster smoke test
python scripts/build_index.py --max-records 0      # full dataset (~47k pairs)
```

### 4. Run the demo

```bash
streamlit run app/streamlit_app.py
```

### 5. Evaluate (numerical metrics)

```bash
python scripts/run_eval.py                  # retrieval + generation (20 samples)
python scripts/run_eval.py --retrieval-only # faster, no Ollama needed
```

Results are saved to `results/metrics.json`.

## Project structure

```
ML-pro/
├── app/streamlit_app.py      # Live demo UI
├── src/
│   ├── config.py             # Settings
│   ├── ingest.py             # MedQuAD download & chunking
│   ├── embed_index.py        # ChromaDB indexing
│   ├── rag.py                # Retrieve + generate
│   ├── ollama_client.py      # Ollama HTTP client
│   └── evaluate.py           # Recall@k, MRR, ROUGE-L
├── scripts/
│   ├── build_index.py        # One-command pipeline
│   └── run_eval.py           # Evaluation runner
├── data/                     # Raw & processed data (gitignored)
├── chroma_db/                # Vector index (gitignored)
├── results/                  # metrics.json
└── report/                   # Presentation materials
```

## Evaluation metrics

| Metric | Description |
|--------|-------------|
| **Recall@5** | Fraction of queries where the correct document appears in top-5 retrieval |
| **MRR** | Mean reciprocal rank of the first relevant document |
| **ROUGE-L** | Lexical overlap between generated and reference answers |
| **Latency** | Mean / p95 response time (seconds) |

## CLI usage

```bash
# Ask a single question
python -m src.rag "What are the symptoms of diabetes?"

# Ingest only
python -m src.ingest
```

## Configuration

Edit `src/config.py` to change:

- `OLLAMA_MODEL` — default `llama3.2`
- `MAX_RECORDS` — subset size for indexing (default 3000)
- `TOP_K`, `CHUNK_SIZE`, `SIMILARITY_THRESHOLD`

## University project

- **Track:** Local LLM + RAG
- **Domain:** Healthcare
- **Deliverables:** Dataset sourcing, live demo, technical report, numerical evaluation

Presentation slides: `report/MedAssist_Local_Premium_v2.pptx`
