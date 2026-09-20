# Lab 04 · Training Loop, Loss and Optimizer — the 3 × 3 controlled experiment
> **AI Application Development** · Week 5 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末
>
> Official lab number: **实验 4** (this is the Week 5 lab). Module 2 opens here.

| | |
|---|---|
| **Week / 周次** | 5 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 2 · Core Deep Learning: Techniques and Model Training (Week 5–8) — first week |
| **Stack** | Python 3.11, PyTorch 2.x, scikit-learn (`load_digits`), matplotlib |
| **Dataset** | `sklearn.datasets.load_digits` — 1,797 samples × 64 raw pixel features, 10 classes (ships with scikit-learn, no download) |
| **Deliverables** | `lab-05.ipynb` + `train_sweep.py`, the 3 × 3 hyper-parameter table, loss/accuracy curves, one "does not converge" debugging log |
| **Weight** | Formative: in-class labs (实验 0–13) = 15 marks of the course (this lab is 1/14 of them) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** which loss to use for multi-class, binary and regression tasks, and why a `WithLogits` loss must never be handed a probability
- **Know** how SGD, SGD + momentum and Adam differ in *what they do to the gradient* before the step
- **Know** how the learning rate shows up in a loss curve — explosion, oscillation, crawl — and what the curve looks like when it is right
- **Do** write the five-step training loop from memory: zero grads → forward → loss → backward → step
- **Do** run a controlled 3 optimizers × 3 learning rates experiment where exactly two variables change and everything else is pinned
- **Do** read nine runs of evidence and defend one winning combination with numbers rather than preference

## 2. Before You Start · 课前准备

```bash
python -c "import torch, sklearn, matplotlib; print(torch.__version__)"
```

- [ ] Week 4 lab committed (baseline locked; metric chosen)
- [ ] `import torch` works in the `ai-app` environment — no `ModuleNotFoundError`
- [ ] Chapter 5.1–5.5 read (loss, optimizers, learning rate, the training loop)
- [ ] **Pencil and paper out.** Part A requires you to write before you type.

**Device line** (same as Week 4 — keep it at the top of the notebook):

```python
import torch
device = torch.device("mps" if torch.backends.mps.is_available()
                      else "cuda" if torch.cuda.is_available() else "cpu")
print("using", device)
```

## 3. Lab Tasks · 实验任务

### Part A — Write the five steps from memory (8 min)

**Close the slides. Do not look at Part B yet.** Write the five steps of a PyTorch training loop on paper, with the exact method call for each one and the order they must run in.

When you are done, compare with this page of the deck: **slide p17** (the flow diagram). Score yourself honestly and write one sentence next to any step you got wrong.

> **Checkpoint A** — your handwritten five steps, photographed or typed into a Markdown cell, with the corrected version beside it.
> **Pitfall**: the step people drop is step 1, `optimizer.zero_grad()`. If you dropped it, say so — this is the single most common bug in the course.

**Why step 1 matters.** PyTorch *accumulates* gradients into `.grad` by default; it does not overwrite them. Run this and watch the number grow:

```python
import torch, torch.nn as nn
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

X, y = load_digits(return_X_y=True)
Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
Xtr = torch.tensor(Xtr, dtype=torch.float32); ytr = torch.tensor(ytr, dtype=torch.long)

net = nn.Sequential(nn.Linear(64, 64), nn.ReLU(), nn.Linear(64, 10))
opt = torch.optim.SGD(net.parameters(), lr=1e-2)
crit = nn.CrossEntropyLoss()

for step in range(3):
    loss = crit(net(Xtr[:64]), ytr[:64])
    loss.backward()                    # NO zero_grad() anywhere
    total = sum(p.grad.abs().sum().item() for p in net.parameters())
    print(f"step {step}: |grad| summed over all params = {total:.2f}")
    opt.step()
```

Expected output — the gradients never reset, so the sum keeps climbing:

```
step 0: |grad| summed over all params = 11.78
step 1: |grad| summed over all params = 23.58
step 2: |grad| summed over all params = 35.39
```

Now add `opt.zero_grad()` as the **first** line inside the loop and run it again. The three numbers become comparable. That is the whole point of step 1.

> **Checkpoint A2** — both runs' output pasted, plus one sentence: what did the accumulated version do to the effective learning rate?

### Part B — One honest training run (14 min)

Build the model, the loss and the optimizer once, and write the training loop with a log. This is the code you will reuse for the whole rest of the semester.

