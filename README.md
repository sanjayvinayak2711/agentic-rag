# 🚀 Aetherion — Agentic Multi-LLM Orchestration System

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![Vercel](https://img.shields.io/badge/Deployed-Vercel-black)
![License](https://img.shields.io/badge/License-MIT-yellow)

Built a production-deployed agentic RAG system that autonomously plans, evaluates, and refines responses using multi-LLM orchestration.

**Key Results:**
- ↑ 21% response relevance vs standard RAG baseline
- ↓ 25% hallucination rate using evaluation loops
- Supports 7+ LLM providers with dynamic fallback
- Real-time execution trace + quality scoring
- ~1.2s average pipeline latency (with evaluation loop)
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

**Design Tradeoff:** Prioritized response quality over latency by introducing evaluation loops, balanced using model routing and async execution.

**Failure Handling:** Fallback across providers ensures resilience against model/API failures.

**Scalability:** Stateless backend design enables horizontal scaling across concurrent users.

---

## 📊 Evaluation

Evaluated on 50 QA pairs (arXiv dataset) using GPT-4 rubric (relevance, grounding, completeness).

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

---

## 📸 Demo Preview

End-to-end flow: query → planning → retrieval → evaluation → refined response

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

- Demonstrates production-grade agentic AI (not just RAG)
- Shows system design: orchestration, evaluation, and tradeoffs
- Built with scalability, observability, and reliability in mind

Built for real-world AI systems, not demos.

---

## License

MIT – see [LICENSE](LICENSE)
