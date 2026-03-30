# 🤖 Agentic RAG System

[![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green.svg)](https://fastapi.tiangolo.com)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An intelligent document Q&A system that plans, retrieves, reasons, and self-corrects using advanced agentic AI patterns.

## What It Does

Takes user questions about documents and answers them using a multi-step agentic pipeline:
1. **Plans** execution strategy based on query analysis
2. **Retrieves** relevant document chunks with query rewriting for better results
3. **Selects tools** based on content type (retrieval, interpretation, or fallback)
4. **Iterates** - tries, evaluates, improves, retries if needed
5. **Self-corrects** via critic agent that validates output quality
6. **Reports** full reasoning trace including confidence, tools used, and evaluation scores

## Key Features

| Feature | Implementation |
|---------|---------------|
| **Planning Layer** | 6-step execution plan generated before any action |
| **Tool System** | Dynamic tool selection: `retrieve_tool`, `interpret_tool`, `fallback_tool` |
| **Iteration Loop** | Evaluates each attempt, retries with improvements if grounding < 0.9 |
| **Query Rewrite** | Generates 3 variants, selects best based on predicted performance |
| **Critic Agent** | Evaluates grounding, completeness, relevance; triggers self-correction |
| **Multi-Strategy Routing** | Detects sparse vs dense content, selects appropriate processing |
| **Transparent Output** | Shows PLAN, TOOLS USED, AGENT ACTIONS, ITERATION, CRITIC VERDICT, EVALUATION |

## Architecture

```
User Query
    ↓
Planning Agent → Execution Plan
    ↓
Query Agent → Intent Classification + Technical Detection
    ↓
Retrieval Agent → ChromaDB Search + Reranking
    ↓
Tool Selector → retrieve_tool / interpret_tool / fallback_tool
    ↓
Generation Agent → Answer with source grounding
    ↓
Critic Agent → Validate & Score
    ↓
Iteration Loop (if needed)
    ↓
Formatted Response with full trace
```

## Technical Stack

- **API**: FastAPI + Uvicorn
- **Vector Store**: ChromaDB with sentence-transformer embeddings
- **LLM**: OpenAI GPT-3.5/4 for generation, Gemini for query analysis
- **Reranker**: Cross-encoder for result refinement
- **Testing**: pytest with verification harness

## Project Structure

```
backend/
├── agents/
│   ├── orchestrator.py      # Main coordination logic
│   ├── query_agent.py       # Intent classification
│   ├── retrieval_agent.py   # Document search + reranking
│   ├── generation_agent.py  # Answer synthesis
│   ├── critic_agent.py      # Self-correction
│   ├── query_rewrite_agent.py
│   └── smart_document_agent.py
├── core/
│   ├── reranker.py          # Cross-encoder reranking
│   ├── memory.py            # Conversation context
│   └── evaluation_system.py # Performance metrics
└── api/routes.py            # REST endpoints

tests/
├── test_level4.py           # Feature verification
├── test_dense_detection.py  # Technical content handling
└── test_10_10_final.py      # Output quality checks
```

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- OpenAI API key

### Installation

```bash
# Clone the repository
git clone <repository-url>
cd agentic-rag

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Add your OPENAI_API_KEY to .env file
```

### Running the Application

```bash
# Option 1: Direct run
python backend/main.py

# Option 2: Using the start script
python start.py

# Option 3: Batch file (Windows)
run.bat
```

🌐 **Access the application at:** http://localhost:8000

📚 **API Documentation:** http://localhost:8000/docs

## API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/query` | POST | Ask questions with full agent trace |
| `/api/v1/upload` | POST | Upload documents (PDF, TXT) |
| `/api/v1/health` | GET | System status |
| `/api/v1/evaluate` | POST | Run evaluation suite |

## Example Output

```
PLAN:
- 1. Analyze query intent and technical indicators
- 2. Attempt document retrieval
- 3. Detect content type (sparse / low / full)
- 4. Select appropriate processing strategy
- 5. Generate response using selected tool
- 6. Evaluate output quality and completeness

TOOLS USED:
- Mode: interpret_sparse
- Tool: interpret_tool
- Description: Direct semantic interpretation

CONFIDENCE: MIXED
- Content-based extraction: MEDIUM
- Contextual inference: MEDIUM

AGENT ACTIONS:
- Initial retrieval: LOW coverage
- Query rewritten: NO (already optimal)
- Strategy switch: Direct semantic interpretation

ITERATION:
- Attempt 1: Accepted → Technical content detected

CRITIC VERDICT: ACCEPTED
Reason: Sparse but high-density statement correctly interpreted

SUMMARY:
[Answer content]

INSIGHT:
[Domain-specific reasoning]

EVALUATION:
- Retrieval relevance: 0.20
- Grounding: 0.90
- Completeness: 0.60
```

## What Makes This Different

Most RAG systems: retrieve → generate → return.

This system: plan → analyze → retrieve → evaluate → select tool → generate → criticize → evaluate → return with full reasoning trace.

The difference is the loop. It doesn't just answer—it checks its own work and improves if needed. The output shows exactly what happened, not just the final answer.

## Development Status

**Implemented:**
- Planning layer with 6-step execution plan
- Tool system with dynamic selection
- Iteration loop (try → evaluate → improve → retry)
- Query rewriting with 3 variants + selection
- Critic agent with self-correction
- Multi-strategy routing (sparse/dense/fallback)
- Cross-encoder reranking
- Transparent output formatting
- Memory for conversation context

**Not implemented:**
- Persistent vector store (resets on restart)
- Multi-hop reasoning (complex chains)
- Parallel tool execution

## 🧪 Testing

```bash
# Run all tests
python -m pytest tests/

# Run specific test suites
python tests/test_level4.py           # Verify all features
python tests/test_dense_detection.py  # Test technical content handling
python tests/test_10_10_final.py     # Check output quality

# Run with coverage
python -m pytest tests/ --cov=backend --cov-report=html
```

## 📊 Monitoring & Logs

- **Application logs**: `logs/server.log`
- **Health check**: GET `/api/v1/health`
- **System metrics**: Available in the admin panel

## License

MIT
