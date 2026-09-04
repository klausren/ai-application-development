# Lab 03 · The scikit-learn Workflow: fit → predict → evaluate
> **AI Application Development** · Week 3 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 3 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 1 · Machine Learning Foundations |
| **Stack** | scikit-learn (Pipeline, StandardScaler, GridSearchCV) |
| **Dataset** | `load_digits` + `load_diabetes` (built-in) |
| **Deliverables** | `lab-03.ipynb` with pipeline + hyperparameter sweep |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** why `Pipeline` exists and what it prevents (leakage in cross-validation)
- **Know** the difference between a parameter and a *hyper*parameter
- **Do** build a `Pipeline` with preprocessing + model and use it like a single estimator
- **Do** run a hyperparameter sweep with `GridSearchCV` and read `best_params_`
- **Do** switch a task from classification to regression without changing your mental model

## 2. Before You Start · 课前准备

- [ ] Week 2 lab committed (your Titanic cleaning works)
- [ ] Watch the 82-second *sklearn workflow* micro-lesson in the course drive
- [ ] Chapter 3 skimmed

## 3. Lab Tasks · 实验任务

### Part A — Baseline without a pipeline (10 min)

```python
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression
X, y = load_digits(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.2, random_state=42)
LogisticRegression(max_iter=1000).fit(X_tr, y_tr).score(X_te, y_te)
```

> **Checkpoint A** — record the accuracy. If a `ConvergenceWarning` appears, write what it is telling you.

### Part B — Same model, inside a Pipeline (15 min)

```python
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import StandardScaler
pipe = Pipeline([("scale", StandardScaler()), ("clf", LogisticRegression(max_iter=1000))])
pipe.fit(X_tr, y_tr)
pipe.score(X_te, y_te)
```

> **Checkpoint B** — did scaling change accuracy? Write one sentence on why scaling matters for *this* model but not for a tree.
> **Pitfall**: fitting the scaler on all data before splitting leaks information. Inside a `Pipeline` the scaler is fitted **only on each training fold** — that is the whole point.

### Part C — Hyperparameter sweep (20 min)

```python
from sklearn.model_selection import GridSearchCV
grid = {"clf__C": [0.01, 0.1, 1, 10]}
search = GridSearchCV(pipe, grid, cv=5, n_jobs=-1)
search.fit(X_tr, y_tr)
print(search.best_params_, search.best_score_, search.score(X_te, y_te))
```

> **Checkpoint C** — report `best_params_`, CV score and test score. In one sentence: why is the CV score usually *lower* than the test score here?

### Part D — Same workflow, regression (20 min)

```python
from sklearn.datasets import load_diabetes
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, r2_score
```

Repeat fit → predict → evaluate, but score with `mean_absolute_error` and `r2_score` instead of accuracy.

> **Checkpoint D** — report MAE and R². Write one sentence: what does R² = 0.45 mean to a stakeholder?
> **Pitfall**: for regressors, `model.score()` returns R², **not** accuracy. Reading the wrong metric is the most common lab error this week.

### Part E — Wrap up (10 min)

In one Markdown cell, write the three lines you would reuse in *any* future ML project (they should be model-agnostic).

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-03.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Every **Checkpoint** cell executed and its output visible in the submitted notebook
- [ ] Markdown cells contain your own sentences (not just copied code output)
- [ ] Pushed to GitHub with **≥ 2 meaningful commits** (`feat: ...` style messages)
- [ ] Repository is public (or the TA is added as collaborator) so it can be graded

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Baseline vs pipeline (Parts A–B) | 25 | both run, difference explained, leakage point articulated |
| GridSearchCV (Part C) | 30 | sweep executed, best_params_ + CV/test scores reported and interpreted |
| Regression branch (Part D) | 25 | MAE + R² computed, R² explained in plain language |
| Reusable three-lines summary (Part E) | 10 | genuinely model-agnostic, not copy-pasted code |
| Exit ticket | 10 | three questions answered |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add lab-03.ipynb
git commit -m "feat: complete lab 03"
git push origin main
```

Then paste your repo URL into the LMS submission box. **A commit hash counts as your timestamp**, not the LMS upload time.

## 8. Exit Ticket · 课后反思 (answer in the last Markdown cell)

1. What was the single most surprising thing you observed today?
2. Which step would you do differently next time, and why?
3. One question you still have (the instructor reads these and answers the best ones next week).

## 9. 中文摘要

本周把第 1 周的三步工作流升级成「工程可用版」。

三个要点：
1. **Pipeline 的价值不在省代码，而在防泄漏**：预处理只拟合训练折，交叉验证才可信。
2. **超参数不是从数据里学出来的**，是你在外面设定的（如 `C`、树的数量）。用 `GridSearchCV` 系统地扫。
3. **换任务不换思路**：分类用 accuracy/F1，回归用 MAE/R²，`fit → predict → evaluate` 骨架完全一样。

最常犯的错：把 `score()` 当成万能——回归任务里它返回 R²，不是准确率。
