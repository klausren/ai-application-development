# MODEL_CARD.md · 模型卡模板

> Start after Week 4 (baseline), update through Week 15. Graded under team rubric §C and §D.
> Write it for a reader who is smart but does not know ML. **"Limitations" is not a
> formality** — it is where the grade is decided.
>
> W4 基线出来后开始写，持续更新到 W15。写给「聪明但不懂机器学习」的人看。
> **「局限性」不是走过场** —— 分数主要在这里拉开。

---

## 1. Model details · 基本信息

| | |
|---|---|
| **Name / version** | |
| **Task** | *(e.g. multi-class classification, 6 classes)* |
| **Architecture** | |
| **Pretrained weights** | *(which, and their licence — or "trained from scratch")* |
| **Framework & version** | |
| **Training date** | |
| **Owner** | *(Model Lead)* |

## 2. Intended use · 预期用途

- **Intended users:**
- **Intended use cases:**
- **Out of scope:**

## 3. Data · 数据

| | |
|---|---|
| **Training data** | *(link to `DATA.md`)* |
| **Size** | |
| **Preprocessing** | *(link to `src/data/`)* |
| **Known data limitations that limit the model** | |

## 4. Metrics · 指标

**Primary metric:**  *(and why this one — one paragraph)*

### Results · 结果

| Model | Metric | Δ vs previous | Notes |
|---|---|---|---|
| Dumb baseline | | — | |
| Simple baseline (W4) | | | |
| v1 (W5) | | | |
| + change X (W6 ablation) | | | |
| **Final** | | | |

*Report on the **held-out test set**, touched once. Note the confidence interval or
variance across seeds if you measured it.*

### Per-class breakdown · 分类别表现

| Class | Precision | Recall | F1 | Support |
|---|---|---|---|---|
| | | | | |

*Include a confusion matrix image in the repo and link it here.*

## 5. Ablation · 消融实验

Link or paste `experiments/ablation.md`. **Which single change bought the most?**

> Answer in one sentence. If you cannot, the team rubric §C caps at "Adequate".

## 6. Limitations & failure modes · 局限与失败模式

### Known failure modes · 已知失败模式

| # | Failure | Frequency | Hypothesis | Severity |
|:---:|---|---|---|---|
| 1 | | | | H/M/L |
| 2 | | | | |
| 3 | | | | |
| 4 | | | | |
| 5 | | | | |

*Group them into categories if you have many. Five analysed cases beats twenty listed ones.*

### What this model cannot do · 这个模型做不到什么

-
-

## 7. Ethics & safety · 伦理与安全

| | |
|---|---|
| **Who could be harmed if this fails?** | |
| **Bias check** | *(did you evaluate performance across subgroups present in the data?)* |
| **Misuse potential** | |
| **Human-in-the-loop?** | *(is a human supposed to review the output? say so plainly.)* |

## 8. Cost · 成本

| | |
|---|---|
| **Training time & hardware** | |
| **Inference latency** | *(p50 / p95)* |
| **Model size** | |
| **Cost per 1 000 inferences** | *(if applicable)* |

*Was the expensive model worth it? Answer honestly — this is a graded question in W11.*
