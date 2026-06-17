"""MedAssist Local — iOS-style Streamlit demo UI."""
from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from src.config import EMBEDDING_MODEL, OLLAMA_MODEL, TOP_K  # noqa: E402
from src import ollama_client  # noqa: E402
from src.embed_index import CHROMA_PATH, CHUNKS_FILE  # noqa: E402
from src.rag import RAGResponse, ask  # noqa: E402

st.set_page_config(
    page_title="MedAssist Local",
    page_icon="🩺",
    layout="wide",
    initial_sidebar_state="expanded",
)

EXAMPLES = [
    ("💊", "Side effects of aspirin", "What are common side effects of aspirin?"),
    ("❤️", "Hypertension", "What is hypertension?"),
    ("🩸", "Diabetes symptoms", "What are the symptoms of diabetes?"),
    ("🫁", "Asthma diagnosis", "How is asthma diagnosed?"),
]

# iOS Human Interface palette
IOS = {
    "bg": "#F2F2F7",
    "card": "#FFFFFF",
    "label": "#8E8E93",
    "text": "#1C1C1E",
    "text2": "#3A3A3C",
    "blue": "#007AFF",
    "blue_bg": "#E8F2FF",
    "green": "#34C759",
    "green_bg": "#E8F8ED",
    "red": "#FF3B30",
    "red_bg": "#FFEBEA",
    "orange": "#FF9500",
    "orange_bg": "#FFF4E5",
    "purple": "#AF52DE",
    "purple_bg": "#F5ECFA",
    "separator": "#D1D1D6",
    "fill": "#E5E5EA",
}

