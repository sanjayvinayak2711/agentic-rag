# Aetherion

**Agentic Multi-LLM Orchestration Platform**

![Python](https://img.shields.io/badge/Python-3.10-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-backend-green)
![Vercel](https://img.shields.io/badge/Deployed-Vercel-black)
![License](https://img.shields.io/badge/License-MIT-yellow)

> **Note:** Repository folder name is `agentic-rag` while project is Aetherion.

---

## 🚀 TL;DR

Aetherion is an agentic RAG system that:

- Routes queries across multiple LLMs  
- Evaluates and self-corrects responses  
- Blocks low-quality outputs before delivery  
- Supports 7+ providers with dynamic fallback  

👉 **Live Demo:** https://agentic-rag-gamma.vercel.app

---

## 🎥 Demo Walkthrough

[![Watch Demo](docs/images/ui.png)](https://github.com/user-attachments/assets/a25725cb-8276-4dd6-80e5-abee429fd004)

▶ Click to watch full demo

---

## 📸 Demo Preview

### UI Interface
![UI](docs/images/ui.png)

### Chat Interface
![Chat](docs/images/chat.png)

---

## 🧠 Key Idea

Traditional RAG pipelines generate once and return output.

**Aetherion introduces:**
- Evaluation-driven generation  
- Iterative refinement loops  
- Quality gating before response delivery  

This shifts RAG systems from **static pipelines → adaptive AI systems**.

---

## 🆕 New Features

### 🧠 Smart Query Mode
Automatically detects query intent and optimizes response strategy:

| Intent | Detected Keywords | Strategy |
|----------|-------------------|----------|
| **Compare** | compare, vs, difference, similarities | Structured side-by-side comparison |
| **Summarize** | summarize, summary, overview, tldr | Document-specific summaries |
| **Extract** | extract, find, what is, who, when | Targeted information extraction |
| **Analyze** | analyze, evaluate, explain, why, how | Deep critical analysis |

### 🎯 Clear Status Mechanism
Non-blocking, clear API status indication:
- **⚠️ Needs Config** (yellow, pulsing) - No API key configured
- **✅ API Active** (green) - Ready to query
- **❌ API Inactive** (red) - Connection issue

### 🔐 BYOK (Bring Your Own Key)
- Session-based API key storage (memory only, cleared on refresh)
- Supports 7+ providers with runtime configuration
- No backend persistence of sensitive keys

## Performance

| Metric | Standard RAG | Aetherion |
|--------|--------------|-----------|
| Response Relevance | 7.1/10 | **8.6/10** (+21%) |
| Hallucination Rate | High | **-25%** |
| Quality Assurance | None | **Up to 3 Iterations** |
| Query Intent Detection | None | **4 Smart Modes** |

*All metrics evaluated using GPT-4 rubric (relevance, grounding, completeness) on 50 QA pairs (arXiv dataset).*

---

## Live Demo

**Frontend:** https://agentic-rag-gamma.vercel.app  
**API:** https://agentic-rag-production.up.railway.app

**What you'll see:**
- **Smart Query Mode** — Auto-detects intent (compare, summarize, extract, analyze)
- **Clear Status Badge** — Know exactly when API is ready (⚠️ Needs Config → ✅ API Active)
- **Model Selection** — Choose from 7+ providers (OpenAI, Gemini, Claude, NVIDIA, Groq, HuggingFace, Ollama)
- **Evaluation Score** — Real-time quality rating (e.g., 8.7/10)
- **Execution Trace** — Step-by-step agent pipeline visibility
- **Self-Correction Loop** — Watch iterations until quality threshold is met
- **Session-Based Security** — API keys in memory only, never persisted

---

## Example Output

**Query:** What is attention mechanism?

**Final Response (after evaluation & refinement):**
> Attention allows models to dynamically weight token importance, enabling parallel processing of sequences (Vaswani et al., 2017).

**Metadata:**
| Attribute | Value |
|-----------|-------|
| **Model Used** | GPT-4 |
| **Quality Score** | 8.7/10 |
| **Iterations** | 2 (self-corrected) |
| **Source Document** | `attention-is-all-you-need.pdf` |
| **Pipeline Time** | 1.2s |

---

## The Problem with Traditional RAG

Standard RAG pipelines retrieve context, generate an answer, and ship it. No validation. No feedback loop. No quality guarantee.

**The result:** Hallucinations, incomplete answers, and untrusted outputs.

**Aetherion's approach:**
- **Validation Layer** — Every answer scored before delivery
- **Self-Correction Loop** — Auto-refinement until quality threshold met
- **Quality Gating** — Low-scoring responses blocked, not shipped
- **Full Observability** — Execution trace shows exactly what happened

---

## Architecture

```
┌─────────┐   ┌─────────────┐   ┌──────────┐   ┌──────────┐   ┌────────┐   ┌─────────────┐
│  User   │ → │ Smart Query │ → │ Retrieval│ → │   LLM    │ → │ Critic │ → │ Final Answer│
└─────────┘   │ Intent Detect│   └──────────┘   └──────────┘   └────────┘   └─────────────┘
              └─────────────┘         ↑___________________________________________↓
                                           (Self-Correction Loop)
```

**Pipeline:** Query → **Intent Detection** → Hybrid Retrieval → Generation → Critic Evaluation → Score Check → [Refine if needed] → Final Answer

### Agent Structure
```python
backend/agents/
├── planner_agent.py      # 🧠 Smart Query intent detection
├── critic_agent.py       # 🔍 Quality evaluation
├── reasoning_agent.py    # 💬 Response generation
├── retry_agent.py        # 🔄 Auto-correction
└── orchestrator.py       # 🎛️ Pipeline coordination
```

---

## Intelligent Model Routing

Aetherion supports 7+ LLM providers with dynamic selection and automatic fallback:

| Provider | Use Case | Fallback Chain |
|----------|----------|----------------|
| **OpenAI** | GPT-4, GPT-3.5 | Claude, Gemini |
| **Anthropic** | Claude 3 Opus/Sonnet | GPT-4, Gemini |
| **Google** | Gemini Pro/Ultra | GPT-4, Claude |
| **NVIDIA** | Local inference | Groq, OpenAI |
| **Groq** | Ultra-low latency | OpenAI, Anthropic |
| **HuggingFace** | Open models | Ollama, OpenAI |
| **Ollama** | On-premise | HuggingFace, OpenAI |

**Bring Your Own Keys:** Users configure their own API credentials—no vendor lock-in, full cost control.

**Routing Strategy:** Model selection based on latency requirements, cost constraints, and accuracy needs.

**Security:** API keys are stored in frontend memory only (`sessionConfig`) and sent with each query request. Backend is stateless - no persistent storage of credentials.

Enables adaptive inference: selecting the right model for the right task in real-time.

---

## Tech Stack

| Layer | Technology |
|-------|------------|
| **API Framework** | FastAPI |
| **Vector Store** | ChromaDB (hybrid dense + sparse) |
| **LLM Providers** | OpenAI, Anthropic, Google, NVIDIA, Groq, HuggingFace, Ollama |
| **Embeddings** | sentence-transformers |
| **Frontend** | Vanilla JS + Tailwind |
| **Deployment** | Vercel (frontend) + Railway (backend) | Docker |

---

## Quick Start

```bash
git clone https://github.com/kcsanjayj/agentic-rag.git
cd agentic-rag
pip install -r requirements.txt
python start.py
```

**Setup:**
1. Open http://localhost:8000
2. Click **AI Config** → Select provider → Enter API key → Save
3. Wait for **✅ API Active** badge (green)
4. Upload document → Ask question → See execution trace

**Smart Query Examples:**
- `"Compare project A vs project B"` → Structured comparison
- `"Summarize this resume"` → Executive summary
- `"Extract all skills mentioned"` → Targeted extraction
- `"Analyze the methodology"` → Deep analysis

---

## Documentation

| Doc | Purpose |
|-----|---------|
| [Architecture](docs/ARCHITECTURE.md) | System design & agent orchestration |
| [API Reference](docs/API.md) | REST endpoints & schemas |
| [Evaluation](docs/EVALUATION.md) | Scoring rubric & methodology |
| [Deployment](docs/DEPLOYMENT.md) | Production setup (Vercel + Railway) |
| [Edge Cases](docs/FAILURES.md) | Failure modes & handling |
| [Smart Query](docs/SMART_QUERY.md) | Intent detection & routing |

---

## Deployment

### Vercel (Frontend)
```bash
# Install Vercel CLI
npm i -g vercel

# Deploy frontend
cd frontend
vercel --prod
```

**Environment Variables:**
- `VITE_API_URL` = `https://your-railway-app.up.railway.app/api/v1`

### Railway (Backend)
```bash
# Install Railway CLI
npm i -g @railway/cli

# Deploy backend
railway login
railway init
railway up
```

**Required Environment Variables:**
```env
# Optional: Default model configurations
AI_PROVIDER=openai
OPENAI_MODEL=gpt-4

# CORS (for Vercel frontend)
CORS_ORIGINS=https://your-vercel-app.vercel.app
```

**Note:** API keys are **NOT** stored in environment variables. Users provide their own keys via the UI (BYOK - Bring Your Own Key).

---

## ⚡ Why Engineers Care

- Evaluation-first AI (not just generation)  
- Observable agent pipelines  
- Quality gating at inference time  
- Multi-provider resilience  

Built for production, not demos.

---

## 🚀 Project Highlights

- Designed as a **production-style AI system**, not a demo
- Combines **multi-LLM orchestration + agent evaluation loops**
- Focuses on **reliability, observability, and control**

---

## License

MIT – see [LICENSE](LICENSE)
