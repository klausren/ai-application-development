# Lab 07 · CNNs & Computer Vision
> **AI Application Development** · Week 7 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 7 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 2 · Deep Learning & Computer Vision |
| **Stack** | PyTorch (`torch.nn.Conv2d`), torchvision.models |
| **Dataset** | MNIST + (optional) CIFAR-10 subset |
| **Deliverables** | `lab-07.ipynb` with convolution visualisation + CNN + transfer learning |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** what a convolution kernel actually computes, and what the filters learn to detect
- **Know** why CNNs beat MLPs on images (parameter sharing, translation equivariance)
- **Do** apply hand-written kernels (edge, blur, sharpen) and explain the output in words
- **Do** build and train a small CNN that beats your Week 6 MLP on MNIST
- **Do** run transfer learning with a pretrained ResNet-18 and explain *why* freezing works

## 2. Before You Start · 课前准备

- [ ] Week 6 lab committed (you have a reproducible training loop)
- [ ] Optional: pre-download CIFAR-10 before class if your connection is slow (`torchvision.datasets.CIFAR10(..., download=True)`)
- [ ] Fallback if downloads fail: do Parts A–C on MNIST and run Part D with `weights=None` — you still practise the full transfer-learning API

## 3. Lab Tasks · 实验任务

### Part A — See a convolution with your own eyes (15 min)

```python
import torch.nn.functional as F
kernel = torch.tensor([[-1,-1,-1],[0,0,0],[1,1,1]], dtype=torch.float32).view(1,1,3,3)
out = F.conv2d(gray_img.unsqueeze(0).unsqueeze(0), kernel, padding=1)
```

Apply three hand-written kernels (Sobel-X edge, box blur, sharpen) to one image and show input + 3 outputs side by side.

> **Checkpoint A** — one 4-panel figure, plus **one sentence per kernel** describing what it emphasises.
> **Pitfall**: `conv2d` expects 4-D input `(N, C, H, W)` — a bare 2-D image tensor will raise a confusing rank error.

### Part B — Build a CNN, beat the MLP (25 min)

```python
class SmallCNN(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Conv2d(1, 16, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Conv2d(16, 32, 3, padding=1), nn.ReLU(), nn.MaxPool2d(2),
            nn.Flatten(), nn.Linear(32*7*7, 10))
    def forward(self, x): return self.net(x)
```

Train 5 epochs. Compare against your Week 6 MLP accuracy **and parameter count**.

```python
sum(p.numel() for p in model.parameters())
```

> **Checkpoint B** — a 2-row table: MLP vs CNN (accuracy, #params, training time). One sentence on the trade-off.
> **Think**: the CNN should use *fewer* parameters for *better* accuracy. If not, check your pooling/flatten dimensions.

### Part C — What do the filters see? (15 min)

Visualise the 16 first-layer kernels, then pass one image through and plot 6 feature maps.

```python
w = model.net[0].weight.detach().cpu()      # shape [16, 1, 3, 3]
```

> **Checkpoint C** — 16 kernels + 6 feature maps, and one sentence: what do the feature maps seem to be detecting?

### Part D — Transfer learning with ResNet-18 (20 min)

```python
from torchvision import models
m = models.resnet18(weights=models.ResNet18_Weights.DEFAULT)
for p in m.parameters(): p.requires_grad = False   # freeze the backbone
m.fc = nn.Linear(m.fc.in_features, 10)             # new head for our classes
```

Fine-tune the head on CIFAR-10 (or a 2-class subset if CIFAR is unavailable). Then unfreeze the last block and fine-tune again with a 10× smaller LR.

> **Checkpoint D** — accuracy before/after unfreezing, plus one sentence explaining why the second stage needs a much smaller learning rate.
> **Pitfall**: after changing `requires_grad`, you must rebuild the optimizer (or it will still see the old parameter list).

### Part E — Wrap up (5 min)

Three sentences: when would you *not* use a CNN for an image task?

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-07.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Every **Checkpoint** cell executed, with its output visible
- [ ] Experiment results collected into **one summary table** (not scattered printouts)
- [ ] Markdown cells contain your own interpretation, not just code
- [ ] Pushed to GitHub with **≥ 2 meaningful commits**

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Convolution visualisation (Part A) | 20 | three kernels applied, outputs explained in words |
| CNN vs MLP (Part B) | 30 | CNN trained, accuracy + parameter count compared correctly |
| Filter & feature-map visualisation (Part C) | 20 | kernels and feature maps plotted with interpretation |
| Transfer learning (Part D) | 20 | frozen-backbone fine-tune run, unfreeze experiment done, LR rationale stated |
| Exit ticket | 10 | three questions answered |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add lab-07.ipynb
git commit -m "feat: complete lab 07"
git push origin main
```

## 8. Exit Ticket · 课后反思

1. What surprised you most today?
2. Which knob (hyperparameter) had the biggest effect, and how do you know it wasn't luck?
3. One question you still have.

## 9. 中文摘要

本周把「卷积」从公式变成看得见的东西。

五个要点：
1. **卷积核就是特征检测器**：Sobel 检测边缘、盒式滤波做模糊、锐化核增强对比——手写一遍你就懂为什么网络能学出有意义的特征。
2. **CNN 赢在参数共享**：同一套卷积核扫全图，参数量远小于全连接，且对平移更鲁棒。对比参数量是本周的必答项。
3. **`conv2d` 要 4-D 输入** `(N, C, H, W)`，二维张量直接喂会报维度错误。
4. **迁移学习的套路**：冻结骨干（backbone）→ 只训练新分类头 → 效果不够再解冻最后几层，**学习率要小一个数量级**，否则会把预训练权重冲掉。
5. **改完 `requires_grad` 要重建优化器**，否则优化器还拿着旧的参数列表。

特征图可视化是理解 CNN 最直观的方式：第一层检测边缘纹理，越往后越抽象。