```python
import torch
import torch.nn as nn
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

torch.manual_seed(42)                       # same init, same batch order, every run


def load_data():
    """1,797 handwritten digits, 64 raw pixel features each, 10 classes."""
    X, y = load_digits(return_X_y=True)
    Xtr, Xva, ytr, yva = train_test_split(
        X, y, test_size=0.2, random_state=42, stratify=y)
    as_t = lambda a, dt: torch.tensor(a, dtype=dt)
    return (as_t(Xtr, torch.float32), as_t(ytr, torch.long),
            as_t(Xva, torch.float32), as_t(yva, torch.long))


class Net(nn.Module):
    def __init__(self, n_in=64, n_hidden=64, n_out=10):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(n_in, n_hidden), nn.ReLU(),
            nn.Linear(n_hidden, n_out))     # raw logits out
    def forward(self, x):
        return self.net(x)                  # NO softmax here — see the pitfall below


def make_optimizer(name, model, lr):
    if name == "sgd":
        return torch.optim.SGD(model.parameters(), lr=lr)
    if name == "momentum":
        return torch.optim.SGD(model.parameters(), lr=lr, momentum=0.9)
    if name == "adam":
        return torch.optim.Adam(model.parameters(), lr=lr)
    raise ValueError(f"unknown optimizer: {name}")


def train(model, opt, crit, Xtr, ytr, Xva, yva, epochs=30, bs=64):
    """The five-step loop, once per batch; one log row per epoch."""
    hist = {"train_loss": [], "val_loss": [], "val_acc": []}
    for epoch in range(epochs):
        model.train()
        running, seen = 0.0, 0
        for i in range(0, Xtr.shape[0], bs):
            xb, yb = Xtr[i:i + bs], ytr[i:i + bs]
            opt.zero_grad()                 # 1 clear last batch's gradients
            logits = model(xb)              # 2 forward pass
            loss = crit(logits, yb)         # 3 compute the loss
            loss.backward()                 # 4 backpropagate
            opt.step()                      # 5 update the parameters
            running += loss.item() * xb.size(0)
            seen += xb.size(0)
        hist["train_loss"].append(running / seen)

        model.eval()                        # eval mode: no dropout/BN updates
        with torch.no_grad():               # no graph: we are not training now
            v = model(Xva)
            hist["val_loss"].append(crit(v, yva).item())
            hist["val_acc"].append((v.argmax(1) == yva).float().mean().item())
    return hist


Xtr, ytr, Xva, yva = load_data()
crit = nn.CrossEntropyLoss()                # softmax is INSIDE — do not add one

torch.manual_seed(42)
model = Net()
opt = make_optimizer("adam", model, 1e-3)
hist = train(model, opt, crit, Xtr, ytr, Xva, yva, epochs=30)

for e in range(0, 30, 5):
    print(f"epoch {e:2d}  train_loss {hist['train_loss'][e]:.4f}  "
          f"val_loss {hist['val_loss'][e]:.4f}  val_acc {hist['val_acc'][e]:.4f}")
```

The instructor's reference run prints this shape — yours should look similar, not identical:

```
epoch  0  train_loss 2.0264  val_loss 1.2740  val_acc 0.6306
epoch  5  train_loss 0.1822  val_loss 0.1785  val_acc 0.9583
epoch 10  train_loss 0.1142  val_loss 0.1244  val_acc 0.9722
epoch 15  train_loss 0.0706  val_loss 0.1002  val_acc 0.9750
epoch 20  train_loss 0.0455  val_loss 0.0864  val_acc 0.9778
epoch 25  train_loss 0.0291  val_loss 0.0792  val_acc 0.9778
```

> **Checkpoint B** — the log table for this single run, and one sentence: is the gap between train loss and val loss growing? What would a growing gap mean (Week 4 answer)?

**Pitfall 1 — softmax done twice.** `nn.CrossEntropyLoss` already applies `log_softmax` internally. Feed it probabilities and it normalises them a second time. There is no error message; the loss just falls more slowly.

```python
logits = model(Xtr[:64])
p = torch.softmax(logits, dim=1)

print("CE(logits)          =", round(nn.CrossEntropyLoss()(logits, ytr[:64]).item(), 4))
print("CE(softmax(logits)) =", round(nn.CrossEntropyLoss()(p,     ytr[:64]).item(), 4))
# CE(logits)          = 2.2865     <- correct, raw logits
# CE(softmax(logits)) = 2.3002     <- wrong, quietly worse
```

