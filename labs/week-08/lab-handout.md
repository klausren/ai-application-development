# Lab 07 · Text Classification Pipeline — four ways to read one LSTM, and the bug that hides in `out[:, -1, :]`
**AI Application Development (52015CC3BV)** · School of Software, Dalian Neusoft University of Information · Week 8 Lab (80 min) · English with Chinese summary at the end · 中文摘要见文末

**Official lab number: 实验 7** (this is the Week 8 lab). Module 2, week 4 of 4.
**Course map entry: `8.3 实验 7：文本分类应用实战（课内实践）` — 1.0 学时**, delivered inside the course's 80-minute in-class practical.
**This week is also the M8 midterm checkpoint** — see §7. The three deliverables there are graded separately from this lab's 100 points.

| | |
|---|---|
| **Week / 周次** | 8 · CU(8) Sequence Models and Text Data · Module 2 (Week 5–8) |
| **Duration** | 80 min lab (10 min intro + 70 min hands-on) |
| **Module** | 2 · Core Deep Learning: Techniques and Model Training (Week 5–8) |
| **Stack** | Python 3.11, PyTorch 2.x, scikit-learn, matplotlib — **100 % offline** |
| **Corpus** | This course's own Week 1–6 materials — **748** English passages, **6** classes. Built by `scripts/build_text_corpus.py`; shipped as `data/raw/course-text-corpus.jsonl`. **Zero download, fully offline, licence CC BY-NC-SA 4.0.** |
| **Protocol** | `Embedding(64, padding_idx=0)` → `LSTM(96, batch_first=True)` → `Linear(6)` (**166,278** parameters, seed 42) · Adam(lr=1e-3) · batch 64 · **30 epochs** · `max_len = 96` · seeds 42–46 (mean ± sd) |
| **Deliverables** | `lab-08.ipynb` + `w8_text_lab.py` + `arms.json` + the four-pooling ledger + training curve + confusion matrix + the misclassified passages + the AI pipeline-audit record + **the M8 pack** (runnable prototype + `DATA.md` v1 + 3 slides) + ≥ 2 commits |
| **Weight** | Formative, in-class labs (实验 0–13). This is the lab behind the official assessment row `CNN 与序列模型的搭建与调优` — not a highlighted topic, but **a difficulty point worth 6 % of the final course mark**, assessed through the lab report. W7 and W8 share this row. |

## 1. Learning Objectives · 学习目标

This lab covers the three teaching objectives of the unit, and nothing that is not one of them:

1. **Master the full chain from raw text to a tensor.** 掌握文本数据从原始文本到张量的完整处理链路。
2. **Understand the gating mechanism of recurrent networks and the problem it solves.** 理解循环网络的门控机制及其解决的问题。
3. **Complete an end-to-end text classification application.** 能够完成一个端到端的文本分类应用。

By the end of the lab you will be able to:

- **Know** that "text → tensor" is four steps — tokenise → vocabulary → encode → pad — and that **each step has one characteristic error**, and you can name the error for each step
- **Know** why the vocabulary is built **from the training split only**, and what breaks (silently) when it is built from all of the data
- **Know** what `padding_idx=0` actually does, and what `pack_padded_sequence` actually does, by checking the tensors rather than the docs
- **Know** that on this corpus four pooling choices over the *same* LSTM differ by **26.2 points** — and that the entire difference is one line of code
- **Do** build the pipeline, print the vocabulary size, the per-class counts and the passage-length distribution **before** training anything
- **Do** run four pooling arms `mean_masked` / `packed` / `mean_unmasked` / `last_step` over **at least 3 seeds** and report **accuracy and macro F1**, as mean ± sd
- **Do** dissect the `last_step` bug with two pieces of evidence — a per-length-bucket table and a hard length cut at 96 tokens — and conclude that the task is not too hard, the model read the pad vector
- **Do** run a `max_len` sweep (48 / 96 / 192) and show that length is **not** the lever
- **Do** add Week 6's regularisation to the best arm and report, honestly, that it **does not rescue** the model — with a diagnosis of why
- **Do** open the confusion matrix, read the recall column against class size, and paste the misclassified passages **verbatim**
- **Do** ask an AI for a whole text pipeline, then find its bug by **measuring** the accuracy before and after the fix — "I found a bug" is not a result, a number is

## 2. Before You Start · 课前准备

```bash
python -c "import torch, sklearn, matplotlib; print(torch.__version__)"
```

- [ ] Lab 06 committed (you own a training loop and an error-analysis habit; this lab moves it from images to sequences)
- [ ] `import torch` works in the `ai-app` environment — no `ModuleNotFoundError`
- [ ] Textbook read: 《动手学深度学习（PyTorch 版）》 corresponding chapters on text preprocessing, word embeddings, and recurrent / LSTM networks
- [ ] Pen and paper for Part D — you will write your predicted ranking of the four arms **before** the code prints it

**Device line** (keep it at the top of the notebook):

```python
import torch
device = torch.device("mps" if torch.backends.mps.is_available()
                      else "cuda" if torch.cuda.is_available() else "cpu")
print("using", device)
```

### This week has zero downloads · 本周全程离线

The corpus is **not** a downloaded dataset. It is built from this repository's own Week 1–6 materials — `lesson-plans/week-XX/lecture-en.html`, `lab-en.html`, `textbook/chapter-XX/en.html` and `labs/week-XX/lab-handout.md` — and it ships with the course as `data/raw/course-text-corpus.jsonl`. Rebuild it from source at any time:

```bash
python scripts/build_text_corpus.py
```

The build is deterministic and prints its own audit trail: **748** passages, **3,142** unique tokens in the full corpus, a SHA-256 beginning `87e41aac89ef`, and the one number that matters most — **262** leak-scrubbing replacements.

**Why the corpus is hand-built, and why that matters.** The obvious dataset here would be a public news corpus. `sklearn.datasets.fetch_20newsgroups` depends on figshare, and on this network that channel is simply not available (the downloader returns 202/403, the API returns 403). Rather than fight a third-party mirror, the course uses its own text. That choice buys three things: **no third-party licence risk, no download to fail, and a task we can fully audit.** It also buys the anti-leakage scrub below, which a downloaded dataset would not give us.

### The anti-leakage scrub · 反泄漏清洗

A passage lifted from the Week 3 materials usually *says* "Week 3" inside it. If it does, the classifier can read the label straight out of the text and every accuracy number is meaningless. So the builder replaces every literal identifier before writing the corpus:

| Pattern | Replaced with | Examples |
|---|---|---|
| `Week N` / `WN` / `第 N 周` | `<WEEK>` | "Week 3", "W5" |
| `CU(N)` / `第 N 次课` | `<UNIT>` | "CU(8)" |
| `Lab N` / `实验 N` | `<LAB>` | "Lab 06" |
| `YYYY-MM-DD` | `<DATE>` | lesson-plan footer dates |

That is **262** replacements in total across the 748 kept passages. The count is written into `outputs/w8_corpus_facts.json` so the scrub can be **audited rather than trusted** — which is the point. Read `scripts/build_text_corpus.py` and count them yourself; a scrub you cannot verify is not a scrub.

**Reference run.** The instructor's full experiment lives in `scripts/w8_sequence_experiment.py`, and its output is committed as `outputs/w8_sequence.json` (4 pooling arms × 5 seeds, plus the `max_len` sweep, the per-length buckets, the 5-seed confusion matrix, the misclassified passages and the Chinese tokenisation demo). Every reference number in this handout comes from that file. Re-generate it with:

```bash
python scripts/w8_sequence_experiment.py
```

