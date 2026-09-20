# Lab 03 · Modelling with nn.Module and Controlled Ablations
> **AI Application Development (52015CC3BV)** · School of Software (软件学院), Dalian Neusoft University of Information · Week 4 Lab (80 min) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 4 · CU(4) · Module 1 closing week |
| **Duration** | 80 min lab + 10 min quiz & wrap-up |
| **Module** | 1 · AI Application Development Foundations and PyTorch (W1–4) |
| **Stack** | Python 3.11, PyTorch 2.x, NumPy, scikit-learn (dataset generation only), matplotlib, Git |
| **Dataset** | `make_moons` + `make_circles` (1,000 samples each, 2 features, 2 classes) — generated in code, no download |
| **Deliverables** | `model.py`, `ablation.md`, `run_ablation.py`, module-1 quiz sheet, `AI_USE.md` entry, ≥ 2 commits |
| **Weight** | Formative: in-class labs (实验 0–13) = 15 marks of the course (this lab is 1/14 of them) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** why a hidden layer without a non-linear activation is mathematically a linear model
- **Know** why the dataset matters when measuring an activation's effect: a linear model already scores well on `make_moons`, so the decisive test needs data it cannot separate
- **Know** the four common activations and when each is used
- **Know** the `nn.Module` convention: layers in `__init__`, data flow in `forward`, output logits
- **Do** build an MLP with `nn.Module` and compute its parameter count by hand and in code
- **Do** run a controlled experiment where only one variable changes, and tabulate the result
- **Do** read a (train accuracy, validation accuracy) pair as evidence about capacity and overfitting

## 2. Before You Start · 课前准备

```bash
python -c "import torch, sklearn, matplotlib; print(torch.__version__)"
```

- [ ] Your `ai-app` environment imports `torch`, `sklearn`, `matplotlib` without error
- [ ] Week 3 lab pushed: a `DataLoader` that yields `(B, F)` float32 batches
- [ ] Your capstone repository has `src/data/` committed (milestone M3)
- [ ] `AI_USE.md` has at least the Week 3 entry

> **Note on this lab.** Week 3 established that data sets the ceiling. Today you build the model that will try to reach it — and you learn to justify the architecture with **measurements** rather than intuition. Everything you record today becomes the M4 milestone.

## 3. Lab Tasks · 实验任务

### Part A — Build an MLP with `nn.Module` (15 min)

Put the datasets and the split in place first. From here on, **the split and the seed never change again** — that is what makes the whole lab comparable.

```python
import torch, torch.nn as nn, numpy as np
from sklearn.datasets import make_moons, make_circles
from sklearn.model_selection import train_test_split

device = "cuda" if torch.cuda.is_available() else "cpu"

def set_seed(s=42):
    torch.manual_seed(s); np.random.seed(s)

def load(kind):
    """Two 2-d, 2-class datasets under one identical protocol."""
    if kind == "moons":
        X, y = make_moons(n_samples=1000, noise=0.25, random_state=42)
    else:                                    # circles: not separable by a straight line
        X, y = make_circles(n_samples=1000, noise=0.10, factor=0.5, random_state=42)
    Xtr, Xva, ytr, yva = train_test_split(X, y, test_size=0.3,
                                          random_state=42, stratify=y)
    t = lambda a, d: torch.tensor(a, dtype=d)
    return (t(Xtr, torch.float32), t(Xva, torch.float32),
            t(ytr, torch.long),    t(yva, torch.long))

MOONS, CIRCLES = load("moons"), load("circles")
```

Now the model. Follow the four rules: layers in `__init__`, data flow in `forward`, shapes commented, output logits.

```python
class MLP(nn.Module):
    def __init__(self, in_dim=2, hidden=(16,), n_class=2, use_relu=True):
        super().__init__()
        layers, prev = [], in_dim
        for h in hidden:                      # hidden=(64, 64) -> two hidden layers
            layers += [nn.Linear(prev, h)]
            layers += [nn.ReLU() if use_relu else nn.Identity()]
            prev = h
        layers += [nn.Linear(prev, n_class)]  # output logits, no softmax
        self.net = nn.Sequential(*layers)

    def forward(self, x):
        return self.net(x)                    # (N, 2) -> hidden -> (N, 2)

model = MLP(hidden=(16,)).to(device)
print(model)
print("params:", sum(p.numel() for p in model.parameters()))   # 2*16+16 + 16*2+2 = 82
```

