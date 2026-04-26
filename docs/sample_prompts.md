# Sample Evaluation Prompts

10 example queries from the arXiv QA dataset used for evaluation:

## Technical Questions

1. **What is attention mechanism in Transformers?**
   - Domain: NLP
   - Expected: QKV matrices, parallel processing, Vaswani et al. citation

2. **Explain the difference between encoder and decoder architectures.**
   - Domain: NLP
   - Expected: Bidirectional vs autoregressive, use cases

3. **How does backpropagation work in neural networks?**
   - Domain: Deep Learning
   - Expected: Chain rule, gradient computation, weight updates

4. **What is the vanishing gradient problem?**
   - Domain: Deep Learning
   - Expected: Causes, solutions (ResNet, LSTM), mathematical intuition

5. **Compare CNN and RNN for sequence modeling.**
   - Domain: ML
   - Expected: Architecture differences, strengths, limitations

## Research & Analysis

6. **Summarize the key contributions of the Transformer paper.**
   - Domain: NLP
   - Expected: Self-attention, parallelization, performance results

7. **What are the limitations of large language models?**
   - Domain: AI
   - Expected: Hallucinations, bias, computational cost, context limits

8. **Explain gradient descent and its variants.**
   - Domain: Optimization
   - Expected: SGD, momentum, Adam, learning rate dynamics

9. **How does batch normalization improve training?**
   - Domain: Deep Learning
   - Expected: Covariate shift, stabilization, regularization effect

10. **What is transfer learning in computer vision?**
    - Domain: CV
    - Expected: Pre-trained models, fine-tuning, feature extraction

## Evaluation Criteria

Each answer scored on:
- **Relevance** (0-10): Does it address the question?
- **Grounding** (0-10): Are claims supported by sources/facts?
- **Completeness** (0-10): Is the answer thorough?

**Final Score:** Average of three criteria

See [EVALUATION.md](EVALUATION.md) for full methodology.
