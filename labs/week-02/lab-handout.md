# Lab 01 · Linear Regression with Tensors and Autograd
> **AI Application Development** · Week 2 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 2 |
| **CU** | CU(2) · Module 1 (W1–4) |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 1 · AI Application Development Foundations |
| **Stack** | Python 3.11, PyTorch, matplotlib |
| **Dataset** | Synthetic — generated in the script with a fixed seed |
| **Deliverables** | `lab1_linear_regression.py`, `loss.png`, `report.md`, parameter table |
| **Weight** | Formative: in-class labs (实验 0–13) = 15 marks of the course (this lab is 1/14 of them) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** what `requires_grad` controls, why only leaves receive `.grad`, and why `.grad` accumulates
- **Know** the four moves of one parameter update and the order they must happen in
- **Do** implement linear regression using **only** `torch.Tensor` and autograd — no `nn.Module`, no `torch.optim`
- **Do** record a loss curve and read from it whether optimisation converged, stalled, or diverged
- **Do** compare the trained parameters against the generating truth *and* the closed-form least-squares solution, and explain why the three numbers differ

## 2. Before You Start · 课前准备

```bash
conda activate ai-app
python -c "import torch, matplotlib; print(torch.__version__, matplotlib.__version__)"
```

- [ ] The `ai-app` environment from Lab 00 activates and imports both packages
- [ ] `torch.cuda.is_available()` has been checked; you know whether you are on CPU or GPU (CPU is fine — say so in the report)
- [ ] `w01-lab0/` is committed in your record repository and the repo is pushed
- [ ] You have read the Week 2 slides, Parts 1–4

> **Reminder** — nothing from Lab 00 is dropped. This lab adds `report.md` to `w02-lab1/` inside the *same* record repository. Keep the layout.

## 3. Lab Tasks · 实验任务

### Part A — Generate the data and get a baseline number (10 min)

```python
import torch, matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

torch.manual_seed(42)                                  # fixed seed: a report requirement
X = torch.randn(100, 1)                                # (100, 1)
y = 3.0 * X + 2.0 + 0.1 * torch.randn(100, 1)          # (100, 1)

w = torch.zeros(1, 1)                                  # start at zero
b = torch.zeros(1, 1)
baseline = ((X @ w + b - y) ** 2).mean()
print("baseline MSE:", round(baseline.item(), 4))
```

> **Checkpoint A** — paste the baseline MSE into the report. Print `X.shape`, `y.shape`, `w.shape` and `b.shape` and confirm `X @ w + b` has shape `(100, 1)`.
> **Pitfall**: if `y` is built with `3.0 * X + 2.0 + 0.1 * torch.randn(100)` (a `(100,)` tensor) instead of `(100, 1)`, the expression `X @ w + b - y` silently broadcasts to `(100, 100)` and your loss is a meaningless number. **This does not raise an error.** Print the shape.

### Part B — Train with tensors only (20 min)

```python
w = torch.zeros(1, 1, requires_grad=True)
b = torch.zeros(1, requires_grad=True)
lr, history = 0.1, []

for step in range(200):
    y_hat = X @ w + b                       # forward: (100, 1)
    loss = ((y_hat - y) ** 2).mean()        # MSE
    loss.backward()                         # backward: fills w.grad and b.grad
    with torch.no_grad():                   # the update must not be traced
        w -= lr * w.grad
        b -= lr * b.grad
    w.grad.zero_(); b.grad.zero_()          # skip this -> accumulated gradients
    history.append(loss.item())

print("trained:", round(w.item(), 3), round(b.item(), 3))
```

Rules for this lab, checked in the report:

- **No `nn.Module`.** No `nn.Linear`, no `nn.Parameter`, no `nn.Sequential`.
- **No `torch.optim`.** Write the update line yourself.

