# Lab 02 · Data Preparation and Pipelines
> **AI Application Development** · Week 3 Lab (75 min, 课时 5–6) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 3 · CU(3) |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 1 · AI Application Development Foundations and PyTorch (W1–4) |
| **Stack** | Python 3.11, PyTorch 2.x, pandas, NumPy, matplotlib, Git |
| **Dataset** | `defects.csv` (distributed with the lab kit) — 12,480 rows, 12 features, 5 classes |
| **Deliverables** | `data_pipeline.py`, `data_card.md`, `AI_USE.md` entry, ≥ 2 commits |
| **Weight** | Formative: in-class labs (实验 0–13) = 15 marks of the course (this lab is 1/14 of them) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** the six-step data pipeline: raw data → clean → split → Dataset → DataLoader → batches
- **Know** why splitting must happen *before* any step that learns (scaling, imputation, feature selection, augmentation)
- **Know** the four shapes of data leakage and the one question that detects all of them
- **Do** implement a custom `torch.utils.data.Dataset` with `__len__` and `__getitem__`
- **Do** build a `DataLoader` with a justified `batch_size`, `shuffle`, `num_workers` and a fixed `torch.Generator`
- **Do** measure class imbalance and treat it with a sampler or a cost-sensitive loss, reporting the before/after distribution
- **Do** write a Data Card that states provenance, quality issues, and the limits of use

## 2. Before You Start · 课前准备

```bash
python -c "import torch, pandas, numpy, matplotlib; print(torch.__version__)"
```

- [ ] Your `ai-app` environment imports `torch`, `pandas`, `numpy`, `matplotlib` without error
- [ ] `defects.csv` loads and `pd.read_csv("defects.csv").shape` prints `(12480, 13)` (ask the instructor if the file is missing — never substitute another dataset silently)
- [ ] Your capstone repository exists and has at least one commit from Week 2
- [ ] `AI_USE.md` exists in your repository (create it now if it does not)

> **Note on Week 2.** Last week you built a linear model from raw tensors and autograd. This week the model moves to the side: everything you do today is about the data that will feed it. **The pipeline you build today is the pipeline every later week reuses.**

## 3. Lab Tasks · 实验任务

### Part A — Explore and diagnose (10 min)

Load the raw CSV and produce a quality report. Every claim you write must be backed by **one assert or one plot**.

```python
import pandas as pd, numpy as np, torch, matplotlib.pyplot as plt

df = pd.read_csv("defects.csv")
print("shape:", df.shape)                       # (12480, 13)
print(df["label"].value_counts())               # 5 classes, one of them small
print(df["label"].value_counts(normalize=True).round(4))

# missing values, ranked worst first
print(df.isna().mean().sort_values(ascending=False).head(6))

# numeric summary
print(df.describe().T[["mean", "std", "min", "max"]].round(2))
```

Now **verify** each statement you are about to write down:

```python
share = df["label"].value_counts(normalize=True)
assert share.min() > 0.02, "a class is below 2% - reporting it as an edge case"

# duplicates on the natural key
key = ["batch_id", "timestamp"]
n_dup = df.duplicated(subset=key).sum()
print("duplicate rows on the natural key:", n_dup)

# does missingness relate to the label? (a hint that a feature is partly a proxy)
print(df.assign(age_missing=df["age"].isna()).groupby("label")["age_missing"].mean().round(3))
```

> **Checkpoint A** — paste into a Markdown cell: the class shares, the top three missing columns with their rates, the duplicate count, and one sentence per finding stating the **criterion** you used (not "looks wrong" but "missing rate > 2%").
> **Pitfall**: a missing rate of 0 is not evidence that the data is clean. Check duplicates, units and label agreement too.
> **AI use**: you may ask an AI to draft this exploration block. Every statistical claim it makes must be reproduced by your own assert or plot; if one disagrees with your output, trust yours and log it.

### Part B — A reproducible split (12 min)

