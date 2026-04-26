# 🚀 Aetherion — Agentic Multi-LLM RAG System

> **A self-correcting RAG system that evaluates and rewrites its own answers before returning them.**

**TL;DR:**
- Self-correcting RAG with critic evaluation loop
- Multi-LLM fallback orchestration (7+ providers)
- Evaluation-driven response refinement with bounded retries

A production-style agentic RAG system that improves LLM outputs using retrieval + evaluation + controlled retry loops. Every answer goes through **Generate → Evaluate → Refine → Finalize** before reaching the user.

![Aetherion UI](docs/images/ui.png)

---

## 🧠 What is this?

Instead of trusting a single LLM response, the system acts like an exam system with a built-in examiner (critic agent) that scores every answer and triggers retries for low-quality outputs.

---

## ⚙️ Core Pipeline

### 🧩 Architecture
```
backend/agents/
├── planner_agent      → understands query intent
├── reasoning_agent    → generates response
├── critic_agent       → evaluates quality
├── retry_agent        → triggers refinement loop
└── orchestrator       → controls full pipeline
```

### 🔄 Execution Trace
```
Query: "What is attention mechanism?"
   ↓
┌─────────────┐    Planner: "analyze" intent detected
│   PLANNER   │ →  Strategy: technical deep-dive
└──────┬──────┘
   ↓
┌─────────────┐    Retriever: fetching 5 relevant chunks
│  RETRIEVER  │ →  Found: "attention-is-all-you-need.pdf"
└──────┬──────┘
   ↓
┌─────────────┐    LLM: generating response
│     LLM     │ →  Score: 6.5/10 ❌ (too shallow)
└──────┬──────┘
   ↓
┌─────────────┐    Critic: "missing technical depth, no citations"
│   CRITIC    │ →  Action: trigger retry
└──────┬──────┘
   ↓
┌─────────────┐    Retry Agent: prompting "add QKV details + citations"
│    RETRY    │ →  Feedback sent to LLM
└──────┬──────┘
   ↓
┌─────────────┐    LLM: regenerating with depth
│     LLM     │ →  Score: 8.7/10 ✅
└──────┬──────┘
   ↓
Final Answer: "Self-attention computes Query, Key, Value matrices..."
```

---

## ✨ Key Features

- 🧠 **Evaluation-driven generation** — Every response is scored before being returned
- 🔁 **Self-correction loop** — Automatically retries low-quality outputs (bounded iterations)
- 🔌 **Multi-LLM routing** — OpenAI / Anthropic / Groq / HuggingFace fallback support
- 📊 **Execution trace** — Full visibility into retrieval → generation → evaluation steps
- ⚡ **Async FastAPI backend** — Handles concurrent requests efficiently

---

## 🚀 Why not just LangChain?

| LangChain Agents | Aetherion |
|------------------|-----------|
| Tool-calling loop | Structured evaluation as **first-class pipeline stage** |
| Unlimited retries | **Bounded retry control** (max 3 iterations) |
| Post-hoc filtering | **Scoring-based acceptance** (must pass 7/10 threshold) |
| Black-box execution | **Full execution trace** with intermediate scores |

Unlike standard LangChain agents, Aetherion introduces structured evaluation as a first-class pipeline stage with bounded retry control and scoring-based acceptance.

---

## 📸 Live Demo

**Try it:** https://agentic-rag-gamma.vercel.app

### Before vs After: Hallucination Fix

**Query:** "What is attention mechanism in Transformers?"

| Standard RAG | Aetherion (Agentic) |
|--------------|---------------------|
| "Attention helps models focus on important parts" | "Self-attention computes Q, K, V matrices allowing parallel token processing (Vaswani et al., 2017)" |
| ❌ No citations | ✅ Paper cited |
| 6.8/10 score | 8.7/10 score |

*Critic detected shallow answer → triggered retry → LLM regenerated with technical depth*

![Chat Interface](docs/images/chat.png)

---

## 📊 Results (Controlled Eval)

Evaluation on 50 QA pairs from arXiv research papers using GPT-4 as judge.

| Metric | Baseline | Aetherion | Improvement |
|--------|----------|-----------|-------------|
| **Relevance** | 7.1/10 | 8.6/10 | +21% |
| **Hallucination Rate** | ~35% | ~10% | -25% |
| **Avg Latency** | ~0.8s | ~1.2s | Evaluation loop cost |
| **Max Retries** | 0 | 3 | Self-correction bound |

### 🎯 Scoring Rubric (GPT-4 Judge)

Every answer scored on 3 dimensions (0-10 each):

| Dimension | What we measure | Weight |
|-----------|-----------------|--------|
| **Relevance** | Does it directly answer the question? | 33% |
| **Grounding** | Are claims supported by retrieved context? | 33% |
| **Completeness** | Is it technically thorough with proper depth? | 33% |

**Final Score = (Relevance + Grounding + Completeness) / 3**

**Hallucination Detection:** GPT-4 flags any claim not found in retrieved context or ground truth as hallucinated. We count unsupported statements per answer and compare rates across systems.

---

## ⚖️ Design Tradeoffs

| Tradeoff | Choice |
|----------|--------|
| ⏱️ **Higher latency** | due to evaluation + retry loop |
| 🎯 **Higher accuracy** | critic filters weak responses before final output |
| 💰 **Higher cost** | multiple LLM calls per query |
| 🧩 **Better reliability** | fallback routing + failure recovery |

---

## 🛡️ Production Features

- Rate limiting middleware
- Structured JSON logging
- Timeout handling + graceful fallback
- Multi-provider resilience layer
- Health check endpoint

---

## 🧪 Failure Handling

| Failure Mode | Response |
|--------------|----------|
| LLM timeout | → fallback provider |
| Low-quality output | → retry loop |
| Retrieval noise | → filtered context selection |
| Persistent failure | → safe degraded response |

---

## 🧠 Why this matters

This project demonstrates:

- **Agentic orchestration** (planner + critic + retry loop)
- **Evaluation-as-a-stage** (not post-processing)
- **Real-world tradeoffs** (latency vs quality)
- **Production-ready FastAPI architecture**
- **Multi-LLM routing systems**

---

## 🧪 Tech Stack

FastAPI · ChromaDB · OpenAI / Anthropic / Groq · sentence-transformers · Tailwind · Vercel · Railway · Docker

---

## 🚀 Summary

Aetherion turns a standard RAG pipeline into a **self-evaluating AI system** that improves its own answers before responding.