> **Checkpoint B** — the printed parameters should land near `w = 2.987`, `b = 2.013`.
> **Pitfall**: forgetting `w.grad.zero_()` does not crash. It makes the loss oscillate between roughly 3 and 14 forever. If your curve jumps up and down, this is almost always the cause.

### Part C — Record the loss curve, three learning rates (20 min)

Loop over `lr ∈ {0.001, 0.1, 1.0}`. Each run must be a **fresh** model (re-create `w` and `b` inside the loop) with the same data and the same seed.

```python
curves = {}
for lr in [0.001, 0.1, 1.0]:
    torch.manual_seed(42)
    X = torch.randn(100, 1)
    y = 3.0 * X + 2.0 + 0.1 * torch.randn(100, 1)
    w = torch.zeros(1, 1, requires_grad=True)
    b = torch.zeros(1, 1, requires_grad=True)
    hist = []
    for s in range(200):
        loss = ((X @ w + b - y) ** 2).mean()
        loss.backward()
        with torch.no_grad():
            w -= lr * w.grad; b -= lr * b.grad
        w.grad.zero_(); b.grad.zero_()
        hist.append(loss.item())
    curves[lr] = hist

for lr, hist in curves.items():
    plt.plot(hist, label=f"lr={lr}")
plt.yscale("log"); plt.xlabel("step"); plt.ylabel("MSE loss")
plt.legend(); plt.savefig("loss.png", dpi=150)
```

> **Checkpoint C** — `loss.png` shows all three curves on one figure with a legend. Write one sentence for each: did it converge, stall, or diverge? Mark on the figure where the `lr = 0.1` curve stops dropping noticeably.
> **Note**: the log scale is not decoration. Without it the late descent of the `lr = 0.1` run is invisible.

### Part D — Verify convergence against the truth and against OLS (15 min)

```python
# closed-form least squares on the same data (the "best possible on this sample")
X1 = torch.cat([X, torch.ones_like(X)], dim=1)          # (100, 2)
theta = torch.linalg.lstsq(X1, y).solution              # [w_ols, b_ols]
print("OLS:", theta.flatten().tolist())
print("truth: [3.0, 2.0]")
```

> **Checkpoint D** — produce a table with four columns and three rows:

| Parameter | Generating truth | Closed-form OLS | GD, 200 steps | Relative error vs OLS |
|---|---|---|---|---|
| `w` | 3.000 | *(your value)* | *(your value)* | *(compute it)* |
| `b` | 2.000 | *(your value)* | *(your value)* | *(compute it)* |
| train MSE | 0.0100 (noise variance) | *(your value)* | *(your value)* | not comparable |

Then answer in three or four sentences: **why are these three numbers not equal?** Each one means something different, and your report must say which one your "error" is measured against.

### Part E — Shape pitfall log and one AI trace (10 min)

Keep a log while you work. Every time something goes wrong, write down the wrong expression, the **full** error message, and the fix.

```python
# at least the following two, reproduced by you:
a = torch.arange(6.).view(2, 3)
a.t().view(6)                     # 1. RuntimeError: view size is not compatible ...
torch.randn(3, 1) + torch.randn(3)   # 2. no error at all — result is (3, 3)
```

> **Checkpoint E** — `report.md` contains at least **two** entries with the verbatim error text, plus one `AI_USE.md` entry: what you asked an AI for, what it returned, **where it was wrong**, and how you found it. A trace that says only "the AI helped me" earns nothing.

### Part F — Capstone milestone · 大作业里程碑 (10 min)

> **M2 · Topic confirmed + `DATA.md` v0 + data loads** — see [`projects/capstone/milestones.md`](../../projects/capstone/milestones.md).

**Apply this week's skill:** you just made a numeric result reproducible — seed, shape, and one command. Do the same for your data.

**Push before the lab ends:**

- `DATA.md` v0: source and licence (a URL, not "from the internet"), row count and target distribution, missing values per column, known flaws, and the split strategy you intend to use **and why that kind**.
- A script or README section proving the data loads: print the shape and the first rows.
- Update `PROJECT_PLAN.md` with the cut list agreed in today's meeting.
- A `DEVLOG.md` entry for W2.

