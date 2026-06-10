"""Generate diagram images and download stock photos for the presentation."""
from __future__ import annotations

import urllib.request
from pathlib import Path

import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ASSETS = Path(__file__).parent

# Professional palette
NAVY = "#0B1D3A"
TEAL = "#00B4A6"
BLUE = "#4A90D9"
LIGHT = "#E8F4F8"
WHITE = "#FFFFFF"
ORANGE = "#F5A623"
PURPLE = "#7B61FF"

PHOTOS = {
    "hero_healthcare.jpg": "https://images.unsplash.com/photo-1576091160399-112ba8d25d1d?w=1920&q=80",
    "doctor_consult.jpg": "https://images.unsplash.com/photo-1559839734-2b71ea197ec2?w=1200&q=80",
    "ai_brain.jpg": "https://images.unsplash.com/photo-1620712943543-bcc4688e7485?w=1200&q=80",
    "data_analytics.jpg": "https://images.unsplash.com/photo-1551288049-bebda4e38f71?w=1200&q=80",
    "privacy_lock.jpg": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=1200&q=80",
    "team_work.jpg": "https://images.unsplash.com/photo-1522071820081-009f0129c71c?w=1200&q=80",
}


def download_photos() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    for name, url in PHOTOS.items():
        dest = ASSETS / name
        if dest.exists() and dest.stat().st_size > 10_000:
            print(f"  skip (exists): {name}")
            continue
        print(f"  downloading: {name}")
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
            with urllib.request.urlopen(req, timeout=30) as resp:
                dest.write_bytes(resp.read())
        except Exception as exc:
            print(f"  warning: could not download {name}: {exc}")


def _rounded_box(ax, x, y, w, h, text, color, text_color="white", fontsize=11):
    box = FancyBboxPatch(
        (x, y), w, h,
        boxstyle="round,pad=0.02,rounding_size=0.08",
        facecolor=color, edgecolor="white", linewidth=2,
        transform=ax.transData, zorder=2,
    )
    ax.add_patch(box)
    ax.text(x + w / 2, y + h / 2, text, ha="center", va="center",
            fontsize=fontsize, fontweight="bold", color=text_color, zorder=3)


def architecture_diagram() -> Path:
    fig, ax = plt.subplots(figsize=(14, 7))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 7)
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)

    ax.text(7, 6.5, "MedAssist Local — RAG Pipeline Architecture",
            ha="center", fontsize=18, fontweight="bold", color=NAVY)

    boxes = [
        (5.5, 5.2, 3, 0.75, "User Question\n(Streamlit UI)", NAVY),
        (5.5, 4.0, 3, 0.75, "Embedding Model\nall-MiniLM-L6-v2", BLUE),
        (5.5, 2.8, 3, 0.75, "Vector Search\nChromaDB (Top-K)", TEAL),
        (5.5, 1.6, 3, 0.75, "Prompt Builder\nContext + Question", PURPLE),
        (5.5, 0.4, 3, 0.75, "Local LLM\nOllama (Llama 3.2)", ORANGE),
    ]
    for x, y, w, h, txt, col in boxes:
        _rounded_box(ax, x, y, w, h, txt, col, fontsize=10)

    for y_from, y_to in [(5.2, 4.75), (4.0, 3.55), (2.8, 2.35), (1.6, 1.15)]:
        ax.annotate("", xy=(7, y_to), xytext=(7, y_from),
                    arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2.5))

    _rounded_box(ax, 10.2, 2.0, 2.8, 1.2, "Knowledge Base\nMedQuAD Chunks\n~5,000 vectors", "#2ECC71", fontsize=9)
    ax.annotate("", xy=(8.5, 3.15), xytext=(10.2, 2.6),
                arrowprops=dict(arrowstyle="<->", color=TEAL, lw=2, connectionstyle="arc3,rad=0.2"))

    _rounded_box(ax, 0.5, 0.4, 3.2, 0.75, "Answer + Citations\n+ Similarity Scores", "#27AE60", fontsize=10)
    ax.annotate("", xy=(3.7, 0.78), xytext=(5.5, 0.78),
                arrowprops=dict(arrowstyle="-|>", color="#27AE60", lw=2.5))

    out = ASSETS / "architecture_diagram.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    return out