Choose **random**, **stratified**, **time-based** or **group** — and write down *why that one*.

```python
import torch
from torch.utils.data import Dataset, Subset, random_split

g = torch.Generator().manual_seed(42)          # fixed seed, no global RNG side effects
labels = torch.tensor(df["label"].values, dtype=torch.long)

# stratified: keep the class shares identical in every split
idx = torch.arange(len(df))
parts, shares = [], labels.value_counts(normalize=True).sort_index()
val_frac, test_frac = 0.15, 0.15
for cls in labels.unique().tolist():
    c = idx[labels == cls]
    c = c[torch.randperm(len(c), generator=g)]
    n_tr = int(len(c) * (1 - val_frac - test_frac))
    n_va = int(len(c) * val_frac)
    parts.append((c[:n_tr], c[n_tr:n_tr + n_va], c[n_tr + n_va:]))

train_idx = torch.cat([p[0] for p in parts])
val_idx   = torch.cat([p[1] for p in parts])
test_idx  = torch.cat([p[2] for p in parts])
print(len(train_idx), len(val_idx), len(test_idx))     # ~8736 / 1872 / 1872
```

Report the **size and class ratio of each split** in a 3-row table:

| Split | Rows | Class-3 share | Class-1 share |
|---|---|---|---|
| train | (fill in) | (fill in) | (fill in) |
| val | (fill in) | (fill in) | (fill in) |
| test | (fill in) | (fill in) | (fill in) |

> **Checkpoint B** — the table above, plus two sentences: which strategy you chose and what would have gone wrong with a plain random split on this data.
> **Think**: `batch_id` repeats across rows. What does that tell you about how the rows should be grouped?

### Part C — A custom `Dataset` (15 min)

Two methods is all it takes. Write `src/data/dataset.py`.

```python
class DefectDataset(Dataset):
    """DataFrame -> PyTorch dataset: two methods only."""

    def __init__(self, df, transform=None):
        self.y = torch.tensor(df["label"].values, dtype=torch.long)
        self.x = torch.tensor(
            df.drop(columns=["label"]).values.astype("float32"))
        self.transform = transform          # passed for the training split only

    def __len__(self):
        return len(self.y)                  # the batch count is computed from this

    def __getitem__(self, i):
        x = self.x[i]                       # exactly one sample
        if self.transform is not None:
            x = self.transform(x)
        return x, self.y[i]                 # (features, label)

feat = df.drop(columns=["batch_id", "timestamp"])   # identifiers never enter the model
ds = DefectDataset(feat)
print(len(ds), ds[0][0].shape, ds[0][1].dtype)
```

Then pick up a real bug on purpose and fix it. Delete the `[i]` index in `__getitem__` so it returns a whole column, and look at what the batch shape becomes:

```python
xb, yb = next(iter(torch.utils.data.DataLoader(ds, batch_size=8)))
print(xb.shape)        # expect (8, 11); a wrong shape here means __getitem__ leaked a column
```

> **Checkpoint C** — `len(ds)`, the shape and `dtype` of `ds[0]`, and the batch shape above. State the shape rule: for batch size B and F features, `xb` must be `(B, F)`.
> **Pitfall**: never compute cross-sample statistics (a column mean, a global vocabulary) inside `__getitem__`. That is a statistics fit over the whole dataset and the most common source of leakage in this lab.

### Part D — `DataLoader` and augmentation (13 min)

```python
from torch.utils.data import DataLoader

train_ds = Subset(ds, train_idx)
val_ds   = Subset(ds, val_idx)
test_ds  = Subset(ds, test_idx)

train_loader = DataLoader(train_ds, batch_size=32, shuffle=True, num_workers=4)
val_loader   = DataLoader(val_ds,   batch_size=64, shuffle=False)
test_loader  = DataLoader(test_ds,  batch_size=64, shuffle=False)

xb, yb = next(iter(train_loader))
print(xb.shape, yb.shape, len(train_loader))
```

