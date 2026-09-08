# Project Charter · 选题提案模板

> Submit **three** of these in Week 1 (`proposals/01.md`, `02.md`, `03.md`). One per
> candidate topic.
> Each one is at most one page. If you cannot fill a box, that is the answer — the
> proposal is not ready.
>
> W1 提交三份（三个文件，对应三个候选选题），每份最多一页。**填不出来的格子本身就是答案**：
> 说明这个选题没想清楚。

---

## Proposal 02 · 提案二

**Your name / repo name:**

### 1. The problem · 问题

| | |
|---|---|
| **Who has this problem?** | *(a specific person or role — not "everyone", not "society")* |
| **What do they do today, without your system?** | *(the current workaround)* |
| **What does it cost them?** | *(time, money, errors, risk — pick one and quantify if you can)* |

**One-sentence problem statement:**
> Given ______________, the system ______________ so that ______________ can ______________.

### 2. Data · 数据

| | |
|---|---|
| **Source** | *(exact URL or collection method)* |
| **Licence** | *(link to it. "public" is not a licence)* |
| **Size** | *(rows / images / documents, and how you will split them)* |
| **Labels** | *(already labelled? by whom? will you label them? with what tool?)* |
| **Do you have it right now?** | ☐ yes, downloaded ☐ yes, accessible ☐ no — plan: __________ |
| **Known or suspected flaws** | *(imbalance, noise, bias, missingness)* |

### 3. The model · 模型

| | |
|---|---|
| **Input → output** | *(e.g. "256×256 image → one of 6 defect classes")* |
| **Dumb baseline** | *(majority class / random / a simple rule — and its expected score)* |
| **Simple baseline** | *(logistic regression, small CNN...)* |
| **Candidate approach** | *(what you actually want to build)* |
| **Primary metric** | *(and one sentence on why this metric, not accuracy)* |
| **Numeric success target** | *(e.g. "macro-F1 ≥ 0.80 on a held-out test set")* |

### 4. Risks · 风险

| Risk | Likelihood | What you'd do about it |
|---|:---:|---|
| *(e.g. dataset turns out to be only 400 rows)* | H/M/L | |
| | | |
| | | |

### 5. Scope boundary · 边界

**This system will NOT:**

- ______________
- ______________

*(Writing this down now prevents the Week-12 conversation where the project has quietly
become three times bigger.)*

---

## Instructor sign-off · 教师意见（W2 面談后填写）

☐ **Approved** ☐ Approved with changes: ______________ ☐ Rejected — use proposal __

**Scope agreed:**
**Must-have vs nice-to-have:**
**Check-in week:**
