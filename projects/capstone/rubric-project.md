# Project Rubric · 作品评分标准（100 分 → 折算 70%）

> Applies to **the artefact you build** — the repo, the model, the interface and the
> documentation. The other 30% (defence, development trace, retrospective) is in
> `rubric-defence.md`.
>
> 本表评的是**你做出来的作品**本身：仓库、模型、接口与文档。另外 30%（答辩、开发轨迹、
> 复盘）见 `rubric-defence.md`。

---

## Overview 总览

| § | Dimension | Pts | What it really asks |
|:---:|---|:---:|---|
| A | Problem & Requirements 问题定义 | 12 | Do you know who you are serving and what "done" means? |
| B | Data 数据 | 18 | Is the data real, documented, tested, and honestly described? |
| C | Modelling & Technical Depth 建模 | 22 | Did you earn your improvement, or just try things until something worked? |
| D | Evaluation Rigour 评估严谨性 | 16 | Are your numbers trustworthy, and do you know where the model breaks? |
| E | Engineering & Reproducibility 工程 | 14 | Can a stranger run it? |
| F | Interface & Packaging 接口与交付 | 10 | Can a user actually use it? |
| G | Communication 演示与文档 | 8 | Can you explain it in five minutes without overselling? |
| | **Total** | **100** | |

**Gate before scoring:** if the repo does not install and run on a clean machine
following the README, **E is 0/14** and the rest is assessed as-is. No exceptions —
an unrunnable project cannot be evaluated.

**Scope note for an individual project.** The bar is a *complete, honest, runnable*
system, not a large one. Dimension F accepts a documented one-command CLI; Docker and a
deployed URL are stretch goals (bonus, §Modifiers). A smaller project that is finished
and explained beats a bigger one that is half-built — every time.

---

## A. Problem & Requirements · 问题定义（12 分）

| Band | Pts | Description |
|---|:---:|---|
| **Excellent** | 11–12 | A specific user and a specific pain. Success is defined with a **numeric target agreed before modelling** (e.g. "≥ 0.80 macro-F1 on held-out set, < 300 ms per request"). Scope boundaries are explicit: what the system does *not* do. There is evidence of talking to a real user or of a well-constructed proxy user. The cut list from W2 matches what was actually built. |
| **Good** | 9–10 | Clear problem and user, quantitative success criterion present, but the boundary between in-scope and out-of-scope is fuzzy, or the target was written after seeing results. |
| **Adequate** | 7–8 | Problem is understandable, but success is defined only as "high accuracy" or "works well". No user beyond "people who need this". |
| **Insufficient** | 0–6 | No stated user or success metric. The README opens with the model architecture instead of the problem. "I wanted to learn CNNs" is not a problem statement. |

**Common trap:** writing the success metric *after* you see the results. The metric is a
promise you make in W2; changing it later is allowed only if you document why.

---

## B. Data · 数据（18 分）

| Band | Pts | Description |
|---|:---:|---|
| **Excellent** | 16–18 | `DATA.md` gives provenance, licence, collection method, size, and **known flaws** (class imbalance, label noise, sampling bias). Splits are justified for the data type (stratified / grouped / **time-based** — a random split on time series is wrong). Cleaning steps are reproducible as code, not manual edits. Automated data tests exist (`tests/test_data.py`: schema, range, null, leakage checks). Labelling protocol stated, including any AI assistance. |
| **Good** | 14–15 | `DATA.md` complete, splits reasonable, cleaning scripted. Minor gaps: no automated tests, or known flaws not stated, or imbalance acknowledged but not quantified. |
| **Adequate** | 11–13 | Data described and cleaned, but provenance/licence unclear, or the split is questionable, or cleaning happened in a notebook cell that is hard to re-run. |
| **Insufficient** | 0–10 | No `DATA.md`. Unknown or illegal provenance. Data leakage between train and test (duplicates, near-duplicates, or future information). Dataset too small to support the claim being made. |

**Automatic −5:** train/test leakage found by the grader. This is the single most
common fatal flaw in student projects and it invalidates every number you report.

---

## C. Modelling & Technical Depth · 建模（22 分）

| Band | Pts | Description |
|---|:---:|---|
| **Excellent** | 20–22 | A **deliberate progression**: dumb baseline → simple model → improved model, each justified. An **ablation table** shows exactly which change bought which improvement (not just "final model is best"). Hyperparameters were searched systematically and the search space is reported. Every non-trivial choice has a one-line reason in code or docs. When a fancier model *lost* to a simpler one, that is reported and the simple one was kept. |
| **Good** | 17–19 | Baseline + improved model with a comparison table. Most choices justified. Limited ablation — you know the final config is better but not precisely why. |
| **Adequate** | 13–16 | A model is trained and it works, but the path is undocumented or arbitrary ("I tried a few and this was best"). No baseline, or baseline is the same model with different seed. |
| **Insufficient** | 0–12 | No baseline. No justification. A large pretrained model used where a linear model would do, without comparison. Copy-pasted tutorial architecture with no adaptation. |

