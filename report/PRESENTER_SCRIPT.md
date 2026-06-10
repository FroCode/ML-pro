# MedAssist Local — Premium Presentation Script (20 slides)

**File:** `report/MedAssist_Local_Premium_Presentation.pptx`  
**Target length:** 8–10 minutes  
Replace `[Your Name]` on slides 1 and 20 before recording.

---

## Slide 1 — Title (40 sec)

> Hello, I am [Your Name]. Welcome to my Machine Learning final project presentation.
>
> Today I present **MedAssist Local** — a **private healthcare question-and-answer assistant** built with **Local LLM and Retrieval-Augmented Generation**.
>
> This project uses **Technical Track 1**, combining **Ollama**, **ChromaDB**, and **Streamlit** to deliver source-grounded medical answers that never leave your machine.

---

## Slide 2 — Agenda (20 sec)

> Here is what I will cover: the problem and motivation, our technical RAG approach, the MedQuAD dataset and implementation plan, evaluation metrics, and the live demo schedule.

---

## Slide 3 — Section: Background (10 sec)

> Part one — background and motivation.

---

## Slide 4 — Problem & Motivation (1 min)

> Medical knowledge is vast. MedQuAD alone contains over **47,000 question-answer pairs** from NIH sources covering more than **12,000 health topics**.
>
> Yet patients and students struggle to find **quick, trustworthy answers with clear sources**.
>
> Sending health questions to cloud AI raises serious **privacy concerns**. And plain LLMs can **hallucinate** medical facts.
>
> My solution: a **100% local system** that retrieves real documents first, then generates cited answers.

---

## Slide 5 — Project Scope (45 sec)

> The application area is **healthcare informational Q&A** — drug information, conditions, and symptoms.
>
> The technical track is **Local LLM plus RAG** using Ollama and ChromaDB.
>
> The privacy goal is **fully offline inference** with no external API calls.
>
> And we will measure performance numerically using **Recall at 5, MRR, ROUGE-L, and latency**.
>
> Important disclaimer: this is **informational only**, not a substitute for professional medical advice.

---

## Slide 6 — Section: Technical Approach (10 sec)

> Part two — our technical approach.

---

## Slide 7 — Why RAG? (1 min)

> This slide compares **Plain LLM** versus **RAG plus Local LLM**.
>
> A plain LLM answers from memory alone — higher hallucination risk, no citations, knowledge frozen at training time.
>
> Our RAG system **retrieves real NIH passages first**, grounds the answer in that context, returns **citations with similarity scores**, and lets us **update knowledge** simply by re-indexing new documents.
>
> That is why RAG is the right architecture for trustworthy healthcare Q&A.

---

## Slide 8 — Architecture (1 min 15 sec)

> Here is the full pipeline.
>
> The user asks a question through **Streamlit**. The question is embedded into a **384-dimensional vector** using **all-MiniLM-L6-v2**.
>
> **ChromaDB** searches roughly five thousand MedQuAD chunks and returns the **top five** most similar passages.
>
> A **prompt builder** combines those passages with the question. **Ollama** running **Llama 3.2** generates the final answer.
>
> The output includes the **answer, source citations, similarity scores, and response time**.

---

## Slide 9 — Prompt Engineering (45 sec)

> To reduce hallucinations, I use a strict **system prompt**: the model must answer **only from provided context**.
>
> If the context is insufficient, it must say so explicitly.
>
> Key parameters: **temperature 0.1** for factual consistency, **max 512 tokens**, **top-5 retrieval**, and a **similarity threshold of 0.5** to filter irrelevant chunks.

---

## Slide 10 — Technology Stack (30 sec)

> The stack has five layers: **Streamlit** for the UI, **Python** for orchestration, **Ollama and sentence-transformers** for AI, **ChromaDB** for vector storage, and **rouge-score plus custom scripts** for evaluation.

---

## Slide 11 — Section: Data & Implementation (10 sec)

> Part three — data and implementation.

---

## Slide 12 — Dataset (1 min)

> Our primary dataset is **MedQuAD** from Hugging Face — **47,457 pairs** sourced from NIH websites including GARD, GHR, NIDDK, and others.
>
> The preprocessing pipeline: download, clean HTML, chunk into **300 to 500 token segments** with **50-token overlap**, embed with **384-dimensional vectors**, and index in **ChromaDB** with full metadata.
>
> We may also add WHO fact sheets as an optional extension.

---

## Slide 13 — Implementation Plan (1 min)

> **Phase one** — data pipeline: download, chunk, embed, index. Deliverable: indexed corpus with statistics.
>
> **Phase two** — RAG core: semantic search, prompt design, Ollama integration. Deliverable: working command-line RAG.
>
> **Phase three** — Streamlit UI with source panel, latency counter, and disclaimer. Deliverable: browser demo.
>
> **Phase four** — evaluation on 100 held-out test questions. Deliverable: metrics CSV and plots for the report.

---

## Slide 14 — Repository Structure (30 sec)

> The codebase is organized for reproducibility: data, source modules, Streamlit app, results folder, and report.
>
> This maps directly to all project deliverables: dataset sourcing, real-time demo, technical report, numerical evaluation, and full source code.

---

## Slide 15 — Section: Evaluation & Delivery (10 sec)

> Part four — evaluation and delivery.

---

## Slide 16 — Evaluation Metrics (1 min)

> The assignment requires numerical measurement. We track four metrics.
>
> **Recall at 5** — is the correct chunk in the top five?
> **MRR** — how highly ranked is the first relevant result?
> **ROUGE-L** — how similar is our answer to the reference?
> **Latency** — wall-clock response time.
>
> Targets: Recall above **0.70**, MRR above **0.55**, ROUGE-L above **0.35**, and under **5 seconds** on CPU.

---

## Slide 17 — Live Demo Plan (45 sec)

> On **June 17th**, I will demo four scenarios live.
>
> Three success cases: aspirin side effects, hypertension, diabetes symptoms — each showing answer, sources, scores, and timing.
>
> One failure case: an out-of-domain question about quantum physics — the system should refuse gracefully.

---

## Slide 18 — Timeline (30 sec)

> Week one: data pipeline. Week two: RAG and UI. Week three: evaluation and report.
>
> Final live demo and report: **June 17, 2026**.

---

## Slide 19 — Risks & Mitigations (30 sec)

> Key risks: slow CPU inference — mitigated with a smaller model; low retrieval accuracy — tune chunk size; hallucinations — strict prompts; ethical concerns — clear disclaimer; English-only dataset bias — documented as a limitation.

---

## Slide 20 — Conclusion (25 sec)

> MedAssist Local delivers **private, source-grounded healthcare Q&A** using Local LLM and RAG.
>
> It meets every project requirement: dataset sourcing, technical depth, numerical evaluation, and a live demo.
>
> Thank you. I am happy to take your questions.

---

## Recording checklist

1. Open `MedAssist_Local_Premium_Presentation.pptx`
2. Edit **[Your Name]** on slides 1 and 20
3. Slide Show → From Beginning (fullscreen)
4. Win + G → record screen + microphone
5. Target **8–10 minutes**
6. Export as **MP4** and upload before **11:59 PM**
