# Lab 06 · Convolutional Neural Networks for Image Classification — 1,898 parameters, and what they actually buy
**AI Application Development (52015CC3BV)** · School of Software, Dalian Neusoft University of Information · Week 7 Lab (80 min) · English with Chinese summary at the end · 中文摘要见文末

**Official lab number: 实验 6** (this is the Week 7 lab). Module 2, week 3 of 4.
**Course map entry: `7.3 实验 6：CNN 图像分类完整实战（课内实践）` — 1.0 学时**, delivered inside the course's 80-minute in-class practical.

| | |
|---|---|
| **Week / 周次** | 7 · CU(7) CNNs for Computer Vision · Module 2 (Week 5–8) |
| **Duration** | 80 min lab (10 min intro + 70 min hands-on) |
| **Module** | 2 · Core Deep Learning: Techniques and Model Training (Week 5–8) |
| **Stack** | Python 3.11, PyTorch 2.x, scikit-learn, matplotlib — **100 % offline** |
| **Dataset** | `sklearn.datasets.load_digits` — 8×8 grayscale, 10 classes, **1,797** samples. Ships inside scikit-learn, so it exists the moment `import sklearn` succeeds. No download, no cache, nothing to fetch. |
| **Protocol** | `conv(1→8,k3,p1)+ReLU+MaxPool2` → `conv(8→16,k3,p1)+ReLU+MaxPool2` → FC 10 (**1,898** parameters, `cnn`) · Adam(lr=1e-3) · batch 64 · **120 epochs** · seeds 42–46 (mean ± sd) |
| **Deliverables** | `lab-07.ipynb` + `w7_cnn_lab.py` + `arms.json` + the five-arm table + training curves + confusion matrix + error case gallery + the AI memory-optimisation record + ≥ 2 commits |
| **Weight** | Formative, in-class labs (实验 0–13). This is the lab behind the official assessment row `CNN 与序列模型的搭建与调优` — not a highlighted topic, but **a difficulty point worth 6 % of the final course mark**, assessed through the lab report. |

## 1. Learning Objectives · 学习目标

This lab covers the three teaching objectives of the unit, and nothing that is not one of them:

1. **Understand convolution and pooling.** 理解卷积与池化。
2. **Build and train a CNN for image classification.** 能够搭建并训练 CNN 完成图像分类任务。
3. **Handle GPU memory problems.** 能够处理 GPU 训练中的显存不足等常见问题。

By the end of the lab you will be able to:

- **Know** what a convolution layer buys relative to a fully connected one, and what it costs — by **counting parameters yourself**, not by repeating the sentence "CNNs use weight sharing"
- **Know** that `out = (in + 2p − k) / s + 1` is checked against real tensors in this lab, and that shape bugs are the most common and cheapest-to-eliminate failure in deep learning
- **Know** how the receptive field grows stage by stage (**3 → 4 → 8 → 10**), and why on an 8×8 image the **second convolution (RF = 8) already sees the whole picture** — there is no more translation invariance to extract at this size
- **Know** that pooling is a **design decision**, not an incantation: swapping max pooling for average pooling costs **4.1 points** with the parameter count held fixed
- **Do** build the model, train it over **at least 3 seeds**, and report **mean ± sd** — never a single number
- **Do** run two controlled ablations (max vs average pooling; with vs without augmentation) and read the result as a trade, not as a score
- **Do** measure translation robustness by shifting the test images ± 1 and ± 2 columns and explain why the fully connected network degrades fastest
- **Do** open the confusion matrix, name the worst class pair, **draw the misclassified digits themselves**, and say — with evidence — *why the model is worse on certain classes* (the official post-class task)
- **Do** measure peak memory as a function of batch size, and reproduce a large batch by gradient accumulation — then find out which scaling rule is actually correct
- **Do** ask an AI for a memory-optimisation checklist, then **test every item** and mark each one effective / ineffective / harmful with the evidence

## 2. Before You Start · 课前准备

```bash
python -c "import torch, sklearn, matplotlib; print(torch.__version__)"
```

- [ ] Lab 05 committed (you own the training loop; this lab extends it from vectors to images)
- [ ] `import torch` works in the `ai-app` environment — no `ModuleNotFoundError`
- [ ] Textbook read: 《动手学深度学习（PyTorch 版）》corresponding chapters on convolution, padding and stride, pooling, and convolutional networks (LeNet)
- [ ] Pen and paper for Part A — you will hand-compute the parameter count **before** the code prints it

**Device line** (keep it at the top of the notebook):

```python
import torch
device = torch.device("mps" if torch.backends.mps.is_available()
                      else "cuda" if torch.cuda.is_available() else "cpu")
print("using", device)
```

### This week has zero downloads · 本周全程离线

`load_digits` is a `.csv.gz` that ships inside the scikit-learn package. There is no MNIST, no CIFAR, no HuggingFace checkpoint and no TensorBoard — nothing to download, nothing to cache, nothing that fails when the campus proxy is down. This is deliberate: the course does not depend on third-party data sources or their licences. Prove it in ten seconds, before writing any model code:

```python
from sklearn.datasets import load_digits
X, y = load_digits(return_X_y=True)
print(X.shape, X.dtype, X.min(), X.max(), len(set(y)))
# (1797, 64) float64 0.0 16.0 10
```

**Reference run.** The instructor's full experiment lives in `scripts/w7_cnn_experiment.py`, and its output is committed as `outputs/w7_cnn.json` (5 architectures × 5 seeds, plus the shift probe, the confusion matrix, the gradient-accumulation probe and the memory sweep). Every reference number in this handout comes from that file. Re-generate it with:

```bash
python scripts/w7_cnn_experiment.py
```