Record your argument values and the reason for each:

| Argument | Your value | Why |
|---|---|---|
| `batch_size` | | |
| `shuffle` | | |
| `num_workers` | | |
| `generator` | | |

Now add augmentation to the **training split only** and show the comparison:

```python
def add_noise(x):
    return x + 0.01 * torch.randn_like(x)     # light tabular augmentation

ds_aug = DefectDataset(feat, transform=add_noise)
train_ds = Subset(ds_aug, train_idx)          # train: augmented
val_ds   = Subset(ds,     val_idx)            # val/test: never augmented
test_ds  = Subset(ds,     test_idx)
```

> **Checkpoint D** — the argument table above, plus one line: why does `shuffle=False` on the validation loader not change the metric but still help you debug?
> **Pitfall**: `shuffle=True` and `sampler=` are mutually exclusive — passing both raises a `ValueError`.

### Part E — Class imbalance (12 min)

```python
import torch.nn as nn
from torch.utils.data import WeightedRandomSampler

y_tr = labels[train_idx]
counts = torch.bincount(y_tr, minlength=5)
print("counts:", counts.tolist())
print("shares:", [round(x, 4) for x in (counts / counts.sum()).tolist()])

# option 1 - resample: rarer class gets a bigger weight
w = (1.0 / counts.float())[y_tr]
sampler = WeightedRandomSampler(weights=w, num_samples=len(w), replacement=True)
balanced_loader = DataLoader(train_ds, batch_size=32, sampler=sampler)

# option 2 - cost-sensitive loss: leave the data alone
criterion = nn.CrossEntropyLoss(weight=1.0 / counts.float())
```

Whichever option you choose, re-measure. Report the **before/after** class shares in the sampled batches:

| Class | Share in train | Share in batches after sampling |
|---|---|---|
| 0 | | |
| 3 (minority) | | |
| 4 | | |

> **Checkpoint E** — the before/after table, which option you chose, and one sentence on the trade-off (what did you give up to help the minority class?).
> **Pitfall**: accuracy is useless here. If one class is 4%, a model that always predicts the majority still reads 0.96. Switch to per-class recall, F1 or AUPRC.

### Part F — Data Card, privacy and the capstone push (13 min)

Write `data_card.md`. Section 5 is not optional:

```markdown
# Data Card - defects-v1

## 1. Provenance and compliance
- Source: <internal line export> · internal licence · collected 2026-09
- De-identified: employee and device IDs removed; never uploaded to public tools

## 2. Scale and structure
- 12,480 samples · 12 features · 5 classes
- Split train 70% / val 15% / test 15% (seed=42, stratified - classes are imbalanced)

## 3. Quality and known issues
- Missing: age 3.2% -> imputed with the training median
- Outliers: clipped to the 1/99 percentiles
- Duplicates: de-duplicated on batch_id + timestamp, 812 rows removed

## 4. Augmentation and imbalance
- Class 3 is only 4.1% -> WeightedRandomSampler (with replacement)
- Train: Gaussian noise; val/test: no augmentation

## 5. Bias and limits of use
- All samples come from a single production line; do not extrapolate to other plants
```

**Capstone milestone M3 · Data pipeline in place.** Push before the lab ends:

- `src/data/` with `load.py`, `clean.py`, `split.py` and your custom `Dataset`
- `src/train.py` that runs a single epoch against your `DataLoader` and prints the loss
- No absolute paths — a fresh clone must run without edits
- `requirements.txt` pinned; `data_card.md` (or the same content inside `DATA.md`) committed

> **Checkpoint F** — `python src/train.py` runs on a fresh clone and prints a loss; the Data Card is pushed and its section 5 names at least one real limitation.
> **Pitfall**: a milestone pushed next week is a milestone you did not do — −2 project points per miss, capped at −20.

## 4. Deliverables Checklist · 交付清单

