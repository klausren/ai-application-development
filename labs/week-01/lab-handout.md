# Lab 01 · Environment Setup & Your First ML Program
> **AI Application Development** · Week 1 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 1 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 1 · Machine Learning Foundations |
| **Stack** | Python 3.11, NumPy, pandas, scikit-learn, Git |
| **Dataset** | Iris (built into scikit-learn) |
| **Deliverables** | `lab-01.ipynb`, `environment.yml`, ≥2 commits |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** the three-command scikit-learn workflow: `fit → predict → evaluate`
- **Know** what `random_state` controls and why fixing it makes experiments reproducible
- **Do** verify your Python environment and read a library version table without panicking
- **Do** train, evaluate and compare two classifiers on the same data
- **Do** initialise a Git repository and push it to GitHub with a meaningful commit history

## 2. Before You Start · 课前准备

```bash
python env-check.py          # shipped in this folder; must print ALL PASS
```

- [ ] `env-check.py` prints **ALL PASS** (if not, work through `setup-guide.html` FAQ first)
- [ ] VS Code / Jupyter kernel shows your course environment (top-right corner)
- [ ] You have a GitHub account and can log in from your terminal

## 3. Lab Tasks · 实验任务

### Part A — Prove your environment works (10 min)

```python
import numpy, pandas, sklearn, torch
print(numpy.__version__, pandas.__version__, sklearn.__version__, torch.__version__)
print("GPU/MPS:", torch.cuda.is_available() or torch.backends.mps.is_available())
```

> **Checkpoint A** — paste your version table and device result into a Markdown cell.
> **Pitfall**: a `ModuleNotFoundError` here means the *kernel* is wrong, not that the package is missing. Switch kernel, don't reinstall.

### Part B — Your first model: `fit → predict → evaluate` (20 min)

```python
from sklearn.datasets import load_iris
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LogisticRegression

X, y = load_iris(return_X_y=True)
X_tr, X_te, y_tr, y_te = train_test_split(X, y, test_size=0.3, random_state=42, stratify=y)
model = LogisticRegression(max_iter=200)
model.fit(X_tr, y_tr)                 # 1. learn from data
preds = model.predict(X_te)           # 2. apply to unseen data
print(model.score(X_te, y_te))        # 3. measure
```

Now train a second model the same way — an `SVC` from `sklearn.svm`.

> **Checkpoint B** — print both accuracies and write 1–2 sentences: which won, and is the gap meaningful on 150 rows?

### Part C — The `random_state` experiment (20 min)

Loop over `random_state` values `[0, 7, 42]`. For each: re-split, retrain **both** models, record test accuracy into a `pandas` DataFrame.

```python
from sklearn.svm import SVC
import pandas as pd
rows = []
for rs in [0, 7, 42]:
    a, b, c, d = train_test_split(X, y, test_size=0.3, random_state=rs, stratify=y)
    rows.append(dict(rs=rs,
                     logreg=LogisticRegression(max_iter=200).fit(a, c).score(b, d),
                     svc=SVC(random_state=rs).fit(a, c).score(b, d)))
pd.DataFrame(rows)
```

> **Checkpoint C** — how much do the numbers move (max − min)? Does the winner stay the same?
> **Think**: if a classmate reports a different "best model", are either of you wrong?

### Part D — Git & GitHub (20 min)

```bash
cd week-01-lab
git init && git branch -M main
printf '__pycache__/\n.ipynb_checkpoints/\n.DS_Store\n' > .gitignore
git add . && git commit -m "feat: week1 lab environment setup"
# create an empty repo on github.com/new, then:
git remote add origin https://github.com/<you>/ai-app-week1-lab.git
git push -u origin main
```

> **Checkpoint D** — `git log --oneline` shows your commits and `git status` is clean.
> **Pitfall**: GitHub no longer accepts account passwords over HTTPS. If prompted, use a Personal Access Token (see setup guide FAQ #8).

### Part E — Wrap up (5 min)

Export your environment (`conda env export > environment.yml` or `pip freeze > requirements.txt`), commit it, and fill in the exit ticket.

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-01.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Every **Checkpoint** cell executed and its output visible in the submitted notebook
- [ ] Markdown cells contain your own sentences (not just copied code output)
- [ ] Pushed to GitHub with **≥ 2 meaningful commits** (`feat: ...` style messages)
- [ ] Repository is public (or the TA is added as collaborator) so it can be graded

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Environment verified (Part A) | 20 | version table + device result present, kernel correct |
| Notebook runs end-to-end | 30 | Restart & Run All passes with no errors |
| Git hygiene | 20 | ≥2 commits, meaningful messages, `.gitignore` present before first commit |
| Model comparison (Parts B–C) | 20 | both models trained, results tabulated, written interpretation included |
| Exit ticket | 10 | all three questions answered in own words |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add lab-01.ipynb
git commit -m "feat: complete lab 01"
git push origin main
```

Then paste your repo URL into the LMS submission box. **A commit hash counts as your timestamp**, not the LMS upload time.

## 8. Exit Ticket · 课后反思 (answer in the last Markdown cell)

1. What was the single most surprising thing you observed today?
2. Which step would you do differently next time, and why?
3. One question you still have (the instructor reads these and answers the best ones next week).

## 9. 中文摘要

本周目标只有一个：把环境跑通，并亲手训练出人生第一个模型。

三个必须理解的点：
1. **fit → predict → evaluate** 是本学期所有实验的骨架，后面只是把 `model` 换成更复杂的东西。
2. **random_state** 控制所有随机来源；固定它，别人的结果才能和你的对上。
3. **Git 提交就是时间戳**——截止以 commit 为准，不是以平台上传时间为准。

常见翻车点：kernel 选错（表现为 import 报错但包其实装了）；GitHub 推送用密码被拒（要 PAT）；`.gitignore` 在第一次 commit 之后才加（等于没加）。