> **Checkpoint A** — `print(model)` output, the parameter count from code, and your hand calculation `in × out + out` for each `nn.Linear`. The two must agree.
> **Pitfall**: a layer created inside `forward` (or as a module-level global) never appears in `print(model)` and is never updated by the optimiser. If it is not in `print(model)`, it does not exist.

### Part B — With and without activation (18 min)

One flag, everything else identical. Write the function once and call it on both datasets.

```python
def run(data, use_relu, hidden=(8,), epochs=300, lr=1e-2, seed=42):
    Xtr, Xva, ytr, yva = data
    set_seed(seed)
    model = MLP(hidden=hidden, use_relu=use_relu).to(device)
    opt = torch.optim.Adam(model.parameters(), lr=lr)
    crit = nn.CrossEntropyLoss()
    hist = []
    for epoch in range(epochs):
        model.train()
        opt.zero_grad()
        loss = crit(model(Xtr), ytr)
        loss.backward(); opt.step()
        hist.append(loss.item())
    model.eval()                               # dropout/batchnorm off before measuring
    with torch.no_grad():
        acc = (model(Xva).argmax(1) == yva).float().mean().item()
    return acc, hist

for name, data in [("moons", MOONS), ("circles", CIRCLES)]:
    a_on,  h_on  = run(data, use_relu=True)
    a_off, h_off = run(data, use_relu=False)
    print(f"{name:8s} with ReLU {a_on:.3f}   without {a_off:.3f}   "
          f"loss_on {h_on[-1]:.3f}  loss_off {h_off[-1]:.3f}")
```

Reference output for this exact protocol (seed 42, Adam `lr=1e-2`, 300 epochs):

| Dataset | 2-8-2 · with ReLU | 2-8-2 · no activation | final loss, no activation |
|---|---|---|---|
| `make_moons` | 0.953 | 0.890 | 0.322 |
| `make_circles` | 0.980 | 0.473 | **0.693** |

Plot all four loss curves on one axes and keep the figure.

> **Checkpoint B** — the four printed numbers, the four-curve plot, and two sentences answering: **on which dataset does removing the activation change the outcome, and why?**
> **Think 1**: on `make_moons` the two settings differ far less (0.953 vs 0.890, about 6 points) than they do on `make_circles`. Does that mean the activation is unnecessary there? Check what a plain `nn.Linear(2, 2)` scores on the same split before you answer.
> **Think 2**: on `make_circles` the no-activation loss stops at 0.693 = ln 2, the loss of guessing between two classes. The 42 parameters are unchanged between the two runs. What is the only difference, and where does non-linearity come from?
> **Warning**: do not conclude "the activation does not matter" from the moons row alone. A linear model already reaches ≈0.89 on `make_moons`, so that dataset cannot detect the difference. Choosing data on which the effect is visible is part of experiment design.

### Part C — Width ablation (12 min)

Change only the hidden width. Keep `epochs`, `lr`, optimiser, seed and split fixed. Use `make_circles` first — it separates the configurations clearly — then repeat on `make_moons`.

```python
for h in [4, 8, 16, 32, 64, 128]:
    acc, _ = run(CIRCLES, use_relu=True, hidden=(h,))
    n = sum(p.numel() for p in MLP(hidden=(h,)).parameters())
    print(f"2-{h}-2   params={n:5d}   val_acc={acc:.3f}")
```

> **Checkpoint C** — the width table with four columns: configuration, parameters, val accuracy, and one conclusion per row. Note where the gain stops being worth the parameters.

### Part D — Depth ablation (10 min)

Same protocol, one extra hidden layer at a time.

```python
for hidden in [(64,), (64, 64), (64, 64, 64), (256, 256)]:
    acc, _ = run(CIRCLES, use_relu=True, hidden=hidden)
    n = sum(p.numel() for p in MLP(hidden=hidden).parameters())
    print(f"{'-'.join(['2'] + [str(h) for h in hidden] + ['2']):14s} "
          f"params={n:7d}   val_acc={acc:.3f}")
```