- [ ] `src/data/dataset.py` with a `Dataset` subclass implementing `__len__` and `__getitem__`
- [ ] `data_pipeline.py` that runs end to end: load → clean → split → `Dataset` → `DataLoader`
- [ ] Split strategy justified in writing, with the seed, sizes and class ratios of all three splits
- [ ] `DataLoader` arguments tabulated with a reason for each value
- [ ] Augmentation applied to the training split only, with a before/after comparison
- [ ] Class imbalance measured, treated, and re-measured (before/after shares reported)
- [ ] `data_card.md` with all five sections including bias and limits of use
- [ ] `AI_USE.md` entry naming one AI statistical claim that your own check falsified
- [ ] ≥ 2 meaningful commits pushed (`feat: ...` style messages)

## 5. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Exploration & diagnosis (Part A) | 15 | every claim backed by an assert or a plot; criteria stated numerically, not by feel |
| Reproducible split (Part B) | 15 | fixed seed, strategy justified for *this* data, three splits reported with class ratios |
| Custom `Dataset` (Part C) | 20 | both methods implemented, shapes and dtypes verified, no cross-sample statistics inside `__getitem__` |
| `DataLoader` & augmentation (Part D) | 15 | every argument justified; augmentation confined to the training split |
| Imbalance (Part E) | 15 | measured, treated, re-measured; per-class metrics used instead of accuracy |
| Data Card & leakage self-check (Part F) | 15 | five sections present, provenance lawful, bias and limits stated concretely |
| Exit ticket | 5 | all three questions answered in your own words |

Late policy: −10% per day, max 3 days, then 0.

*The capstone milestone (Part F, second half) is not scored here — it is graded under the Capstone Project. Missing it costs −2 project points there.*

## 6. Submission · 提交方式

```bash
git add src/data src/train.py data_pipeline.py data_card.md AI_USE.md
git commit -m "feat: week3 data pipeline, dataset and data card"
git push origin main
```

Then paste your repo URL into the LMS submission box. **A commit hash counts as your timestamp**, not the LMS upload time.

## 7. Exit Ticket · 课后反思 (answer in the last Markdown cell)

1. Name one data problem you found today that you would have missed if you had gone straight to training.
2. Which leakage self-check item would your pipeline have failed before today, and what fixed it?
3. One question you still have about splitting or sampling (the instructor answers the best ones next week).

## 8. 中文摘要

本周实验只有一个目标：把「原始数据 → 批次」这条六步管道真正跑通，并留下一张别人能核查的数据卡片。

三个必须理解的点：

1. **划分必须发生在所有「会学习」的步骤之前**——标准化、填补、特征选择、数据增强的统计量只来自训练集。顺序错了，后面所有数字都不可信。
2. **数据泄漏的判据只有一句话**：这个信息在推理时拿得到吗？拿不到，就不该出现在训练里。测试集混入训练、重复样本跨集合、时序数据随机划分、测试集被反复调参，是四种最常见形态。
3. **`Dataset` 定义「一条样本是什么」（`__len__` + `__getitem__`），`DataLoader` 定义「批次怎么来」**（批处理、打乱、并行加载）。增强只加训练集；不平衡用 `WeightedRandomSampler` 或 `CrossEntropyLoss(weight=...)`，并报告处理前后的类别分布。

常见翻车点：`__getitem__` 返回整列而不是单条样本（`xb` 形状立刻不对）；在 `__getitem__` 里算全量统计（泄漏温床）；`shuffle=True` 与 `sampler=` 同时传（直接报错）；不平衡数据上用 accuracy 下结论；数据卡片漏掉「偏差与使用边界」一节。

思政要点：**尊重数据与隐私，来源合规是底线**。只用获得授权的数据，个人信息先去标识化，不把原始数据上传到公网工具。

- [ ] **Capstone milestone M3** pushed to the project repo (`src/data/` + custom `Dataset`/`DataLoader` runnable — graded under the Capstone, not this lab)
