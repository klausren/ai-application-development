# Lab 11 · Transformers & Pre-trained Models
> **AI Application Development** · Week 11 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 11 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 3 · NLP & Large Language Models |
| **Stack** | HuggingFace `transformers`, `datasets`, `evaluate`, PyTorch |
| **Dataset** | IMDB subset (2 000 train / 500 test) |
| **Deliverables** | `lab-11.ipynb` with attention visualisation + fine-tuning vs baseline |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** what self-attention computes, and why it replaces recurrence for long sequences
- **Know** the difference between *feature extraction* and *fine-tuning* with a pretrained model
- **Do** use a pretrained model via `pipeline` and then via explicit `AutoModel`
- **Do** fine-tune DistilBERT on a small dataset and compare it honestly against your Week 9 TF-IDF baseline
- **Do** visualise attention weights and point at what the model is looking at

## 2. Before You Start · 课前准备

- [ ] Week 10 lab committed
- [ ] **Network setup (do this first, it saves 20 minutes):**

```bash
export HF_ENDPOINT=https://hf-mirror.com      # use the mirror if huggingface.co is slow
pip install transformers datasets evaluate accelerate
```

- [ ] Offline fallback: if no model can be downloaded, run Part A with a locally cached model provided by the TA, and do Parts C–D with `AutoModel` loaded from a local directory (`from_pretrained("./models/distilbert")`).

## 3. Lab Tasks · 实验任务

### Part A — Two lines to a working classifier (10 min)

```python
from transformers import pipeline
clf = pipeline("sentiment-analysis")
clf(["This movie was a waste of time.", "A stunning debut."])
```

Then swap the default model for `distilbert-base-uncased-finetuned-sst-2-english` and compare on 5 of your own sentences (including one with sarcasm and one with negation).

> **Checkpoint A** — outputs for both models on 5 sentences, plus one case where both are wrong.
> **Think**: a pretrained model is not magic. Find its failure in 5 minutes and you have learned more than from 5 successes.

### Part B — Look inside: self-attention weights (20 min)

```python
from transformers import AutoTokenizer, AutoModel
tok = AutoTokenizer.from_pretrained("distilbert-base-uncased")
m = AutoModel.from_pretrained("distilbert-base-uncased", output_attentions=True)
```

Compute attention for a sentence with an ambiguous pronoun (*"The trophy didn't fit in the suitcase because **it** was too big."*) and plot the head that resolves `it`.

> **Checkpoint B** — one attention heatmap, plus one sentence on what that head is doing.
> **Pitfall**: attention weights are **not** a faithful explanation of model behaviour. Treat them as a hint, and say so.

### Part C — Fine-tune DistilBERT (25 min)

```python
from transformers import AutoModelForSequenceClassification, TrainingArguments, Trainer
model = AutoModelForSequenceClassification.from_pretrained("distilbert-base-uncased", num_labels=2)
args = TrainingArguments(output_dir="out", num_train_epochs=2, per_device_train_batch_size=8,
                         learning_rate=2e-5, weight_decay=0.01, seed=42,
                         fp16=torch.backends.mps.is_available() is False)
```

Fine-tune on 2 000 IMDB samples, evaluate on 500.

> **Checkpoint C** — accuracy + training time, and **the same numbers as text** in your report (the instructor compiles a class table).
> **Pitfall**: with `batch_size=8` on 2 000 samples, one epoch is ~250 steps. If it takes more than 10 minutes on CPU, reduce the sample count rather than waiting.

### Part D — Was it worth it? The honest comparison (15 min)

| Model | Accuracy | Training time | Needs GPU? | Interpretable? |
|---|---|---|---|---|
| TF-IDF + LogReg (W9) | | | no | yes |
| LSTM (W10) | | | helpful | no |
| DistilBERT (today) | | | near-essential | partially |

> **Checkpoint D** — the table filled, plus **a recommendation**: for a startup with 5 000 labelled samples and no GPU, which would you ship and why?

### Part E — Wrap up (5 min)

One paragraph on the cost side: what do you pay (money, latency, carbon, maintainability) for the accuracy you gained?

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-11.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Every **Checkpoint** cell executed, with its output visible
- [ ] Results collected into **one comparison table**
- [ ] Markdown cells contain your own interpretation, not just code
- [ ] Pushed to GitHub with **≥ 2 meaningful commits**

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Pipeline & failure hunt (Part A) | 15 | both models run, a genuine failure case found and described |
| Attention visualisation (Part B) | 25 | heatmap produced, head behaviour described, caveat acknowledged |
| Fine-tuning run (Part C) | 30 | training completed, accuracy + wall-clock time reported |
| Honest comparison (Part D) | 20 | three-model table filled with a defensible recommendation |
| Exit ticket | 10 | three questions answered |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add lab-11.ipynb
git commit -m "feat: complete lab 11"
git push origin main
```

## 8. Exit Ticket · 课后反思

1. What surprised you most today?
2. Where did your model fail, and what does that failure tell you about the representation it uses?
3. One question you still have.

## 9. 中文摘要

本周用上工业级预训练模型，但重点是**判断它值不值得用**。

五个要点：
1. **`pipeline` 两行就能跑**，但默认模型不一定适合你的任务——换模型、换句子、找它的失败案例，比跑通 demo 有价值得多。
2. **注意力权重不是严谨的可解释性证据**，只能当提示。报告里要如实说明这个局限（学术论文也常犯这个错）。
3. **微调三件套**：`AutoModelForSequenceClassification` + `TrainingArguments` + `Trainer`。学习率用 2e-5 量级（比从头训小两个数量级），否则会冲掉预训练知识。
4. **CPU 上跑不动就减样本**，不要干等。记下实际耗时，这是工程决策的依据。
5. **必须做三方对比**：TF-IDF（快、可解释）vs LSTM vs DistilBERT（准、贵）。给一家没 GPU、只有 5000 条标注数据的创业公司，你推荐哪个？**能回答这个问题，才算真的学会了这一周。**

成本意识：准确率的每一点提升，都要用钱（GPU）、延迟、碳排放和维护复杂度去换。
