# Lab 15 · MLOps & Production Practices
> **AI Application Development** · Week 15 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 15 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 4 · AI Application Engineering |
| **Stack** | MLflow, pytest, pandas (drift metrics), scikit-learn |
| **Deliverables** | `lab-15/` folder: tracked runs, drift report, `test_data.py` |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** what experiment tracking solves ("which run produced this model?")
- **Know** the difference between *code* CI and *data* CI, and why ML needs both
- **Do** log parameters, metrics and artifacts to MLflow and compare runs in the UI
- **Do** write data-validation tests that fail loudly when the input distribution shifts
- **Do** detect injected drift with a simple, defensible statistic

## 2. Before You Start · 课前准备

- [ ] Week 14 lab committed (you have a model and a service)
- [ ] `pip install mlflow` works
- [ ] Read Chapter 15 (experiment tracking, monitoring)

## 3. Lab Tasks · 实验任务

### Part A — Track your runs properly (20 min)

```python
import mlflow
mlflow.set_experiment("sentiment-baselines")
with mlflow.start_run(run_name="tfidf-logreg"):
    mlflow.log_params({"vectorizer": "tfidf", "C": 1.0, "seed": 42})
    mlflow.log_metrics({"accuracy": acc, "f1_macro": f1})
    mlflow.sklearn.log_model(pipe, "model")
    mlflow.log_artifact("confusion_matrix.png")
```

Run at least **three** configurations so there is something to compare.

```bash
mlflow ui --port 5000
```

> **Checkpoint A** — screenshot of the MLflow run comparison table, plus the run ID of your best model.
> **Pitfall**: logging metrics without parameters (or the seed) makes the run unreproducible — the whole point is lost.

### Part B — Model registry & versioning (15 min)

Register the best run and load it back **by version**:

```python
mlflow.register_model(f"runs:/{run_id}/model", "sentiment_clf")
model = mlflow.pyfunc.load_model("models:/sentiment_clf/1")
```

> **Checkpoint B** — you loaded version 1 by name, not by path. Write one sentence on why that matters for rollback.
> **Think**: "it worked on my machine" becomes answerable when every artifact has a version and a run ID.

### Part C — Data validation tests (20 min)

```python
# test_data.py
def test_no_nulls():        assert df[FEATURES].isna().sum().sum() == 0
def test_ranges():          assert df["age"].between(0, 120).all()
def test_categories():      assert set(df["class"]).issubset(EXPECTED)
def test_schema():          assert list(df.columns) == EXPECTED_COLUMNS
```

Run `pytest`. Then break the data on purpose and watch a test fail.

> **Checkpoint C** — pytest output showing 4 passing tests, then a deliberate failing run.
> **Pitfall**: tests that only check row counts catch almost nothing. Test *distributions and schema*, not just shape.

### Part D — Detect drift you injected yourself (20 min)

Take your test set and inject drift: shift a numeric feature by +2σ, or swap 30% of one category's rows.

```python
def psi(expected, actual, bins=10) -> float:
    "Population Stability Index: <0.1 stable, 0.1-0.2 watch, >0.2 act."
```

Compute PSI for 3 features before and after injection.

| Feature | PSI (clean) | PSI (drifted) | Verdict |
|---|---|---|---|
| | | | |

> **Checkpoint D** — the table plus one sentence: what would you *do* operationally if PSI crossed 0.2 in production?
> **Pitfall**: drift in one feature may not change accuracy at all. Monitoring inputs catches problems **before** metrics degrade — that is the entire argument for it.

### Part E — Wrap up (5 min)

Write the 5-line monitoring plan you would hand to an on-call engineer.

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-15.ipynb` (or source files) run / start without errors
- [ ] Every **Checkpoint** executed, with evidence (output, screenshot or log)
- [ ] Results collected into **one summary table**
- [ ] Written interpretation present — code alone is not a deliverable
- [ ] Pushed to GitHub with **≥ 2 meaningful commits**

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| MLflow tracking (Part A) | 25 | ≥3 runs logged with params + metrics + artifacts, comparison screenshot shown |
| Registry & rollback (Part B) | 15 | model registered, loaded by version, rollback rationale stated |
| Data tests (Part C) | 25 | 4 meaningful tests, a deliberate failure demonstrated |
| Drift detection (Part D) | 25 | drift injected, PSI computed for 3 features, operational response described |
| Exit ticket | 10 | three questions answered |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add .
git commit -m "feat: complete lab 15"
git push origin main
```

## 8. Exit Ticket · 课后反思

1. What surprised you most today?
2. What would break first if real users hit your system tomorrow?
3. One question you still have.

## 9. 中文摘要

本周解决一个工程现实问题：**模型上线之后怎么办**。

五个要点：
1. **实验追踪解决「这个模型是哪个跑出来的」**：参数、指标、artifact、种子全部记录，MLflow UI 直接对比。
2. **只记指标不记参数等于白记**——复现不了的实验没有价值。
3. **模型注册表让回滚成为可能**：按版本加载（`models:/name/1`），出问题时能退回上一版，而不是重新训练。
4. **数据测试比代码测试更重要**：ML 系统的故障大多来自输入数据变了。测试 schema、取值范围、类别集合，而不只是行数。
5. **PSI 监控输入分布**：<0.1 稳定，0.1-0.2 观察，>0.2 要处理。**单个特征漂移可能完全不影响准确率**——监控输入的意义就是在指标掉之前发现问题。

交付物是一份能交给运维的 5 行监控计划——这是从「学生作业」到「生产系统」的最后一步。
