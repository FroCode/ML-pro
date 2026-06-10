"""Central configuration for MedAssist Local."""
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Data
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
CHUNKS_FILE = DATA_PROCESSED / "chunks.jsonl"
TEST_SPLIT_FILE = DATA_PROCESSED / "test_split.jsonl"

# Vector store
CHROMA_PATH = ROOT / "chroma_db"
COLLECTION_NAME = "medquad"

# Models
EMBEDDING_MODEL = "all-MiniLM-L6-v2"
OLLAMA_BASE_URL = "http://localhost:11434"
OLLAMA_MODEL = "llama3.2"
OLLAMA_TIMEOUT = 120.0

# RAG
TOP_K = 5
SIMILARITY_THRESHOLD = 0.35
CHUNK_SIZE = 400
CHUNK_OVERLAP = 50
MAX_NEW_TOKENS = 512
TEMPERATURE = 0.1

# Ingest — use 0 for full MedQuAD (~47k pairs); default subset for fast local setup
MAX_RECORDS = 3000
TEST_SIZE = 100
RANDOM_SEED = 42

# Evaluation
EVAL_TOP_K = 5
RESULTS_DIR = ROOT / "results"
METRICS_FILE = RESULTS_DIR / "metrics.json"

SYSTEM_PROMPT = """You are MedAssist, a medical information assistant.
Answer ONLY using the provided context passages.
If the context does not contain enough information, say:
"I don't have enough information in my sources to answer that question."
Always mention which source passages you used.
This is informational only — not medical advice and not a diagnosis."""