You may reproduce the tables from `w8_sequence.json`, but you must **also** run your own training — a table copied from the reference file is evidence about the instructor's run, not about yours. If your environment cannot import torch at all, you may fall back to the JSON for Parts A, C, E and F, and you must say so in one sentence in the report. What is not optional is the interpretation.

### The one protocol, fixed for all four arms

Change exactly one thing per arm. If you touch any knob below, your rows stop being comparable and the lab produces no evidence.

| Knob | Value |
|---|---|
| Corpus | `data/raw/course-text-corpus.jsonl` — 748 passages, 6 classes (week-01 … week-06) |
| Tokeniser | lowercase, regex `[a-z][a-z'-]*` |
| Vocabulary | **from the training split only**, `min_freq=2`, cap **6000**, `<pad>=0`, `<unk>=1` |
| Split | 70 / 15 / 15, stratified by week, `random_state = seed`; `n_train = 523`, `n_val = 112`, `n_test = 113` |
| Model | `Embedding(64, padding_idx=0)` → `LSTM(96, batch_first=True)` → `Linear(6)` |
| Pooling | the one knob under test: `mean_masked` / `packed` / `mean_unmasked` / `last_step` |
| Optimizer | `Adam(lr=1e-3)`, `batch_size=64`, `epochs=30`, `max_len=96`, no weight decay |
| Seeds | 42, 43, 44, 45, 46 — every arm repeated, reported as mean ± sd |

Shared bootstrap for every part below:

```python
import json, random, re, statistics as st
from pathlib import Path
import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.model_selection import train_test_split

SEEDS       = (42, 43, 44, 45, 46)
SWEEP_SEEDS = (42, 43, 44)
EPOCHS, BATCH, LR     = 30, 64, 1e-3
EMB, HID, N_CLASS     = 64, 96, 6
MIN_FREQ, MAX_VOCAB   = 2, 6000
MAX_LEN               = 96
WORD = re.compile(r"[a-z][a-z'-]*")
CORPUS = Path("data/raw/course-text-corpus.jsonl")

BUCKETS = [(20, 29), (30, 49), (50, 99), (100, 10_000)]


def set_seed(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


def load_corpus():
    """748 rows -> (raw rows, list of token lists, list of label ids 0..5)."""
    rows = [json.loads(l) for l in CORPUS.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    X = [WORD.findall(r["text"].lower()) for r in rows]
    y = [r["week"] - 1 for r in rows]
    return rows, X, y
```

## 3. Lab Tasks · 实验任务

### Part A — The pipeline: text → tensor in four steps, each with one characteristic error (10 min)

The official teaching note is explicit: *"把『变长序列 → 定长张量』的处理链路讲清楚（对齐、填充、mask），这是文本任务最常见的错误来源。"* This part builds that chain so that Parts D–I have something to break.

```python
def build_vocab(train_tokens, min_freq=MIN_FREQ, cap=MAX_VOCAB):
    """Frequency table -> vocabulary. The ONLY input is the TRAINING split.
    Reserving 0 and 1 for <pad> and <unk> is why the cap is `cap - 2`."""
    freq = {}
    for doc in train_tokens:
        for t in doc:
            freq[t] = freq.get(t, 0) + 1
    kept = [t for t, c in freq.items() if c >= min_freq]
    kept.sort(key=lambda t: (-freq[t], t))          # frequent first, ties by token
    kept = kept[:cap - 2]
    return {t: i + 2 for i, t in enumerate(kept)}, freq   # <pad>=0, <unk>=1


def encode(doc, vocab, max_len):
    """Tokens -> ids, truncated to max_len. Unknown tokens become <unk>=1.
    Note the truncation is silent and is exactly what Part F measures."""
    ids = [vocab.get(t, 1) for t in doc][:max_len]
    return ids or [1]                                # a document is never empty


def pad_batch(docs, vocab, max_len):
    """Right-pad with <pad>=0 to the longest document in THIS batch.
    Returns (ids, true_lengths); the lengths are the mask, in compact form."""
    enc = [encode(d, vocab, max_len) for d in docs]
    lengths = torch.tensor([len(e) for e in enc])
    T = int(lengths.max())
    x = torch.zeros(len(enc), T, dtype=torch.long)
    for i, e in enumerate(enc):
        x[i, :len(e)] = torch.tensor(e)
    return x, lengths
```

Now look at the data before you look at the model. Print the three things the pipeline is decided by — vocabulary size, per-class counts, and the length distribution:

```python
rows, X, y = load_corpus()
print("passages", len(rows), "classes", len(set(y)))

# per-class counts (full corpus)
from collections import Counter
cnt = Counter(y)
print("per class:", {f"W{k+1}": cnt[k] for k in range(6)})
# {W1: 105, W2: 97, W3: 114, W4: 119, W5: 128, W6: 185}

# split, exactly as the reference run does
idx = np.arange(len(y))
tr, rest = train_test_split(idx, test_size=0.30, stratify=y, random_state=42)
va, te = train_test_split(rest, test_size=0.50,
                          stratify=[y[i] for i in rest], random_state=42)
vocab, freq = build_vocab([X[i] for i in tr])
print("n_train/n_val/n_test", len(tr), len(va), len(te))   # 523 112 113

# length distribution over the full corpus
lens = sorted(len(d) for d in X)
q = lambda p: lens[int(len(lens) * p)]
print("len  min/p25/med/p75/p95/max",
      lens[0], q(.25), q(.5), q(.75), q(.95), lens[-1])
print("mean len", round(sum(lens) / len(lens), 1))
```

Reference numbers you must land on: **748** passages across **6** classes, split **W1 105 / W2 97 / W3 114 / W4 119 / W5 128 / W6 185**; a **523 / 112 / 113** train / val / test split; the vocabulary you build **from the training split only** is about **1,592** tokens (seed 42 gives **1,617**), against **3,142** unique tokens in the full corpus; and the length distribution is **min 20 / p25 26 / median 35 / p75 50 / p95 87 / max 285 / mean 42.1** words.

Three things follow, and they set up the whole lab:

1. **The classes are imbalanced** — W6 (185) is 1.76× W1 (105). Hold that thought until Part H, where it becomes the explanation.
2. **The median passage is 35 words, but `max_len = 96`.** Most documents are short; padding will therefore be most of every batch. Hold that until Part E.
3. **The vocabulary is small** — ~1,592 tokens from 523 training passages. A small vocabulary on a small training set is the shape of every honest result in this lab.

Checkpoint A — the three printed blocks (vocabulary size, per-class counts, length distribution), and one sentence for each of the four pipeline steps naming the error that step is most likely to introduce.

### Part B — Chinese tokenisation: why whitespace splitting is not "doing nothing", it is the worst thing (10 min)

CU(8)'s first keyword is 分词 (tokenisation), and it stops being cosmetic the moment the text is not English. Chinese has no spaces between words, so the "obvious" tokeniser — `s.split()` — produces **one token per sentence**. The reference run measures exactly how bad that is on this repository's own Chinese textbook text (`textbook/chapter-01..06/zh.html`, 750 segments):

| Scheme | Vocab (train) | Singleton share | Test tokens | **OOV rate** |
|---|---|---|---|---|
| Whitespace (no segmentation) | **372** | **0.9946** | **375** | **0.9973** |
| Character level | **880** | 0.2170 | **14 860** | **0.0254** |