def rag_vs_llm_diagram() -> Path:
    fig, axes = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor(WHITE)
    fig.suptitle("Why RAG? Plain LLM vs Retrieval-Augmented Generation",
                 fontsize=16, fontweight="bold", color=NAVY, y=1.02)

    for ax, title, items, color, verdict in [
        (axes[0], "Plain LLM (No RAG)", [
            "Answers from parametric memory only",
            "Higher hallucination risk on niche medical facts",
            "Cannot cite specific document sources",
            "Knowledge frozen at training cutoff date",
        ], "#E74C3C", "Risk: Unverified answers"),
        (axes[1], "RAG + Local LLM", [
            "Retrieves real NIH / MedQuAD passages first",
            "Answers grounded in retrieved context",
            "Returns citations with similarity scores",
            "Update knowledge by re-indexing documents",
        ], TEAL, "Benefit: Traceable & private"),
    ]:
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        ax.axis("off")
        ax.add_patch(FancyBboxPatch((0.3, 0.5), 9.4, 9, boxstyle="round,pad=0.05",
                                    facecolor=LIGHT, edgecolor=color, linewidth=3))
        ax.text(5, 8.8, title, ha="center", fontsize=13, fontweight="bold", color=color)
        for i, item in enumerate(items):
            ax.text(1, 7.2 - i * 1.3, f"  {item}", fontsize=11, color=NAVY, va="center")
        ax.text(5, 1.2, verdict, ha="center", fontsize=11, fontweight="bold", color=color)

    out = ASSETS / "rag_vs_llm.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    return out


def metrics_dashboard() -> Path:
    fig, ax = plt.subplots(figsize=(12, 5))
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.text(6, 4.6, "Target Evaluation Metrics", ha="center",
            fontsize=18, fontweight="bold", color=NAVY)

    metrics = [
        ("Recall@5", "> 0.70", "Retrieval quality", TEAL),
        ("MRR", "> 0.55", "Ranking quality", BLUE),
        ("ROUGE-L", "> 0.35", "Answer similarity", PURPLE),
        ("Latency", "< 5 sec", "Real-time demo", ORANGE),
    ]
    for i, (name, val, desc, col) in enumerate(metrics):
        x = 0.5 + i * 3
        ax.add_patch(FancyBboxPatch((x, 1.2), 2.6, 2.8, boxstyle="round,pad=0.08",
                                    facecolor=col, edgecolor="white", linewidth=2, alpha=0.92))
        ax.text(x + 1.3, 3.4, name, ha="center", fontsize=14, fontweight="bold", color="white")
        ax.text(x + 1.3, 2.5, val, ha="center", fontsize=22, fontweight="bold", color="white")
        ax.text(x + 1.3, 1.7, desc, ha="center", fontsize=9, color="white")

    out = ASSETS / "metrics_dashboard.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    return out


def timeline_diagram() -> Path:
    fig, ax = plt.subplots(figsize=(14, 4))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4)
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.text(7, 3.6, "Project Timeline — June 2026", ha="center",
            fontsize=16, fontweight="bold", color=NAVY)

    weeks = [
        ("Week 1", "Data Pipeline", "MedQuAD download\nChunking & embedding\nChromaDB index", TEAL),
        ("Week 2", "RAG + UI", "Ollama integration\nPrompt engineering\nStreamlit demo app", BLUE),
        ("Week 3", "Evaluate", "Recall@k, MRR, ROUGE-L\nReport writing\nDemo rehearsal", PURPLE),
        ("Jun 17", "Submit", "Live demo at university\nTechnical report", ORANGE),
    ]
    for i, (label, phase, detail, col) in enumerate(weeks):
        x = 0.8 + i * 3.3
        ax.add_patch(FancyBboxPatch((x, 1.0), 2.8, 2.0, boxstyle="round,pad=0.06",
                                    facecolor=col, edgecolor="white", linewidth=2))
        ax.text(x + 1.4, 2.6, label, ha="center", fontsize=12, fontweight="bold", color="white")
        ax.text(x + 1.4, 2.1, phase, ha="center", fontsize=10, color="white")
        ax.text(x + 1.4, 1.5, detail, ha="center", fontsize=8, color="white")
        if i < 3:
            ax.annotate("", xy=(x + 3.0, 2.0), xytext=(x + 2.85, 2.0),
                        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2))

    out = ASSETS / "timeline.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    return out


