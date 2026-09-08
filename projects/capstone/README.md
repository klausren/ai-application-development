# Capstone Project · 期末大作业指导书

> **AI Application Development** · **individual project** · **35% of the final grade**
> Artefact portion 70% + Defence & process portion 30%
> 个人项目 · 占期末总评 35% · 作品部分 70% + 答辩与过程部分 30%
> English with Chinese support · 中英双语

---

## 1. What this is · 这是什么

One semester, **one student**, one working AI application.

You will take a problem that matters to somebody, find or build the data, train a model
that actually beats a dumb baseline, wrap it in something a user can touch, and then
stand up and defend every decision you made — because every decision *is* yours.

**The one-sentence test your project must pass:**

> *A stranger can clone your repo, run one command, and use your thing — and can tell
> from your README whether it is any good.*

If your project fails that test, it is a homework assignment, not a capstone.

### Why it is individual · 为什么是个人项目

| | |
|---|---|
| **You own the whole stack** | data → model → interface → docs. No role to hide inside, and nothing is "somebody else's part". |
| **The scope is deliberately smaller** | see §3.5. A one-person project cannot be a three-person project; the brief is written for what one student can actually finish. |
| **The explanation bar is higher** | there is no teammate to explain the model you didn't write. The Week-16 defence covers *all* of it. |
| **Nobody can coast, and nobody can be carried** | no peer evaluation, no contribution coefficient. Your grade is your own work, measured directly. |

### What you are really being graded on

Not "did you use a Transformer". The grade rewards:

| Rewarded | Not rewarded |
|---|---|
| Choosing the *simplest* thing that solves the problem | Stacking a bigger model because it sounds impressive |
| Saying "my metric went from 0.71 to 0.78, and here is the ablation that proves which change did it" | Saying "I tried several models and picked the best" |
| Showing where your model fails, with examples | Hiding the failure cases |
| A repo someone else can run | A notebook that only runs on your laptop |
| Honest reporting of what you did *not* achieve | A glossy deck that overclaims |
| A scope you finished | An ambitious scope you abandoned in Week 14 |

---

## 2. Timeline · 时间线

| Week | Milestone | Due |
|:---:|---|---|
| 1 | Three topic ideas + `PROJECT_PLAN.md` | End of W1 lab |
| 2 | Topic approved by instructor; dataset verified & profiled | End of W2 lab |
| 3 | Repo scaffolded; data pipeline + first baseline | End of W3 lab |
| 4 | Baseline model + metrics + numeric target locked | End of W4 lab |
| 5–7 | Modelling iterations (see your track) | Weekly |
| **8** | **Midterm checkpoint — working prototype + `DATA.md` + 3-slide deck** | **W8 demo** |
| 9–12 | Representation / architecture improvements | Weekly |
| 13 | Usable interface (CLI / Gradio / API) | End of W13 |
| 14 | Packaging & reproducibility (`Dockerfile`, optional deploy) | End of W14 |
| 15 | MLOps (tracking, data tests) + full docs + `DEVLOG.md` complete | End of W15 |
| 16 | **Demo Day: 5-min demo + 8-min individual defence + retrospective** | W16 |

Every week's lab ends with a **Part F capstone milestone** — see
[`labs/week-XX/lab-handout.md`](../../labs/README.md). You push to your project repo
during the lab; the instructor reviews commits, not promises.

---

## 3. Choosing a topic · 选题（师生商定）

### 3.1 The process

1. **W1 — brainstorm.** You write **three** candidate topics using the
   [`project-charter-template.md`](project-charter-template.md). Three, not one: the
   first idea is usually unimplementable, and you need fallbacks.
2. **W2 — 15-minute meeting with the instructor.** Bring the three charters. The
   instructor will point at the one that is feasible and tell you why the others are
   traps. You leave the meeting with **one approved topic, a stated scope, and a cut
   list** (the things you have agreed *not* to build).
3. **W2–W3 — dataset verification.** Before any modelling, prove the data exists and is
   accessible. A topic without data is not a topic.

### 3.2 Hard requirements · 硬性要求

A topic is only acceptable if all six are true:

| # | Requirement | Why |
|:---:|---|---|
| 1 | **≥ 1 000 labelled samples**, or a credible plan to collect/label them | Below this, you cannot measure anything |
| 2 | **Data is legal and obtainable this semester** | Licence, privacy, API cost, scraper legality |
| 3 | **Clear input → output** | "Given X, predict/classify/generate Y" |
| 4 | **A dumb baseline is beatable** | If majority-class already gets 99%, there is no project |
| 5 | **There is a real (or realistically role-played) user** | Otherwise you cannot write requirements |
| 6 | **You can defend the choice in one sentence** | If it takes a paragraph, you don't understand it yet |

### 3.3 Topic tracks · 方向（不是菜单，是参考）

