# Lab 12 · LLM Prompt Engineering & RAG
> **AI Application Development** · Week 12 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 12 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 3 · NLP & Large Language Models |
| **Stack** | `transformers` (small local LLM), scikit-learn (retriever), Gradio (optional) |
| **Dataset** | Course documents (provided) + local Qwen2.5-0.5B-Instruct |
| **Deliverables** | `lab-12.ipynb` with a prompt matrix + a working RAG pipeline |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** four prompting patterns and when each one helps (zero-shot, few-shot, chain-of-thought, self-consistency)
- **Know** why RAG exists: knowledge lives outside the weights, and weights go stale
- **Do** build a retrieval-augmented QA pipeline with a real retriever and a real generator
- **Do** evaluate it with a small labelled set and report **retrieval** quality separately from **generation** quality
- **Do** identify at least one hallucination in your own system

## 2. Before You Start · 课前准备

- [ ] Week 11 lab committed
- [ ] Documents for retrieval: 10–20 course PDFs / Markdown files in `./docs`
- [ ] Model: `Qwen/Qwen2.5-0.5B-Instruct` (~1 GB). If the download fails, use the `mock_llm()` stub provided in the notebook — **the pipeline you build is identical**, and every evaluation below still works

```python
def mock_llm(prompt: str) -> str:
    "Stand-in generator: returns the retrieved context verbatim."
    return prompt.split("CONTEXT:")[1].split("QUESTION:")[0][:300]
```

> **Why a stub is acceptable**: RAG is 80% retrieval engineering and 20% generation. If retrieval is broken, no model saves you.

## 3. Lab Tasks · 实验任务

### Part A — Prompt pattern matrix (20 min)

Run the same 5 questions through four prompt templates and record results in one table:

| Pattern | Template sketch | Correct? | Notes |
|---|---|---|---|
| Zero-shot | `"Answer: {q}"` | | |
| Few-shot (3 examples) | 3 worked examples, then `{q}` | | |
| Chain-of-thought | `"Let's think step by step. {q}"` | | |
| Constrained output | `"Answer with JSON: {\"answer\": str, \"confidence\": float}"` | | |

> **Checkpoint A** — the 5×4 matrix, plus one sentence on which pattern helped **and why you think it helped**.
> **Pitfall**: a 0.5B model is weak. Small models often get *worse* with chain-of-thought. Report what you observe, not what the textbook says.

### Part B — Build the retriever (20 min)

```python
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

chunks = [chunk_text(d, size=300, overlap=50) for d in docs]   # chunking matters
vec = TfidfVectorizer().fit(chunks)
def retrieve(q, k=3):
    qv = vec.transform([q])
    return np.argsort(-cosine_similarity(qv, vec.transform(chunks))[0])[:k]
```

> **Checkpoint B** — 5 queries × top-3 chunks printed, with a yes/no on whether the right chunk was retrieved.
> **Pitfall**: chunk size is a hyperparameter. Try 150 / 300 / 600 tokens and report hit-rate@3 for each.

### Part C — Assemble RAG and test it (20 min)

```python
def rag_answer(q, k=3):
    ctx = "\n\n".join(chunks[i] for i in retrieve(q, k))
    prompt = f"Answer ONLY from the context.\nCONTEXT:{ctx}\nQUESTION:{q}\nANSWER:"
    return llm(prompt)
```

Build **10 labelled questions** (question → expected answer) *before* testing. Then run:
1. `rag_answer(q)` — with retrieval
2. `llm(q)` without any context — the baseline

> **Checkpoint C** — 10-row table: query | retrieved correctly? | RAG answer correct? | no-context answer correct?
> **Pitfall**: if both are equally bad, your questions may be unanswerable from the docs — check retrieval first.

### Part D — Find a hallucination (10 min)

Deliberately ask something **not** in the documents and see what happens.

> **Checkpoint D** — paste one hallucinated answer and explain mechanically why it happened (the model must produce *something*; an empty context does not force abstention).
> **Then fix it**: add `"If the answer is not in the context, say 'I don't know'."` and re-test.

### Part E — Wrap up (5 min)

Report two numbers separately: **hit-rate@k** (retrieval) and **answer accuracy** (generation). Which one is your bottleneck?

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-12.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Every **Checkpoint** cell executed, with its output visible
- [ ] Results collected into **one comparison table**
- [ ] Markdown cells contain your own interpretation, not just code
- [ ] Pushed to GitHub with **≥ 2 meaningful commits**

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Prompt matrix (Part A) | 20 | 5×4 matrix completed, observed effects reported honestly (incl. weak-model findings) |
| Retriever (Part B) | 25 | chunking implemented, hit-rate@3 measured for ≥2 chunk sizes |
| RAG pipeline (Part C) | 30 | 10 labelled questions, RAG vs no-context baseline compared |
| Hallucination hunt & fix (Part D) | 15 | a real hallucination captured, mechanism explained, guardrail added and re-tested |
| Exit ticket | 10 | three questions answered |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add lab-12.ipynb
git commit -m "feat: complete lab 12"
git push origin main
```

## 8. Exit Ticket · 课后反思

1. What surprised you most today?
2. Where did your model fail, and what does that failure tell you about the representation it uses?
3. One question you still have.

## 9. 中文摘要

本周构建 RAG（检索增强生成），这是目前企业落地 LLM 最主流的形态。

五个要点：
1. **RAG 的本质是把知识放在权重外面**——模型记不住、会过期、会编造，检索能解决这三点。
2. **提示词不是玄学，要矩阵化测试**：zero-shot / few-shot / 思维链 / 约束输出，同一批问题跑四遍，记录真实结果。**小模型上思维链可能反而变差**——报告你看到的，不是教材说的。
3. **RAG 八成是检索工程**：分块大小（chunk size）是超参，150/300/600 各测一遍 hit-rate@3，你会发现差别很大。
4. **必须在测试前先写好 10 条标注问题**，否则你会不自觉地挑成功的案例。
5. **幻觉是必然的**：上下文为空时，模型也必须输出点什么。**加一句「不在上下文里就说不知道」，然后重测**——这是本周最实用的一行提示词。

评估要拆成两个数：**检索命中率**和**生成准确率**。哪个低，就知道该优化哪一段。
