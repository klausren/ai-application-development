# Capstone Milestones · 16 周里程碑

> One push per week, during the lab. The instructor reviews **commits and `DEVLOG.md`,
> not promises**.
>
> Each row: what you push to the project repo, how this week's lab skill feeds it, and
> what gets checked. Milestones marked **[track]** apply only if you chose that track —
> otherwise do the **[all]** version of that week.
>
> 每周实验课结束前推一次。评的是提交记录和 `DEVLOG.md`，不是口头承诺。标 **[方向]** 的
> 里程碑按选题选做，其余做 **[通用]** 版本。

**Late penalty:** −2 project points per missed milestone, capped at −20.

---

## Summary table 总表

| W | Milestone | Push to repo | Lab skill feeding it | Check |
|:---:|---|---|---|---|
| 1 | Three ideas & plan | `PROJECT_PLAN.md`, `proposals/`, `DEVLOG.md` v0 | env setup, git basics | 3 proposals + plan exist |
| 2 | Topic & data verified | `DATA.md` v0, `data/` pointer | EDA, profiling | data exists, ≥ 1 000 rows |
| 3 | Repo & pipeline | `src/data/`, `src/train.py` stub | sklearn `Pipeline` | pipeline runs |
| 4 | Baseline locked | baseline metric in `experiments/` | metrics, CV, overfitting | number recorded + target committed |
| 5 | First improvement | improved model v1 | NumPy MLP → PyTorch | beats baseline (or honest "did not, here's why") |
| 6 | Ablation | `experiments/ablation.md` | optimiser/regularisation sweep | table with ≥ 3 rows |
| 7 | Main model v1 | `src/models/` frozen | CNN / transfer learning | model + eval script |
| **8** | **Midterm checkpoint** | **prototype + DATA.md v1 + 3-slide deck** | **error analysis** | **live 3-min demo** |
| 9 | Representation upgrade | feature/embedding change | TF-IDF vs BoW | measurable delta |
| 10 | Sequence model **[NLP]** | RNN vs LSTM comparison | padding, LSTM | comparison table |
| 10 | Augmentation **[CV]** | augmentation ablation | transforms | comparison table |
| 11 | Pretrained **[NLP]** | DistilBERT vs baseline | fine-tuning | worth-it analysis |
| 11 | Architecture **[CV]** | backbone comparison | transfer learning | worth-it analysis |
| 12 | RAG **[LLM track]** | retrieval pipeline | embeddings, vector store | ≥ 5 eval questions |
| 12 | Threshold & errors **[all]** | threshold tuning + error analysis | precision/recall tradeoff | chosen operating point |
| 13 | Interface | `src/app/` (CLI / Gradio / API) | agents, Gradio | a user can use it |
| 14 | Packaging | `Dockerfile` (optional) + one-command run | FastAPI, error contract | a grader can run it |
| 15 | MLOps & docs freeze | tracking, `tests/`, `MODEL_CARD.md`, full README, `AI_USE.md` | MLflow, drift, data tests | README is complete; docs freeze |
| 16 | Demo day | final tag `v1.0`, `RETROSPECTIVE.md` | — | 5-min demo + 8-min defence |

---

## W1 · Three ideas + project plan

**Push:** `PROJECT_PLAN.md` + `proposals/01.md`, `02.md`, `03.md` + a stub `DEVLOG.md`
(one entry per week from W1 onward — start the habit now, while there is almost
nothing to write).

**From this week's lab:** you just set up Python and git. Use them for real — one
repo per student, public, with a first commit today.

**Each proposal (1 page, use the charter template):**
- The problem, in one sentence, naming a user
- Where the data would come from, and whether it is legal and available
- A dumb baseline you expect to beat
- The single biggest risk

**Checked:** three real proposals (not one idea split in three) **and** a
`PROJECT_PLAN.md` with a weekly working slot and a cut list. One is usually
unimplementable — that is the point.

**Trap:** "I'll do something with medical images." Which images? From whom? Under what
licence? If you cannot answer in W1, you will not have data in W3.

