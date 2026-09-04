# Lab 04 · Model Evaluation, Overfitting & Regularization
> **AI Application Development** · Week 4 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 4 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 1 · Machine Learning Foundations |
| **Stack** | scikit-learn (metrics, learning_curve, Ridge/Lasso) |
| **Dataset** | `load_breast_cancer` + synthetic polynomial data |
| **Deliverables** | `lab-04.ipynb` with metric report + overfitting diagnosis |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** why accuracy is misleading on imbalanced data, and which metric to use instead
- **Know** how to read a learning curve to diagnose overfitting vs underfitting
- **Do** produce a full classification report (precision / recall / F1 / ROC-AUC) and explain it
- **Do** reproduce overfitting on purpose, then fix it with regularization
- **Do** choose a decision threshold based on a cost argument, not by default

## 2. Before You Start · 课前准备

- [ ] Week 3 pipeline runs
- [ ] Read Chapter 4 (evaluation & regularization)
- [ ] Know the TP / FP / FN / TN definitions

## 3. Lab Tasks · 实验任务

### Part A — Accuracy is a trap (15 min)

```python
from sklearn.datasets import load_breast_cancer
from sklearn.dummy import DummyClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score
```

Train `DummyClassifier(strategy="most_frequent")` and a real model. Compare accuracies.

> **Checkpoint A** — by how many points does the real model beat the dummy? Rewrite that sentence using precision and recall instead.

### Part B — Full metric report (20 min)

```python
print(classification_report(y_test, preds, target_names=data.target_names))
print("ROC-AUC:", roc_auc_score(y_test, proba[:, 1]))
```

> **Checkpoint B** — for this dataset (cancer diagnosis), is a false negative or a false positive worse? Which metric should you therefore optimise?
> **Pitfall**: `roc_auc_score` needs **probabilities** (`predict_proba`), not hard labels.

### Part C — Threshold tuning (15 min)

```python
from sklearn.metrics import precision_recall_curve
precision, recall, thresholds = precision_recall_curve(y_test, proba[:, 1])
```

Plot precision and recall against the thresholds, then pick one.

> **Checkpoint C** — state your chosen threshold and justify it with the cost argument from Part B.

### Part D — Overfit on purpose, then fix it (20 min)

```python
from sklearn.preprocessing import PolynomialFeatures
from sklearn.linear_model import Ridge, LinearRegression
from sklearn.model_selection import learning_curve
```

1. Fit `PolynomialFeatures(degree=15)` + `LinearRegression` on 30 training points: train error ≈ 0, test error huge.
2. Plot the learning curve and identify the gap.
3. Swap in `Ridge(alpha=...)` and sweep alpha; find the value that minimises test error.

> **Checkpoint D** — the learning-curve plot plus one sentence: how do you tell overfitting from underfitting by looking at the two curves?
> **Pitfall**: a *good* test score obtained after tuning on the test set is not a good score — you have started fitting the test set. Use a validation split or CV.

### Part E — Wrap up (5 min)

Write the four-metric summary you would paste into a project README, then fill in the exit ticket.

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-04.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Every **Checkpoint** cell executed and its output visible in the submitted notebook
- [ ] Markdown cells contain your own sentences (not just copied code output)
- [ ] Pushed to GitHub with **≥ 2 meaningful commits** (`feat: ...` style messages)
- [ ] Repository is public (or the TA is added as collaborator) so it can be graded

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Dummy baseline comparison (Part A) | 15 | baseline run, gap quantified correctly |
| Metric report (Part B) | 25 | classification_report + ROC-AUC present, FN/FP cost argument made |
| Threshold choice (Part C) | 20 | threshold justified by cost, not picked at random |
| Overfitting experiment (Part D) | 30 | overfit reproduced, learning curve plotted, Ridge alpha tuned |
| Exit ticket | 10 | three questions answered |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add lab-04.ipynb
git commit -m "feat: complete lab 04"
git push origin main
```

Then paste your repo URL into the LMS submission box. **A commit hash counts as your timestamp**, not the LMS upload time.

## 8. Exit Ticket · 课后反思 (answer in the last Markdown cell)

1. What was the single most surprising thing you observed today?
2. Which step would you do differently next time, and why?
3. One question you still have (the instructor reads these and answers the best ones next week).

## 9. 中文摘要

本周回答一个问题：**凭什么说这个模型好？**

四个要点：
1. **准确率会骗人**——先跟 `DummyClassifier` 比，才知道模型到底有没有学到东西。
2. **指标要对齐代价**：癌症筛查里漏诊（FN）代价远高于误诊（FP），所以看 recall 而不是 accuracy。
3. **ROC-AUC 要喂概率**（`predict_proba`），喂硬标签结果失真。
4. **过拟合诊断看两条曲线的缝**：训练误差低、验证误差高且缝大 = 过拟合；两条都高 = 欠拟合。正则化（Ridge/Lasso）就是给模型复杂度上税。

最大的坑：在测试集上调参。调完得到的「好分数」已经不客观了。