You may reproduce the tables from `w7_cnn.json`, but you must **also** run your own training — a table copied from the reference file is evidence about the instructor's run, not about yours. If your environment cannot import torch at all, you may fall back to the JSON for Parts A, B, E, F and G, and you must say so in one sentence in the report. What is not optional is the interpretation.

### The one protocol, fixed for all five arms

Change exactly one thing per arm. If you touch any knob below, your rows stop being comparable and the lab produces no evidence.

| Knob | Value |
|---|---|
| Dataset | `load_digits`, pixels `/ 16.0` → 0–1, kept as 8×8 images (not flattened) |
| Split | 70 / 15 / 15, stratified, `random_state = seed`; `n_train ≈ 1258`, `n_val = n_test = 270` |
| CNN | `conv(1→8,k3,p1)+ReLU+MaxPool2` → `conv(8→16,k3,p1)+ReLU+MaxPool2` → `Linear(64,10)` |
| MLP (control) | `64 → 128 → 64 → 10`, ReLU, raw logits |
| Optimizer | `Adam(lr=1e-3)`, `batch_size=64`, `epochs=120`, no weight decay |
| Seeds | 42, 43, 44, 45, 46 — every arm repeated, reported as mean ± sd |
| Augmentation | random ± 1 px shift, **training batches only** |

Shared bootstrap for every part below:

```python
import json, random, statistics as st
import numpy as np
import torch
import torch.nn as nn
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.metrics import confusion_matrix

SEEDS  = (42, 43, 44, 45, 46)
EPOCHS = 120
BATCH  = 64
LR     = 1e-3


def set_seed(seed):
    random.seed(seed); np.random.seed(seed); torch.manual_seed(seed)


def get_data(seed):
    """70/15/15 stratified. The exact recipe used in Lab 05, so the MLP row in
    this lab is directly comparable to last week's numbers."""
    X, y = load_digits(return_X_y=True)
    X = (X / 16.0).astype(np.float32)                  # 0..15 -> 0..1
    Xtr, Xrest, ytr, yrest = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=seed)
    Xva, Xte, yva, yte = train_test_split(
        Xrest, yrest, test_size=0.50, stratify=yrest, random_state=seed)
    t = lambda a, d: torch.tensor(a, dtype=d)
    return (t(Xtr, torch.float32), t(ytr, torch.long),
            t(Xva, torch.float32), t(yva, torch.long),
            t(Xte, torch.float32), t(yte, torch.long))
```

## 3. Lab Tasks · 实验任务

### Part A — Parameter accounting: do the arithmetic by hand, then let the code agree (10 min)

This is the part the official teaching note asks for: *"用参数量对比让学生直观理解卷积的权值共享"*. Fill the table on paper **before** you run the cell.

A convolution layer with kernel `k`, `C_in` input channels and `C_out` output channels has

```
params = k * k * C_in * C_out + C_out        # the second term is the bias
```

```python
class CNN(nn.Module):
    """conv(1->8,3,pad1) ReLU maxpool2 -> conv(8->16,3,pad1) ReLU maxpool2 -> FC 10.
    `pool` and `in_size` are knobs for the ablation and the memory probe; the
    default is the arm under test."""

    def __init__(self, pool=nn.MaxPool2d, in_size=8, fc=10):
        super().__init__()
        self.in_size = in_size
        self.body = nn.Sequential(
            nn.Conv2d(1, 8, 3, padding=1), nn.ReLU(), pool(2),
            nn.Conv2d(8, 16, 3, padding=1), nn.ReLU(), pool(2),
        )
        self.flat = 16 * (in_size // 4) ** 2          # 8x8 -> 4x4 -> 2x2
        self.head = nn.Linear(self.flat, fc)

    def forward(self, x):
        x = self.body(x.view(-1, 1, self.in_size, self.in_size))
        return self.head(x.view(x.shape[0], -1))


class MLP(nn.Module):
    """Last week's network, now trained on the full split instead of 80 images."""

    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(64, 128), nn.ReLU(),
                                 nn.Linear(128, 64), nn.ReLU(),
                                 nn.Linear(64, 10))

    def forward(self, x):
        return self.net(x.view(x.shape[0], -1))


print("conv1", 3 * 3 * 1 * 8 + 8)      # 80
print("conv2", 3 * 3 * 8 * 16 + 16)    # 1168
print("fc   ", 64 * 10 + 10)           # 650
print("total", 80 + 1168 + 650)        # 1898

print("cnn params", sum(p.numel() for p in CNN().parameters()))   # 1898
print("mlp params", sum(p.numel() for p in MLP().parameters()))   # 17226
```

Reference numbers you must land on: **conv1 = 3·3·1·8 + 8 = 80**, **conv2 = 3·3·8·16 + 16 = 1,168**, **FC = 64·10 + 10 = 650**, **total = 1,898**. The MLP is **17,226** — **9.07×** the CNN's parameter count.

**The verdict you are allowed to write.** On the reference run the CNN reaches **0.9808 ± 0.0084** test accuracy with 1,898 parameters; the MLP reaches **0.9785 ± 0.0084** with 17,226. The gap is **0.0023**, which is **smaller than one standard deviation (0.0084)**. Write **"no significant difference was observed"**. Do **not** write "the CNN is more accurate" — the numbers do not support it, and a 9× parameter reduction with no measured accuracy cost is the actual, and much more interesting, result.

Checkpoint A — your hand-computed four numbers, the two `sum(p.numel())` values, and one sentence answering: **what did weight sharing buy, and what did it cost?** (Hint: the cost is not in accuracy on this task; look at Part E.)

### Part B — The arithmetic of shapes, and the receptive field (10 min)

