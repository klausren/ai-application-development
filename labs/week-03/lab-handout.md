# Lab 02 · Data Preparation and Pipelines

> **AI Application Development (52015CC3BV)** · School of Software (软件学院), Dalian Neusoft University of Information · Week 3 Lab (80 min) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 3 · CU(3) |
| **Duration** | 80 min lab + 10 min quiz & wrap-up |
| **Module** | 1 · AI Application Development Foundations and PyTorch (W1–4) |
| **Stack** | Python 3.11, PyTorch 2.x, pandas, NumPy, matplotlib, Git |
| **Dataset** | `data/raw/defects.csv` (in this repo) — 12,480 rows, 13 columns, 5 classes |
| **Deliverables** | `src/data/clean.py`, `src/data/dataset.py`, `data_pipeline.py`, `data_card.md`, `AI_USE.md` entry, ≥ 2 commits |
| **Weight** | Formative: in-class labs (实验 0–13) = 15 marks of the course (this lab is 1/14 of them) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** the six-step data pipeline: raw data → clean → split → Dataset → DataLoader → batches
- **Know** the one dividing line that decides whether a cleaning step may run before the split: *does it need a statistic fitted on the data?*
- **Know** why splitting must happen *before* any step that learns (imputation, clipping, scaling, feature selection, augmentation)
- **Know** the four shapes of data leakage and the one question that detects all of them
- **Do** find six planted defects in a table — missing values, duplicates on the natural key, two units in one column, sensor-fault outliers, inconsistent category codes, label noise — and fix each with a **stated criterion**, not by eye
- **Do** implement a custom `torch.utils.data.Dataset` with `__len__` and `__getitem__`
- **Do** build a `DataLoader` with a justified `batch_size`, `shuffle`, `num_workers` and a fixed `torch.Generator`
- **Do** measure class imbalance and treat it with a sampler or a cost-sensitive loss, reporting the before/after distribution
- **Do** write a Data Card that states provenance, quality issues, and the limits of use

## 2. Before You Start · 课前准备

```bash
python -c "import torch, pandas, numpy, matplotlib; print(torch.__version__)"
python -c "import pandas as pd; print(pd.read_csv('data/raw/defects.csv').shape)"
```

- [ ] Your `ai-app` environment imports `torch`, `pandas`, `numpy`, `matplotlib` without error
- [ ] `data/raw/defects.csv` loads and prints `(12480, 13)` (it ships **inside this repo** — nothing to download, so a dead network cannot stop this lab; never substitute another dataset silently)
- [ ] Your capstone repository exists and has at least one commit from Week 2
- [ ] `AI_USE.md` exists in your repository (create it now if it does not)

> **Note on Week 2.** Last week you built a linear model from raw tensors and autograd. This week the model moves to the side: everything you do today is about the data that will feed it. **The pipeline you build today is the pipeline every later week reuses.**

> **This table is dirty on purpose.** `defects.csv` was generated with six defects planted in it. Your job is to find them with a criterion rather than by eye, and to know which of them may be fixed before the split and which may not. The reference run for every number in this handout is `scripts/w3_reference_pipeline.py`.

## 3. Lab Tasks · 实验任务

### Part A — Explore and diagnose (8 min)

Load the raw CSV and produce a quality report. Every claim you write must be backed by **one assert or one plot**.

```python
import pandas as pd, numpy as np, torch, matplotlib.pyplot as plt

df = pd.read_csv("data/raw/defects.csv")
print("shape:", df.shape)                       # (12480, 13)
print(df["label"].value_counts())               # 5 classes, one of them small
print(df["label"].value_counts(normalize=True).round(4))

# missing values, ranked worst first
print(df.isna().mean().sort_values(ascending=False).head(6))

# numeric summary
print(df.describe().T[["mean", "std", "min", "max"]].round(2))
```

Then **verify** each statement you are about to write down. An assert records a **fact you checked**, not a fact you hoped for:

```python
share = df["label"].value_counts(normalize=True).sort_index()
print(share.round(4))
# assert the fact, do not assert your wish: this says "no class is empty"
assert share.min() > 0.0, "a class has zero rows - the export is truncated"
if share.min() < 0.05:
    print(f"smallest class share {share.min():.4f} -> treat it as the rare class")

# duplicates on the natural key
key = ["batch_id", "timestamp"]
n_dup = df.duplicated(subset=key).sum()
print("duplicate rows on the natural key:", n_dup)      # 812

# does missingness relate to the label? (a hint that a feature is partly a proxy)
print(df.assign(age_missing=df["age"].isna()).groupby("label")["age_missing"].mean().round(4))
```