The gap looks small on an untrained model. Let it train for 30 epochs and the two curves separate by tens of accuracy points. **Rule: if a loss name contains `WithLogits`, or is `CrossEntropyLoss`, pass raw logits.**

**Pitfall 2 — a missing `zero_grad()`.** Already reproduced in Part A. Symptom to recognise later: the loss curve is jagged and unrelated to the epoch number.

> **Checkpoint B2** — write the two pitfalls in your own words, one sentence each. These go into your notebook's Markdown cells, not into your head.

### Part C — The 3 × 3 grid: the actual experiment (25 min)

Now the controlled experiment. **Nine runs: 3 optimizers × 3 learning rates.** Exactly two variables change; the data, the split, the network, the batch size, the epoch count and the initial weights are all pinned.

| | `lr=1e-1` | `lr=1e-3` | `lr=1e-5` |
|---|---|---|---|
| **SGD** | run 1 | run 2 | run 3 |
| **SGD + momentum (0.9)** | run 4 | run 5 | run 6 |
| **Adam** | run 7 | run 8 | run 9 |

```python
import json

crit = nn.CrossEntropyLoss()
results = []                                # one dict per run

for name in ["sgd", "momentum", "adam"]:
    for lr in [1e-1, 1e-3, 1e-5]:
        torch.manual_seed(42)               # identical weights for every run
        model = Net()
        opt = make_optimizer(name, model, lr)
        hist = train(model, opt, crit, Xtr, ytr, Xva, yva, epochs=30)

        results.append({
            "optimizer": name,
            "lr": lr,
            "min_val_loss": min(hist["val_loss"]),
            "max_val_acc": max(hist["val_acc"]),
            "final_train_loss": hist["train_loss"][-1],
            "first_train_loss": hist["train_loss"][0],
            "history": hist,
        })
        r = results[-1]
        print(f"{name:9s} lr={lr:<6g} min_val_loss={r['min_val_loss']:.3f} "
              f"max_val_acc={r['max_val_acc']:.3f} "
              f"train {r['first_train_loss']:.2f}->{r['final_train_loss']:.2f}")

with open("grid_results.json", "w") as f:   # evidence, not a screenshot
    json.dump([{k: v for k, v in r.items() if k != "history"} for r in results], f, indent=2)
```

> **Checkpoint C** — all nine lines printed. Before moving on, answer in writing: which runs did **not** converge, and what is the symptom of each?

The instructor's reference run (same code, same seed) gives this table. Your numbers will differ slightly — machine, PyTorch version and thread count all move the last digit. **Do not copy these numbers into your submission.**

| # | Optimizer | lr | Min val loss | Max val acc | Verdict |
|:--:|---|---|---:|---:|---|
| 1 | SGD | 1e-1 | 0.209 | 0.944 | converges, but below the winner |
| 2 | SGD | 1e-3 | 0.434 | 0.906 | converging too slowly for 30 epochs |
| 3 | SGD | 1e-5 | 2.853 | 0.153 | crawls — loss barely moves |
| 4 | SGD + momentum | 1e-1 | 1.701 | 0.300 | **diverges** — train loss rises 2.13 → 2.31 |
| 5 | SGD + momentum | 1e-3 | 0.116 | 0.972 | converges well |
| 6 | SGD + momentum | 1e-5 | 1.871 | 0.364 | crawls |
| 7 | Adam | 1e-1 | 1.612 | 0.361 | **unstable** — first loss already 7.35 |
| 8 | **Adam** | **1e-3** | **0.076** | **0.983** | **best on both metrics** |
| 9 | Adam | 1e-5 | 2.220 | 0.239 | crawls |

Three things worth noticing in that table, and you should be able to explain all three:

1. **`1e-1` is not "too large" in the abstract.** Plain SGD survives it (run 1, 0.944), while momentum diverges on it (run 4). The safe threshold is a property of the *optimizer and the data*, not a universal constant.
2. **Momentum amplifies.** It accumulates direction, which is exactly what you want at `1e-3` (run 5 beats run 2) and exactly what destroys you at `1e-1` (run 4 beats nothing).
3. **Adam at `1e-3` wins here.** Adaptive per-parameter steps buy real speed on this problem — and cost roughly twice the optimizer-state memory, which matters later when batch size meets VRAM.

> **Think**: run 1 (SGD, `1e-1`) reaches 0.944 and run 5 (momentum, `1e-3`) reaches 0.972. Which of the two would you *ship*, if training took 10 hours instead of 10 seconds? Write your answer down — it is exactly the kind of question the W16 defence asks.