```python
def out_size(size, k, s=1, p=0):
    """out = (in + 2p - k) / s + 1"""
    return (size + 2 * p - k) // s + 1


print([out_size(8, 3, 1, 1), out_size(8, 2, 2, 0)])   # [8, 4]

h = torch.zeros(1, 1, 8, 8)
body = CNN().body
for tag, layer in (("conv1", body[0]), ("pool1", body[2]),
                   ("conv2", body[3]), ("pool2", body[5])):
    h = layer(h)
    print(f"{tag:6s} real tensor {tuple(h.shape[1:])}")
# conv1  real tensor (8, 8, 8)
# pool1  real tensor (8, 4, 4)
# conv2  real tensor (16, 4, 4)
# pool2  real tensor (16, 2, 2)
```

The formula and the real tensors agree on every stage — the shape chain is **`8×8 → conv+P → 8×8 → pool → 4×4 → conv+P → 4×4 → pool → 2×2 → flatten 64 → FC 10`**.

Now grow the receptive field stage by stage. Start at `RF = 1`, `jump = 1`; each layer with kernel `k` and stride `s` updates `RF = RF + (k − 1) · jump` and `jump = jump · s`:

| Stage | k | s | jump after | RF after | feature map |
|---|---|---|---|---|---|
| conv1 | 3 | 1 | 1 | **3** | 8×8 |
| pool1 | 2 | 2 | 2 | **4** | 4×4 |
| conv2 | 3 | 1 | 2 | **8** | 4×4 |
| pool2 | 2 | 2 | 4 | **10** | 2×2 |

Two things follow, and both matter for Part E:

1. **The receptive field sequence is 3 → 4 → 8 → 10.** The final value (10) is larger than the image (8) simply because the input is zero-padded at its borders.
2. **The last convolution already has RF = 8 — the whole 8×8 image.** This architecture therefore *cannot* manufacture any more translation invariance than it already has; the input is simply too small for depth to add anything. On a 224×224 photo the same RMS stack would still be looking at a patch.

Checkpoint B — the four printed tensor shapes, the formula table, and one sentence: at which layer does the receptive field first cover the whole image, and what does that imply about a deeper network on this dataset?

### Part C — Train it: three seeds minimum, mean ± sd, curves (20 min)

```python
def shift_batch(imgs, dx, dy):
    """Zero-filled translation of an (n,1,8,8) batch: the augmentation AND the
    test-time probe share this one function, so a shift means the same thing in
    both places."""
    out = torch.roll(imgs, shifts=(dy, dx), dims=(2, 3))
    if dy > 0:   out[:, :, :dy, :] = 0
    elif dy < 0: out[:, :, dy:, :] = 0
    if dx > 0:   out[:, :, :, :dx] = 0
    elif dx < 0: out[:, :, :, dx:] = 0
    return out


@torch.no_grad()
def evaluate(model, X, y, dx=0, dy=0):
    """Accuracy and logits, ALWAYS in eval mode."""
    model.eval()
    if dx or dy:
        X = shift_batch(X.view(-1, 1, 8, 8), dx, dy).view(X.shape[0], 64)
    out = model(X)
    return (out.argmax(1) == y).float().mean().item(), out


def train_model(seed, arch="cnn", pool=nn.MaxPool2d, aug=False, batch=BATCH,
                accum=1, accum_mode="none", epochs=EPOCHS):
    set_seed(seed)
    Xtr, ytr, Xva, yva, Xte, yte = get_data(seed)
    model = MLP() if arch == "mlp" else CNN(pool=pool)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    g = torch.Generator().manual_seed(seed)
    n = Xtr.shape[0]
    group = batch * accum                      # equivalent batch
    accum_steps = group // batch
    hist = {"train_acc": [], "val_acc": []}

    for ep in range(1, epochs + 1):
        model.train()
        perm = torch.randperm(n, generator=g)
        for g0 in range(0, n, group):
            chunk = perm[g0:g0 + group]
            size = len(chunk)
            opt.zero_grad()
            for m0 in range(0, size, batch):          # micro-batches
                sel = chunk[m0:m0 + batch]
                xb, yb = Xtr[sel], ytr[sel]
                if aug and arch != "mlp":
                    dx = int(torch.randint(-1, 2, (1,), generator=g))
                    dy = int(torch.randint(-1, 2, (1,), generator=g))
                    xb = shift_batch(xb.view(-1, 1, 8, 8), dx, dy).view(-1, 64)
                loss = nn.functional.cross_entropy(model(xb), yb)
                w = (len(sel) / size if accum_mode == "exact"
                     else 1.0 / accum_steps if accum_mode == "naive"
                     else 1.0)
                (loss * w).backward()
            opt.step()
        tr, _ = evaluate(model, Xtr, ytr)
        va, _ = evaluate(model, Xva, yva)
        hist["train_acc"].append(round(tr, 4))
        hist["val_acc"].append(round(va, 4))

    te, logits = evaluate(model, Xte, yte)
    return {"seed": seed, "arch": arch,
            "params": sum(p.numel() for p in model.parameters()),
            "train_acc": hist["train_acc"][-1], "val_acc": hist["val_acc"][-1],
            "test_acc": round(te, 4), "hist": hist,
            "logits": logits, "X_test": Xte, "y_test": yte, "model": model}


rows = [train_model(s) for s in SEEDS]                       # cnn
for r in rows:
    print(f"seed {r['seed']}  train {r['train_acc']:.4f}  "
          f"val {r['val_acc']:.4f}  test {r['test_acc']:.4f}")

test = [r["test_acc"] for r in rows]
print(f"cnn test {st.mean(test):.4f} +- {st.stdev(test):.4f}")
```

Seed 42's training curve, sampled every 6 epochs (reference run):