```python
def token_stats(segments, tok_fn, name):
    """Build a vocab on the first half, score OOV on the second half."""
    split = len(segments) // 2
    train, test = segments[:split], segments[split:]
    vocab = {}
    for s in train:
        for t in tok_fn(s):
            vocab[t] = vocab.get(t, 0) + 1
    n_tok = sum(len(tok_fn(s)) for s in test)
    oov = sum(1 for s in test for t in tok_fn(s) if t not in vocab)
    single = sum(1 for c in vocab.values() if c == 1)
    print(f"{name:12s} vocab={len(vocab):4d}  singleton={single/max(len(vocab),1):.4f}  "
          f"test_tokens={n_tok:6d}  OOV={oov/max(n_tok,1):.4f}")
    return vocab


# segments: CJK-only strings of >= 12 characters, taken from the Chinese textbook
token_stats(segments, lambda s: s.split(), "whitespace")
token_stats(segments, lambda s: list(s),   "character")
```

**Read the two rows together and the mechanism is unavoidable.**

- The whitespace row has **375 test tokens for 375 test segments** — exactly one token per segment. The "tokeniser" treated each whole sentence as a single word.
- Its vocabulary is **372**, of which **370 are singletons** (share **0.9946**) — a vocabulary in which almost nothing is seen twice is a vocabulary that transfers nothing.
- Its **OOV rate is 0.9973**: 374 of the 375 test tokens were never seen in training. Every test segment therefore becomes a **single `<unk>`** — the model is handed an unbroken signal that carries no content at all.
- The character-level row collapses the same text to a **880**-token vocabulary and an OOV of **0.0254**. That is a **39×** reduction in OOV (0.9973 / 0.0254 ≈ 39) for one line of code.

So, in one sentence to write in your report: **splitting Chinese on whitespace does not "leave the text alone"; it maps every sentence to a single `<unk>`, which is strictly worse than character-level tokenisation for this data.** The engineering rule is: use a real segmenter (jieba or equivalent); if none is available, fall back to **character level**; never fall back to `split()`.

Checkpoint B — the two-row table from your own run, and a two-sentence explanation of why the whitespace row has exactly one test token per segment. Include the OOV ratio.

### Part C — Train it: one model, mean ± sd, curves (10 min)

```python
class TextLSTM(nn.Module):
    """The model is fixed for every arm. `pooling` is the only knob that moves."""

    def __init__(self, vocab_size, pooling, dropout=0.0):
        super().__init__()
        self.pooling = pooling
        self.emb = nn.Embedding(vocab_size, EMB, padding_idx=0)   # 0 never trains
        self.rnn = nn.LSTM(EMB, HID, batch_first=True)
        self.head = nn.Linear(HID, N_CLASS)
        self.drop = nn.Dropout(dropout)                            # 0.0 -> identity

    def forward(self, x, lengths):
        e = self.drop(self.emb(x))
        if self.pooling == "packed":
            packed = nn.utils.rnn.pack_padded_sequence(
                e, lengths, batch_first=True, enforce_sorted=False)
            _, (h, _) = self.rnn(packed)
            z = h[-1]                                  # final state of the REAL length
        else:
            out, _ = self.rnn(e)
            if self.pooling == "last_step":
                z = out[:, -1, :]                      # final SLOT, padding included
            elif self.pooling == "mean_unmasked":
                z = out.mean(1)                        # mean over padding too
            else:                                      # mean_masked
                mask = (x != 0).unsqueeze(-1).float()
                z = (out * mask).sum(1) / mask.sum(1).clamp(min=1)
        return self.head(self.drop(z))


@torch.no_grad()
def predict(model, X, y, vocab, max_len, batch=128):
    model.eval()
    preds = []
    order = sorted(range(len(X)), key=lambda i: -len(X[i]))    # pack-friendly
    for i in range(0, len(order), batch):
        idx = order[i:i + batch]
        x, ln = pad_batch([X[j] for j in idx], vocab, max_len)
        preds.extend(model(x, ln).argmax(1).tolist())
    out = [0] * len(X)
    for pos, j in enumerate(order):
        out[j] = preds[pos]
    return out


def train(arm, seed, max_len=MAX_LEN, epochs=EPOCHS, want_curve=False,
          dropout=0.0, wd=0.0):
    set_seed(seed)
    rows, X, y = load_corpus()
    idx = np.arange(len(y))
    tr, rest = train_test_split(idx, test_size=0.30, stratify=y, random_state=seed)
    va, te = train_test_split(rest, test_size=0.50,
                              stratify=[y[i] for i in rest], random_state=seed)
    Xtr = [X[i] for i in tr]; ytr = [y[i] for i in tr]
    Xte = [X[i] for i in te]; yte = [y[i] for i in te]

    vocab, _ = build_vocab(Xtr)                        # TRAIN ONLY. Always.
    model = TextLSTM(len(vocab) + 2, arm, dropout=dropout)
    opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=wd)
    g = torch.Generator().manual_seed(seed)
    hist = {"train_acc": [], "val_acc": []}

    for ep in range(epochs):
        model.train()
        perm = torch.randperm(len(Xtr), generator=g).tolist()
        for i in range(0, len(perm), BATCH):
            sel = perm[i:i + BATCH]
            x, ln = pad_batch([Xtr[j] for j in sel], vocab, max_len)
            opt.zero_grad()
            nn.functional.cross_entropy(model(x, ln),
                                        torch.tensor([ytr[j] for j in sel])).backward()
            opt.step()
        if want_curve and (ep % 3 == 0 or ep == epochs - 1):
            p = predict(model, Xtr, ytr, vocab, max_len)
            hist["train_acc"].append(round(float(np.mean(np.array(p) == np.array(ytr))), 4))
            p = predict(model, [X[i] for i in va], [y[i] for i in va], vocab, max_len)
            hist["val_acc"].append(round(float(np.mean(
                np.array(p) == np.array([y[i] for i in va]))), 4))

    pred = predict(model, Xte, yte, vocab, max_len)
    yt, yp = np.array(yte), np.array(pred)
    return {"arm": arm, "seed": seed, "max_len": max_len,
            "vocab_size": len(vocab) + 2,
            "params": sum(p.numel() for p in model.parameters()),
            "test_acc": round(float((yt == yp).mean()), 4),
            "test_macro_f1": round(float(f1_score(yt, yp, average="macro")), 4),
            "curve": hist if want_curve else None,
            "predictions": yp.tolist(), "test_idx": [int(i) for i in te],
            "model": model, "vocab": vocab, "yte": yt, "Xte": Xte}


rows_packed = [train("packed", s) for s in SEEDS]
for r in rows_packed:
    print(f"seed {r['seed']}  vocab {r['vocab_size']:5d}  params {r['params']}  "
          f"test {r['test_acc']:.4f}  macroF1 {r['test_macro_f1']:.4f}")
accs = [r["test_acc"] for r in rows_packed]
print(f"packed test {st.mean(accs):.4f} +- {st.stdev(accs):.4f}")
```

Reference, `packed`, seed 42 (per-seed rows are in `w8_sequence.json`): **166,278** parameters, training accuracy **0.9885**, validation accuracy **0.4196**, test accuracy **0.4248**. Over five seeds the arm is **0.4248 ± 0.0360**.

The training curve, sampled every 3 epochs (11 points, seed 42):

```
epoch      :   1      4      7     10     13     16     19     22     25     28     30
train acc  : 0.2849 0.2696 0.4857 0.6386 0.7400 0.8375 0.8853 0.8967 0.9675 0.9866 0.9885
val acc    : 0.2143 0.2411 0.2589 0.2500 0.3036 0.3393 0.3571 0.3036 0.3661 0.4196 0.4196
```

The training curve climbs to **0.9885**; the validation curve crawls to **0.4196** and never falls back. The gap at epoch 30 is **0.9885 − 0.4196 = 0.5689** — a severely overfit model. But note the shape: **validation never declines.** This is not "trained too long"; it is "capacity pointed at the wrong thing". Part G proves it.

