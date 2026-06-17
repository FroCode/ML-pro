# Presentation Diagrams — MedAssist Local (Icon-First)

Two **icon-based** diagrams — minimal text, visual flow. Insert PNGs into PowerPoint.

| File | Use on slide |
|------|----------------|
| `report/assets/diagram1_system_architecture.png` | System architecture overview |
| `report/assets/diagram2_rag_query_flow.png` | RAG query flow (6 steps) |

**Regenerate:**
```powershell
python report/assets/generate_presentation_diagrams.py
```

---

## Diagram 1 — Icon map (what each icon means)

| Icon | Meaning |
|------|---------|
| 📄 Stack of pages | MedQuAD dataset |
| 🧩 Puzzle pieces | Text chunking |
| ⊞ Dot grid | Embedding vectors |
| 🛢 Cylinder | ChromaDB index |
| 👤 Person | User |
| 🖥 Monitor | Streamlit UI |
| ⊛ Hub | RAG orchestrator |
| 🔍 Magnifying glass | Vector search |
| 🧠 Brain/chip | Ollama LLM |
| 💬 Check bubble | Answer |
| 📑 Stacked bars | Source citations |
| 📊 Bar chart | Metrics |
| 🔒 Lock | Everything runs local |

**Say in 20 sec:** “Top row builds the index offline. Bottom row is runtime: user asks in Streamlit, RAG searches ChromaDB, Ollama generates, we return answer + sources + metrics — all local.”

---

## Diagram 2 — Six icon steps

| # | Icon | Step |
|---|------|------|
| 1 | Person | User asks |
| 2 | Monitor | Streamlit input |
| 3 | Dot grid | Embed question |
| 4 | Magnifying glass | Search index |
| 5 | Funnel | Re-rank & filter |
| 6 | Document | Build prompt |
| 7 | Brain | Ollama generate |
| ↓ | Answer · Sources · Metrics | Output |

**Say in 20 sec:** “One question flows left to right through six steps — embed, search, rank, prompt, generate — then we output the answer with sources and timing metrics.”