```
epoch      :   1      7      13     19     25     31     37     43     49     55    ...   115
train acc  : 0.3317 0.8679 0.9181 0.9459 0.9586 0.9722 0.9793 0.9849 0.9905 0.9912 ...  1.0
val acc    : 0.3111 0.8259 0.8852 0.9296 0.9407 0.9556 0.9630 0.9704 0.9667 0.9667 ...  0.9741
```

```python
import matplotlib.pyplot as plt

fig, axes = plt.subplots(1, 2, figsize=(13, 4.5))
h = rows[0]["hist"]
axes[0].plot(h["train_acc"], label="train")
axes[0].plot(h["val_acc"], label="val")
axes[1].plot(h["val_acc"])
axes[0].set(xlabel="epoch", ylabel="accuracy", title="CNN seed 42")
axes[1].set(xlabel="epoch", ylabel="val accuracy", title="Validation, zoomed")
for ax in axes:
    ax.legend(fontsize=8); ax.grid(alpha=0.3)
plt.tight_layout(); plt.savefig("curves_cnn.png", dpi=150)
```

The training curve saturates at 1.000; the validation curve plateaus near 0.974 and stops moving. On this dataset the CNN is **not** the thing that overfits — the training set is large enough that it simply runs out of learning signal.

Reference five-arm ledger (5 seeds, mean ± sd — this is the table your numbers should resemble):

| Arm | Parameters | Train acc | Val acc | **Test acc** |
|---|---|---|---|---|
| `mlp` (64→128→64→10) | 17,226 | 1.0000 ± 0.0000 | 0.9660 ± 0.0084 | **0.9785 ± 0.0084** |
| `cnn` (8/16 ch, MaxPool2d) | **1,898** | 0.9987 ± 0.0009 | 0.9704 ± 0.0101 | **0.9808 ± 0.0084** |
| `cnn_avg` (same, AvgPool2d) | 1,898 | 0.9497 ± 0.0089 | 0.9289 ± 0.0164 | **0.9400 ± 0.0081** |
| `cnn_wide` (16/32 ch + FC 128) | 21,312 | 0.9992 ± 0.0010 | 0.9763 ± 0.0062 | **0.9867 ± 0.0081** |
| `cnn_aug` (8/16 + ±1 px aug) | 1,898 | 0.9535 ± 0.0120 | 0.9385 ± 0.0171 | **0.9504 ± 0.0217** |

Note the last row before you panic in Part D: the wide CNN reaches **0.9867** — genuinely higher — but it has grown to **21,312** parameters, i.e. more than the MLP it was supposed to beat, for **+0.6 points**. A win and a bill.

Checkpoint C — your own `cnn` and `mlp` rows over ≥ 3 seeds with mean ± sd, plus `curves_cnn.png`. Then answer: the CNN's test standard deviation is 0.0084 — how many of the 270 test images is that worth? (One image = 1/270.)

### Part D — Ablation: pooling is a decision, augmentation is a trade (15 min)

```python
def arm_stats(tag, **kw):
    accs = [train_model(s, **kw)["test_acc"] for s in SEEDS]
    print(f"{tag:10s} test {st.mean(accs):.4f} +- {st.stdev(accs):.4f}")
    return accs


maxpool = arm_stats("cnn_max")
avgpool = arm_stats("cnn_avg", pool=nn.AvgPool2d)
aug     = arm_stats("cnn_aug", aug=True)
```

**Ablation 1 — max pooling vs average pooling.** Same architecture, same 1,898 parameters, one line changed:

- `cnn` (max pool): **0.9808 ± 0.0084**
- `cnn_avg` (average pool): **0.9400 ± 0.0081**

That is **4.1 points** for a choice that many students never consciously make. Max pooling keeps the strongest activation in each window, which on a binarised-ish digit image preserves a stroke edge; averaging blurs it away. Pooling is a design decision with a price tag attached.

**Ablation 2 — augmentation.** The augmentation arm adds a random ± 1 px shift to each *training* batch (test images are never shifted at dx = 0):

- `cnn`: **0.9808**
- `cnn_aug`: **0.9504**

Augmentation makes the clean-accuracy number **worse by 3.0 points**. On the training curve it also refuses to reach 1.000 — at epoch 115 it is **0.9292**, i.e. it is *underfitting*, not overfitting. Do not "fix" this by deleting the arm. Part E is where the 3 points get explained.

Checkpoint D — the two comparisons with mean ± sd, and a one-sentence mechanism for each: why does average pooling lose 4.1 points, and what exactly did the augmentation do to the training curve?

### Part E — Translation robustness: where augmentation pays (10 min)

Shift every test image by `dx` columns (zero-filled) and re-measure. Nothing is retrained — this is the same model, a different test set.

```python
def probe(arch, **kw):
    out = {}
    for dx in (-2, -1, 0, 1, 2):
        accs = [evaluate(train_model(s, arch=arch, **kw)["model"],
                         train_model(s, arch=arch, **kw)["X_test"],
                         train_model(s, arch=arch, **kw)["y_test"], dx=dx)[0]
                for s in (42,)]
        out[dx] = round(accs[0], 4)
    return out


print(probe("cnn"))
```

The line above is written for clarity, not efficiency — it retrains for every `(dx, seed)`. In your own notebook, **train once per seed and reuse the returned model** across the five `dx` values (the reference script does exactly this, which is why it does not cost 5× the compute).

Reference results (test accuracy, averaged over seeds):

| Arm | dx = −2 | dx = −1 | **dx = 0** | dx = +1 | dx = +2 |
|---|---|---|---|---|---|
| `mlp` | 0.1667 | 0.4555 | **0.9785** | 0.5089 | 0.1822 |
| `cnn` | 0.2348 | 0.6481 | **0.9808** | 0.6504 | 0.2778 |
| `cnn_aug` | 0.5170 | **0.9415** | **0.9504** | **0.9526** | 0.5518 |