Checkpoint C — your `packed` rows over ≥ 3 seeds with mean ± sd, plus `curves_text.png` (train and validation on the same axes, and a second panel with validation zoomed). Then answer: the reference single-seed test accuracy is 0.4248 over 113 test documents — how many documents is one test document worth?

### Part D — Four ways to read one LSTM: the core of the lab (15 min)

Everything in this part changes exactly one line: how a `(B, T, H)` output tensor is compressed into a `(B, H)` document vector. Write your predicted **ranking** of the four arms on paper first, then run them.

| Arm | What it does | The line |
|---|---|---|
| `mean_masked` | average over the **real** timesteps only | `(out * mask).sum(1) / mask.sum(1).clamp(min=1)` |
| `packed` | `pack_padded_sequence`, take the final hidden state | `_, (h, _) = self.rnn(packed); z = h[-1]` |
| `mean_unmasked` | average over **every** timestep, padding included | `z = out.mean(1)` |
| `last_step` | no packing, take the last **slot** | `z = out[:, -1, :]` |

```python
def arm_stats(arm, seeds=SEEDS, **kw):
    rows = [train(arm, s, **kw) for s in seeds]
    a = [r["test_acc"] for r in rows]
    f = [r["test_macro_f1"] for r in rows]
    print(f"{arm:13s} acc {st.mean(a):.4f} +- {st.stdev(a):.4f}   "
          f"macroF1 {st.mean(f):.4f} +- {st.stdev(f):.4f}")
    return rows


ledger = {a: arm_stats(a) for a in
          ("mean_masked", "packed", "mean_unmasked", "last_step")}
```

Reference ledger (5 seeds, mean ± sd — this is the table your numbers should resemble):

| Arm | Test accuracy | **Macro F1** |
|---|---|---|
| `mean_masked` | **0.5027 ± 0.0449** | **0.4774 ± 0.0482** |
| `packed` | 0.4248 ± 0.0360 | 0.3843 ± 0.0422 |
| `mean_unmasked` | 0.3929 ± 0.0684 | 0.3315 ± 0.0935 |
| `last_step` | **0.2407 ± 0.0040** | **0.0711 ± 0.0095** |

Four readings, all required in your report:

1. **The gap is 26.2 points, and it is one line of code.** Best (`mean_masked`, 0.5027) minus worst (`last_step`, 0.2407) is **0.2620**. The model, the data, the optimizer and the seed list are identical in every row.
2. **The masked mean is worth +11.0 points over the unmasked mean** — 0.3929 → **0.5027** (0.1098). Masking is not a formality; it is the single largest lever in the lab.
3. **`[-1]` → `packed` is worth +18.4 points** — 0.2407 → **0.4248** (0.1841). And `[-1]` → best is **+26.2 points**.
4. **`last_step` has a macro F1 of 0.0711.** The 6-class random baseline is **1/6 ≈ 0.1667**, so `last_step`'s macro F1 is **below random**. Its *accuracy* (0.2407) is above random, which is the trap: the headline number looks survivable while the per-class performance is worse than guessing. Part H is about exactly this split.

Checkpoint D — the four-arm ledger with **both** accuracy and macro F1, mean ± sd over ≥ 3 seeds, your pre-registered ranking next to the actual one, and one sentence naming which line of code produced the 26.2-point spread.

### Part E — Dissecting that bug: two pieces of evidence that it is the padding (15 min)

`last_step` does not crash. It trains, it converges, it scores above random. The only way to catch it is to **look where the damage lands**. Build two pieces of evidence.

**Evidence 1 — accuracy by true document length.** The bug should bite hardest on the shortest documents, because those carry the most padding.

```python
def by_length(pred, yte, te_idx, X):
    lens = [len(X[i]) for i in te_idx]
    yt, yp = np.array(yte), np.array(pred)
    for lo, hi in BUCKETS:
        sel = [k for k, L in enumerate(lens) if lo <= L <= hi]
        if sel:
            tag = f"{lo}-{hi if hi < 10_000 else 'max'}"
            print(f"  {tag:>8}  n={len(sel):3d}  acc={(yt[sel]==yp[sel]).mean():.4f}")


detail = train("packed", 42)
bug    = train("last_step", 42)
print("packed");    by_length(detail["predictions"], detail["yte"], detail["test_idx"], load_corpus()[1])
print("last_step"); by_length(bug["predictions"],    bug["yte"],    bug["test_idx"],    load_corpus()[1])
```

Reference (seed 42), `packed` vs `last_step`:

| Bucket (words) | n | `packed` | `last_step` |
|---|---|---|---|
| 20–29 | 38 | 0.4211 | **0.1579** |
| 30–49 | 41 | 0.3902 | **0.1707** |
| 50–99 | 29 | 0.4483 | 0.4138 |
| 100–max | 5 | 0.6000 | 0.4000 |

The two columns separate exactly where the padding is: the shortest two buckets collapse to **0.1579** and **0.1707**, both **below the 0.1667 random baseline**, while the 50–99 bucket barely moves (0.4483 vs 0.4138).

**Evidence 2 — a hard cut at `max_len`.** If the bug is "reading the pad vector", then documents long enough to *have no pad vector* should be immune.

```python
lens = [len(X[i]) for i in bug["test_idx"]]
yt, yp = bug["yte"], np.array(bug["predictions"])
eq = [k for k, L in enumerate(lens) if L >= MAX_LEN]
lt = [k for k, L in enumerate(lens) if L <  MAX_LEN]
print(f">= max_len : n={len(eq):3d}  acc={(yt[eq]==yp[eq]).mean():.4f}")
print(f"<  max_len : n={len(lt):3d}  acc={(yt[lt]==yp[lt]).mean():.4f}")
```

Reference, `last_step`, seed 42: documents with length **≥ 96** (`n = 5`) score **0.4000**; documents with length **< 96** (`n = 108`) score **0.2315**. Across the whole test split, **95.58 %** of documents are shorter than `max_len = 96` — so almost every document is reading a pad vector.

**Write the conclusion in these words.** When a document is long enough to have no padding, `out[:, -1, :]` really does point at the end of the sentence, and accuracy jumps to 0.4000. When it is shorter, `out[:, -1, :]` points at a `<pad>` position and accuracy falls to 0.2315. The two buckets share every other variable. Therefore the failure is **not** "this task is too hard" — it is "the model read the pad vector". The same LSTM, read by its real length (`packed`) or by a masked mean, does not have this problem.

Checkpoint E — your own per-bucket table and your own `≥ 96` / `< 96` split, plus the two-sentence conclusion above in your own words. Name the specific tensor and the specific index that is wrong.

### Part F — Sweep `max_len`: 48 / 96 / 192 (10 min)

A natural first instinct is "the model saw too much padding, so let us change how much padding there is". Test it.

```python
sweep = {}
for arm in ("packed", "last_step"):
    sweep[arm] = {}
    for ml in (48, 96, 192):
        vals = [train(arm, s, max_len=ml)["test_acc"] for s in SWEEP_SEEDS]
        sweep[arm][ml] = round(st.mean(vals), 4)
        print(f"{arm:10s} max_len={ml:3d}  {st.mean(vals):.4f}  (sd {st.stdev(vals):.4f})")
```

Reference (3 seeds 42–44):

| `max_len` | `packed` | `last_step` |
|---|---|---|
| 48 | **0.4572** (sd 0.0135) | 0.2891 (sd 0.0358) |
| 96 | **0.4454** (sd 0.0285) | 0.2389 (sd 0.0000) |
| 192 | **0.4454** (sd 0.0357) | 0.2478 (sd 0.0000) |

