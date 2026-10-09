# Capstone Milestones · 16 周里程碑

> One push per week, during the lab. The instructor reviews **commits and `DEVLOG.md`,
> not promises**.
>
> 每周实验课结束前推一次。评的是提交记录和 `DEVLOG.md`，不是口头承诺。
>
> Each row: what you push to the project repo, how this week's lab feeds it, and what gets
> checked. This table follows the official 16-week spine of course **52015CC3BV**
> (see [`syllabus.md`](../../syllabus.md)) — Week *n*'s lab is **实验 *n*−1**.
>
> 每条里程碑对应官方教学日历的同一周：本周实验即 **实验 (n−1)**。四条模块里程碑
> （**M4 / M8 / M12 / M16**）同时是课程「阶段评审」的评分点，各占 4 分。
>
> Not a text/sequence project? Replace the week's technique with its equivalent from your own
> domain (a backbone comparison instead of a Transformer, for example). The rule that does not
> change: **one change at a time, measured against the same split and the same metric.**
>
> 选题不是文本／序列方向？把该周技术换成你所在方向的等价一步即可。不变的规则是：**一次只改一处，
> 同一切分、同一指标对照。**

**Late penalty:** −2 project points per missed milestone, capped at −20.

> ⚠️ **Scope, effective 2026-10-09 — Weeks 1–4 are superseded.** The W1–W4 milestones were never
> issued with a deadline anyone acted on, so the −2 penalty does **not** apply to them. Their
> content is remapped into **W6** (原 W1+W2: proposals + plan, data pipeline) and **W7**
> (M4: baseline + numeric target). **M8 in W8 and everything from W9 on is unchanged.**
> See [`PUSH-PLAN-2026F.md`](PUSH-PLAN-2026F.md) §2–§3 and [`START-HERE-W6.md`](START-HERE-W6.md).
> The 16-week spine below is kept as the official record.
>
> 第 1–4 周里程碑**已作废、不追溯扣分**（从未形成有效的到期义务）；内容重映射到 **W6**（原 W1+W2）
> 与 **W7**（M4）。**M8 及其后不动。** 下表保留为官方记录。

---

## Summary table 总表

| W | Milestone | Push to repo | Lab skill feeding it | Check |
|:---:|---|---|---|---|
| 1 | Three ideas & plan | `PROJECT_PLAN.md`, `proposals/`, `DEVLOG.md` v0 | 实验 0: environment, GPU check, reproducibility, git repo | 3 proposals + plan exist |
| 2 | Topic confirmed & data reachable | topic sign-off, `DATA.md` v0, `data/` pointer | 实验 1: tensors, autograd, hand-written linear regression | ≥ 1 000 rows load; a reproducible minimal run recorded |
| 3 | Data pipeline & Data Card | `src/data/`, `data_card.md` | 实验 2: custom `Dataset`/`DataLoader`, splits, leakage, augmentation | one command loads and splits; card justifies the split |
| **4** | **M4 · Model v0 (MLP) — Module 1 milestone** | `src/train.py`, first model, ablation table | 实验 3: `nn.Module`, activations, width/depth ablations | **runs on a fresh clone**; baseline + target number committed |
| 5 | First improvement | model v1 vs baseline | 实验 4: training loop, losses, optimiser × learning-rate grid | same split & metric comparison (or an honest "did not") |
| 6 | Evaluation protocol & ablation | `experiments/ablation.md` (≥ 3 rows) | 实验 5: six-arm regularisation, validation-loss verdict | each row changes one thing; validation loss shown, not just accuracy |
| 7 | Main model v1 | `src/models/`, `src/evaluate.py`, error analysis | 实验 6: CNN classification, confusion matrix, misclassification | metric prints; ≥ 3 concrete failure cases |
| **8** | **M8 · Midterm checkpoint ★ — Module 2 milestone** | prototype + `DATA.md` v1 + 3-slide deck | 实验 7: sequence models — tokenisation → embeddings → LSTM | **live 3-min demo**; slide 3 is about failures |
| 9 | Pre-trained upgrade | fine-tuned vs from-scratch comparison | 实验 8: transfer learning — fine-tune vs train from scratch | delta + training/inference cost |
| 10 | Representation upgrade | Transformer (or equivalent) vs M9 | 实验 9: attention & Transformer vs the M7/M8 LSTM | one change isolated; a "was it worth it?" line |
| 11 | LLM integration | prompt matrix, strict-JSON output, retry log | 实验 10: LLM API, prompt engineering, structured output & retries | output is machine-parseable; cost & latency reported |
| **12** | **M12 · Retrieval / operating point — Module 3 milestone** | RAG chain **or** threshold tuning + error analysis | 实验 11: retrieval → generation → citation, failure analysis | **≥ 5 failure cases** grouped, each with a hypothesis |
| 13 | Usable interface | `src/app/` (CLI / HTTP endpoint) | 实验 12: model export, HTTP serving, P50/P95 latency | a stranger can use it; latency measured |
| 14 | Tracking, versioning & monitoring | experiment tracking + parameter–metric table | 实验 13: MLOps — tracking, versioning, monitoring, drift | reproducible from a clean checkout; runs traceable to a commit |
| 15 | Responsible AI & documentation freeze | `MODEL_CARD.md`, ethics review form, full README, `AI_USE.md`, complete `DEVLOG.md` | CU15 seminar: fairness, explainability, safety review | review form complete; **docs freeze** |
| **16** | **M16 · Acceptance & defence — Module 4 milestone** | final tag `v1.0`, `RETROSPECTIVE.md` | — | 5-min demo + 8-min individual defence |