Three readings, all required in your report:

1. **The fully connected network collapses fastest.** At dx = −1 the MLP falls from 0.9785 to **0.4555** — it loses about **47 points**. The CNN at the same shift holds **0.6481** (roughly 66 % of its clean accuracy). Reason: the MLP's first layer is `Linear(64, 128)`, i.e. 64 independent weights per feature, one per pixel position. Move the image one column and every one of those weights is now attached to the wrong pixel. The convolution's kernel, by contrast, is applied at every position, so a shifted stroke still lands on the same weights eventually — the CNN degrades gracefully, the MLP does not degrade at all gracefully.
2. **Augmentation's ledger.** At dx = −1 it takes the CNN from 0.6481 to **0.9415** — it **buys +29 points**. At dx = 0 it takes the CNN from 0.9808 to **0.9504** — it **pays 3 points**. Augmentation did not raise the ceiling; **it flattened the curve**. Whether that is worth it depends entirely on whether your deployment sees shifted inputs.
3. **Notice dx = 0: `cnn_aug` is the lowest of the three.** Augmentation is not a free accuracy button, and a student who reports only the dx = 0 column will conclude — incorrectly — that augmentation is a mistake.

Checkpoint E — the filled table from your own run, and one paragraph: if you were shipping a model that must survive a scanner that misaligns digits by one pixel, which arm do you ship, and what did you pay for it?

### Part F — Error analysis: open the matrix and look at the digits (15 min)

**This is the official focus of the lab.** The post-class task is verbatim: *提交 CNN 实验报告（含错分案例分析）；说明为什么模型在某些类别上表现更差。* "98 %" is not a result; it is an unfinished sentence.

```python
r  = train_model(42)
pred = r["logits"].argmax(1)
cm = confusion_matrix(r["y_test"].numpy(), pred.numpy(), labels=list(range(10)))
print(cm)
print("test", r["test_acc"], " wrong", int((pred != r["y_test"]).sum()))
```

Reference, summed over all five seeds: **1,350** test predictions, **1,324** correct, accuracy **0.9807**, **26** off-diagonal errors — of which **12 involve the digit 8 (46.2 % of all errors)**. The single worst class pair is **8 predicted as 1**, which happens **3 times**. Every one of the 26 errors lives on a "dense / connected strokes" pair such as 8↔1, 8↔9 and 3↔8.

Now draw the wrong ones — this is the step most reports skip:

```python
probs = torch.softmax(r["logits"], 1)
wrong = (pred != r["y_test"]).nonzero(as_tuple=True)[0].tolist()
print("misclassified:", [(int(r["y_test"][i]), int(pred[i])) for i in wrong])

fig, axes = plt.subplots(1, max(len(wrong), 1), figsize=(2.3 * max(len(wrong), 1), 2.8))
for ax, i in zip(np.atleast_1d(axes), wrong):
    ax.imshow(r["X_test"][i].view(8, 8), cmap="gray_r", vmin=0, vmax=1)
    ax.set_title(f"true {int(r['y_test'][i])}\npred {int(pred[i])}"
                 f"\np={probs[i][pred[i]]:.2f}", fontsize=8)
    ax.axis("off")
plt.tight_layout(); plt.savefig("misclassified.png", dpi=150)
```

Seed 42's CNN gets 5 of 270 wrong. Read them as a narrative, not a list:

| true | pred | confidence | probability on the true class |
|---|---|---|---|
| 8 | 7 | 0.9829 | 0.0144 |
| 8 | 1 | 0.9576 | 0.0217 |
| 6 | 8 | 0.8852 | 0.0271 |
| 8 | 2 | 0.6419 | 0.1747 |
| 9 | 8 | 0.6007 | 0.3827 |

Three of the five involve the digit 8. The first two are **confidently wrong** — the model assigns under 2.2 % to the correct answer, which means the pixels it is given genuinely resemble the predicted class more than the labelled one at 8×8 resolution. The last one (9 → 8, confidence 0.60, true probability 0.38) is a **genuine hesitation**: the two candidates are nearly tied, and a tiny perturbation would flip it.

**Answering the official question with evidence, not adjectives.** "The model is worse on some classes" is worth nothing. A defensible sentence looks like this:

The three worst classes, with counts and the reason the pixels justify it —

```python
off = cm.copy(); np.fill_diagonal(off, 0)
pairs = sorted(((int(v), i, j) for i in range(10) for j in range(10)
                if (v := off[i][j])), reverse=True)
for v, i, j in pairs:
    print(f"true {i} -> pred {j}: {v}")
```

For each of the top three pairs, name **what the two digits share and where they differ**, using the drawn image: 8 and 1 share a strong vertical stroke on the right (the 8 of `load_digits` is often drawn with a narrow right loop that reads as a single stroke at 8×8); 8 and 9 share a closed upper loop; 3 and 8 share two right-hand curves. Then state the mechanism: **the information that separates them is high-frequency detail that an 8×8 grid has already averaged away.** That is why the errors are concentrated on that family of pairs and nowhere else.

Checkpoint F — the confusion matrix (as a figure with `imshow` or `ConfusionMatrixDisplay`), the total error count, the worst class pair with its count, the gallery of misclassified digits with true/pred/confidence, and **for at least three top pairs a written explanation that cites specific shared and differing strokes visible in the drawn images**. "Because they are similar" is not an explanation; "both have a closed upper loop, and the only difference is the lower-left stroke, which is 2 pixels wide at this resolution" is.

### Part G — Memory, batch size, and OOM (15 min)