| Track | Example projects | Typical stack |
|---|---|---|
| **Computer Vision** | Steel surface defect detection; plant disease classifier; PCB inspection; sign-language alphabet recognition | CNN, transfer learning (ResNet/EfficientNet), augmentation |
| **NLP / Text** | Domain sentiment analysis; contract clause classifier; resume–job matching; fake-news detection | TF-IDF → DistilBERT, threshold tuning |
| **LLM / RAG / Agent** | Course-assistant over lecture PDFs; lab-report grader; campus FAQ bot with tool calling | Embeddings, vector store, prompt matrix, ReAct agent |
| **Tabular / Forecasting** | Equipment failure prediction; energy load forecasting; student-risk early warning | sklearn pipelines, gradient boosting, time-series split |
| **Multimodal / Speech** | Image captioning for accessibility; keyword spotting; audio tagging | Encoders, cross-attention |

### 3.4 Topics that will be rejected · 会被打回的选题

- "I will train a model on ImageNet" — no engineering, no problem, no data work.
- Anything requiring data you do not have and cannot get by W3.
- Anything requiring labelling 100 000 samples by hand in one semester.
- A Kaggle competition where the leaderboard is the goal and the code is somebody else's notebook.
- Anything involving scraping personal data, faces of real people, or medical records without an explicit plan for consent and deletion.
- Anything that needs a GPU cluster you do not have. Check your compute before W2.

### 3.5 Scope: MVP and stretch · 范围：必做与加分

You are one person with roughly **4–6 hours a week** alongside other courses. The brief
is therefore split in two. **The MVP is what passing looks like; the stretch is what
excellence looks like.** Agree the split with the instructor in W2 and write it into
your `PROJECT_PLAN.md`.

| Layer | Contents | Where it is graded |
|---|---|---|
| **MVP (must ship)** | problem + numeric target · `DATA.md` · reproducible pipeline · dumb + simple baseline · **one** justified improvement with an ablation · honest evaluation with error analysis · one-command entry point (CLI or API) · `MODEL_CARD.md` · `DEVLOG.md` | dimensions A–E, G |
| **Stretch (bonus)** | deployed URL · Docker image · experiment tracking (MLflow/W&B) · data tests · latency/cost benchmark · a second, genuinely different approach compared | dimension F, bonus up to +3 |

**The cut list is part of the plan, not a confession.** A project that ships the MVP and
documents three things it deliberately did not build scores higher than a project that
half-builds seven things. Scope collapse in W14 is the most common way individual
projects fail — plan the cut in W2, not in W14.

---

## 4. Working alone, on purpose · 独立完成意味着什么

You have no teammates, so the safeguards that teams rely on have to be replaced by
things you do yourself.

### 4.1 You own all three hats · 三个角色都是你的

| Hat | What it owns | Artefact |
|---|---|---|
| **Data** | acquisition, cleaning, versioning, labelling, licensing, data tests | `DATA.md`, `src/data/` |
| **Model** | baseline → improvements, ablation experiments, metric choice, experiment tracking | `src/models/`, `experiments/`, `MODEL_CARD.md` |
| **Product** | interface, packaging, documentation, demo | `src/app/` or `predict.py`, `Dockerfile`, `README.md`, demo deck |

You do not need to be equally good at all three. You *do* need all three to exist, and
you need to be able to explain all three in W16 — the defence asks questions in every
area on purpose.

### 4.2 What replaces peer review · 用什么替代同伴审查

| Mechanism | When | Replaces |
|---|---|---|
| **`DEVLOG.md`, one entry per week** | every week, committed with the milestone | the "is anyone invisible?" check — it makes your own progress visible to you and to me |
| **Instructor review #1** | W4 — metric choice and numeric target | a second opinion before you commit to a metric |
| **Instructor review #2 ★** | W8 — midterm checkpoint demo | the biggest course-correction point of the semester |
| **Instructor review #3** | W12 — scope check and cut-list revision | the "is this still survivable?" conversation |
| **Classmate demo feedback (optional)** | W16 demo day | peer perspective; not graded, but the written feedback is yours to keep |

Weekly `DEVLOG.md` entry — three lines, not an essay:

```markdown
## W6 (date)
- Did: dropout + AdamW sweep; 3 rows added to ablation.md
- Result: dropout 0.3 helped (+0.014), AdamW did not (−0.003)
- Next: freeze main model, start error analysis
- Blocked: — (or: waiting on the licence reply for dataset X)
```

**Two rules that matter more than they look:**

- **Every line you commit is a line you can explain.** In the W16 defence,
  "I'm not sure, the AI wrote that" scores zero on that question and triggers an
  academic-integrity review (§6).
- **A 3-week silence triggers a check-in.** More than three consecutive weeks with no
  commit means a mandatory meeting, and a second trigger caps the development-trace
  section at 18/30. This is not a punishment — it is the individual-project equivalent
  of a teammate noticing you have gone quiet.

### 4.3 Your plan document · 计划文档