**Conclusion: `max_len` is not the lever.** For `packed`, the three values (0.4572 / 0.4454 / 0.4454) move by less than one standard deviation — the sweep is noise. For `last_step`, no setting rescues the arm: it is bad at every length. The bug is not "how much padding"; it is "**which positions the final read touches**". Changing `max_len` never changes *that*, so it cannot fix anything — it can only redistribute which documents happen to be unaffected. Fixing the read (Part D) moves the number 26 points; tuning the length moves nothing.

Checkpoint F — the 2 × 3 sweep table from your own run, and one sentence: why does changing `max_len` fail to close the gap that Part D closed?

### Part G — Add Week 6's regularisation: the honest result of the week (10 min)

Last week you learned that Dropout and weight decay help. This week, apply the **same** two knobs to the best arm and report what actually happens.

```python
reg = arm_stats("mean_masked", dropout=0.3, wd=1e-3)   # Dropout 0.3 + weight decay 1e-3
```

Reference (5 seeds):

| Arm | Test accuracy | Macro F1 |
|---|---|---|
| `mean_masked` (baseline) | **0.5027 ± 0.0449** | 0.4774 ± 0.0482 |
| `mean_masked` + Dropout 0.3 + wd 1e-3 | **0.4672 ± 0.0595** | 0.4433 ± 0.0625 |

**Regularisation made it worse.** Accuracy fell from 0.5027 to **0.4672** — a drop of **3.6 percentage points**; macro F1 fell from 0.4774 to 0.4433 — a drop of **3.4 points**; and the standard deviation across seeds *widened* from ±0.0449 to ±0.0595. This is the week's most important honest conclusion, so write it carefully:

**The diagnosis: the bottleneck is the data, not the capacity.** There are **523** training passages and **1,592** vocabulary entries. The model already overfits (0.9885 train vs 0.4196 val), which means it has more than enough capacity to memorise the training set — so **removing capacity cannot help; it only removes the little signal it has.** Dropout on an already-starved dataset simply hides the features that were doing the work.

**Why last week was different — and why the same tool has the opposite answer here.** In Week 6 the dataset was large and the model was oversized, so regularisation removed *memorisation* and left *signal*. Here the training set is 523 passages, so regularisation removes *signal* along with the noise. **The same technique, under two different bottlenecks, has two opposite correct answers.** "Always add Dropout" is a superstition, not a method. The binding constraint here is data; the fix, if any, is more labelled passages, not a smaller model.

Checkpoint G — your `mean_masked` vs `mean_masked_reg` rows with mean ± sd for **both** metrics, and one paragraph stating the diagnosis (bottleneck = data, not capacity) **and** explaining why Week 6's regularisation succeeded where this one fails.

### Part H — Error analysis: open the matrix, read the recalls, paste the passages (15 min)

**This is the official focus of the lab.** The post-class task is verbatim: *记录精度、混淆矩阵与典型错误样本分析。* "0.4248" is not a result; it is an unfinished sentence.

```python
# 5-seed summed confusion — the matrix in the reference table below
conf = np.zeros((N_CLASS, N_CLASS), dtype=int)
for s in SEEDS:
    rs = train("packed", s)
    conf += confusion_matrix(rs["yte"], np.array(rs["predictions"]),
                             labels=list(range(N_CLASS)))
print(conf)
print("total", conf.sum(), " correct", int(np.trace(conf)),
      " acc", round(float(np.trace(conf) / conf.sum()), 4))

# one seed, with the misclassified passages kept for Part H's verbatim print
r  = train("packed", 42)
cm = confusion_matrix(r["yte"], np.array(r["predictions"]),
                      labels=list(range(N_CLASS)))
print(cm)
print("seed 42 test", r["test_acc"],
      " wrong", int((np.array(r["predictions"]) != r["yte"]).sum()))
```

Reference, summed over all five seeds (`packed`) — the matrix your own run should resemble:

| true ＼ pred | W1 | W2 | W3 | W4 | W5 | W6 |
|---|---|---|---|---|---|---|
| **W1** (n=80) | 14 | 12 | 10 | 22 | 8 | 14 |
| **W2** (n=75) | 16 | 14 | 13 | 11 | 13 | 8 |
| **W3** (n=85) | 12 | 4 | 36 | 13 | 7 | 13 |
| **W4** (n=90) | 7 | 4 | 16 | 43 | 10 | 10 |
| **W5** (n=95) | 6 | 10 | 9 | 11 | 40 | 19 |
| **W6** (n=140) | 8 | 8 | 11 | 11 | 9 | 93 |

Totals: **565** predictions, **240** correct, accuracy **0.4248**. Two features stand out:

1. **The off-diagonal is almost flat.** Every off-diagonal cell is between **4** and **22** — there is no "disaster cell" where one week is systematically dumped into another. The confusion is spread across the whole grid.
2. **The diagonal is only high for W6 (93).** With one clear exception, every true week leaks its predictions roughly evenly into all the others. That exception is not content — it is size.

Now read the recall column against class size:

| True week | Recall | Test n |
|---|---|---|
| W1 | **0.1750** | 80 |
| W2 | **0.1867** | 75 |
| W3 | 0.4235 | 85 |
| W4 | 0.4778 | 90 |
| W5 | 0.4211 | 95 |
| W6 | **0.6643** | 140 |

**Recall rises with class size** (test counts 80, 75, 85, 90, 95, 140), with a Spearman rho of **0.77**. There are two small inversions: W2 (n=75) edges above W1 (n=80), and W5 (0.4211) sits just below W4 (0.4778). W6's recall is **3.80×** W1's (0.6643 / 0.1750). **This is the direct evidence that the model is learning the prior, not the content**: it is best at the biggest class and worst at the smallest, which is what a model does when it has not found features that separate the classes and falls back on "bet on the common one".

**Then read the passages themselves.** The `packed` arm at seed 42 misclassifies **14** of 113 test passages. Print them verbatim — sorted shortest-first, because short documents carry the heaviest vocabulary burden — and the reference file does exactly that:

```python
rows, X, y = load_corpus()
wrong = []
for k, p in enumerate(r["predictions"]):
    i = r["test_idx"][k]
    if p != y[i]:
        wrong.append({"true": y[i] + 1, "pred": p + 1,
                      "tokens": len(X[i]), "text": rows[i]["text"][:170]})
wrong.sort(key=lambda w: w["tokens"])
for w in wrong:
    print(f"true W{w['true']} -> pred W{w['pred']}  ({w['tokens']} tok)  {w['text']}")
```

Paste **at least three** and group them. The reference 14 fall into three families:

| Family | Example (verbatim) | True → Pred | Words |
|---|---|---|---|
| **Short sentence** — the vocabulary burden is heaviest when there are few tokens to average | `Hidden layers transform the features first; the output layer decides afterwards. The same data becomes separable in the new space.` | W4 → W3 | 20 |
| **Generic engineering sentence** — true of every week | `Hyper-parameters, data paths, batch size and split ratios live in a file or a single dictionary — not scattered through the code and not in your memory.` | W1 → W2 | 26 |
| **Term reused across weeks** — the number is real but appears in two weeks' materials | `Explain how a training set of 80 samples against 17,226 parameters produces overfitting on purpose, and why that is the point of the lab` | W6 → W4 | 22 |