Look carefully at the last two lines of `describe()`. One column has a maximum that the other rows cannot explain. Write down the criterion you would use to decide whether it is a real reading or a unit error — Part B will ask you to act on it.

> **Checkpoint A** — paste into a Markdown cell: the class shares, the top three missing columns with their rates, the duplicate count, the age-missing rate per class, and one sentence per finding stating the **criterion** you used (not "looks wrong" but "missing rate > 2 %").
> **Pitfall**: a missing rate of 0 is not evidence that the data is clean. Check duplicates, units and label agreement too.
> **Pitfall**: an extreme value is not automatically an error. A stuck sensor and a genuine rare event look identical in a table — the next Part is about telling them apart with a rule.
> **AI use**: you may ask an AI to draft this exploration block. Every statistical claim it makes must be reproduced by your own assert or plot; if one disagrees with your output, trust yours and log it.

### Part B — Clean the raw table: the steps that need no statistic (12 min)

Some cleaning steps are **rules**. They transform each row on its own and never look at the other rows, so they may run before the split. There are three of them here.

**B1 — De-duplicate on the natural key.**

```python
before = len(df)
df = df.drop_duplicates(subset=["batch_id", "timestamp"], keep="first").reset_index(drop=True)
print(before, "->", len(df))                    # 12480 -> 11668
assert before - len(df) == n_dup, "the rows you removed must equal the rows you counted"
```

That assert is the whole discipline of cleaning: **the number you predicted must equal the number the code removed.** If they differ, one of the two numbers is wrong.

**B2 — Unify the unit.**

```python
mask_f = df["temperature_c"] > 120              # your criterion, stated numerically
print("rows recorded in Fahrenheit:", int(mask_f.sum()))     # 935
print("max before:", round(df["temperature_c"].max(), 2))    # 214.01
df.loc[mask_f, "temperature_c"] = (df.loc[mask_f, "temperature_c"] - 32) * 5 / 9
print("max after :", round(df["temperature_c"].max(), 2))    # 108.94
assert df["temperature_c"].max() < 120
```

Do **not** delete these rows. They are correct measurements written in the wrong unit — the number is a fact, the label `_c` was wrong.

**B3 — Unify the category coding, then encode it.**

```python
print(sorted(df["material_code"].unique()))
# ['A-2','A1','A2','B-2','B1','B2','C1','a1','b1','c1'] -> ten spellings of five codes

df["material_code"] = df["material_code"].str.upper().str.replace("-", "", regex=False)
print(sorted(df["material_code"].unique()))     # ['A1','A2','B1','B2','C1']

# a string column makes astype("float32") fail outright - encode it while you are here
df["material_code"] = df["material_code"].map({"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4})
assert df["material_code"].notna().all()
```

> **Checkpoint B** — one table with a row per defect you fixed:

| Defect | Rows affected | Action taken | Criterion used |
|---|---|---|---|
| Duplicates | | | |
| Unit mixed in one column | | | |
| Category coding inconsistent | | | |

> **Pitfall**: `drop_duplicates` on the wrong key silently removes *different* rows. `batch_id` alone would collapse ~10 legitimate rows of the same batch into one. The key is `batch_id + timestamp`.
> **Pitfall**: do not "clean" the Fahrenheit rows by clipping them to the column maximum. That destroys real information and hides the bug from the next person.
> **AI use**: ask an AI for the detection rule for each defect. Then check the rule against your own output: if it reports a count you cannot reproduce, keep yours and write the disagreement into `AI_USE.md`.

### Part C — Split first, then clean with training-only statistics (15 min)

Here is the dividing line the whole week turns on.

| Cleaning step | Needs a statistic? | May run before the split? |
|---|---|---|
| De-duplicate, unify units, unify codes, encode | no — a rule per row | **yes** |
| Impute a missing value, clip to a percentile, standardise | yes — a number fitted on data | **no, and only from train** |

Choose **random**, **stratified**, **time-based** or **group** — and write down *why that one*. For this table the answer is not free: `batch_id` repeats, and one batch contributes about ten rows.

```python
from torch.utils.data import Dataset, Subset, random_split

g = torch.Generator().manual_seed(42)          # fixed seed, no global RNG side effects
labels = torch.tensor(df["label"].values, dtype=torch.long)

# stratified: keep the class shares identical in every split
idx = torch.arange(len(df))
parts = []
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
print(len(train_idx), len(val_idx), len(test_idx))      # 8165 1747 1756
```