> **Checkpoint F** — at least 1 000 samples actually load from a fresh checkout, and the cut list is committed. If the data does not load this week, switch topic now — bring your other two proposals.
> **Pitfall**: a dataset found on a blog with no licence is illegal to ship and impossible to cite.

## 4. Deliverables Checklist · 交付清单

- [ ] `lab1_linear_regression.py` runs top-to-bottom without edits, with the seed fixed
- [ ] `loss.png` — three learning-rate curves on one figure, log scale, legend, convergence point marked
- [ ] Parameter convergence table — truth vs OLS vs GD 200 steps, with relative errors
- [ ] Written answer to "why are the three numbers not equal?"
- [ ] Shape pitfall log with ≥ 2 entries including verbatim error messages
- [ ] Reproducible command in the README (environment + seed + one command)
- [ ] `AI_USE.md` with ≥ 1 trace naming **where the AI was wrong**
- [ ] Capstone M2 pushed: `DATA.md` v0 + a loading proof + updated `DEVLOG.md`

## 5. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Training loop correctness (Part B) | 25 | tensors and autograd only; `no_grad` update; gradients zeroed; no `nn`/`optim` anywhere |
| Loss curve and reading (Part C) | 20 | three curves on one figure, log scale, and a correct one-line reading per curve |
| Convergence verification (Part D) | 20 | all three numbers reported, relative errors computed, and the difference explained rather than hidden |
| Shape pitfall log (Part E) | 15 | ≥ 2 entries, verbatim errors, correct fixes — including the one that raises no error |
| Reproducibility | 10 | fixed seed, pinned environment, one runnable command in the README |
| Exit ticket | 10 | all three questions answered in your own words |

Late policy: −10% per day, max 3 days, then 0.

*Part F (the capstone milestone) is not scored here — it is graded under the Capstone Project. Missing it costs −2 project points there.*

## 6. Submission · 提交方式

```bash
git add .
git commit -m "feat(w02): lab 1 linear regression with tensors and autograd"
git push origin main
git log --oneline -1        # paste this hash into the LMS box
```

Paste the repository URL plus the commit hash. **A commit hash counts as your timestamp**, not the LMS upload time.

## 7. Exit Ticket · 课后反思 (answer at the end of `report.md`)

1. What was the single most surprising thing you observed today?
2. Which step would you do differently next time, and why?
3. One question you still have (the instructor reads these and answers the best ones next week).

## 8. 中文摘要

本实验的目标：**不使用 `nn.Module`、不使用任何优化器**，只用张量和 autograd，把一条 `y = 3x + 2` 的直线学出来。

三个必须理解的点：
1. **一次参数更新有四个动作，顺序不能乱**：`backward()` → 在 `with torch.no_grad():` 里更新 → 立刻 `grad.zero_()` → 记录损失。少任何一件，训练都不会按预期收敛。
2. **`.grad` 是累加的**——不清零，梯度会一层层叠上去，损失表现为来回震荡而不是下降，而且**不会报错**。
3. **收敛要跟谁比，必须写清楚**：数据生成真值（3, 2）、闭式最小二乘解、200 步梯度下降解，三者本来就不完全相等。报告里不写清对照对象，「误差」这个词就没有意义。

常见翻车点：`y` 用 `(n,)` 而不是 `(n,1)`，广播成 `(n,n)` 后 MSE 量级全错且不报错；学习率 1.0 直接发散；对转置后的张量用 `view` 报非连续错误（改用 `reshape`）；只贴成功结果、不写踩坑记录——踩坑记录是能力证据，不是扣分项。

底线：不编造输出，不美化曲线，换设备出现微小差异如实写明。

- [ ] **Capstone milestone M2** pushed to the project repo (Part F — graded under the Capstone, not this lab)