def tech_stack_diagram() -> Path:
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.text(6, 5.5, "Technology Stack", ha="center", fontsize=18, fontweight="bold", color=NAVY)

    layers = [
        ("Presentation Layer", "Streamlit Web UI", "#3498DB"),
        ("Application Layer", "Python 3.10+  |  RAG Orchestrator", NAVY),
        ("AI Layer", "Ollama (Llama 3.2)  |  sentence-transformers", TEAL),
        ("Data Layer", "ChromaDB Vector Store  |  MedQuAD Corpus", PURPLE),
        ("Evaluation Layer", "scikit-learn  |  rouge-score  |  Custom scripts", ORANGE),
    ]
    for i, (layer, tools, col) in enumerate(layers):
        y = 4.2 - i * 0.95
        ax.add_patch(FancyBboxPatch((1, y), 10, 0.75, boxstyle="round,pad=0.04",
                                    facecolor=col, edgecolor="white", linewidth=2, alpha=0.9))
        ax.text(1.3, y + 0.38, layer, fontsize=10, fontweight="bold", color="white", va="center")
        ax.text(6, y + 0.38, tools, fontsize=10, color="white", va="center", ha="center")

    out = ASSETS / "tech_stack.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    return out


def data_pipeline_diagram() -> Path:
    fig, ax = plt.subplots(figsize=(14, 4.5))
    ax.set_xlim(0, 14)
    ax.set_ylim(0, 4.5)
    ax.axis("off")
    fig.patch.set_facecolor(WHITE)
    ax.text(7, 4.1, "Data Preprocessing Pipeline", ha="center",
            fontsize=16, fontweight="bold", color=NAVY)

    steps = [
        ("MedQuAD\n(HuggingFace)", NAVY),
        ("Text\nCleaning", BLUE),
        ("Chunking\n300-500 tokens", TEAL),
        ("Embedding\n384-dim vectors", PURPLE),
        ("ChromaDB\nIndex", ORANGE),
    ]
    for i, (label, col) in enumerate(steps):
        x = 0.5 + i * 2.7
        _rounded_box(ax, x, 1.5, 2.2, 1.4, label, col, fontsize=10)
        if i < len(steps) - 1:
            ax.annotate("", xy=(x + 2.35, 2.2), xytext=(x + 2.2, 2.2),
                        arrowprops=dict(arrowstyle="-|>", color=NAVY, lw=2))

    ax.text(7, 0.5, "Metadata per chunk: source_url | question_id | chunk_id | token_count",
            ha="center", fontsize=10, color="#666", style="italic")

    out = ASSETS / "data_pipeline.png"
    fig.savefig(out, dpi=180, bbox_inches="tight", facecolor=WHITE)
    plt.close(fig)
    return out


def main() -> None:
    ASSETS.mkdir(parents=True, exist_ok=True)
    print("Downloading stock photos...")
    download_photos()
    print("Generating diagrams...")
    for fn in (architecture_diagram, rag_vs_llm_diagram, metrics_dashboard,
               timeline_diagram, tech_stack_diagram, data_pipeline_diagram):
        path = fn()
        print(f"  created: {path.name}")
    print("Done.")


if __name__ == "__main__":
    main()