### Part D — Curves, the verdict, and one debugging log (15 min)

**(a) Plot.** One figure for loss, one for accuracy. Put each combination on shared axes with a labelled legend.

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
for r in results:
    label = f"{r['optimizer']} lr={r['lr']:g}"
    axes[0].plot(r["history"]["val_loss"], label=label)
    axes[1].plot(r["history"]["val_acc"], label=label)

axes[0].set(xlabel="epoch", ylabel="val loss", title="Validation loss")
axes[1].set(xlabel="epoch", ylabel="val accuracy", title="Validation accuracy")
for ax in axes:
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("curves.png", dpi=150)
```

Nine curves on one axes is unreadable. **Also produce three "small multiples" figures**: one per optimizer, three learning rates each. That is the figure that actually answers the question.

**(b) State the winner and argue it.** Not "Adam felt better" — a claim with numbers:

> The best combination is **Adam with `lr = 1e-3`** (run 8): minimum validation loss **0.076** and maximum validation accuracy **0.983**, both the best of the nine runs. It wins because Adam keeps a per-parameter running estimate of the gradient's first and second moments, so each weight gets its own effective step size. On a 64-dimensional input where some pixels vary far more than others, that rescaling removes the need to hand-tune one global learning rate. The runner-up (momentum at `1e-3`, run 5: loss 0.116, accuracy 0.972) has the same inertia but a single global step size, so it advances slower on the directions that need a different scale.

Notice what that argument contains: **a number, a comparison, and a mechanism**. Your version needs all three.

**(c) One "training does not converge" log.** Pick the worst run — run 4 (momentum, `1e-1`) or run 7 (Adam, `1e-1`) — and write the investigation in this exact order. Follow the diagnostic helper:

```python
import math

def diagnose(hist):
    """First question is always the learning rate. Then data. Then code."""
    first, last = hist["train_loss"][0], hist["train_loss"][-1]
    if math.isnan(last) or math.isinf(last):
        return "loss is nan/inf     -> lr far too large; divide by 10"
    if last > first:
        return "loss is RISING      -> lr too large; divide by 10"
    if abs(last - first) < 0.05:
        return "loss is FLAT        -> lr too small; multiply by 10"
    return "loss is FALLING      -> now look at the val curve for overfitting"

for r in results:
    print(f"{r['optimizer']:9s} lr={r['lr']:<6g} -> {diagnose(r['history'])}")
```

Then write the log as four labelled lines, in this order:

```
Symptom      : val accuracy stuck at 0.300; train loss rises 2.13 -> 2.31 over 30 epochs
Hypothesis 1 : learning rate too large for momentum          -> test: same config at lr=1e-3
Evidence     : run 5 (same optimizer, lr=1e-3) reaches 0.972; run 4 does not  -> CONFIRMED
Hypothesis 2 : if lr=1e-3 also failed, check the five-step order and the labels
Conclusion   : momentum accumulates the previous gradients (momentum=0.9), so it
               effectively triples the step length; 1e-1 is stable for plain SGD
               and fatal for momentum. Fix: lr=1e-3, or keep 1e-1 with momentum<=0.5.
```

> **Checkpoint D** — `curves.png`, the small-multiples figures, the written verdict (number + comparison + mechanism), and the four-line debugging log.

### Part E — Wrap up (5 min)

Fill in your own version of the 3 × 3 table in a Markdown cell, answer the exit ticket, and confirm the notebook runs clean: `Kernel → Restart & Run All`.

### Part F — Capstone milestone (10 min) · 大作业里程碑

> **M5 · Training loop + optimizer × learning-rate comparison table** — see [`projects/capstone/milestones.md`](../../projects/capstone/milestones.md) for the full table.

**Apply this week's skill:** this is the first week your project gets a *real* trainer. Until now your baseline came from a library call. Now you own the loop.

**Push to your project repo before the lab ends:**

- `src/train.py` — a training script with the five-step loop, a per-epoch log, and a command that reproduces it.
- The **optimizer × learning-rate comparison table** from this lab, re-run on *your* project's data and *your* project's metric. Same split and same seed as the W4 baseline.
- One row per experiment, one sentence per row on why it was kept or dropped.
- A `DEVLOG.md` entry for W5.

> **Checkpoint F** — the comparison table exists in the repo with at least three rows, each row changing exactly one thing, and the best row named. *"None of them beat the baseline, and here is what the curves say"* is an acceptable submission. Silence is not.
> **Pitfall**: a milestone you push next week is a milestone you did not do. Late = −2 project points, each time, up to −20.

## 4. Deliverables Checklist · 交付清单

- [ ] `lab-05.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Handwritten five steps (Part A) transcribed into a Markdown cell, with corrections marked
- [ ] Both pitfalls reproduced and explained in your own sentences (Part A + B)
- [ ] All **nine** runs of the 3 × 3 grid executed, output visible, saved to `grid_results.json`
- [ ] Loss and accuracy curves plotted — at least one shared-axes figure **and** the per-optimizer small multiples
- [ ] The winning combination named, with validation loss, validation accuracy and a mechanism
- [ ] One four-line "does not converge" debugging log (symptom → hypothesis → evidence → conclusion)
- [ ] Pushed to GitHub with **≥ 2 meaningful commits** (`feat: ...` style messages)