---

## W2 · Topic approved & dataset verified

**Push:** `DATA.md` v0 + a script or README section proving the data loads; updated
`PROJECT_PLAN.md` (cut list agreed in the W2 meeting).

**From this week's lab:** `info()` / `describe()` / `isna().sum()`. Run them on *your*
data. This is where most projects die, and dying in W2 costs one week instead of six.

**`DATA.md` v0 must contain:**
- Source and licence (a URL, not "from the internet")
- Row count and target distribution
- Missing values per column
- Known or suspected flaws
- The split strategy you intend to use, and **why that kind of split**

**Checked:** ≥ 1 000 samples actually loadable, and the cut list is committed. If you
cannot get the data this week, you change topic now — bring the other two proposals.

**Trap:** dataset found on a blog with no licence. Illegal to ship, impossible to cite.

---

## W3 · Repository & data pipeline

**Push:** `src/data/` (load, clean, split) + `src/train.py` that runs end-to-end and
prints *something*.

**From this week's lab:** the sklearn `Pipeline` — `fit` → `predict` → `evaluate`. Build
your project the same way: cleaning inside a pipeline, never as manual edits to a CSV.

**Requirements:**
- Split lives in code, with the strategy justified (stratified / grouped / time-based)
- No absolute paths — a clean checkout must run without edits
- `requirements.txt` pinned
- `DEVLOG.md` has a W3 entry

**Checked:** `python src/train.py` runs on a fresh clone without edits.

---

## W4 · Baseline locked

**Push:** baseline result recorded in `experiments/results.md` — model, metric, split,
seed — **and** a numeric success target, also committed.

**From this week's lab:** metrics and overfitting. This is where you choose the metric
you will live with all semester, and you must justify it now, before you can be tempted
by results. This is also the first instructor review checkpoint (brief, 10 min).

**Requirements:**
- A **dumb** baseline (majority class, random, or heuristic) — not another model
- A **simple** baseline (logistic regression / small tree / small CNN)
- Your chosen primary metric, with a one-paragraph justification
- A **numeric success target**, written down now

**Checked:** the target number is committed to git. Changing it later requires a commit
message explaining why.

---

## W5 · First improvement

**Push:** model v1 that beats the simple baseline (or a documented failure).

**From this week's lab:** going from a NumPy perceptron to PyTorch. If your project needs
a neural network, this is the week it starts.

**Checked:** a number comparing v1 against the W4 baseline, same split, same metric.
"If it doesn't beat the baseline, say so and explain what you'll try instead" is an
acceptable submission. Silence is not.

---

## W6 · Ablation

**Push:** `experiments/ablation.md` — a table with ≥ 3 rows.

**From this week's lab:** optimiser × regularisation × learning-rate sweeps. Do exactly
that, on your project, and record it.

**Format:**

| Change | Metric | Δ vs previous | Keep? |
|---|---|---|---|
| + dropout 0.3 | 0.782 | +0.014 | yes |
| Adam → AdamW | 0.779 | −0.003 | no |
| lr 1e-3 → 3e-4 | 0.791 | +0.012 | yes |

**Checked:** each row is one change, not three at once. This table is the single
strongest signal on the whole project that you know *why* your model works.

---

## W7 · Main model v1

**Push:** `src/models/` with your main architecture and an evaluation script.

**From this week's lab:** CNNs and transfer learning (or your track's equivalent).
Adapt a pretrained model to your data rather than training from scratch, unless you can
argue otherwise.

**Checked:** `python src/evaluate.py` prints the metric. The model file's provenance is
recorded (which pretrained weights, which licence).

---

## W8 · Midterm checkpoint ★

**Push:** working prototype + `DATA.md` v1 + 3-slide deck.

**From this week's lab:** error analysis. The deck has three slides, and the third one is
about failures.

**3-minute live demo (per student):**
1. What the system does — live, not slides
2. Where you are versus your W4 target
3. The three failure cases that worry you most

