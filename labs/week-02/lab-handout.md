# Lab 02 · EDA & Data Cleaning on Titanic
> **AI Application Development** · Week 2 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 2 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 1 · Machine Learning Foundations |
| **Stack** | NumPy, pandas, matplotlib, seaborn |
| **Dataset** | Titanic (`titanic.csv`, 891 rows) |
| **Deliverables** | `lab-02.ipynb` with 3 charts + hypotheses + cleaning log |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** the 5-step EDA workflow and the three missing-value strategies
- **Know** why imputation must happen **after** the train/test split (data leakage)
- **Do** profile an unfamiliar dataset in three commands and write findings in prose
- **Do** build three diagnostic charts and turn each into a testable hypothesis
- **Do** apply a per-column cleaning strategy and re-verify afterwards

## 2. Before You Start · 课前准备

- [ ] Download `titanic.csv` from the course drive into this folder
- [ ] Read Chapter 2.5–2.6 (EDA five-step method, missing values)
- [ ] `import pandas as pd` works

## 3. Lab Tasks · 实验任务

### Part A — NumPy warm-up: slicing is a *view* (10 min)

```python
import numpy as np
m = np.arange(16).reshape(4, 4)
sub = m[1:3, 1:3]
sub[0, 0] = 999      # now check m again — surprise?
```

> **Checkpoint A** — write one sentence explaining what just happened and how to get a copy instead (`sub.copy()`).
> **Pitfall**: this single NumPy behaviour causes more silent bugs in this course than anything else.

### Part B — Data health check (25 min)

```python
df = pd.read_csv("titanic.csv")
df.info(); df.describe(); df.isna().sum()
```

Answer these four questions **in code**, each followed by one English sentence beginning *"I found that…"*:

1. Which columns have missing values, and how many?
2. Mean fare per passenger class?
3. Survival rate of males over 30?
4. How many times higher is the female survival rate than the male rate?

> **Checkpoint B** — four code cells + four sentences. Write **3 surprising findings** in a Markdown cell.

### Part C — Three charts, three questions (20 min)

| Chart | Type | Question it answers |
|---|---|---|
| Age distribution | histogram | *How is age spread?* |
| Survival rate by class | bar | *Which class fared better?* |
| Age × fare | scatter | *Is there a relationship?* |

Under each chart, write 1–2 sentences of interpretation, then list **≥3 testable hypotheses** (e.g. "3rd class survived least").

> **Checkpoint C** — three charts rendered, three interpretations written, three hypotheses listed.

### Part D — Cleaning with intent (15 min)

For each step, write a **one-line justification before** the code:

```python
med = df["age"].median()
df["age"] = df["age"].fillna(med)
df["age_missing"] = df["age"].isna().astype(int)   # keep the signal that it was missing
df["embarked"] = df["embarked"].fillna(df["embarked"].mode()[0])
q1, q3 = df["fare"].quantile([.25, .75])
df["fare"] = df["fare"].clip(q1 - 1.5*(q3-q1), q3 + 1.5*(q3-q1))
df.drop_duplicates(inplace=True)
```

Then re-run `info()` and `describe()` and confirm nothing is missing.

> **Checkpoint D** — before/after tables of missing counts, plus your justification lines.
> **Pitfall**: filling before splitting leaks test-set statistics into training. Today you clean the whole frame — in Week 4 you will fix that with a `Pipeline`.

### Part E — Submit (5 min)

Commit and push; fill in the exit ticket.

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-02.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Every **Checkpoint** cell executed and its output visible in the submitted notebook
- [ ] Markdown cells contain your own sentences (not just copied code output)
- [ ] Pushed to GitHub with **≥ 2 meaningful commits** (`feat: ...` style messages)
- [ ] Repository is public (or the TA is added as collaborator) so it can be graded

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| NumPy view demo (Part A) | 10 | correct explanation of the view/copy behaviour |
| Data profiling (Part B) | 25 | four questions answered in code + four written findings |
| Three charts (Part C) | 25 | charts rendered, each with interpretation and ≥3 hypotheses total |
| Cleaning log (Part D) | 30 | every step justified in writing, before/after verification shown |
| Exit ticket | 10 | three questions answered |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add lab-02.ipynb
git commit -m "feat: complete lab 02"
git push origin main
```

Then paste your repo URL into the LMS submission box. **A commit hash counts as your timestamp**, not the LMS upload time.

## 8. Exit Ticket · 课后反思 (answer in the last Markdown cell)

1. What was the single most surprising thing you observed today?
2. Which step would you do differently next time, and why?
3. One question you still have (the instructor reads these and answers the best ones next week).

## 9. 中文摘要

本周把「先理解数据，再碰模型」这件事做成肌肉记忆。

四个必须掌握的点：
1. **NumPy 切片是视图**——改子矩阵会改原矩阵，要副本就 `.copy()`。
2. **体检三连**：`info()` / `describe()` / `isna().sum()`，任何陌生数据集都从这里开始。
3. **EDA 五步法**：体检 → 单变量 → 双变量 → 假设 → 清洗。图不是目的，**假设**才是。
4. **检测 ≠ 删除**：IQR 只是标出异常值，删还是截断要你根据业务判断。

关键纪律：每一步清洗前先写一行「为什么这么做」。说不出理由的清洗，就是把噪声当成数据。
