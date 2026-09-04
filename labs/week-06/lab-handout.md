# Lab 06 · Training Deep Networks in Practice
> **AI Application Development** · Week 6 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 6 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 2 · Deep Learning & Computer Vision |
| **Stack** | PyTorch, torchvision, TensorBoard |
| **Dataset** | MNIST (torchvision, ~11 MB) |
| **Deliverables** | `lab-06.ipynb` with an ablation table (optimizer × regularization × LR) |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** what Adam does differently from SGD, and when each is preferable
- **Know** what BatchNorm and Dropout each fix, and that they are *not* interchangeable
- **Do** run a controlled ablation: change one factor at a time, keep everything else fixed
- **Do** log runs to TensorBoard and compare them honestly
- **Do** read a training curve and decide: underfitting, overfitting, or unstable?

## 2. Before You Start · 课前准备

- [ ] Week 5 lab committed (PyTorch training loop works)
- [ ] Disk space for MNIST (~11 MB)
- [ ] Offline fallback if the download fails: `sklearn.datasets.load_digits()` (8×8, 1797 images) — the whole lab works with it, just note it in your report

```python
from torchvision import datasets, transforms
train = datasets.MNIST("./data", train=True, download=True,
                       transform=transforms.ToTensor())
loader = torch.utils.data.DataLoader(train, batch_size=128, shuffle=True)
```

> **Pitfall**: always `transforms.Normalize((0.1307,), (0.3081,))` — unnormalised inputs make every comparison below noisy.

## 3. Lab Tasks · 实验任务

### Part A — Baseline and a reproducible setup (10 min)

```python
torch.manual_seed(42)      # do this once at the top of your notebook
```

Train a 3-layer MLP (784-256-128-10) for 5 epochs with Adam. Record test accuracy.

> **Checkpoint A** — baseline accuracy + a note on how you made the run reproducible.
> **Pitfall**: without a seed, your "improvement" in Part B may just be noise.

### Part B — Optimizer ablation (20 min)

Same architecture, same seed, change only the optimizer:

| Run | Optimizer | Test acc | Epochs to 97% |
|---|---|---|---|
| 1 | `SGD(lr=0.1)` | | |
| 2 | `SGD(lr=0.1, momentum=0.9)` | | |
| 3 | `Adam(lr=1e-3)` | | |

> **Checkpoint B** — the filled table and one sentence on the accuracy/**speed** trade-off.
> **Think**: Adam converges faster. Does it always generalise better? Check test accuracy, not just training speed.

### Part C — Regularization ablation (20 min)

Take the best optimizer and ablate:

1. no regularization (baseline)
2. `nn.Dropout(0.3)` after each hidden layer
3. `nn.BatchNorm1d` after each hidden linear layer
4. both

```python
nn.Sequential(nn.Linear(784,256), nn.BatchNorm1d(256), nn.ReLU(), nn.Dropout(0.3), ...)
```

> **Checkpoint C** — four numbers in a table, plus **one sentence per row** explaining the observed effect.
> **Pitfall**: `model.train()` and `model.eval()` matter. Dropout and BatchNorm behave differently in the two modes — forgetting `.eval()` before testing is a classic silent bug.

### Part D — Learning-rate schedule + TensorBoard (20 min)

```python
from torch.utils.tensorboard import SummaryWriter
writer = SummaryWriter("runs/exp1")
writer.add_scalar("loss/train", loss, step)
scheduler = torch.optim.lr_scheduler.StepLR(opt, step_size=3, gamma=0.5)
```

Run two configs (constant LR vs StepLR) and compare in TensorBoard:

```bash
tensorboard --logdir runs
```

> **Checkpoint D** — a screenshot of the TensorBoard scalar panel comparing the two runs, plus one observation.
> **Pitfall**: call `scheduler.step()` once per **epoch** (not per batch) unless you intentionally use per-batch scheduling.

### Part E — Wrap up (5 min)

Consolidate all runs into one DataFrame: `optimizer | regularization | lr schedule | test acc | notes`.

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-06.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Every **Checkpoint** cell executed, with its output visible
- [ ] Experiment results collected into **one summary table** (not scattered printouts)
- [ ] Markdown cells contain your own interpretation, not just code
- [ ] Pushed to GitHub with **≥ 2 meaningful commits**

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Baseline + reproducibility (Part A) | 15 | seed set, baseline recorded, normalisation applied |
| Optimizer ablation (Part B) | 25 | three runs, one variable changed, table filled, trade-off discussed |
| Regularization ablation (Part C) | 30 | four runs, train/eval modes handled correctly, effects explained |
| LR schedule + TensorBoard (Part D) | 20 | two runs logged, screenshot included, scheduler step placement correct |
| Exit ticket | 10 | three questions answered |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add lab-06.ipynb
git commit -m "feat: complete lab 06"
git push origin main
```

## 8. Exit Ticket · 课后反思

1. What surprised you most today?
2. Which knob (hyperparameter) had the biggest effect, and how do you know it wasn't luck?
3. One question you still have.

## 9. 中文摘要

本周的核心方法论是**控制变量实验**（ablation）：一次只改一个因素，其余全部固定，否则你不知道是哪个改动起了作用。

五个要点：
1. **先固定随机种子**再比较，不然「提升」可能只是噪声。
2. **Adam 快，SGD+momentum 往往泛化更好**——到底选谁要看测试集准确率，不能只看谁先收敛。
3. **Dropout 和 BatchNorm 解决的不是同一个问题**：Dropout 抑制过拟合（随机丢神经元），BatchNorm 稳定分布、加速收敛。二者可以叠加。
4. **`.eval()` 一定不能忘**——Dropout 和 BatchNorm 在训练/评估模式下行为不同，忘了会让测试指标莫名其妙地差。
5. **scheduler.step() 按 epoch 调**（除非你明确要按 batch），放错位置等于没有调度。

工具习惯：从本周起，所有实验都记到 TensorBoard，期末写项目报告时直接截图。
