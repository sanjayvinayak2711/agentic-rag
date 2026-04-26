# 🚀 Aetherion — Agentic Multi-LLM Orchestration System

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![Vercel](https://img.shields.io/badge/Deployed-Vercel-black)
![License](https://img.shields.io/badge/License-MIT-yellow)

> 🧠 **What this system does:** An AI system that improves LLM answers using self-evaluation + retry loops, reducing hallucinations by 25%.

A self-improving RAG system with evaluation-driven retry loops and multi-LLM routing.

Built a production-deployed agentic RAG system that autonomously plans, evaluates, and refines responses using multi-LLM orchestration.

**Key Results:**
- ↑ 21% response relevance vs standard RAG baseline
- ↓ 25% hallucination rate using evaluation loops
- Supports 7+ LLM providers with dynamic fallback
- Real-time execution trace + quality scoring
- ~1.2s average pipeline latency (vs ~0.8s standard RAG)
- Handles concurrent requests via async FastAPI execution

👉 Independently designed and implemented end-to-end system (architecture, backend, orchestration, evaluation)

**Live Demo:** https://agentic-rag-gamma.vercel.app

---

## 👨‍💻 My Contribution

- Designed agent architecture (planner, critic, retry loop)
- Implemented multi-LLM routing and fallback strategy
- Built FastAPI backend with async execution
- Developed evaluation pipeline for response scoring
- Deployed full-stack system (Vercel + Railway)

---

## 🏗️ Architecture

```
┌─────────┐   ┌─────────────┐   ┌──────────┐   ┌──────────┐   ┌────────┐   ┌─────────────┐
│  User   │ → │ Smart Query │ → │ Retrieval│ → │   LLM    │ → │ Critic │ → │ Final Answer│
└─────────┘   │ Intent Detect│   └──────────┘   └──────────┘   └────────┘   └─────────────┘
              └─────────────┘         ↑___________________________________________↓
                                           (Self-Correction Loop)
```

**Pipeline:** Query → Intent Detection → Hybrid Retrieval → Generation → Critic Evaluation → Score Check → [Refine if needed] → Final Answer

### Agent Structure
```python
backend/agents/
├── planner_agent.py      # 🧠 Smart Query intent detection
├── critic_agent.py       # 🔍 Quality evaluation
├── reasoning_agent.py    # 💬 Response generation
├── retry_agent.py        # 🔄 Auto-correction
└── orchestrator.py       # 🎛️ Pipeline coordination
```

**Simple Mental Model:**
> Think of it like a student taking an exam: Understand the question → Fetch your notes → Write an answer → Check your work like a teacher would → Fix mistakes before submitting.

**Design Tradeoff:** Prioritized response quality over latency by introducing evaluation loops, balanced using model routing and async execution.

**Failure Handling:** Fallback across providers ensures resilience against model/API failures.

**Scalability:** Stateless backend design enables horizontal scaling across concurrent users.

---

## 📊 Evaluation

**Verified Engineering:** See full methodology in [`docs/EVALUATION.md`](docs/EVALUATION.md)

| Proof Item | Details |
|------------|---------|
| **Dataset** | 50 QA pairs from arXiv papers ([`data/qa_pairs.json`](data/qa_pairs.json)) |
| **Sample Prompts** | See [`docs/sample_prompts.md`](docs/sample_prompts.md) for 10 example queries |
| **Judge** | GPT-4 with structured rubric ([`docs/evaluation_rubric.md`](docs/evaluation_rubric.md)) |
| **Raw Outputs** | Evaluation logs in [`logs/evaluation/`](logs/evaluation/) |
| **Reproducibility** | `python scripts/evaluate.py --dataset data/qa_pairs.json` |
| **Ablation Study** | Critic agent adds +0.7 score, evaluation loop improves consistency +23% |

Results (50 QA pairs, arXiv dataset, GPT-4 rubric):

| Metric | Result |
|--------|--------|
| Relevance | 7.1 → 8.6 (+21%) |
| Hallucination rate | Reduced by ~25% |
| Refinement iterations | Up to 3 per query |

---

## ⚡ Core Features

- Agentic pipeline with planning + self-correction
- Evaluation-driven generation (quality scoring)
- Multi-LLM routing with fallback
- Execution trace for observability
- Bring-your-own-key (secure, no storage)

## 🛡️ Production Signals

| Feature | Implementation |
|---------|----------------|
| **Rate Limiting** | Middleware with configurable requests/minute |
| **Structured Logging** | JSON logs with request tracing |
| **Health Endpoint** | `GET /health` returns system status |
| **Timeout Handling** | 30s LLM timeout with graceful degradation |
| **Error Classification** | Categorized API errors (retryable vs fatal) |

---

## 📸 Demo Preview

End-to-end flow: query → planning → retrieval → evaluation → refined response

### 🔥 Before vs After: Hallucination Fix

**Query:** "What is attention mechanism in Transformers?"

|  | Normal RAG | Aetherion (Agentic) |
|--|------------|---------------------|
| **Answer** | "Attention helps models focus on important parts" | "Self-attention computes Q, K, V matrices allowing parallel token processing (Vaswani et al., 2017)" |
| **Citations** | ❌ None | ✅ Paper cited |
| **Depth** | Surface-level | Technical (QKV, multi-head, complexity O(n²)) |
| **Score** | 6.8/10 | 8.7/10 |

**What happened:** Critic detected shallow answer → triggered retry with "include technical details and citations" → LLM regenerated with depth.

### UI Interface
![UI](docs/images/ui.png)

### Chat Interface
![Chat](docs/images/chat.png)

---

## Live Demo

**Frontend:** https://agentic-rag-gamma.vercel.app  
**API:** https://agentic-rag-production.up.railway.app

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **API Framework** | FastAPI |
| **Vector Store** | ChromaDB (hybrid dense + sparse) |
| **LLM Providers** | OpenAI, Anthropic, Google, NVIDIA, Groq, HuggingFace, Ollama |
| **Embeddings** | sentence-transformers |
| **Frontend** | Vanilla JS + Tailwind |
| **Deployment** | Vercel (frontend), Railway (backend), Docker |

---

## Quick Start

### Local Development

```bash
git clone https://github.com/kcsanjayj/agentic-rag.git
cd agentic-rag
pip install -r requirements.txt
python start.py
```

### One-Click Deploy

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/new/template?template=https://github.com/kcsanjayj/Aetherion&envs=AI_PROVIDER,OPENAI_MODEL,CORS_ORIGINS)

**Setup:**
1. Open http://localhost:8000
2. Click **AI Config** → Select provider → Enter API key → Save
3. Wait for **✅ API Active** badge (green)
4. Upload document → Ask question → See execution trace

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [Architecture](docs/ARCHITECTURE.md) | System design & agent orchestration |
| [API Reference](docs/API.md) | REST endpoints & schemas |
| [Evaluation](docs/EVALUATION.md) | Scoring rubric & methodology |
| [Deployment](docs/DEPLOYMENT.md) | Production setup (Vercel + Railway) |

---

## ⚡ Why Engineers Care

- Production-grade agentic AI with observable orchestration
- System design: evaluation loops, tradeoffs, failure handling
- Built for scalability, reliability, and real-world deployment

---

## ❌ Known Limitations

| Limitation | Impact | Mitigation |
|------------|--------|------------|
| **Increased latency** | ~1.2s avg (vs ~0.8s baseline) due to critic loop | Async execution, model routing |
| **Judge LLM dependency** | Evaluation quality tied to GPT-4 capabilities | Structured rubric, multi-criteria scoring |
| **Small dataset** | 50 QA pairs (research papers only) | Ablation studies, cross-validation |
| **Cost overhead** | Multiple LLM calls per query | BYOK model, caching layer ready |

---

## License

MIT – see [LICENSE](LICENSE)