## 5. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Five-step loop from memory (Part A) | 15 | all five steps correct and in order; the missing `zero_grad()` reproduced and explained |
| Single honest run + logging (Part B) | 15 | loop is correct, log has one row per epoch with train and val, softmax pitfall reproduced with both numbers |
| The 3 × 3 grid (Part C) | 30 | nine genuine runs, only optimizer and lr varied, results tabulated, non-converging runs identified with their symptom |
| Curves and the verdict (Part D) | 20 | readable figures with legends; winner stated with number + comparison + mechanism; failing runs named |
| Debugging log (Part D) | 10 | four labelled lines, learning rate checked first, evidence compared against a control run |
| Exit ticket | 10 | three questions answered in your own words |

Late policy: −10% per day, max 3 days, then 0.

*Part F (the capstone milestone) is not scored here — it is graded under the Capstone Project (35%). Missing it costs −2 project points there.*

## 6. Submission · 提交方式

```bash
git add lab-05.ipynb train_sweep.py grid_results.json curves.png
git commit -m "feat: complete lab 04 (training loop, 3x3 optimizer x lr grid)"
git push origin main
```

Then paste your repo URL into the LMS submission box. **A commit hash counts as your timestamp**, not the LMS upload time.

## 7. Exit Ticket · 课后反思 (answer in the last Markdown cell)

1. Which of the nine runs surprised you most, and was it a surprise because of what you expected or because of what the deck told you to expect?
2. Your AI assistant suggested a hyper-parameter combination. Did your run confirm it? Which part of its suggestion had no basis you could verify?
3. One question you still have about the training loop (the instructor reads these and answers the best ones next week).

## 8. 中文摘要

**实验 4（第 5 周）**：写出完整训练循环，并用 **3 种优化器 × 3 组学习率 = 9 次运行**做一次真正的对照实验。

四个必须拿到手的东西：

1. **五步法要能默写**：`zero_grad()` → 前向 → 计算损失 → `backward()` → `step()`。顺序不可交换，第一步最常被漏。漏掉它，梯度会跨批次累加——实测三次迭代的梯度绝对值从 11.78 涨到 35.39。
2. **损失函数收原始 logits**。`CrossEntropyLoss` 内含 softmax，先做一次 softmax 就是做了两次：不报错，只是损失下降变慢、准确率上不去。
3. **学习率的"过大"没有普适标准**。本次实测里，`lr=1e-1` 对纯 SGD 能跑（准确率 0.944），对 Momentum 直接发散（准确率 0.300、训练损失从 2.13 升到 2.31）。所以"异常先查学习率"要连着一起查**优化器和数据尺度**。
4. **最优组合必须用数据说话**。本次参考运行里 Adam + `lr=1e-3` 最优（最低验证损失 0.076、最高验证准确率 0.983）；Momentum + `1e-3` 次之（0.116 / 0.972）。理由是 Adam 给每个参数各自的步长，而 Momentum 只有一个全局步长。你自己的 9 组实测才是你的证据。

排查一次不收敛的顺序：**先查学习率 → 再查数据（标签、尺度、划分）→ 最后查代码（五步顺序）**。这四行（现象 / 假设 / 证据 / 结论）就是"训练不收敛排查记录"要交的东西。

大作业里程碑 **M5**：把训练循环搬进 `src/train.py`，并在自己的项目数据上重跑这张优化器 × 学习率对照表。

- [ ] **Capstone milestone** pushed to the project repo (Part F — graded under the Capstone, not this lab)