CSS = f"""
/* ── iOS base ─────────────────────────────────────────────── */
html, body, [class*="css"] {{
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Text', 'Segoe UI', sans-serif !important;
    -webkit-font-smoothing: antialiased;
}}

.stApp {{
    background-color: {IOS["bg"]} !important;
}}

[data-testid="stAppViewContainer"] > .main {{
    background-color: {IOS["bg"]} !important;
}}

[data-testid="stAppViewContainer"] > .main .block-container {{
    padding-top: 1.25rem;
    padding-bottom: 3rem;
    max-width: 980px;
}}

#MainMenu, footer, header[data-testid="stHeader"] {{
    visibility: hidden;
    height: 0;
}}

/* ── Sidebar (iOS Settings style) ─────────────────────────── */
section[data-testid="stSidebar"] {{
    background-color: {IOS["bg"]} !important;
    border-right: 0.5px solid {IOS["separator"]};
}}

section[data-testid="stSidebar"] > div {{
    background-color: {IOS["bg"]} !important;
}}

section[data-testid="stSidebar"] [data-testid="stMarkdown"] p,
section[data-testid="stSidebar"] [data-testid="stMarkdown"] li,
section[data-testid="stSidebar"] label,
section[data-testid="stSidebar"] .stCaption {{
    color: {IOS["text"]} !important;
}}

section[data-testid="stSidebar"] .section-label {{
    color: {IOS["label"]} !important;
    font-size: 13px !important;
    font-weight: 400 !important;
    text-transform: uppercase;
    letter-spacing: 0.02em;
    margin: 18px 0 8px 0;
}}

section[data-testid="stSidebar"] hr {{
    border: none;
    border-top: 0.5px solid {IOS["separator"]};
    margin: 16px 0;
}}

section[data-testid="stSidebar"] div.stButton > button {{
    background: {IOS["card"]} !important;
    color: {IOS["blue"]} !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 15px !important;
    font-weight: 400 !important;
    padding: 12px 14px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06) !important;
    text-align: left !important;
}}

section[data-testid="stSidebar"] div.stButton > button:hover {{
    background: {IOS["blue_bg"]} !important;
}}

section[data-testid="stSidebar"] [data-testid="stSlider"] {{
    background: {IOS["card"]};
    border-radius: 14px;
    padding: 12px 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}

/* ── Streamlit native widgets ─────────────────────────────── */
div[data-testid="stVerticalBlockBorderWrapper"] {{
    background: {IOS["card"]} !important;
    border: none !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04) !important;
    padding: 16px 18px !important;
}}

.stTextArea textarea {{
    background: {IOS["fill"]} !important;
    border: none !important;
    border-radius: 10px !important;
    color: {IOS["text"]} !important;
    font-size: 17px !important;
    padding: 12px 14px !important;
    line-height: 1.4 !important;
}}

.stTextArea textarea:focus {{
    box-shadow: 0 0 0 3px rgba(0, 122, 255, 0.25) !important;
}}

div.stButton > button[kind="primary"] {{
    background: {IOS["blue"]} !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 17px !important;
    font-weight: 600 !important;
    padding: 12px 20px !important;
    min-height: 50px !important;
    box-shadow: none !important;
}}

div.stButton > button[kind="primary"]:hover {{
    background: #0066DD !important;
    color: white !important;
}}

div.stButton > button[kind="secondary"],
div.stButton > button:not([kind="primary"]) {{
    background: {IOS["card"]} !important;
    color: {IOS["blue"]} !important;
    border: 0.5px solid {IOS["separator"]} !important;
    border-radius: 12px !important;
    font-weight: 500 !important;
    min-height: 50px !important;
}}

[data-testid="stExpander"] {{
    background: {IOS["card"]};
    border: none !important;
    border-radius: 14px !important;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}

/* ── Custom iOS components ──────────────────────────────────── */
.ios-large-title {{
    font-size: 34px;
    font-weight: 700;
    letter-spacing: -0.02em;
    color: {IOS["text"]};
    margin: 0 0 4px 0;
    line-height: 1.1;
}}

.ios-subtitle {{
    font-size: 17px;
    color: {IOS["label"]};
    margin: 0 0 20px 0;
    font-weight: 400;
}}

.ios-section-label {{
    font-size: 13px;
    font-weight: 400;
    color: {IOS["label"]};
    text-transform: uppercase;
    letter-spacing: 0.02em;
    margin: 24px 0 8px 4px;
}}

.ios-group {{
    background: {IOS["card"]};
    border-radius: 14px;
    overflow: hidden;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06), 0 1px 2px rgba(0,0,0,0.04);
    margin-bottom: 20px;
}}

.ios-row {{
    display: flex;
    align-items: center;
    padding: 14px 16px;
    border-bottom: 0.5px solid {IOS["separator"]};
    gap: 12px;
}}

.ios-row:last-child {{ border-bottom: none; }}

.ios-icon {{
    width: 36px;
    height: 36px;
    border-radius: 9px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 18px;
    flex-shrink: 0;
}}

.ios-icon.blue {{ background: {IOS["blue_bg"]}; }}
.ios-icon.green {{ background: {IOS["green_bg"]}; }}
.ios-icon.orange {{ background: {IOS["orange_bg"]}; }}
.ios-icon.purple {{ background: {IOS["purple_bg"]}; }}
.ios-icon.red {{ background: {IOS["red_bg"]}; }}

.ios-row-title {{
    font-size: 17px;
    font-weight: 400;
    color: {IOS["text"]};
    flex: 1;
}}

.ios-row-value {{
    font-size: 17px;
    color: {IOS["label"]};
    font-weight: 400;
}}

.ios-row-value.on {{ color: {IOS["green"]}; font-weight: 600; }}
.ios-row-value.off {{ color: {IOS["red"]}; font-weight: 600; }}

.ios-banner {{
    background: {IOS["orange_bg"]};
    border-radius: 14px;
    padding: 14px 16px;
    margin-bottom: 20px;
    display: flex;
    gap: 12px;
    align-items: flex-start;
    border: 0.5px solid rgba(255, 149, 0, 0.25);
}}

.ios-banner-icon {{
    font-size: 22px;
    line-height: 1;
}}

.ios-banner-text {{
    font-size: 15px;
    line-height: 1.45;
    color: #8B5A00;
}}

.ios-banner-text strong {{
    color: {IOS["orange"]};
    font-weight: 600;
}}

.ios-stat-grid {{
    display: grid;
    grid-template-columns: repeat(4, 1fr);
    gap: 12px;
    margin-bottom: 20px;
}}

.ios-stat {{
    border-radius: 14px;
    padding: 14px 16px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}

.ios-stat.blue {{ background: {IOS["blue_bg"]}; }}
.ios-stat.green {{ background: {IOS["green_bg"]}; }}
.ios-stat.purple {{ background: {IOS["purple_bg"]}; }}
.ios-stat.orange {{ background: {IOS["orange_bg"]}; }}

.ios-stat-label {{
    font-size: 13px;
    color: {IOS["label"]};
    margin-bottom: 4px;
}}

.ios-stat-value {{
    font-size: 22px;
    font-weight: 700;
    color: {IOS["text"]};
    letter-spacing: -0.02em;
}}

.ios-stat-value.blue {{ color: {IOS["blue"]}; }}
.ios-stat-value.green {{ color: {IOS["green"]}; }}
.ios-stat-value.purple {{ color: {IOS["purple"]}; }}
.ios-stat-value.orange {{ color: {IOS["orange"]}; }}

.ios-answer-box {{
    background: {IOS["card"]};
    border-radius: 14px;
    padding: 18px 18px 20px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    margin-bottom: 16px;
}}

.ios-answer-header {{
    display: flex;
    align-items: center;
    gap: 10px;
    margin-bottom: 14px;
    padding-bottom: 12px;
    border-bottom: 0.5px solid {IOS["separator"]};
}}

.ios-chip {{
    background: {IOS["blue_bg"]};
    color: {IOS["blue"]};
    font-size: 13px;
    font-weight: 600;
    padding: 4px 10px;
    border-radius: 999px;
}}

.ios-chip-sub {{
    font-size: 13px;
    color: {IOS["label"]};
}}

.ios-answer-text {{
    font-size: 17px;
    line-height: 1.55;
    color: {IOS["text"]};
}}

.ios-source-card {{
    background: {IOS["card"]};
    border-radius: 14px;
    padding: 16px;
    margin-bottom: 10px;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
    border-left: 4px solid {IOS["blue"]};
}}

.ios-source-card:nth-child(2) {{ border-left-color: {IOS["green"]}; }}
.ios-source-card:nth-child(3) {{ border-left-color: {IOS["purple"]}; }}
.ios-source-card:nth-child(4) {{ border-left-color: {IOS["orange"]}; }}
.ios-source-card:nth-child(5) {{ border-left-color: #5856D6; }}

.ios-source-top {{
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 10px;
}}

.ios-source-num {{
    font-size: 15px;
    font-weight: 600;
    color: {IOS["text"]};
}}

.ios-score {{
    font-size: 13px;
    font-weight: 600;
    color: {IOS["blue"]};
    background: {IOS["blue_bg"]};
    padding: 3px 8px;
    border-radius: 6px;
    font-variant-numeric: tabular-nums;
}}

.ios-progress {{
    height: 6px;
    background: {IOS["fill"]};
    border-radius: 3px;
    overflow: hidden;
    margin-bottom: 12px;
}}

.ios-progress-fill {{
    height: 100%;
    background: {IOS["blue"]};
    border-radius: 3px;
}}

.ios-source-body {{
    font-size: 15px;
    line-height: 1.5;
    color: {IOS["text2"]};
}}

.ios-source-id {{
    font-size: 12px;
    color: {IOS["label"]};
    margin-top: 8px;
    font-family: ui-monospace, 'SF Mono', monospace;
}}

.ios-empty {{
    background: {IOS["card"]};
    border-radius: 14px;
    padding: 48px 24px;
    text-align: center;
    box-shadow: 0 1px 3px rgba(0,0,0,0.06);
}}

.ios-empty-icon {{
    width: 64px;
    height: 64px;
    background: {IOS["blue_bg"]};
    border-radius: 16px;
    display: flex;
    align-items: center;
    justify-content: center;
    font-size: 28px;
    margin: 0 auto 16px;
}}

.ios-empty-title {{
    font-size: 20px;
    font-weight: 600;
    color: {IOS["text"]};
    margin-bottom: 6px;
}}

.ios-empty-sub {{
    font-size: 15px;
    color: {IOS["label"]};
    line-height: 1.45;
}}

.ios-sidebar-title {{
    font-size: 28px;
    font-weight: 700;
    color: {IOS["text"]} !important;
    letter-spacing: -0.02em;
    margin-bottom: 2px !important;
}}

.ios-sidebar-sub {{
    font-size: 15px;
    color: {IOS["label"]} !important;
    margin-bottom: 8px !important;
}}

@media (max-width: 768px) {{
    .ios-stat-grid {{ grid-template-columns: repeat(2, 1fr); }}
    .ios-large-title {{ font-size: 28px; }}
}}
"""