> **Checkpoint D** — the depth table. Answer in one sentence: did depth beat width on *this* dataset, and would you expect the same answer on a harder one?

### Part E — Assemble the ablation table (10 min)

Merge Parts B–D into one table. This is the artifact the assignment asks for. Record the dataset for every row — a number without its dataset is not a result.

| Dataset | Configuration | Parameters | Train acc | Val acc | Conclusion |
|---|---|---|---|---|---|
| circles | 2→2 (linear baseline) | 6 | | | |
| circles | 2-8-2 · no activation | 42 | | | |
| circles | 2-8-2 · ReLU | 42 | | | |
| circles | 2-64-2 · ReLU | 322 | | | |
| circles | 2-64-64-2 · ReLU | 4,482 | | | |
| moons | 2→2 (linear baseline) | 6 | | | |
| moons | 2-8-2 · no activation | 42 | | | |
| moons | 2-8-2 · ReLU | 42 | | | |

Then make the whole thing reproducible with one command:

```python
# run_ablation.py
CONFIGS = [("circles 2-8-2 none", "circles", (8,), False),
           ("circles 2-8-2 ReLU", "circles", (8,), True),
           ("circles 2-64-2 ReLU", "circles", (64,), True),
           ("moons   2-8-2 none", "moons",   (8,), False),
           ("moons   2-8-2 ReLU", "moons",   (8,), True)]
DATA = {"moons": MOONS, "circles": CIRCLES}
set_seed(42)
for name, kind, hidden, use_relu in CONFIGS:
    acc, _ = run(DATA[kind], use_relu, hidden)
    print(f"{name:22s} {acc:.3f}")
```

> **Checkpoint E** — `python run_ablation.py` reproduces every number in your table. Record the exact command and the seed in the report.
> **Pitfall**: numbers without a conclusion do not count. Every row needs a sentence saying what it proves.
> **AI use**: ask an AI which architecture it recommends for this data. Then test it as one more row. If your data falsifies the suggestion, that goes into `AI_USE.md` — it is evidence of verification, not a failure.

### Part F — Module 1 milestone M4 and the integrated quiz (13 min)

Two things must leave this room with you.

**1. Module 1 integrated quiz (in class, closed book, 10 min).** Three parts, mirroring the module:

| Part | What you submit | Since |
|---|---|---|
| A · Problem definition sheet | target user, the problem, available data, one success metric, one failure criterion | W1 |
| B · Data pipeline | `src/data/` + custom `Dataset`/`DataLoader`, split ratios in code, leakage self-check done | W3 |
| C · Model v0 | `model.py` following the `nn.Module` convention + parameter count + the ablation table | today |

**2. Capstone milestone M4 · Model v0 (MLP).** Push before the lab ends:

- `src/models/model.py` — an `nn.Module` MLP with a documented `forward`
- `src/train.py` extended to train it on your own `DataLoader` and print train/val metrics
- `experiments/ablation.md` — the table above, on **your** data
- One committed command that reruns every configuration

> **Checkpoint F** — the quiz sheet is complete; `python src/train.py` runs on a fresh clone and prints both train and validation metrics; the ablation table is committed.
> **Pitfall**: a milestone pushed next week is a milestone you did not do — −2 project points per miss, capped at −20.

## 4. Deliverables Checklist · 交付清单

- [ ] `model.py` — `nn.Module` subclass, all layers in `__init__`, `forward` with shape comments, output logits
- [ ] Parameter count printed and matching your hand calculation
- [ ] `ablation.md` — at least 6 rows, each naming its dataset, including a with/without activation pair and width/depth variations
- [ ] Every table row carries a conclusion, not just a number
- [ ] A written answer to the Part B question: on which dataset the activation matters, and why the other dataset cannot show it
- [ ] `run_ablation.py` reproduces every number with one command, seed recorded
- [ ] Four loss curves (2 datasets × with/without activation) saved as one figure
- [ ] `AI_USE.md` entry: what structure the AI suggested, how you tested it, whether the data supported it
- [ ] Module 1 quiz sheet (problem sheet + pipeline + model) handed in
- [ ] ≥ 2 meaningful commits pushed