**Peak memory vs batch size.** Measure it in a subprocess, because the process's own baseline dominates otherwise.

```python
import resource, subprocess, sys


def rss_mb():
    # macOS reports ru_maxrss in BYTES; Linux reports kilobytes. Dividing by the
    # wrong power of 1024 silently reports megabytes that are off by 1024x.
    return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 ** 2, 1)


def mem_probe(bs):
    if bs == 0:
        print("baseline (interpreter + torch only):", rss_mb(), "MB")
        return rss_mb()
    model = CNN(in_size=32)                    # 32x32: the 8x8 model is too small to move RSS
    opt = torch.optim.Adam(model.parameters(), lr=1e-3)
    x = torch.randn(bs, 1, 8, 8)
    x = x.repeat_interleave(4, dim=2).repeat_interleave(4, dim=3)   # -> 32x32
    y = torch.randint(0, 10, (bs,))
    for _ in range(3):
        opt.zero_grad()
        nn.functional.cross_entropy(model(x), y).backward()
        opt.step()
    print("batch", bs, "peak", rss_mb(), "MB")
    return rss_mb()
```

Reference sweep (the input is upsampled to 32×32 so the batch-size effect is actually measurable; the model is otherwise unchanged):

| Batch | Peak RSS | Above baseline |
|---|---|---|
| baseline (no training) | **306.5 MB** | — |
| 32 | 390.1 MB | +83.6 MB |
| 64 | 397.8 MB | +91.3 MB |
| 128 | 410.8 MB | +104.3 MB |
| 256 | 436.2 MB | +129.7 MB |
| 512 | 483.0 MB | +176.5 MB |
| 1024 | **582.0 MB** | +275.5 MB |

**Peak memory grows roughly linearly with batch size.** On this laptop nothing gets close to OOM, which is exactly why the discipline must be learned here — on a real model the same linear slope starts from a much larger intercept, and the first thing that happens in a real project is a `CUDA out of memory` traceback.

**Gradient accumulation: buy the large batch, but pay the right price.** When the batch will not fit, you split it into micro-batches and accumulate gradients over several steps. The question the reference run answers is *how to weight them*:

| Mode | Weight applied to each micro-batch | Identical to a single big batch |
|---|---|---|
| `exact` | `w = len(micro-batch) / group_size` | **5 / 5** |
| `naive` | `w = 1 / accum_steps` | **3 / 5** |
| `unscaled` | no scaling, gradients summed | **2 / 5** |
| `none` | no scaling, no reduction | **2 / 5** |

Only `exact` reproduces the large-batch run bit-for-bit on all five seeds. The reason is in the arithmetic, not in the optimizer: **`n_train = 1258` is not divisible by the group size**, so the last micro-batch of every epoch is short (at group size 128 it holds 106 samples, and its final micro-batch holds 10). A fixed `1 / accum_steps` over-weights that short tail; weighting by the actual share `len(sel) / size` does not.

```python
def match_against_big_batch():
    ref = [train_model(s, batch=128, accum=1, accum_mode="none")["test_acc"] for s in SEEDS]
    for mode in ("exact", "naive", "unscaled", "none"):
        got = [train_model(s, batch=32, accum=4, accum_mode=mode)["test_acc"] for s in SEEDS]
        print(f"{mode:9s} {sum(a == b for a, b in zip(got, ref))}/5  {got}")


match_against_big_batch()
```

One honest note to write down: **Adam is fairly insensitive to an overall rescaling of the gradient**, because its second-moment estimate absorbs a constant factor. That is why the `naive` rule still converges to roughly the same accuracy and only misses the bit-exact match. Had this been SGD, the same bug would blow up the effective learning rate by the accumulation factor and the gap would be far larger. "It happened to work with Adam" is not "it is correct".

Checkpoint G — your measured batch-size / peak-memory table (with the baseline row), a statement of whether the growth is linear, the 4-row accumulation table with your match counts, and one sentence naming the source of the mismatch.

### Part H — AI co-pilot: a memory-optimisation checklist you have to test (10 min)

Ask your AI assistant this, with the protocol table pasted into the prompt (not the whole notebook):

**"Given this exact training setup, give me a checklist of ways to reduce GPU memory use, ordered by how much they help and what they cost."**

A generic checklist will almost always contain the following. **Test every item you are given** — including the ones you expect to work — and fill in the verdict with the evidence. This table is the official 赋能 deliverable: *AI 给出显存优化方案 → 学生实测各方案效果与代价，标注有效与无效的建议.*

| AI suggestion | How you test it today | Verdict |
|---|---|---|
| "Reduce the batch size." | Your Part G sweep already measures the slope | *your evidence* — **effective**, but re-read Part G: it also changes the gradient |
| "Use gradient accumulation to keep the effective batch." | Part G's 4-mode table | *your evidence* — **effective** only with `exact` weighting |
| "Use mixed precision (`torch.autocast`)." | Measure peak RSS with and without | *measure it* — at this model size the saving is small and it changes numerics |
| "Switch to `channels_last` memory format." | Measure peak RSS | *measure it* — often **no effect** on CPU / MPS at this size |
| "Delete intermediate tensors / call `torch.cuda.empty_cache()`." | Measure peak RSS | often **ineffective**: peak RSS is peak, not current |
| "Make the model smaller / use fewer channels." | Compare `CNN()` against a narrower variant | **effective**, but you are spending accuracy — read Part C's `cnn_wide` row backwards |
| "Use `torch.no_grad()` for evaluation." | Measure peak RSS during eval | **effective** for eval memory, and you should be doing it anyway |

Write each verdict as three lines: `claim — how you tested it — measured evidence — EFFECTIVE / INEFFECTIVE / HARMFUL`. A real answer with a measured "this did nothing" is worth more than a checklist you never ran. Do not accept "it is generally recommended" as evidence.