**The conclusion you are allowed to write.** In all 14 cases the model did not "look wrong" at a passage that plainly belonged to one week — it looked at a passage for which **there is no single correct week**. A generic sentence about `batch size`, a concept introduced in Week 2 and reused in Weeks 3–6, is *genuinely* ambiguous under this label scheme; a 20-word fragment has almost no vocabulary to average. **This is not the model failing at an easy task; it is the task definition having a boundary.** The 0.4248/0.0711 split, the flat off-diagonal, and the three families of misclassified passages are three views of the same fact: the labels are week-of-origin, not topic, and week boundaries are not topic boundaries.

Checkpoint H — the confusion matrix (as a figure with `imshow` or `ConfusionMatrixDisplay`), the total and correct counts, the six recall values, the W6/W1 ratio, a two-sentence statement of what the recall-versus-class-size curve means, and **≥ 3 misclassified passages pasted verbatim and classified into the three families**. "The model is bad at short texts" is not an explanation; "this 20-word passage has too few tokens for a masked mean to recover any week-specific signal, and the model defaults to the largest neighbour class" is.

### Part I — AI co-pilot: generate a whole pipeline, then find its bug by measuring it (10 min)

This is the official 赋能 deliverable. The task is not "get an AI to write a pipeline" — that is easy and the AI is good at it. The task is to **catch the errors that a plausible-looking pipeline contains**, and to prove you caught them **with a number**.

Ask your AI assistant this, pasting the protocol table (Part 2) into the prompt — not the whole notebook:

**"Write a complete PyTorch text-classification pipeline for this setup: a tokeniser, a vocabulary, an `nn.Embedding`, an `nn.LSTM`, and a classifier head. Return one self-contained script with a training loop and an accuracy printout."**

A generic answer will almost always contain the following defects. Find every one, then fill in the record table. This table **is** the deliverable — three columns, no prose.

| AI original code (the defect) | What you changed it to | Accuracy before → after |
|---|---|---|
| Pooling with bare `out.mean(1)` | masked mean: `(out * (x != 0).unsqueeze(-1)).sum(1) / mask.sum(1).clamp(min=1)` | 0.3929 → **0.5027** · **+11.0 points** |
| Reading `out[:, -1, :]` with no `lengths` passed at all | pass `lengths`, use `pack_padded_sequence`, take the final hidden state | 0.2407 → **0.4248** · **+18.4 points** |
| Vocabulary built from **all** documents (train + val + test) | build it from the **training split only** | *your measurement* |
| `nn.Embedding(V, EMB)` with no `padding_idx` | `nn.Embedding(V, EMB, padding_idx=0)` | *your measurement* |
| `forward(self, x)` with **no `lengths` argument** — the model has no way to know the real lengths | `forward(self, x, lengths)`, and pass lengths all the way from `pad_batch` | *see the first two rows: no lengths is the same defect as row 2* |
| Sort the whole dataset before splitting, then split | split first, pad **per batch** (padding to the batch max, not the corpus max) | *your measurement* |

Four of these are checkable without training, and you should say so:

- **Did the AI pass `lengths` into `forward`?** If the signature is `forward(self, x)`, the model *cannot* mask or pack — this is the root defect behind rows 2 and 5.
- **Was the vocabulary built on all the data?** Search for `build_vocab` and check which split it is called on. A full-corpus vocabulary leaks validation tokens into training and inflates the score for the wrong reason.
- **Is there `padding_idx=0` on the `Embedding`?** Without it, the `<pad>` row trains as if it were a word, and the mask in the pooling step must carry the whole burden.
- **Is the pooling a masked mean, or a bare `mean`?** `out.mean(1)` averages the pad positions; look for the `mask` variable and see whether it is actually used.

**Two rows are pre-filled with the reference numbers**, because they are the two defects with the largest measured cost: **bare mean → masked mean is +11.0 points** (0.3929 → 0.5027), and **`[-1]` → packed is +18.4 points** (0.2407 → 0.4248). The other rows you must fill with a number from **your own** run. **"I found the bug" is not evidence. "The bug cost me 11.0 points" is.**

Checkpoint I — the three-column record table, every row backed by a measured before/after accuracy gap, and the two pre-filled rows reproduced from your own arms. At least one row must be a defect you found that was **not** in this list.

## 4. After the lab · 课后作业 (not counted in the 80 min)

1. **Text classification report** — the official post-class task: *提交文本分类实验报告。* One section per Part. It must contain: the pipeline printouts (Part A), the Chinese tokenisation table (Part B), the `packed` seed sweep and curve (Part C), the four-arm ledger with accuracy **and** macro F1 (Part D), the per-bucket and ≥ 96 / < 96 evidence (Part E), the `max_len` sweep (Part F), the regularisation comparison and diagnosis (Part G), the confusion matrix, recall table and ≥ 3 verbatim misclassified passages (Part H), and the AI pipeline-audit record (Part I).
2. **One paragraph graded on its own** — the official post-class task: *写出"若换成长文本，现有方案会遇到什么问题"的预判分析。* Predict what breaks when passages grow from a median of 35 words to thousands of words, and name the specific line in your pipeline that fails first.

Both are due before the Week 9 lab.

## 5. M8 · Midterm Checkpoint ★ — Module 2 milestone (this week's extra deliverable)

**This week is the module-2 milestone.** It is graded as part of the course's 15-point stage review (M4 / M8 / M12 / M16, 4 points each), **separately from this lab's 100 points**. The M8 requirements are not optional because they are not part of the 80-minute lab — they are a checkpoint on your capstone.

**Three deliverables:**

1. **A runnable prototype.** On a *clean machine*, `git clone` the repo, follow the README, and the prototype runs. Not "it runs on my laptop" — on a clean clone. If a step needs a secret, a path or a manual download that the README does not mention, it does not run and the checkpoint is not met.
2. **`DATA.md` v1.** One page: where the data comes from, its licence, its size and shape, how it splits, and any known leakage or bias. This is the Week 8 version of exactly what Part A and Part B of this lab taught you to ask about a corpus.
3. **A three-slide deck.** Slide 1 — what the project does. Slide 2 — the numbers. **Slide 3 — what failed.** The third slide is the graded one: a deck that reports only successes is treated as **incomplete**.

**Format: live demo, 3 minutes, then 2 minutes of questions.** Rules:

- **No screen recordings.** You run the prototype in the room.
- **No PPT animation standing in for a live run.** A slide deck may *frame* the demo; it may not *replace* it.
- **Slide 3 is the point.** "What failed" means a specific failure with a number or an error message, what you tried, and what you concluded. From this lab, the natural candidates are right in front of you: the `last_step` bug (0.2407 with a macro F1 of 0.0711), or the regularisation result (0.5027 → 0.4672, the opposite of what Week 6 taught).

**What a strong Slide 3 looks like on this lab's material:** "My best arm reached 0.5027, which is barely above the 0.1667 random baseline for six classes. I added Dropout and weight decay, expecting them to help as they did in Week 6, and accuracy *fell* to 0.4672 with a wider seed spread. The diagnosis is that my bottleneck is 523 training passages, not model capacity — so the fix is more data, not a smaller model." That is a failure, a number, and a conclusion. That is what M8 is checking for.

## 6. Deliverables Checklist · 交付清单