---

## W1 · Three ideas + project plan

**Push:** `PROJECT_PLAN.md` + `proposals/01.md`, `02.md`, `03.md` + a stub `DEVLOG.md`
(one entry per week from W6 onward — start the habit now, while there is almost
nothing to write).

**From this week's lab (实验 0):** you just built an environment, verified the GPU, and pinned
reproducibility — seed, config, versions. Use them for real: one repo per student, with a first
commit today, and the same three reproducibility facts written down in the project README.

**Each proposal (1 page, use the charter template):**
- The problem, in one sentence, naming a user
- Where the data would come from, and whether it is legal and available
- A dumb baseline you expect to beat
- The single biggest risk

**Checked:** three real proposals (not one idea split in three) **and** a
`PROJECT_PLAN.md` with a weekly working slot and a cut list. One is usually
unimplementable — that is the point.

**Trap:** "I'll do something with medical images." Which images? From whom? Under what
licence? If you cannot answer in W6, you will not have data in W7.

---

## W2 · Topic confirmed & data reachable

**Push:** the signed-off topic (updated `PROJECT_PLAN.md`) + `DATA.md` v0 + a script or README
section proving the data loads + one reproducible minimal run in `experiments/`.

**From this week's lab (实验 1):** you wrote a linear model by hand from tensors and autograd,
and you recorded the four facts that make a result reproducible — data, seed, hyper-parameters,
result. Do exactly that for your own dataset: load it into tensors and produce one number you
can regenerate with one command. Nothing fancy yet.

**`DATA.md` v0 must contain:**
- Source and licence (a URL, not "from the internet")
- Row count and target distribution
- Missing values per column
- Known or suspected flaws
- The split strategy you intend to use, and **why that kind of split**

**Checked:** ≥ 1 000 samples actually load from a fresh checkout, and the cut list is committed.
If you cannot get the data this week, you change topic now — bring the other two proposals.

**Trap:** dataset found on a blog with no licence. Illegal to ship, impossible to cite.

---

## W3 · Data pipeline & Data Card

**Push:** `src/data/` (load, clean, split) + `data_card.md` + `src/train.py` that runs end-to-end
and prints *something*.

**From this week's lab (实验 2):** the custom `Dataset` / `DataLoader`, the split you can justify,
the leakage you learned to spot, and the Data Card with provenance, scale, quality issues and
augmentation policy. This is where most projects die, and dying in W3 costs one week instead of six.