@st.cache_resource
def _index_ready() -> bool:
    return CHUNKS_FILE.exists() and CHROMA_PATH.exists() and bool(list(CHROMA_PATH.iterdir()))


def _escape(text: str) -> str:
    return (
        text.replace("&", "&amp;")
        .replace("<", "&lt;")
        .replace(">", "&gt;")
        .replace("\n", "<br>")
    )


def _init_session() -> None:
    defaults = {"question": "", "response": None, "history": []}
    for key, val in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = val


def _render_sidebar() -> int:
    st.markdown('<p class="ios-sidebar-title">Settings</p>', unsafe_allow_html=True)
    st.markdown('<p class="ios-sidebar-sub">MedAssist Local</p>', unsafe_allow_html=True)

    ollama_ok = ollama_client.is_available()
    index_ok = _index_ready()

    st.markdown('<p class="section-label">System Status</p>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ios-group">
            <div class="ios-row">
                <div class="ios-icon {'green' if ollama_ok else 'red'}">🤖</div>
                <span class="ios-row-title">Ollama</span>
                <span class="ios-row-value {'on' if ollama_ok else 'off'}">
                    {'Online' if ollama_ok else 'Offline'}
                </span>
            </div>
            <div class="ios-row">
                <div class="ios-icon {'green' if index_ok else 'red'}">📚</div>
                <span class="ios-row-title">Vector Index</span>
                <span class="ios-row-value {'on' if index_ok else 'off'}">
                    {'Ready' if index_ok else 'Missing'}
                </span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    if not index_ok:
        st.error("Run: python scripts/build_index.py")

    st.markdown('<p class="section-label">Models</p>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ios-group">
            <div class="ios-row">
                <div class="ios-icon blue">🧠</div>
                <span class="ios-row-title">LLM</span>
                <span class="ios-row-value">{OLLAMA_MODEL}</span>
            </div>
            <div class="ios-row">
                <div class="ios-icon purple">📐</div>
                <span class="ios-row-title">Embeddings</span>
                <span class="ios-row-value" style="font-size:13px;">MiniLM</span>
            </div>
            <div class="ios-row">
                <div class="ios-icon orange">🗄️</div>
                <span class="ios-row-title">Store</span>
                <span class="ios-row-value">ChromaDB</span>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    st.markdown('<p class="section-label">Retrieval</p>', unsafe_allow_html=True)
    top_k = st.slider(
        "Top-K passages",
        1,
        10,
        TOP_K,
        help="Sources sent to the LLM",
        label_visibility="visible",
    )

    st.markdown('<p class="section-label">Quick Prompts</p>', unsafe_allow_html=True)
    for icon, short, full in EXAMPLES:
        if st.button(f"{icon}  {short}", key=f"ex_{short}", use_container_width=True):
            st.session_state.question = full
            st.session_state.trigger_query = full
            st.rerun()

    return top_k


def _render_header() -> None:
    st.markdown(
        f"""
        <p class="ios-large-title">MedAssist Local</p>
        <p class="ios-subtitle">Private healthcare Q&A · Local LLM + RAG</p>
        <div class="ios-banner">
            <span class="ios-banner-icon">⚠️</span>
            <div class="ios-banner-text">
                <strong>Medical disclaimer</strong> — Informational use only.
                Not medical advice. Always consult a healthcare professional.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_stats(response: RAGResponse) -> None:
    llm = "Ollama" if response.used_ollama else "Fallback"
    st.markdown('<p class="ios-section-label">Performance</p>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ios-stat-grid">
            <div class="ios-stat blue">
                <div class="ios-stat-label">Latency</div>
                <div class="ios-stat-value blue">{response.latency_sec}s</div>
            </div>
            <div class="ios-stat green">
                <div class="ios-stat-label">Retrieval</div>
                <div class="ios-stat-value green">{response.retrieval_sec}s</div>
            </div>
            <div class="ios-stat purple">
                <div class="ios-stat-label">Sources</div>
                <div class="ios-stat-value purple">{len(response.chunks)}</div>
            </div>
            <div class="ios-stat orange">
                <div class="ios-stat-label">Generator</div>
                <div class="ios-stat-value orange" style="font-size:17px;padding-top:4px;">{llm}</div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_answer(response: RAGResponse) -> None:
    st.markdown('<p class="ios-section-label">Answer</p>', unsafe_allow_html=True)
    st.markdown(
        f"""
        <div class="ios-answer-box">
            <div class="ios-answer-header">
                <span class="ios-chip">AI Response</span>
                <span class="ios-chip-sub">Grounded in NIH sources</span>
            </div>
            <div class="ios-answer-text">{_escape(response.answer)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_sources(chunks) -> None:
    st.markdown('<p class="ios-section-label">Sources</p>', unsafe_allow_html=True)
    if not chunks:
        st.markdown(
            f"""
            <div class="ios-group">
                <div class="ios-row">
                    <div class="ios-icon orange">🔍</div>
                    <span class="ios-row-title" style="color:{IOS["label"]};">
                        No relevant passages found for this query.
                    </span>
                </div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        return

    for i, chunk in enumerate(chunks, 1):
        pct = min(int(chunk.score * 100), 100)
        preview = chunk.text if len(chunk.text) <= 480 else chunk.text[:480] + "…"
        st.markdown(
            f"""
            <div class="ios-source-card">
                <div class="ios-source-top">
                    <span class="ios-source-num">Source {i}</span>
                    <span class="ios-score">{chunk.score:.2f}</span>
                </div>
                <div class="ios-progress">
                    <div class="ios-progress-fill" style="width:{pct}%;"></div>
                </div>
                <div class="ios-source-body">{_escape(preview)}</div>
                <div class="ios-source-id">{chunk.doc_id}</div>
            </div>
            """,
            unsafe_allow_html=True,
        )
        if len(chunk.text) > 480:
            with st.expander(f"Full text · Source {i}"):
                st.markdown(
                    f'<p style="color:{IOS["text2"]}; font-size:15px; line-height:1.5;">'
                    f"{_escape(chunk.text)}</p>",
                    unsafe_allow_html=True,
                )


def _render_empty() -> None:
    st.markdown(
        f"""
        <div class="ios-empty">
            <div class="ios-empty-icon">💬</div>
            <p class="ios-empty-title">Ask a question</p>
            <p class="ios-empty-sub">
                Type a medical question below or pick a quick prompt from Settings.
                Answers run locally with cited sources.
            </p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.markdown(f"<style>{CSS}</style>", unsafe_allow_html=True)
    _init_session()

    top_k = _render_sidebar()
    _render_header()

    if not _index_ready():
        st.stop()

    st.markdown('<p class="ios-section-label">Your Question</p>', unsafe_allow_html=True)
    with st.container(border=True):
        question = st.text_area(
            "question_input",
            value=st.session_state.question,
            height=100,
            placeholder="What are common side effects of aspirin?",
            label_visibility="collapsed",
        )

    c1, c2 = st.columns([3, 1])
    with c1:
        ask_clicked = st.button("Ask MedAssist", type="primary", use_container_width=True)
    with c2:
        if st.button("Clear", use_container_width=True):
            st.session_state.question = ""
            st.session_state.response = None
            st.rerun()

    st.session_state.question = question

    run_query = ask_clicked or st.session_state.pop("trigger_query", None)
    if run_query and question.strip():
        with st.spinner("Searching sources…"):
            st.session_state.response = ask(question.strip(), top_k=top_k)
            st.session_state.history.insert(
                0,
                {"q": question.strip(), "sources": len(st.session_state.response.chunks)},
            )

    response: RAGResponse | None = st.session_state.response

    if response is None:
        _render_empty()
    else:
        _render_stats(response)
        _render_answer(response)
        _render_sources(response.chunks)

        if st.session_state.history:
            st.markdown('<p class="ios-section-label">History</p>', unsafe_allow_html=True)
            rows = ""
            for item in st.session_state.history[:6]:
                rows += f"""
                <div class="ios-row">
                    <div class="ios-icon blue">💬</div>
                    <span class="ios-row-title">{_escape(item['q'][:70])}{'…' if len(item['q']) > 70 else ''}</span>
                    <span class="ios-row-value">{item['sources']} src</span>
                </div>
                """
            st.markdown(f'<div class="ios-group">{rows}</div>', unsafe_allow_html=True)


if __name__ == "__main__":
    main()