**This is the most important checkpoint of the semester.** Students who are behind find
out now, with eight weeks left. The instructor will tell you plainly whether you are on
track, and if not, what to cut.

**Checked:** it runs. A demo that fails to run scores 0 for this checkpoint regardless
of how good the slides are. **"敢讲失败的项目分数更高"** — the slide about failures is
the one the grader pays most attention to.

---

## W9 · Representation upgrade

**Push:** a measurable change in how input is represented.

**From this week's lab:** BoW vs TF-IDF (or the CV equivalent: augmentation strategy,
input resolution, colour space).

**Checked:** delta recorded against W7, one change isolated.

---

## W10 · Sequence model **[NLP]** / Augmentation **[CV]** / Feature set **[tabular]**

**Push:** comparison table.

**From this week's lab:** RNN vs LSTM with padding (NLP), or transforms and augmentation
(CV), or feature selection (tabular).

**Checked:** an honest "was it worth it?" line. If the sequence model lost to TF-IDF,
**say so** — that is a real result and it earns points in section C of the project rubric.

---

## W11 · Pretrained **[NLP]** / Architecture **[CV]**

**Push:** fine-tuned model vs your W10 model.

**From this week's lab:** DistilBERT fine-tuning and cost comparison (or backbone
sweeping for CV).

**Must include:** training time and inference cost next to the metric. A +2 point gain
that costs 40× inference time is a decision, not a win.

---

## W12 · RAG **[LLM track]** / Threshold & error analysis **[all]**

**Push (LLM):** retrieval pipeline with ≥ 5 evaluation questions and scored answers
**Push (all):** threshold tuning with a chosen operating point + written error analysis.

**From this week's lab:** prompt matrix and RAG evaluation, or precision/recall tradeoffs.
This is the third (and last) instructor review checkpoint: scope check, cut-list
revision, "is this still survivable?".

**Checked (all tracks):** ≥ 5 concrete failure cases, grouped into categories, with a
hypothesis for each. This feeds rubric section D directly.

---

## W13 · Interface

**Push:** `src/app/` — a CLI, a Gradio/Streamlit UI, or an API.

**From this week's lab:** ReAct agents and Gradio demos. Make it usable by someone who
has never seen your code.

**Checked:** a stranger can use it without reading the source. For an individual project
the MVP is a documented one-command CLI; an API/UI + Dockerfile is stretch.

---

## W14 · Packaging

**Push:** `Dockerfile` (stretch) **plus** the one-command run contract.

**From this week's lab:** FastAPI, error contracts, load testing.

**Checked:** `python predict.py --input …` (or equivalent) runs from a clean checkout.
Bad input returns a clean error, not a traceback. If `Dockerfile` exists, `docker build`
succeeds and the service answers a request — stretch bonus up to +3.

---

## W15 · MLOps & documentation freeze

**Push:** experiment tracking, `tests/test_data.py`, `MODEL_CARD.md`, complete
`README.md`, `AI_USE.md`, and a complete `DEVLOG.md` (W1–W15).

**From this week's lab:** MLflow tracking, data tests, drift detection.

**Documentation freeze after this week.** Nothing but bug fixes in W16 — you should be
rehearsing, not writing.

**Checked:** clone into a fresh directory and follow your own README. If it doesn't work
for you, it definitely won't work for the grader.

---

## W16 · Demo day

**Push:** final tag `v1.0`; `RETROSPECTIVE.md`.

**Schedule per student:**
- 5 min — live demo
- 8 min — individual defence, one-on-one with the instructor

**Checked:** demo runs live; every claim in the deck traces to a number in the repo;
you can explain every line committed under your name.

---

## What the instructor looks at, weekly · 每周评审清单

For each project, every week, three questions:

1. **Did they push?** (one commit is enough — zero is a signal)
2. **Is it the right thing?** (does this week's push build on last week's, or restart?)
3. **Is the scope still survivable?** (is the cut list being honoured, or is it being quietly ignored? — silent scope creep is the most common W14 cause of failure)
