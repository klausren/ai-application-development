# Lab 10 · Word Embeddings & Sequence Models
> **AI Application Development** · Week 10 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 10 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 3 · NLP & Large Language Models |
| **Stack** | PyTorch (`nn.Embedding`, `nn.LSTM`), matplotlib |
| **Dataset** | Small sentiment corpus (provided) |
| **Deliverables** | `lab-10.ipynb` with embeddings + RNN vs LSTM comparison |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** what an embedding *is*: a lookup table of dense vectors trained as model parameters
- **Know** why a vanilla RNN forgets long-range dependencies and how an LSTM gate fixes it
- **Do** train embeddings on a tiny corpus and show that similar words end up close together
- **Do** build an RNN and an LSTM for sentiment classification and compare them fairly
- **Do** handle variable-length sequences correctly (padding + `pack_padded_sequence`)

## 2. Before You Start · 课前准备

- [ ] Week 9 lab committed (you have a text pipeline)
- [ ] Download `sentiment_small.csv` (5 000 labelled sentences) from the course drive
- [ ] Read Chapter 10 (word embeddings, RNN/LSTM)

## 3. Lab Tasks · 实验任务

### Part A — Embeddings are just a lookup table (15 min)

```python
import torch.nn as nn
emb = nn.Embedding(num_embeddings=5000, embedding_dim=50)
ids = torch.tensor([12, 847, 3])
emb(ids).shape        # -> torch.Size([3, 50])
```

Train a tiny skip-gram model (or fine-tune `emb` inside a classifier) on your corpus, then check nearest neighbours:

```python
from sklearn.metrics.pairwise import cosine_similarity
W = emb.weight.detach().numpy()
# find the 5 nearest words for: good, bad, movie, boring
```

> **Checkpoint A** — nearest neighbours for 4 query words, plus one sentence on whether the similarities make sense given only 5 000 sentences.
> **Pitfall**: embeddings trained on a corpus this small are noisy. If neighbours look random, that is a **finding**, not a bug — say so and explain why (data volume).

### Part B — Padding: the bug everyone hits (15 min)

```python
from torch.nn.utils.rnn import pad_sequence, pack_padded_sequence
```

Build batches of variable-length sequences. Show the wrong way (pad, then let the RNN read the zeros) and the right way (`pack_padded_sequence`).

> **Checkpoint B** — print one batch's lengths and demonstrate that the naive version's final hidden state differs from the packed version's.
> **Pitfall**: reading padding tokens changes the final hidden state. This silently costs you 1–3 accuracy points and is very hard to spot.

### Part C — RNN vs LSTM (25 min)

```python
rnn  = nn.RNN(50, 64, batch_first=True)
lstm = nn.LSTM(50, 64, batch_first=True)
```

Train both for 5 epochs on the same data, same seed, same everything. Report accuracy **and** training time.

| Model | Test acc | Time/epoch | Gradient behaviour |
|---|---|---|---|
| Vanilla RNN | | | |
| LSTM | | | |

Also log the gradient norm of the first layer per epoch for both.

```python
torch.nn.utils.clip_grad_norm_(model.parameters(), 1.0)   # add this and re-run
```

> **Checkpoint C** — the table plus one sentence: what did gradient clipping change, and why does an LSTM need it less?
> **Pitfall**: exploding gradients in vanilla RNNs. If loss goes `nan`, clip first, then investigate.

### Part D — Attention as a fix for the bottleneck (15 min)

Add a single-line attention pooling over the LSTM outputs instead of using only the final hidden state:

```python
scores = torch.softmax(torch.matmul(out, torch.randn(64)), -1)
context = (out * scores.unsqueeze(-1)).sum(1)
```

> **Checkpoint D** — accuracy with vs without attention pooling, plus one intuition sentence.
> **Think**: this one line is the conceptual ancestor of everything you will do in Week 11.

### Part E — Wrap up (5 min)

One paragraph: when is a TF-IDF + logistic regression baseline (Week 9) the *better* engineering choice?

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-10.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Every **Checkpoint** cell executed, with its output visible
- [ ] Results collected into **one comparison table**
- [ ] Markdown cells contain your own interpretation, not just code
- [ ] Pushed to GitHub with **≥ 2 meaningful commits**

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Embedding intuition (Part A) | 20 | nearest neighbours computed and honestly interpreted (incl. small-data caveat) |
| Padding handled correctly (Part B) | 20 | packed sequences used, difference demonstrated |
| RNN vs LSTM (Part C) | 30 | both trained under identical conditions, table filled, gradient clipping applied |
| Attention pooling (Part D) | 20 | added, compared, intuition articulated |
| Exit ticket | 10 | three questions answered |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add lab-10.ipynb
git commit -m "feat: complete lab 10"
git push origin main
```

## 8. Exit Ticket · 课后反思

1. What surprised you most today?
2. Where did your model fail, and what does that failure tell you about the representation it uses?
3. One question you still have.

## 9. 中文摘要

本周从「词袋」升级到「词向量 + 序列模型」，也第一次直面 RNN 的硬伤。

五个要点：
1. **Embedding 就是一张可训练的查表**：`nn.Embedding(vocab, dim)` 把词 ID 映射成稠密向量，梯度会反向传播回这张表。
2. **小语料训出来的词向量会很吵**——如果近邻词看起来是随机的，这是**数据量不足的真实结果**，要如实写进报告，而不是怀疑代码写错了。
3. **padding 必须 pack**：让 RNN 读到补的 0 会污染最终隐状态，损失 1-3 个点且极难排查。用 `pack_padded_sequence`。
4. **RNN 会梯度爆炸**（loss 变 nan 先加 `clip_grad_norm_`），LSTM 靠门控机制缓解遗忘，代价是更慢。
5. **注意力池化一行代码就能提点**——不再只依赖最后一步隐状态，而是加权看重所有时间步。它就是下周 Transformer 的思想雏形。

工程判断：数据少、要求快、要可解释时，第 9 周的 TF-IDF + 逻辑回归往往比 LSTM 更合适。**先跑简单基线，再决定是否上复杂模型。**