Fill in [`project-plan-template.md`](project-plan-template.md) in Week 1 and commit it.
It is the conversation you would otherwise have with yourself in Week 14 at midnight:

- Your weekly working slot (repeating, realistic, in your calendar)
- The scope boundary and the cut list
- Your biggest personal risk (usually: "I will start late" / "I will over-scope")
- Fallback plan if the dataset dies
- Environment, branching and commit conventions

---

## 5. Repository requirements · 仓库规范

Minimum structure. Not a suggestion — the grader looks for these paths:

```
your-project/
├── README.md              # what it does, how to run it, what the numbers are
├── requirements.txt       # or environment.yml — pinned versions
├── DATA.md                # provenance, licence, size, splits, known flaws  [template]
├── MODEL_CARD.md          # intended use, metrics, limitations, failure modes  [template]
├── DEVLOG.md              # one entry per week, W1–W16                      (see §4.2)
├── RETROSPECTIVE.md       # what worked, what didn't, what you'd do differently
├── AI_USE.md              # which AI tools you used and for what  (see §6)
├── src/
│   ├── data/              # loading, cleaning, splitting
│   ├── models/            # training, evaluation
│   └── app/               # serving (or predict.py at root)
├── tests/                 # at minimum: data tests + one model smoke test
├── experiments/           # tracked runs, ablation results
└── Dockerfile             # optional (stretch), but it must build if present
```

**Reproducibility bar:** the grader will clone your repo and run the command in your
README. If it fails on a clean machine, that is −14 points on the project rubric before
anything else is assessed.

---

## 6. AI usage policy · AI 使用政策

You are training to be an AI application developer. Using AI tools is not cheating —
**being unable to explain what the tools produced is**.

**Allowed, with disclosure:**
- Copilot / ChatGPT / Claude for boilerplate, debugging, docstrings
- AI-assisted data labelling or augmentation (must be stated in `DATA.md`)
- Pretrained models and public datasets (cite them)

**Required:**
- Commit an `AI_USE.md` listing the tools and what you used them for.
- **You must be able to explain every line you committed.** "The AI wrote that" scores
  zero on that defence question and triggers an integrity review.

**Not allowed:**
- Committing code or text you have not read.
- Submitting someone else's repo, a Kaggle notebook, or a GitHub project as your own.
- Using AI to generate your retrospective or `DEVLOG.md`. These are graded on
  specificity, and generic text is detectable and scores poorly.

---

## 7. Deliverables · 最终交付清单

Submitted by the end of Week 16 — **all ten are yours**:

| # | Deliverable | Evidence |
|:---:|---|---|
| 1 | Public GitHub repo, clean-machine installable | README + clone test |
| 2 | `DATA.md` — provenance, licence, splits, flaws | file |
| 3 | `MODEL_CARD.md` — metrics, intended use, limitations | file |
| 4 | Reproducible training script + tracked experiments | `experiments/` |
| 5 | Automated tests (data + model smoke) | `tests/` |
| 6 | Usable entry point — CLI or API; Docker/deploy optional | one command / URL |
| 7 | 5-minute demo + 6-slide deck | Demo Day |
| 8 | `RETROSPECTIVE.md` | file |
| 9 | `AI_USE.md` | file |
| 10 | Weekly milestone commits + `DEVLOG.md` entries, W1–W16 | git history |

---

## 8. How the 35% is calculated · 35 分怎么算

```
Capstone grade (35 points)
  = Project score      (out of 100) × 0.70 × 35%     ← the artefact 作品
  + Defence score      (out of 100) × 0.30 × 35%     ← you, and how you worked 你本人
```

with one modifier:

- **Late milestone penalty.** Milestones are due at the end of each lab.
  −2 points per late milestone on the project score, capped at −20. The cap exists
  because a project that ships late should still beat one that never ships.

There is **no peer-evaluation coefficient** — nobody is rating your contribution but
you and me, and the evidence is the git history plus the defence.

See [`rubric-project.md`](rubric-project.md) and
[`rubric-defence.md`](rubric-defence.md) for the full rubrics. Milestone-by-milestone
expectations are in [`milestones.md`](milestones.md).

---

## 9. Templates · 模板

| File | Use it when | |
|---|---|---|
| [`project-charter-template.md`](project-charter-template.md) | W1–W2, three copies | 选题提案 |
| [`project-plan-template.md`](project-plan-template.md) | W1, once | 个人计划与范围 |
| [`templates/DATA.md`](templates/DATA.md) | W2, updated continuously | 数据文档 |
| [`templates/MODEL_CARD.md`](templates/MODEL_CARD.md) | W4 onward | 模型卡 |
| [`templates/RETROSPECTIVE.md`](templates/RETROSPECTIVE.md) | W16 | 个人复盘 |
| [`templates/DEVLOG.md`](templates/DEVLOG.md) | W1 onward, weekly | 每周开发日志 |
