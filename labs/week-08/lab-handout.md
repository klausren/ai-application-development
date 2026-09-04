# Lab 08 · CV Application & Midterm Project Lab
> **AI Application Development** · Week 8 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 8 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 2 · Deep Learning & Computer Vision |
| **Stack** | PyTorch, torchvision, Gradio (optional) |
| **Dataset** | Team's own choice (approved by instructor) |
| **Deliverables** | midterm repo: dataset + model + 3-slide deck + demo notebook |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Do** curate and document a dataset you chose yourself (and justify the choice)
- **Do** train a baseline model and evaluate it with a metric appropriate to *your* problem
- **Do** perform error analysis: look at the worst predictions and explain them
- **Do** present a 3-slide lightning demo to another team and give written peer feedback

> This is a **project lab**, not a code-along. Your team works; the instructor circulates. The deliverable is a *working demo*, not a perfect model.

## 2. Before You Start · 课前准备

- [ ] Team of 2–3 formed, dataset idea approved by the instructor **before** this lab
- [ ] Every member has pushed at least one commit to the team repo
- [ ] Week 7 lab committed individually

## 3. Lab Tasks · 实验任务

### Part A — Dataset curation & documentation (15 min)

Create `DATA.md` in your team repo answering:

1. Where did the data come from, and what is the licence / usage term?
2. How many samples per class? (paste the table — do not describe it)
3. How will you split it, and is there any leakage between splits (duplicates, near-duplicates, same subject appearing twice)?
4. What is your **baseline to beat** (a dumb rule, not a model)?

> **Checkpoint A** — `DATA.md` committed. Attach the per-class counts table.
> **Pitfall**: "I found 5000 images on the internet" is not a dataset — it is an unlicensed liability. Document the source or switch datasets today.

### Part B — Baseline model & honest evaluation (30 min)

Train the simplest model that could work. Record one number: your chosen metric on a held-out test set that you touch **once**.

```python
# evaluate once. If you evaluate again after changing the model, say so in the report.
```

> **Checkpoint B** — baseline metric in the README, plus the exact command to reproduce it.
> **Pitfall**: choosing accuracy on an imbalanced dataset. Revisit Week 4 — pick precision, recall or macro-F1 and justify it.

### Part C — Error analysis (20 min)

Take the 10 worst predictions (lowest confidence on the wrong class) and display them.

```python
probs, preds = torch.softmax(logits, 1).max(1)
worst = (probs * (preds != labels).float()).topk(10).indices
```

For each, write one clause: *"this failed because …"* (label noise? ambiguity? genuinely hard?).

> **Checkpoint C** — 10 images with a one-line diagnosis each, and one pattern you noticed across them.
> **Think**: error analysis is where real ML engineers spend their time. Three good diagnoses beat three more epochs of tuning.

### Part D — Lightning demo draft (10 min)

Build 3 slides: **①** the problem & data **②** the approach & metric **③** the result & the biggest failure. Rehearse in 90 seconds per team.

> **Checkpoint D** — 3 slides committed to the repo (`slides.pdf` or `slides.md`).

### Part E — Peer feedback (5 min)

Each team gives written feedback to one other team using: *"One thing that worked, one thing I'd question, one suggestion."*

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-08.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Every **Checkpoint** cell executed, with its output visible
- [ ] Experiment results collected into **one summary table** (not scattered printouts)
- [ ] Markdown cells contain your own interpretation, not just code
- [ ] Pushed to GitHub with **≥ 2 meaningful commits**

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| DATA.md documentation (Part A) | 25 | source/licence stated, class counts tabled, split justified, baseline defined |
| Baseline + metric (Part B) | 30 | model trained, metric appropriate to problem, reproduce command included |
| Error analysis (Part C) | 25 | 10 failures displayed and diagnosed, a cross-cutting pattern identified |
| 3-slide demo (Part D) | 10 | slides committed, honest failure slide included |
| Peer feedback & teamwork (Part E) | 10 | written feedback given, all members committed |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add lab-08.ipynb
git commit -m "feat: complete lab 08"
git push origin main
```

## 8. Exit Ticket · 课后反思

1. What surprised you most today?
2. Which knob (hyperparameter) had the biggest effect, and how do you know it wasn't luck?
3. One question you still have.

## 9. 中文摘要

本周从「跟着做」切换到「自己做」，是期中项目的第一个检查点。

五个要点：
1. **数据先过合规关**：来源、许可、每类样本数、有没有重复/泄漏。说不清来源的数据集现在就换，不要等到答辩被问。
2. **基线要笨**：先定一个「傻规则」的分数（比如全猜多数类），模型连它都打不过就说明方案有问题。
3. **指标选对**：不平衡数据看 macro-F1 / recall，别用 accuracy（第 4 周的内容在这里第一次真刀真枪用上）。
4. **测试集只碰一次**：调完模型再回头测，那个分数就不客观了。要在报告里如实说明你测了几次。
5. **错误分析比调参更有价值**：找出 10 个最差预测，逐个写「为什么错」，你大概率会发现真正的瓶颈（标注噪声/样本不足/任务本身有歧义）。

展示要求：3 页幻灯片，第 3 页必须是你最大的失败——敢讲失败的团队分数更高。
