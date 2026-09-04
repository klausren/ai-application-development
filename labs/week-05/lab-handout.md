# Lab 05 · Neural Network Fundamentals — from a NumPy perceptron to PyTorch
> **AI Application Development** · Week 5 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 5 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 2 · Deep Learning & Computer Vision |
| **Stack** | NumPy, PyTorch (`torch.nn`), matplotlib |
| **Dataset** | Logic gates (synthetic) + `make_moons` |
| **Deliverables** | `lab-05.ipynb` with NumPy MLP + PyTorch MLP comparison |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** why a single perceptron cannot solve XOR, and what a hidden layer adds
- **Know** what each of `nn.Linear` / activation / loss / optimizer contributes
- **Do** implement forward pass and gradient descent for a 2-layer net **in NumPy** by hand
- **Do** rebuild the same net in PyTorch and confirm you get comparable results
- **Do** explain, empirically, why ReLU replaced sigmoid in hidden layers

## 2. Before You Start · 课前准备

- [ ] Week 4 lab committed
- [ ] `python -c "import torch; print(torch.__version__)"` works
- [ ] Read Chapter 5 (perceptron, MLP, backpropagation)

**Device setup** (put this in your first cell and reuse it all semester):

```python
import torch
device = torch.device("mps" if torch.backends.mps.is_available()
                      else "cuda" if torch.cuda.is_available() else "cpu")
print("using", device)
```

## 3. Lab Tasks · 实验任务

### Part A — A perceptron you can solve on paper (15 min)

Build AND and OR gates by **choosing weights by hand** (do not train):

```python
import numpy as np
X = np.array([[0,0],[0,1],[1,0],[1,1]])
def step(z): return (z >= 0).astype(int)
w_and, b_and = np.array([1, 1]), -1.5     # verify all four rows
```

> **Checkpoint A** — truth tables for AND and OR printed, correct.
> **Then try XOR by hand.** Spend 3 minutes. You will fail — write down *why* in one sentence before moving on.

### Part B — XOR needs a hidden layer: NumPy MLP (20 min)

Implement a 2-2-1 network with sigmoid hidden + sigmoid output, trained by plain gradient descent:

```python
W1 = np.random.randn(2, 4) * 0.5; b1 = np.zeros(4)
W2 = np.random.randn(4, 1) * 0.5; b2 = np.zeros(1)
sigmoid = lambda z: 1/(1+np.exp(-z))
for epoch in range(10000):
    h = sigmoid(X @ W1 + b1)
    y_hat = sigmoid(h @ W2 + b2)
    loss = np.mean((y_hat - y)**2)
    # TODO: backprop — dY, then W2/b2, then W1/b1 (chain rule, 6 lines)
    W2 -= lr * h.T @ dY;  b2 -= lr * dY.sum(0)
    W1 -= lr * X.T @ dh;  b1 -= lr * dh.sum(0)
```

> **Checkpoint B** — final predictions on all four XOR rows, plus a loss curve. State your learning rate and epoch count.
> **Pitfall**: if loss plateaus at 0.25, your gradient or your learning rate is wrong, not your architecture.

### Part C — The same network in PyTorch (20 min)

```python
import torch.nn as nn
model = nn.Sequential(nn.Linear(2, 4), nn.Sigmoid(), nn.Linear(4, 1), nn.Sigmoid()).to(device)
opt = torch.optim.SGD(model.parameters(), lr=1.0)
crit = nn.MSELoss()
```

Train it on XOR, then swap the dataset for `sklearn.datasets.make_moons(n_samples=400, noise=0.2)` and retrain (2-8-1 with ReLU hidden, BCEWithLogitsLoss).

> **Checkpoint C** — accuracy on `make_moons` and a decision-boundary plot.
> **Pitfall**: `BCEWithLogitsLoss` expects raw logits — do **not** add a sigmoid at the output. This is the single most common PyTorch bug in this course.

### Part D — Activation function shootout (15 min)

Retrain the moons net three times, changing only the hidden activation: `Sigmoid` vs `Tanh` vs `ReLU`. Plot the three loss curves on one figure.

> **Checkpoint D** — one figure, three curves, plus one sentence: which converged fastest and what does that have to do with vanishing gradients?

### Part E — Wrap up (5 min)

Fill the summary table (activation → final loss → epochs to converge) and answer the exit ticket.

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-05.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Every **Checkpoint** cell executed, with its output visible
- [ ] Experiment results collected into **one summary table** (not scattered printouts)
- [ ] Markdown cells contain your own interpretation, not just code
- [ ] Pushed to GitHub with **≥ 2 meaningful commits**

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Hand-built gates (Part A) | 15 | AND/OR truth tables correct, XOR failure explained correctly |
| NumPy MLP backprop (Part B) | 30 | gradients derived and coded by hand, XOR solved, loss curve shown |
| PyTorch rebuild (Part C) | 25 | PyTorch net trains, moons decision boundary plotted, logits pitfall avoided |
| Activation comparison (Part D) | 20 | three curves on one figure, vanishing-gradient point made |
| Exit ticket | 10 | three questions answered |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add lab-05.ipynb
git commit -m "feat: complete lab 05"
git push origin main
```

## 8. Exit Ticket · 课后反思

1. What surprised you most today?
2. Which knob (hyperparameter) had the biggest effect, and how do you know it wasn't luck?
3. One question you still have.

## 9. 中文摘要

本周从「手算神经网络」开始，目的是让你知道 PyTorch 在帮你做什么。

五个要点：
1. **单层感知机解不了 XOR**——因为它只能画一条直线；隐藏层的作用是做特征变换，把问题变成线性可分的。
2. **手写反向传播是本周最值钱的部分**：损失函数 → 输出层梯度 → 隐藏层梯度，链式法则走一遍，后面所有调参才有手感。
3. **PyTorch 五件套**：`nn.Linear`（层）→ 激活 → 损失函数 → 优化器 → 训练循环。本学期后面全部是这套骨架。
4. **BCEWithLogitsLoss 要喂 logits**，输出层别再加 sigmoid，否则既不收敛又难排查。
5. **ReLU 取代 sigmoid 的原因**：正区间梯度恒为 1，深层网络不会梯度消失。

判断学习率对不对：loss 卡在 0.25 不动，先怀疑梯度和学习率，不要急着改结构。