**The question this section asks:** *if your improvement disappeared tomorrow, would
you know which change to revert?* An ablation table is the answer.

**Note on scale:** a well-executed logistic-regression project with a rigorous ablation
scores higher here than a fine-tuned LLM nobody can explain. Depth is in the reasoning,
not the parameter count.

---

## D. Evaluation Rigour · 评估严谨性（16 分）

| Band | Pts | Description |
|---|:---:|---|
| **Excellent** | 15–16 | Metric choice is **argued** for the problem (why macro-F1 over accuracy for imbalanced classes; why recall over precision for a screening tool). Report includes a confusion matrix and **per-class breakdown**. There is a genuine **error analysis**: ≥ 5 concrete failure cases, grouped into categories, with a hypothesis for each. Limitations are stated plainly. Overfitting/underfitting diagnosed from curves, not guessed. |
| **Good** | 13–14 | Appropriate metric with justification, confusion matrix shown, some error analysis (2–4 cases), limitations mentioned. |
| **Adequate** | 10–12 | Correct metric but no justification. Aggregate number only, no per-class view. Failure cases mentioned in passing without analysis. |
| **Insufficient** | 0–9 | Wrong metric for the problem (accuracy on a 95/5 dataset). Test set tuned repeatedly. No error analysis. Claimed performance contradicted by the shown confusion matrix. |

**Automatic −5:** evidence of tuning on the test set (e.g. dozens of commits each
improving test score, no validation split). Keep a held-out set you touch once.

---

## E. Engineering & Reproducibility · 工程（14 分）

| Band | Pts | Description |
|---|:---:|---|
| **Excellent** | 13–14 | Clones and runs from README on a clean machine. Dependencies pinned. Code is modular (`src/data`, `src/models`, `src/app`), not one 800-line notebook. Seeds set; results reproducible within stated variance. Automated tests exist and pass. Git history is meaningful across the semester (not three giant commits in W16). |
| **Good** | 11–12 | Runs with minor friction. Mostly modular. Pinned dependencies. Some tests. History shows steady work. |
| **Adequate** | 8–10 | Runs only with undocumented manual steps, or only on your machine. Monolithic notebook. No tests. |
| **Insufficient** | 0–7 | Does not run. No README or a README that does not explain how to run it. Single commit the week before the deadline. |

---

## F. Interface & Packaging · 接口与交付（10 分）

> For an individual project the requirement is **a documented one-command entry point**.
> Containerisation and a public URL are stretch goals, not the baseline.

| Band | Pts | Description |
|---|:---:|---|
| **Excellent** | 9–10 | A user can actually call it: a documented `/predict` API or a Gradio/Streamlit UI, **plus** a `Dockerfile` that builds and runs. Graceful error handling — bad input returns a clear error, not a stack trace. Latency measured and reported. |
| **Good** | 7–8 | A documented one-command CLI (`python predict.py --input …`) a grader can run without reading the source, and it works. Container optional; if present it builds. Error handling present but incomplete. |
| **Adequate** | 5–6 | Runs only after undocumented manual steps, or only from inside a notebook. Or Docker exists but does not build. |
| **Insufficient** | 0–4 | No usable entry point at all — the "product" is a notebook cell. |

---

## G. Communication · 演示与文档（8 分）

| Band | Pts | Description |
|---|:---:|---|
| **Excellent** | 8 | 5-minute demo that shows the system working on live input, not slides about the system. 6-slide deck: problem → data → approach → results → failures → what's next. Every claim traceable to a number in the repo. Model card written for a non-expert. |
| **Good** | 6–7 | Clear demo and deck. Minor overclaiming, or the demo is a recording rather than live, or results and claims are slightly out of sync. |
| **Adequate** | 4–5 | Understandable but rushed or slide-heavy. Some claims not backed by evidence. |
| **Insufficient** | 0–3 | No working demo. Deck only. Marketing language where numbers should be. |

---

## Modifiers · 加减分

| Modifier | Effect |
|---|---|
| Repo does not run on a clean machine | **E = 0**, gate applies before anything else |
| Train/test leakage | **−5** on B |
| Test-set tuning | **−5** on D |
| Late milestone (each) | **−2** on the project score, capped at **−20** |
| Stretch work: deployed URL, working Docker image, experiment tracking, data tests, documented negative results | **up to +3** bonus, at instructor's discretion |

---

## Grader's one-page checklist · 评分人速查

- [ ] Does it install and run? *(gate)*
- [ ] Is there a numeric success target agreed before modelling? *(A)*
- [ ] Is `DATA.md` honest about flaws, and is the split appropriate? *(B)*
- [ ] Is there a dumb baseline, and an ablation showing what helped? *(C)*
- [ ] Is the metric argued, and are failures analysed? *(D)*
- [ ] Is the history steady across 16 weeks? *(E)*
- [ ] Can I run it with one command, and does it fail gracefully? *(F)*
- [ ] Is the demo live and are claims traceable? *(G)*