Checkpoint H — the filled table above with your own measurements, at least one item marked **INEFFECTIVE** and one marked **HARMFUL** (or a written justification of why nothing in your list was harmful). Commit the table as `ai_memory_optimisation.md`, and put the same table in the report.

### After the lab · 课后作业 (not counted in the 80 min)

1. **CNN experiment report** — the official post-class task: *提交 CNN 实验报告（含错分案例分析）；说明为什么模型在某些类别上表现更差。* Turn the notebook into a written report with one section per Part. It must contain the parameter accounting, the shape and receptive-field tables, the five-arm ledger with mean ± sd, the curves, the confusion matrix, the error gallery, the ablation and shift results, the memory and accumulation tables, and the AI verification table.
2. **One paragraph that is graded on its own**: why the model is worse on certain classes — citing the drawn pixels, not adjectives.

Both are due before the Week 8 lab.

## 4. Deliverables Checklist · 交付清单

- [ ] `lab-07.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Parameter accounting verified in-cell: `80 / 1168 / 650 → 1898`, and `17226` for the MLP (Part A)
- [ ] `w7_cnn_lab.py` — one script that re-runs the full grid and writes `arms.json`
- [ ] `arms.json` — raw per-seed rows for every arm (evidence, not a screenshot)
- [ ] Five-arm ledger with mean ± sd (Part C) and `curves_cnn.png`
- [ ] Ablation table: max vs average pooling (**0.9808 vs 0.9400**, 4.1 points) and with vs without augmentation (**0.9504 vs 0.9808**) (Part D)
- [ ] Translation-robustness table for `mlp`, `cnn`, `cnn_aug` over dx = −2 … +2, with the "why the MLP collapses" paragraph (Part E)
- [ ] `confusion_matrix.png` + `misclassified.png`; total error count, worst class pair with its count, and a written, pixel-level "why these classes" analysis of ≥ 3 pairs (Part F)
- [ ] Batch-size / peak-memory table with the baseline row; 4-row gradient-accumulation table with your match counts (Part G)
- [ ] `ai_memory_optimisation.md` — the AI checklist with a measured verdict and evidence for every item (Part H)
- [ ] Pushed to GitHub with **≥ 2 meaningful commits** (`feat: ...` style messages)
- [ ] *(after the lab)* CNN experiment report including the misclassification analysis

## 5. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Parameter accounting (Part A) | 12 | The four numbers hand-computed **before** the code; `80 / 1168 / 650 / 1898` and `17226` all verified in-cell; the CNN-vs-MLP gap written as **"no significant difference"** with the 0.0023 vs 0.0084 arithmetic shown |
| Shapes and receptive field (Part B) | 12 | Formula checked against real tensors at every stage; the shape chain written out; the RF sequence **3 → 4 → 8 → 10** derived rather than copied; the "RF = 8 already covers the image" implication stated |
| Training, seeds and curves (Part C) | 16 | ≥ 3 seeds run; mean ± sd everywhere; `curves_cnn.png` present; the MLP control row reproduced; one test image = 1/270 discussed |
| Ablation: pooling and augmentation (Part D) | 14 | Both comparisons run with mean ± sd; the **4.1-point** pooling cost reproduced; augmentation reported as *worse* at dx = 0 and labelled underfitting, not hidden |
| Translation robustness (Part E) | 10 | Full dx = −2…+2 table; the MLP collapse quantified (0.9785 → 0.4555); the "+29 points / −3 points" augmentation ledger stated; a ship-decision paragraph |
| **Misclassification analysis (Part F)** | **16** | Confusion matrix drawn; total errors, worst pair (8 → 1, 3 times) and the 8-cluster named; **the misclassified digits drawn with true/pred/confidence**; ≥ 3 pairs explained at pixel level with named shared and differing strokes — **this is the official focus of the lab** |
| Memory, gradient accumulation and OOM (Part G) | 10 | Batch-size / peak-memory table incl. the 306.5 MB baseline; the linear trend stated; the 4-mode accumulation table with match counts; the short-tail mechanism named; the Adam-insensitivity caveat included |
| **AI co-pilot verification record (Part H)** | **10** | Every AI suggestion given a **measured** verdict with the evidence; at least one INEFFECTIVE and one HARMFUL (or a justified explanation); no verdict is "it is generally recommended" |

Late policy: −10 % per day, max 3 days, then 0.

*This rubric mirrors the official assessment row `CNN 与序列模型的搭建与调优` — non-highlighted but a difficulty point, **6 % of the final course mark**, assessed through the lab report. The in-class work is formative; the report is what carries the 6 %.*

## 6. Submission · 提交方式

```bash
git add lab-07.ipynb w7_cnn_lab.py arms.json \
        curves_cnn.png confusion_matrix.png misclassified.png \
        ai_memory_optimisation.md