**Requirements:**
- Split lives in code, with the strategy justified (stratified / grouped / time-based)
- No absolute paths — a clean checkout must run without edits
- `requirements.txt` pinned
- `DEVLOG.md` has a W3 entry

**Checked:** `python src/train.py` runs on a fresh clone without edits; the Data Card answers
"what is in this data and what is wrong with it".

**Trap:** cleaning a CSV by hand and committing the edited file. The cleaning step must be code
someone else can re-run.

---

## W4 · M4 · Model v0 (MLP) — **Module 1 milestone (4 pts)**

**Push:** `src/train.py` with a real (small) neural network, the width/depth ablation table, a
recorded baseline in `experiments/results.md`, and a **numeric success target**, also committed.

**From this week's lab (实验 3):** the canonical `nn.Module`, why the activation function is what
buys you non-linearity, and the width/depth ablation you just ran. That ablation table is the
first instalment of the table you will keep all semester.

**Requirements:**
- A **dumb** baseline (majority class, random, or heuristic) — not another model
- A **simple** baseline (logistic regression / small tree)
- Your chosen primary metric, with a one-paragraph justification
- A **numeric success target**, written down now, plus the ablation table

**Checked:** the integrated module quiz is complete, `python src/train.py` runs on a fresh clone
and prints **both** train and validation metrics, and the target number is committed. Changing it
later requires a commit message explaining why.

---

## W5 · First improvement

**Push:** model v1 that beats the simple baseline (or a documented failure), plus the optimiser ×
learning-rate grid you ran.

**From this week's lab (实验 4):** the five-step training loop, three loss functions, and the
3 × 3 optimiser × learning-rate grid. Run that grid on *your* model — this is the first week you
can legitimately claim an improvement, because you now control the loop.

**Checked:** a number comparing v1 against the W4 baseline, same split, same metric.
"If it doesn't beat the baseline, say so and explain what you'll try instead" is an
acceptable submission. Silence is not.

---

## W6 · Evaluation protocol & ablation

**Push:** `experiments/ablation.md` — a table with ≥ 3 rows — and your evaluation protocol written
down (which metric, which split, when the test set is touched).

**From this week's lab (实验 5):** you ran six regularisation arms on a deliberately overfitted
model and learned the honest verdict: regularisation mostly **holds the validation loss down**
instead of raising accuracy, and some interventions make things worse. Do exactly that on your
project, and record the validation loss next to the accuracy — not just the accuracy.

**Format:**

| Change | Metric | Validation loss | Δ vs previous | Keep? |
|---|---|---|---|---|
| + dropout 0.3 | 0.782 | 0.471 | +0.014 | yes |
| Adam → AdamW | 0.779 | 0.480 | −0.003 | no |
| lr 1e-3 → 3e-4 | 0.791 | 0.462 | +0.012 | yes |

**Checked:** each row is one change, not three at once. This table is the single
strongest signal on the whole project that you know *why* your model works.

---

## W7 · Main model v1 + error analysis

**Push:** `src/models/` with your main architecture, `src/evaluate.py`, and the confusion-matrix
error analysis.

**From this week's lab (实验 6):** CNN classification plus the confusion matrix — the table that
turns "86% accurate" into "these two classes are being swapped". Attach at least three concrete
misclassified examples, with your hypothesis for each.

**Checked:** `python src/evaluate.py` prints the metric. The model file's provenance is
recorded (which pretrained weights, which licence, if any). The error analysis names the worst
class pair.

**Trap:** reporting a single aggregate number and calling the analysis done. The confusion
matrix is where the marks are.

---

## W8 · M8 · Midterm checkpoint ★ — **Module 2 milestone (4 pts)**

**Push:** working prototype + `DATA.md` v1 + 3-slide deck.