- [ ] `lab-08.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Pipeline printouts verified in-cell: **748** passages / **6** classes; per-class **105 / 97 / 114 / 119 / 128 / 185**; **523 / 112 / 113** split; length distribution **min 20 / p25 26 / med 35 / p75 50 / p95 87 / max 285 / mean 42.1** (Part A)
- [ ] `w8_text_lab.py` — one script that re-runs the full grid and writes `arms.json`
- [ ] `arms.json` — raw per-seed rows for every arm (evidence, not a screenshot)
- [ ] Chinese tokenisation table: whitespace **OOV 0.9973 / singleton 0.9946 / vocab 372 / test tokens 375** vs character **OOV 0.0254 / singleton 0.2170 / vocab 880 / test tokens 14 860** (Part B)
- [ ] Four-arm ledger with mean ± sd over ≥ 3 seeds, **accuracy and macro F1** (Part D): `mean_masked` **0.5027 ± 0.0449 / 0.4774 ± 0.0482**, `packed` 0.4248 ± 0.0360 / 0.3843 ± 0.0422, `mean_unmasked` 0.3929 ± 0.0684 / 0.3315 ± 0.0935, `last_step` **0.2407 ± 0.0040 / 0.0711 ± 0.0095**
- [ ] `curves_text.png` — training and validation curves (Part C)
- [ ] Per-length-bucket table and the `≥ 96` / `< 96` split (Part E), plus the "it is the pad vector" conclusion
- [ ] `max_len` sweep table 48 / 96 / 192 for `packed` and `last_step` (Part F)
- [ ] Regularisation comparison and diagnosis paragraph (Part G)
- [ ] `confusion_matrix.png`; the **565 / 240 / 0.4248** totals; the six recalls; the W6/W1 **3.80×** ratio; **≥ 3 verbatim misclassified passages** classified into families (Part H)
- [ ] `ai_pipeline_audit.md` — the three-column AI audit with a measured before/after gap per row, including the two pre-filled rows (Part I)
- [ ] Pushed to GitHub with **≥ 2 meaningful commits** (`feat: ...` style messages)
- [ ] **M8 pack**: runnable prototype (clean clone), `DATA.md` v1, 3 slides with Slide 3 = failure (§5)
- [ ] *(after the lab)* Text classification report + the long-text prediction paragraph

## 7. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Pipeline: tokenise → vocab → encode → pad (Part A) | 10 | All four steps in-cell; vocabulary built **from the training split only** and stated as such; vocabulary size, per-class counts and length distribution all printed; the `<pad>=0 / <unk>=1` reservation and the `cap − 2` arithmetic shown |
| Chinese tokenisation contrast (Part B) | 8 | Both schemes run; the whitespace row shows **one test token per segment**; OOV **0.9973 vs 0.0254** reproduced; the "splitting on whitespace maps each sentence to a single `<unk>`" mechanism written out |
| Training protocol, seeds and curves (Part C) | 10 | ≥ 3 seeds; mean ± sd everywhere; `curves_text.png` present; the **0.9885 vs 0.4196** overfit gap stated and the "validation never declines" observation made |
| **Four pooling arms ledger (Part D)** | **16** | All four arms run over ≥ 3 seeds; **accuracy and macro F1** both reported as mean ± sd; the **26.2-point** spread and the **+11.0 / +18.4** gaps reproduced; `last_step`'s macro F1 **0.0711 below the 0.1667 baseline** stated explicitly; a pre-registered ranking compared to the actual one |
| **Dissecting the bug (Part E)** | **14** | Per-length-bucket table reproduced (short buckets **0.1579 / 0.1707**); the **≥ 96 (n=5, 0.4000)** vs **< 96 (n=108, 0.2315)** split reproduced; the conclusion names the specific tensor and index and rules out "the task is too hard" |
| `max_len` sweep (Part F) | 8 | 48 / 96 / 192 run for both arms; the **0.4572 / 0.4454 / 0.4454** and **0.2891 / 0.2389 / 0.2478** rows reproduced; the "not the lever" conclusion stated with the reason (it does not change which positions the read touches) |
| **Regularisation is not the lever (Part G)** | **12** | Dropout 0.3 + wd 1e-3 applied to `mean_masked`; **0.5027 → 0.4672** and the widened sd (±0.0449 → ±0.0595) reported honestly; the diagnosis (bottleneck = 523 passages, not capacity) written; **contrasted with why Week 6 succeeded** |
| **Error analysis (Part H)** | **14** | Confusion matrix drawn; **565 / 240 / 0.4248** reproduced; the flat off-diagonal (4–22) noted; six recalls and the **3.80×** ratio given; the recall-versus-class-size reading stated (Spearman rho = 0.77, two inversions); **≥ 3 misclassified passages pasted verbatim** and classified into the three families |
| **AI co-pilot measured record (Part I)** | **8** | Three-column table (AI original / what you changed / before→after); every row backed by a **measured** number; the two pre-filled rows reproduced; at least one defect found that was not on the list; no row is "it looked wrong" |

Late policy: −10 % per day, max 3 days, then 0.

*This rubric mirrors the official assessment row `CNN 与序列模型的搭建与调优` — non-highlighted but a difficulty point, **6 % of the final course mark**, assessed through the lab report. W7 and W8 share this row. The M8 checkpoint (§5) is graded separately, as 4 of the course's 15 stage-review points.*

## 8. Submission · 提交方式

```bash
git add lab-08.ipynb w8_text_lab.py arms.json \
        curves_text.png confusion_matrix.png \
        ai_pipeline_audit.md DATA.md slides.pdf