Now finish the cleaning. **Measure first, then act** — the order matters, because imputing moves the statistics you are about to compare:

```python
train = df.iloc[train_idx]

# 1. measure the leak BEFORE you act on it
full_median  = df["age"].median()               # 6.4886  <- fitted on everything
train_median = train["age"].median()            # 6.4861  <- the honest one
print(f"{full_median:.4f} vs {train_median:.4f}",
      f"-> {abs(full_median-train_median)/train_median*100:.3f} %")

# 2. now impute, with the training median only
med = train[["age", "pressure_kpa", "humidity_pct"]].median().round(4)
print(med.to_dict())
# {'age': 6.4861, 'pressure_kpa': 314.3376, 'humidity_pct': 45.7531}
df[["age", "pressure_kpa", "humidity_pct"]] = df[["age", "pressure_kpa", "humidity_pct"]].fillna(med)

# 3. clip outliers to the training 1st/99th percentile
lo, hi = train["thickness_mm"].quantile([0.01, 0.99])
print(round(lo, 4), round(hi, 4))               # 1.5743 2.1827
df["thickness_mm"] = df["thickness_mm"].clip(lo, hi)
assert df[["age", "pressure_kpa", "humidity_pct"]].isna().sum().sum() == 0
```

The gap is **0.039 %**. If you swap those two lines, nothing crashes and the metric barely moves. Compare medians, means and percentiles for the four numeric columns and fill in the table:

| Column | Statistic | Full data | Train only | Relative gap |
|---|---|---|---|---|
| age | median | | | |
| pressure_kpa | mean | | | |
| humidity_pct | median | | | |
| thickness_mm | 99th pct | | | |

Then restrict the same comparison to the rare class (`df["label"] == 3`, 479 unique rows, 335 of them in train). The gap grows to **0.44 %–1.23 %** — an order of magnitude larger. **Data quantity decides how loud a leak is**, and the class you care most about is exactly the one with the least data.

> **Checkpoint C** — the 3-row split table (rows and class ratios), the strategy you chose and what a plain random split would have broken given that `batch_id` repeats, **plus** the two comparison tables above and one sentence: why is "the numbers look about right" not a defence against leakage?
> **Think**: `batch_id` repeats across rows. What does that tell you about how the rows should be grouped?
> **Pitfall**: the full-data median is not "more accurate". It is fitted on rows you are about to call test data, so your reported score no longer describes a real deployment.
> **Pitfall**: imputing before splitting is the single most common leak in student projects — it is one line of code in the wrong place.

### Part D — A custom `Dataset` (13 min)

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
print(len(ds), ds[0][0].shape, ds[0][1].dtype)      # 11668 torch.Size([10]) torch.int64
```

Ten features, not thirteen: `batch_id` and `timestamp` are identifiers, and `label` is the target. If that number is not 10, a column leaked in or was dropped by accident.

Then pick up a real bug on purpose and fix it. Delete the `[i]` index in `__getitem__` so it returns a whole column, and look at what the batch shape becomes:

```python
xb, yb = next(iter(torch.utils.data.DataLoader(ds, batch_size=8)))
print(xb.shape)        # expect (8, 10); a wrong shape here means __getitem__ leaked a column
```

> **Checkpoint D** — `len(ds)`, the shape and `dtype` of `ds[0]`, and the batch shape above. State the shape rule: for batch size B and F features, `xb` must be `(B, F)`.
> **Pitfall**: never compute cross-sample statistics (a column mean, a global vocabulary) inside `__getitem__`. That is a statistics fit over the whole dataset and the most common source of leakage in this lab.
> **Pitfall**: `astype("float32")` fails outright on a string column. If you skipped the encoding in Part B, the error surfaces here, far from its cause.

### Part E — `DataLoader` and augmentation (11 min)

```python
from torch.utils.data import DataLoader

train_ds = Subset(ds, train_idx)
val_ds   = Subset(ds, val_idx)
test_ds  = Subset(ds, test_idx)

train_loader = DataLoader(train_ds, batch_size=32, shuffle=True, num_workers=0)
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

