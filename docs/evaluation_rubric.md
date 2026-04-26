# Evaluation Rubric (GPT-4 Judge)

Structured scoring criteria used for evaluating RAG responses.

## Scoring Dimensions

### 1. Relevance (0-10)
Does the answer address the user's question?

| Score | Criteria |
|-------|----------|
| 8-10 | Directly answers, stays focused, no tangents |
| 5-7 | Partially answers, some relevant info |
| 0-4 | Off-topic or fails to address question |

### 2. Grounding (0-10)
Are claims supported by retrieved context or verifiable facts?

| Score | Criteria |
|-------|----------|
| 8-10 | All claims supported by sources, accurate citations |
| 5-7 | Mostly supported, minor unsupported claims |
| 0-4 | Hallucinations, unsupported statements |

### 3. Completeness (0-10)
Is the answer thorough and technically deep?

| Score | Criteria |
|-------|----------|
| 8-10 | Comprehensive, technical depth, examples |
| 5-7 | Adequate but lacks depth |
| 0-4 | Surface-level, missing key details |

## Prompt Template

```
You are an expert evaluator assessing AI-generated answers.

Question: {query}
Answer to evaluate: {answer}
Retrieved context: {context}

Score the answer on THREE dimensions (0-10 each):

1. RELEVANCE: Does it directly address the question?
2. GROUNDING: Are claims supported by context/facts?
3. COMPLETENESS: Is it thorough and technically deep?

Provide scores and brief justification for each.
Final Score = (Relevance + Grounding + Completeness) / 3

Response format:
Relevance: X/10 - [justification]
Grounding: X/10 - [justification]
Completeness: X/10 - [justification]
Final: X.X/10
```

## Baseline vs Agentic Comparison

| System | Avg Score | Hallucination Rate |
|--------|-----------|-------------------|
| Baseline RAG | 7.1/10 | ~35% |
| Aetherion | 8.6/10 | ~10% (-25%) |

## Judge Configuration

- **Model:** GPT-4 (`gpt-4-1106-preview`)
- **Temperature:** 0.2 (low for consistency)
- **Max Tokens:** 500
- **Evaluation Count:** 50 QA pairs × 2 systems = 100 evaluations

See [sample_prompts.md](sample_prompts.md) for test queries.