## 5. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| MLP built to convention (Part A) | 20 | layers in `__init__`, clean `forward`, logits out, parameter count verified two ways |
| With/without activation (Part B) | 20 | both datasets run under one protocol, four curves shown, the 0.693 plateau explained, and the moons null result explained rather than ignored |
| Width ablation (Part C) | 15 | ≥ 4 widths, one variable changed, each row concluded |
| Depth ablation (Part D) | 10 | ≥ 3 depths, same protocol, one-variable discipline respected |
| Ablation table (Part E) | 20 | six columns complete, dataset named per row, one-command reproducibility, seed stated |
| M4 milestone + quiz (Part F) | 10 | model + pipeline + problem sheet all present in the repo |
| Exit ticket | 5 | all three questions answered in your own words |

Late policy: −10% per day, max 3 days, then 0.

*Part F, second half (the capstone milestone and the integrated quiz) is graded under the Capstone / module milestone review. Missing it costs −2 project points there.*

## 6. Submission · 提交方式

```bash
git add src/models src/train.py experiments/ablation.md run_ablation.py AI_USE.md
git commit -m "feat: week4 mlp model and ablation table"
git push origin main
```

Then paste your repo URL into the LMS submission box. **A commit hash counts as your timestamp**, not the LMS upload time.

## 7. Exit Ticket · 课后反思 (answer in the last Markdown cell)

1. Which single number in your ablation table surprised you most, and why?
2. On `make_moons` a linear model already reaches about 0.89, while on `make_circles` it stays at 0.50. Write the sentence you would say to a classmate who claims "our network has a hidden layer, so it is non-linear".
3. One question you still have about activations or initialisation (the instructor answers the best ones next week).

## 8. 中文摘要

本周实验的目标：用一个规范的 `nn.Module` 搭出 MLP，并用**对照实验**而不是直觉来决定它的结构。

三个必须理解的点：

1. **激活函数是非线性能力的唯一来源。** 两层 `Linear` 之间没有非线性时，它们会合并成一次仿射变换。这一点可以直接验证：装上 `nn.Identity()`、训练后把两个权重矩阵相乘，网络输出与「一个 `nn.Linear(2,2)`」的结果完全一致（浮点误差约 1e-7）。
2. **要证明这一点，数据集必须选对。** 在 `make_moons` 上，线性模型本身就能达到约 0.89，所以「有/无激活」两行的差距小得多（0.953 与 0.890，只差约 6 个百分点）——**这个数据集测不出这个效应有多剧烈**。换到 `make_circles`（两类同心圆，一条直线分不开），无激活的那一行损失钉在 0.693（= ln 2，二分类瞎猜水平）、准确率掉到 0.473，而加上 ReLU 后升到 0.980——同参数量下差 51 个百分点。**同一个实验，换数据才有信号**——这本身就是实验设计的一部分。
3. **`nn.Module` 规范不是形式主义。** 层必须在 `__init__` 里创建并赋给 `self`，`forward` 只描述张量怎么流过去，输出是 logits（`CrossEntropyLoss` 里已含 softmax）。层写在 `forward` 里或作为全局变量，参数不会被优化器更新——而且不报错，这是最危险的一种错。

参数量的口径（与官方课件一致）：`nn.Linear(in, out)` 永远是 `in × out + out`；2-8-2 = 42、2-64-2 = 322、2-64-64-2 = 4,482、2-256-256-2 = 67,074。

常见翻车点：在 `forward` 里新建层；层没注册到 `self`；输出又手工加了一次 softmax；评估前忘记 `model.eval()`；全零初始化让隐藏单元永远对称，等于每层只有一个神经元在学（ReLU 配 kaiming 初始化）；**以及只在一个测不出差异的数据集上做对照，就下结论**。

思政要点：**反对形式主义——模型结构不是越复杂越好，适用才是最好。** AI 生成的结构建议只是**待验证的假设**，必须用你自己的对照实验来证实或证伪。

- [ ] **Capstone milestone M4** pushed to the project repo (model v0 + `experiments/ablation.md` — graded under the Capstone, not this lab)