train_idx = train_idx.clone()                 # indices are positions in df, unchanged
ds_aug = DefectDataset(feat, transform=add_noise)
train_ds = Subset(ds_aug, train_idx)          # train: augmented
val_ds   = Subset(ds,     val_idx)            # val/test: never augmented
test_ds  = Subset(ds,     test_idx)
```

> **Checkpoint E** — the argument table above, plus one line: why does `shuffle=False` on the validation loader not change the metric but still help you debug?
> **Pitfall**: `shuffle=True` and `sampler=` are mutually exclusive — passing both raises a `ValueError`.
> **Pitfall**: augmentation must never touch validation or test. If your validation score moves when you change the augmentation, you have already leaked.

### Part F — Class imbalance (10 min)

```python
import torch.nn as nn
from torch.utils.data import WeightedRandomSampler

y_tr = labels[train_idx]
counts = torch.bincount(y_tr, minlength=5)
print("counts:", counts.tolist())               # [2771, 2276, 1801, 335, 982]
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
| 3 (rare) | | |
| 4 | | |

> **Checkpoint F** — the before/after table, which option you chose, and one sentence on the trade-off (what did you give up to help the rare class?).
> **Pitfall**: accuracy is useless here. Class 3 is 4.1 % of the rows, so a model that always predicts the majority still reads about 0.96. Switch to per-class recall, F1 or AUPRC.
> **Pitfall**: oversampling with `replacement=True` duplicates rows. If those duplicates end up in a validation split you are back to Part C's problem with a different name.

### Part G — Data Card, privacy and the capstone push (11 min)

Write `data_card.md`. Section 5 is not optional:

```markdown
# Data Card - defects-v1

## 1. Provenance and compliance
- Source: <internal line export> · internal licence · collected 2026-09
- De-identified: employee and device IDs removed; never uploaded to public tools

## 2. Scale and structure
- 11,668 unique rows (12,480 raw, 812 duplicates on batch_id+timestamp removed)
- 10 features · 5 classes · split train 70% / val 15% / test 15% (seed=42, stratified)

## 3. Quality and known issues
- Missing: age 3.2%, pressure_kpa 1.1%, humidity_pct 0.6% -> training median
- Missingness is class-dependent: age is absent in 25% of class 3 rows vs ~2.3% elsewhere,
  so `age` is partly a proxy for the label - do not trust it as a neutral feature
- Unit mixed: 935 temperature readings recorded in Fahrenheit, converted to Celsius
- Outliers: 35 thickness readings from a stuck sensor, clipped to the training 1st/99th pct
- Category coding: material_code appeared in 10 spellings, normalised to 5 codes
- Label noise: approximately 2% of labels are believed wrong; not corrected

## 4. Augmentation and imbalance
- Class 3 is only 4.1% -> WeightedRandomSampler (with replacement)
- Train: Gaussian noise; val/test: no augmentation

## 5. Bias and limits of use
- All samples come from a single production line; do not extrapolate to other plants
- Label noise (~2%) bounds the accuracy any model can reach on this table
```

**Capstone milestone M3 · Data pipeline in place.** Push before the lab ends:

- `src/data/` with `load.py`, `clean.py`, `split.py` and your custom `Dataset`
- `src/train.py` that runs a single epoch against your `DataLoader` and prints the loss
- No absolute paths — a fresh clone must run without edits
- `requirements.txt` pinned; `data_card.md` (or the same content inside `DATA.md`) committed

> **Checkpoint G** — `python src/train.py` runs on a fresh clone and prints a loss; the Data Card is pushed and its section 5 names at least one real limitation.
> **Pitfall**: a milestone pushed next week is a milestone you did not do — −2 project points per miss, capped at −20.

## 4. Deliverables Checklist · 交付清单

- [ ] `src/data/clean.py` performing the three rule-based steps, each with a stated criterion and a before/after count
- [ ] `src/data/dataset.py` with a `Dataset` subclass implementing `__len__` and `__getitem__`
- [ ] `data_pipeline.py` that runs end to end: load → clean → split → impute/clip → `Dataset` → `DataLoader`
- [ ] Split strategy justified in writing, with the seed, sizes and class ratios of all three splits
- [ ] Imputation and clipping fitted on the training split only, with the full-data-vs-train comparison table
- [ ] `DataLoader` arguments tabulated with a reason for each value
- [ ] Augmentation applied to the training split only, with a before/after comparison
- [ ] Class imbalance measured, treated, and re-measured (before/after shares reported)
- [ ] `data_card.md` with all five sections including bias and limits of use
- [ ] `AI_USE.md` entry naming one AI statistical claim that your own check falsified
- [ ] ≥ 2 meaningful commits pushed (`feat: ...` style messages)

