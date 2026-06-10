"""MedAssist Local — Streamlit demo UI."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import OLLAMA_MODEL, TOP_K
from src import ollama_client
from src.embed_index import CHROMA_PATH, CHUNKS_FILE
from src.rag import ask

st.set_page_config(
    page_title="MedAssist Local",
    page_icon="🏥",
    layout="wide",
    initial_sidebar_state="expanded",
)

CUSTOM_CSS = """
<style>
    .main-header { font-size: 2.2rem; font-weight: 700; color: #0B1D3A; }
    .sub-header { color: #00B4A6; font-size: 1rem; margin-bottom: 1rem; }
    .disclaimer {
        background: #FFF3CD; border-left: 4px solid #F5A623;
        padding: 0.75rem 1rem; border-radius: 4px; font-size: 0.9rem;
    }
    .metric-box {
        background: #F4F7FB; padding: 0.75rem; border-radius: 8px;
        border: 1px solid #E0E6ED;
    }
    .source-card {
        background: #fff; border: 1px solid #E0E6ED; border-radius: 8px;
        padding: 1rem; margin-bottom: 0.5rem;
    }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


@st.cache_resource
def _index_ready() -> bool:
    return CHUNKS_FILE.exists() and CHROMA_PATH.exists() and bool(list(CHROMA_PATH.iterdir()))


def main() -> None:
    st.markdown('<p class="main-header">MedAssist Local</p>', unsafe_allow_html=True)
    st.markdown(
        '<p class="sub-header">Private Healthcare Q&A · Local LLM + RAG · Ollama + ChromaDB</p>',
        unsafe_allow_html=True,
    )
    st.markdown(
        '<div class="disclaimer">⚠️ <b>Disclaimer:</b> Informational use only. '
        "Not medical advice. Not a substitute for professional care.</div>",
        unsafe_allow_html=True,
    )

    with st.sidebar:
        st.header("Settings")
        top_k = st.slider("Top-K retrieval", 1, 10, TOP_K)
        ollama_status = ollama_client.is_available()
        st.metric("Ollama", "Online" if ollama_status else "Offline")
        st.caption(f"Model: {OLLAMA_MODEL}")
        st.metric("Index", "Ready" if _index_ready() else "Not built")
        if not _index_ready():
            st.error("Run: `python scripts/build_index.py`")
        st.divider()
        st.subheader("Example questions")
        examples = [
            "What are common side effects of aspirin?",
            "What is hypertension?",
            "What are the symptoms of diabetes?",
            "How is asthma diagnosed?",
        ]
        for ex in examples:
            if st.button(ex, key=ex, use_container_width=True):
                st.session_state["question"] = ex

    if not _index_ready():
        st.stop()

    question = st.text_area(
        "Your medical question",
        value=st.session_state.get("question", ""),
        height=100,
        placeholder="Ask a healthcare question…",
    )

    if st.button("Ask MedAssist", type="primary", use_container_width=True) and question.strip():
        with st.spinner("Retrieving context and generating answer…"):
            response = ask(question.strip(), top_k=top_k)

        col1, col2, col3, col4 = st.columns(4)
        col1.metric("Latency", f"{response.latency_sec}s")
        col2.metric("Retrieval", f"{response.retrieval_sec}s")
        col3.metric("Sources", len(response.chunks))
        col4.metric("LLM", "Ollama" if response.used_ollama else "Fallback")

        st.subheader("Answer")
        st.write(response.answer)

        st.subheader("Retrieved sources")
        if not response.chunks:
            st.info("No passages met the similarity threshold.")
        for i, chunk in enumerate(response.chunks, 1):
            st.markdown(
                f'<div class="source-card">'
                f"<b>Source {i}</b> · score <code>{chunk.score}</code> · "
                f"<code>{chunk.doc_id}</code><br><br>{chunk.text}"
                f"</div>",
                unsafe_allow_html=True,
            )


if __name__ == "__main__":
    main()