**From this week's lab (实验 7):** tokenisation, vocabulary, embeddings, sequence models. If your
project involves text or sequences, this is your representation upgrade; if it does not, this is
the week you finish the sequence you started in W4.

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

## W9 · Pre-trained upgrade

**Push:** a fine-tuned model versus your W7 model — same split, same metric.

**From this week's lab (实验 8):** fine-tuning a pre-trained model against training from scratch.
If a pre-trained model applies to your data, this is the week to stop training from zero; the lab
gives you the head-to-head template.

**Must include:** training time and inference cost next to the metric. A +2 point gain
that costs 40× inference time is a decision, not a win.

---

## W10 · Representation upgrade

**Push:** a model whose representation changed — a Transformer instead of a recurrent model, a
different backbone, a different feature set — compared against W9.

**From this week's lab (实验 9):** attention and the Transformer, run against the earlier
sequence model. Same protocol, one change.

**Checked:** delta recorded against W9, one change isolated, and an honest "was it worth it?" line.
If the new model lost, **say so** — that is a real result and it earns points in section C of the
project rubric.

---

## W11 · LLM integration

**Push:** a prompt matrix, the strict-JSON output contract, and a retry log.

**From this week's lab (实验 10):** calling a large language model, prompt patterns, forcing
structured output, and retrying when it does not comply. An output your program cannot parse is
not a feature — this week is where you make it parseable.

**Checked:** the output validates against a schema; failures and retries are logged; cost and
latency have numbers attached.

**Trap:** trusting one lucky response. Run the same prompt several times before you commit.

---

## W12 · M12 · Retrieval / operating point — **Module 3 milestone (4 pts)**

**Push (RAG):** retrieval pipeline with ≥ 5 evaluation questions and scored answers.
**Push (all projects):** the chosen operating point (threshold tuning) + written error analysis.

**From this week's lab (实验 11):** retrieval → generation → citation, and the failure analysis
that tells you which part of the chain broke. This is the third (and last) instructor review
checkpoint: scope check, cut-list revision, "is this still survivable?".

**Checked (all projects):** ≥ 5 concrete failure cases, grouped into categories, with a
hypothesis for each. This feeds rubric section D directly.

---

## W13 · Usable interface

**Push:** `src/app/` — a CLI, a UI, or an HTTP endpoint; plus the model export you served.

**From this week's lab (实验 12):** export the model, wrap it in an HTTP endpoint, and measure
P50/P95 latency. Make it usable by someone who has never seen your code.

**Checked:** a stranger can use it without reading the source. Latency numbers are reported.
For an individual project the MVP is a documented one-command CLI or endpoint; a container is stretch.

---

## W14 · Tracking, versioning & monitoring

**Push:** experiment tracking, a parameter–metric summary table, and a monitoring/drift check.

**From this week's lab (实验 13):** tracking runs, versioning data and models, watching for drift.
Gather the numbers currently scattered across notebooks into one table a grader can audit.

**Checked:** clone into a fresh directory and follow your own README. If it doesn't work
for you, it definitely won't work for the grader. Every reported number traces to a commit
and a tracked run.

---

## W15 · Responsible AI & documentation freeze

**Push:** `MODEL_CARD.md`, the completed ethics & safety review form, a complete `README.md`,
`AI_USE.md`, and a complete `DEVLOG.md` (W6–W15).

**From this week's seminar (CU15):** fairness, explainability and safety — the same questions the
review form asks about your own system. Expect at least one honest "we do not know" in there;
that is a finding, not a failure.

**Documentation freeze after this week.** Nothing but bug fixes in W16 — you should be
rehearsing, not writing.

**Checked:** the review form is complete, and the claims in your README match what the code
actually does.

---

## W16 · M16 · Acceptance & defence — **Module 4 milestone (4 pts)**

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

Module milestone reviews land in **W4 / W8 / W12 / W16** — 4 points each, 15 points total
inside the formative assessment (阶段评审 15 分). **M4 is delivered in W7** this run (see the scope
note at the top); M8 / M12 / M16 keep their official weeks.