## 5. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Exploration & diagnosis (Part A) | 12 | every claim backed by an assert or a plot; criteria stated numerically, not by feel |
| Cleaning (Part B) | 18 | all three rule-based defects found; predicted and removed counts match; units converted rather than clipped |
| Split & training-only statistics (Part C) | 18 | fixed seed, strategy justified for *this* data (grouping), statistics fitted on train only, comparison table filled |
| Custom `Dataset` (Part D) | 18 | both methods implemented, shapes and dtypes verified, no cross-sample statistics inside `__getitem__` |
| `DataLoader` & augmentation (Part E) | 12 | every argument justified; augmentation confined to the training split |
| Imbalance (Part F) | 12 | measured, treated, re-measured; per-class metrics used instead of accuracy |
| Data Card (Part G) | 5 | five sections present, provenance lawful, bias and limits stated concretely |
| Exit ticket | 5 | all three questions answered in your own words |

Late policy: −10% per day, max 3 days, then 0.

*The capstone milestone (Part G, second half) is not scored here — it is graded under the Capstone Project. Missing it costs −2 project points there.*

## 6. Submission · 提交方式

```bash
git add src/data src/train.py data_pipeline.py data_card.md AI_USE.md
git commit -m "feat: week3 data pipeline, cleaning drill and data card"
git push origin main
```

Then paste your repo URL into the LMS submission box. **A commit hash counts as your timestamp**, not the LMS upload time.

## 7. Exit Ticket · 课后反思 (answer in the last Markdown cell)

1. Name one data defect you found today that you would have missed if you had gone straight to training.
2. Which of the six planted defects could only be fixed *after* the split, and why?
3. The full-data median and the training median differed by 0.039 %. Does that make the leak harmless? Defend your answer (the instructor answers the best ones next week).

## 8. 中文摘要

本周实验只有一个目标：把「原始数据 → 批次」这条六步管道真正跑通，并留下一张别人能核查的数据卡片。**这份 `defects.csv` 是故意做脏的**，里面预埋了六类缺陷。

三个必须理解的点：

1. **划分必须发生在所有「会学习」的步骤之前**——填补、截断、标准化、特征选择、数据增强的统计量只来自训练集。顺序错了，后面所有数字都不可信。判据只有一句话：**这一步用到的数字，是在哪些行上算出来的？**
2. **清洗动作要按「是否需要统计量」分成两组**。去重、单位换算、编码统一是**逐行规则**，可以在划分前做；缺失填补、异常值截断、标准化**必须**在划分后、只用训练集。把两组混在一起写，泄漏就进来了。
3. **数据泄漏的判据只有一句话**：这个信息在推理时拿得到吗？拿不到，就不该出现在训练里。测试集混入训练、重复样本跨集合、时序数据随机划分、测试集被反复调参，是四种最常见形态。

**本周六类预埋缺陷与判据**：重复行（主键 `batch_id + timestamp`，812 条）；温度单位混用（`temperature_c > 120` 实为华氏，935 条）；材料编码不一致（`A-2`/`a1` 等 10 种写法对应 5 个编码）；传感器异常值（`thickness_mm` 卡死，35 条）；缺失值（age 3.2%、pressure_kpa 1.1%、humidity_pct 0.6%）；标签噪声（约 2%）。**每一类都要写出数值判据，并让「预测删除数」等于「实际删除数」**。

**最该记住的一件事**：全量中位数与训练集中位数只差 **0.039 %**。也就是说，**你把那两行代码写反了，程序不报错、指标几乎不动**。只有把比较范围缩到少数类（3 类，训练集仅 335 条）时，差距才放大到 0.44 %–1.23 %。**泄漏不会自己喊出来**——防住它靠的是写代码时定好顺序，而不是事后看数字对不对。

常见翻车点：`__getitem__` 返回整列而不是单条样本（`xb` 形状立刻不对）；在 `__getitem__` 里算全量统计（泄漏温床）；`shuffle=True` 与 `sampler=` 同时传（直接报错）；不平衡数据上用 accuracy 下结论；数据卡片漏掉「偏差与使用边界」一节；把华氏温度当成异常值直接删掉。

思政要点：**尊重数据与隐私，来源合规是底线**。只用获得授权的数据，个人信息先去标识化，不把原始数据上传到公网工具。同时要**如实报告发现的缺陷**——包括自己没能修好的那部分（如标签噪声），不为了让结果好看而删掉不利的数据。

- [ ] **Capstone milestone M3** pushed to the project repo (`src/data/` + custom `Dataset`/`DataLoader` runnable — graded under the Capstone, not this lab)