git commit -m "feat: complete lab 06 (CNN image classification and error analysis)"
git push origin main
```

Then paste your repo URL into the LMS submission box. **A commit hash counts as your timestamp**, not the LMS upload time. Deadline: **TBD by instructor**.

## 7. Exit Ticket · 课后反思 (answer in the last Markdown cell)

1. The CNN matches the MLP's accuracy with **9.07×** fewer parameters. If you stopped at that sentence, what would you be missing? Look at Part E's dx = −1 row for both arms and finish the thought.
2. Augmentation makes the headline number *worse* (0.9808 → 0.9504) and the worst-case number *much better* (0.6481 → 0.9415). **Write down your own criterion** for which of the two arms you would deploy, and then say which number your criterion is actually optimising.
3. Gradient accumulation with `naive` weighting matched the big batch on only **3 of 5** seeds while `exact` matched **5 of 5**. Give the arithmetic reason in one line, then say whether "Adam hid the bug" is an argument for shipping the buggy rule.

## 8. 中文摘要

**实验 6（第 7 周）**：用 **1,898** 个参数搭一个两层卷积网络，把 8×8 手写数字分类做到 **0.9808**，然后回答四个问题：卷积到底买到了什么、池化不同选择值多少分、数据增强的账本怎么算、模型的错分能不能讲清楚。

协议固定不变：`sklearn.datasets.load_digits`（8×8、10 类、1797 张，**随 sklearn 自带，全程零下载**）→ 像素除以 16 → 70/15/15 分层划分（`n_train ≈ 1258`）→ `conv(1→8,k3,p1)+ReLU+MaxPool2 → conv(8→16,k3,p1)+ReLU+MaxPool2 → FC 10` → Adam(lr=1e-3)、batch 64、**120 轮** → **5 个种子（42–46）报均值 ± 标准差**。

七件必须自己做出来的事：

1. **参数对账。** 手算 `conv1 = 3·3·1·8+8 = 80`、`conv2 = 3·3·8·16+16 = 1168`、`FC = 64·10+10 = 650`，合计 **1,898**；对照组 MLP 是 **17,226**，是 CNN 的 **9.07 倍**。两者测试准确率 **0.9808 vs 0.9785**，差 **0.0023**，**小于一个标准差 0.0084** —— 只能写「**未观察到显著差异**」，**不能**写「卷积更准」。省下 9 倍参数而不掉精度，才是这组数字真正的看点。
2. **形状与感受野。** `out = (in+2p−k)/s+1` 与真实张量逐层核对；形状链 `8×8 → 8×8 → 4×4 → 4×4 → 2×2 → flatten 64 → FC 10`；感受野递推 **3 → 4 → 8 → 10**，**最后一层卷积 RF = 8，已经覆盖整张 8×8 图**——这个尺寸下结构再深也榨不出更多平移不变性。
3. **池化是设计选择，不是默认值。** 只把 `MaxPool2d` 换成 `AvgPool2d`，参数量一模一样，测试准确率从 **0.9808 掉到 0.9400**，差 **4.1 个百分点**。
4. **增强是交易，不是加分。** dx=0 时增强臂 **0.9504**，比不增强的 **0.9808** 低 3 个点，训练准确率也不再冲到 1.000（第 115 轮 0.9292）——它**压住了过拟合，同时压住了上限**。真正的好处出现在平移测试里：dx=−1 时 **0.6481 → 0.9415**，**买 +29 个点**。**增强没有抬高上限，它把曲线压平了。**
5. **全连接网络崩得最快。** dx=−1 时 MLP 从 0.9785 掉到 **0.4555**（**掉约 47 个点**），CNN 只到 **0.6481**。原因在结构：MLP 第一层每个像素一个独立权重，图平移一列，权重全部错位；卷积核在每个位置复用同一组权重，笔画挪一格仍然落在同一套核上。
6. **错分分析是本实验的重点。** 5 个种子合计 **1,350** 次测试预测、**1,324** 次正确、准确率 **0.9807**、非对角错误 **26** 个，其中 **12 个与数字 8 有关（占 46.2%）**，最差类对是 **8 被当成 1，出现 3 次**。必须**把错分的数字本身画出来**看：种子 42 的 CNN 在 270 张里错 5 张，其中 3 张涉及 8，两张是「**自信地错**」（如 true 8 → pred 7，置信度 0.9829，正确类概率仅 0.0144），一张是「**犹豫**」（true 9 → pred 8，置信度 0.6007，正确类概率 0.3827）。回答官方问题「为什么模型在某些类别上表现更差」时，要**指认两类数字共享哪一笔、差异在哪一笔**，并指出差异是 8×8 已经抹掉的高频细节——不能只写「因为它们长得像」。
7. **显存与梯度累积。** 实测峰值内存：基线 **306.5 MB**，batch 1024 时 **582.0 MB**，**随 batch 近似线性增长**。梯度累积的四种写法里，只有按「组内实际样本占比」加权的 `exact` 与单次大 batch **5/5 完全一致**；`naive` 3/5、`unscaled` 2/5、`none` 2/5。差异来源是**每个 epoch 最后一组微批大小不等**（`n_train = 1258` 不能被组大小整除）。诚实补一句：**Adam 对整体梯度缩放不敏感**，所以 `naive` 也能大致收敛，换成 SGD 差异会显著放大。

必须点名的坑：把 `size` 写成硬编码（形状对不上还找不到原因）；测试集也做了平移/增强（评估被污染，dx=0 的数字就不是 dx=0 了）；只看 dx=0 就判增强无用（把 Part E 撕掉一半）；只跑一个种子就下结论（测试标准差 0.0084 已经接近你想要证明的差异）；把 AI 给的显存清单一整页抄进报告却一条没实测。

【思政】**绿色计算**：算力是有限资源，要学会用更少的成本达成目标。本周的实验就是这句话的算术版——**1,898 个参数**完成了 17,226 个参数的工作，而盲目的「加宽」（21,312 参数）只换来 0.6 个点。省下来的不是电费，是你下一次实验还能跑得动的时间。

## 9. Reference · 参考

- 全部实验数字来源：`scripts/w7_cnn_experiment.py` → `outputs/w7_cnn.json`（5 架构 × 5 种子 + 平移探针 + 混淆矩阵 + 梯度累积探针 + 内存扫描）。**不要手改这些数字，改协议就重跑脚本。**
- 本实验完全基于 scikit-learn 内置数据集 `load_digits`，**不依赖任何外部论文、权重或数据集**；无需引用外部来源。