git commit -m "feat: complete lab 07 (text classification pipeline and the padding bug)"
git push origin main
```

Then paste your repo URL into the LMS submission box. **A commit hash counts as your timestamp**, not the LMS upload time. Deadline: **TBD by instructor**.

## 9. Exit Ticket · 课后反思 (answer in the last Markdown cell)

1. `mean_masked` reaches 0.5027 and `last_step` reaches 0.2407 on the **same** data, model, optimizer and seeds. Describe the difference in one sentence without using the words "better" or "worse" — describe the **tensor operation** each one performs.
2. Week 6 taught you that Dropout and weight decay help; in Part G they cost 3.6 percentage points. Write the **one sentence** that decides which answer is correct on a given dataset, and then classify this dataset with it.
3. `last_step` has accuracy 0.2407 (above the 0.1667 baseline) but macro F1 0.0711 (below it). Which number would you put on a slide, and which number would you want a user of the model to see? Answer with the 0.1750 / 0.6643 recall pair as your evidence.

## 10. 中文摘要

**实验 7（第 8 周）**：把一段英文文本变成张量，然后用一个 LSTM 判断它出自本课程第 1–6 周中的哪一周（6 分类），最后回答一个问题——**同一个模型，四种读法，准确率差 26.2 个点，差在哪一行代码上。**

协议固定不变：语料 = **本课程第 1–6 周自有材料**（748 段 / 6 类，**零下载、完全离线**，CC BY-NC-SA 4.0）→ 分词（小写 + 正则 `[a-z][a-z'-]*`）→ 词表（**只从训练集**、`min_freq=2`、上限 6000、`<pad>=0`/`<unk>=1`）→ 70/15/15 分层划分（**523 / 112 / 113**）→ `Embedding(64, padding_idx=0) → LSTM(96, batch_first=True) → Linear(6)`（166,278 参数，种子 42）→ Adam(lr=1e-3)、batch 64、**30 轮**、`max_len=96` → **5 个种子（42–46）报均值 ± 标准差**。

**语料是手造的，而且必须先清洗。** 第 3 周材料里写着「Week 3」，不清洗的话标签就从文本里读出来了。构建脚本把 `Week N` / `WN` / `CU(N)` / `Lab N` / `实验 N` / `第 N 周` / 日期替换成占位符，共 **262 处**，并把计数写进 JSON 供审计。语料 SHA-256 前 12 位 `87e41aac89ef`。不用公开数据集还有一个现实原因：`fetch_20newsgroups` 依赖 figshare，本网络该通道不可用（下载端返回 202/403、API 403）。自有语料换来三件事——**零第三方许可风险、零下载、可完全离线复现**。

九件必须自己做出来的事：

1. **管线四步，每一步都有一个典型错误。** 分词 → 词表（**只能从训练集建**）→ 编码 → 填充。打印词表大小（训练集约 **1,592**，种子 42 为 1,617；全语料 3,142）、每类样本数（W1 105 / W2 97 / W3 114 / W4 119 / W5 128 / **W6 185**）、段落长度分布（min 20 / p25 26 / **中位 35** / p75 50 / p95 87 / max 285 / **均值 42.1**）。
2. **中文不能按空白分词。** 中文没有空格，`s.split()` 把**整段变成一个词**。实测（本课程中文教材 750 段）：按空白切分 OOV **0.9973**、单例占比 **0.9946**、词表 372、测试 token **375**；字符级 OOV **0.0254**、单例 0.2170、词表 880、测试 token **14 860**。**OOV 差 39 倍**；按空白切分时 375 段测试只有 375 个 token，**每段都变成一个 `<unk>`**。工程做法：先上分词器，不可用时退回**字符级**，**绝不能按空格切**。
3. **四种池化的总账（本实验核心）。** 同一个 LSTM，只换「怎么把 (B,96,96) 压成 (B,96)」这一句：`mean_masked`（**掩码均值**）**0.5027 ± 0.0449**、宏 F1 **0.4774 ± 0.0482**；`packed` 0.4248 ± 0.0360（0.3843 ± 0.0422）；`mean_unmasked`（裸均值）0.3929 ± 0.0684（0.3315 ± 0.0935）；`last_step` **0.2407 ± 0.0040**、宏 F1 **0.0711 ± 0.0095**。**最好与最差差 0.2620（26.2 个点）。** 6 分类随机基线 = **1/6 ≈ 0.1667**，**`last_step` 的宏 F1 低于随机**。掩码的量化价值：**裸均值 → 掩码均值 = +11.0 个点**；**`[-1]` → packed = +18.4 个点**。
4. **解剖那个 bug。** 按长度分桶（种子 42）对比 `packed` / `last_step`：20–29 词（n=38）0.4211 vs **0.1579**；30–49（n=41）0.3902 vs **0.1707**；50–99（n=29）0.4483 vs 0.4138；100–max（n=5）0.6000 vs 0.4000。硬证据：`last_step` 下长度 **≥ 96** 的 5 篇 **0.4000**，**< 96** 的 108 篇 **0.2315**。**长度够的文档没有填充位置，`out[:, -1, :]` 真的指向句末——这排除了「任务太难」的解释，说明模型读到的是填充向量。**（95.58% 的测试文档短于 max_len=96。）
5. **调 `max_len` 不是杠杆。** 48 / 96 / 192 各跑一遍：`packed` **0.4572 / 0.4454 / 0.4454**（波动在 sd 以内）；`last_step` 0.2891 / 0.2389 / 0.2478。**换长度救不了选错的读法。**
6. **本周最重要的诚实结论：正则化救不回来。** 给最好的臂加 Dropout 0.3 + 权重衰减 1e-3：**0.5027 → 0.4672（下降 3.6 个百分点）**，宏 F1 0.4774 → 0.4433，标准差反而从 **±0.0449 扩大到 ±0.0595**。诊断：**瓶颈是 523 个训练段落（数据），不是容量。** 对照第 6 周——那里数据够、模型大，同样两招有效。**同一手段在两个瓶颈下正确答案相反。** 所以 0.5027 是真实成绩、**不是好成绩**，必须如实写。
7. **错分分析（官方重点）。** 混淆矩阵（5 种子合计 **565** 个预测、**240** 个正确、**0.4248**）：非对角几乎全平（每格 **4–22**），没有重灾区；只有 W6 对角明显（93）。各类召回 **W1 0.1750 / W2 0.1867 / W3 0.4235 / W4 0.4778 / W5 0.4211 / W6 0.6643**：**召回随类大小总体上升（Spearman ρ = 0.77，两处小逆序）**（测试样本数 80/75/85/90/95/140），W6 是 W1 的 **3.80 倍**——**这是「模型在学先验，而不是在学内容」的直接证据。** 还要把错分样本**原文**贴出来（种子 42 共 14 篇），至少 3 篇并归类：**短句**（词表负担最重，20 词：真 W4 → 判 W3）、**通用工程句**（哪一周都成立，26 词：真 W1 → 判 W2）、**术语跨周复用**（22 词：真 W6 → 判 W4，段中 17,226 在第 4 周也讲过）。**14 篇里没有一篇是「模型看错了」——这一段属于哪一周，语义上本来就没有唯一答案。**
8. **AI 协同（官方 赋能 落点）。** 让 AI 生成一整条文本处理管道，然后**按检查清单逐条找错**：有没有传 `lengths`（没有 lengths 就既不能掩码也不能打包）？词表是不是在**全量**上建的？有没有 `padding_idx=0`？池化是**掩码均值**还是裸 `mean`？记录表**三列：AI 原代码 / 你改成什么 / 修正前后准确率差**。参考量级：裸均值 → 掩码均值 **+11.0 个点**；`[-1]` → packed **+18.4 个点**。**「我发现了 bug」不算数，要有数字。**
9. **M8 期中检查点（本周额外交付，模块二里程碑 4 分）**：① **能跑的原型**（干净 clone 能跑）② **`DATA.md` v1** ③ **3 页幻灯片**（第 1 页做什么、第 2 页数字、**第 3 页讲失败**）。形式：**当场演示 3 分钟 + 提问 2 分钟**；**不许放录屏、不许用 PPT 动画代替运行**。**第 3 页是重点——只讲成绩的幻灯片按未完成处理。** 它是课程「阶段评审 15 分」里的一块（M4/M8/M12/M16 各 4 分）。

必须点名的坑：词表建在全量数据上（验证/测试 token 泄进训练，分数虚高）；忘了 `padding_idx=0`（填充向量当词训练）；`out.mean(1)` 把填充位置也平均进去（-11.0 个点）；`out[:, -1, :]` 不传长度（-18.4 到 -26.2 个点，且不报错）；只看准确率不看宏 F1（0.2407 的准确率看着还行，宏 F1 0.0711 已经低于随机）；跑一个种子就下结论（测试标准差 0.0449 接近你想证明的差异）；把 AI 生成的管道直接采信（它很可能连 `lengths` 都没传）。

【思政】**以用户为中心：文本分类的错误代价并不对称，指标选择要贴合业务。** 这周的实验就是这句话的算术版——`last_step` 的准确率 **0.2407** 看着还过得去，宏 F1 却只有 **0.0711**，已经低于随机；W1 的召回 **0.1750**、W6 的召回 **0.6643**，**相差 3.80 倍**。如果这个分类器被用来给某一周的学生推荐复习材料，它对小类（W1）近乎失效，对大类（W6）尚可——**错误的代价在不同类别上并不相等**。所以先问「错了会怎样」，再决定报哪个指标：只看总准确率，就是拿多数类的成绩掩盖少数类的失效。**指标不是越漂亮越好，是越贴合用户的实际代价越好。**

## 11. Reference · 参考

- 全部实验数字来源：`scripts/w8_sequence_experiment.py` → `outputs/w8_sequence.json`（4 池化臂 × 5 种子 + `max_len` 扫描 + 长度分桶 + 5 种子混淆矩阵 + 错分样本 + 中文分词对照）；语料事实来源：`scripts/build_text_corpus.py` → `outputs/w8_corpus_facts.json`。**不要手改这些数字，改协议就重跑脚本。**
- 本实验完全基于本课程第 1–6 周自有语料（CC BY-NC-SA 4.0），**不依赖任何外部论文、权重或数据集**；无需引用外部来源。
