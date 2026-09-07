# Capstone Project · 期末大作业指导书

> **AI Application Development** · 3-person team project · **35% of the final grade**
> Team portion 70% + Individual portion 30%
> 三人团队项目 · 占期末总评 35% · 小组部分 70% + 个人部分 30%
> English with Chinese support · 中英双语

---

## 1. What this is · 这是什么

One semester, one team of three, one working AI application.

You will take a problem that matters to somebody, find or build the data, train a model
that actually beats a dumb baseline, wrap it in something a user can touch, deploy it,
and then stand up and defend every decision you made.

**The one-sentence test your project must pass:**

> *A stranger can clone your repo, run one command, and use your thing — and can tell
> from your README whether it is any good.*

If your project fails that test, it is a homework assignment, not a capstone.

### What you are really being graded on

Not "did you use a Transformer". The grade rewards:

| Rewarded | Not rewarded |
|---|---|
| Choosing the *simplest* thing that solves the problem | Stacking a bigger model because it sounds impressive |
| Saying "our metric went from 0.71 to 0.78, and here is the ablation that proves which change did it" | Saying "we tried several models and picked the best" |
| Showing where your model fails, with examples | Hiding the failure cases |
| A repo someone else can run | A notebook that only runs on your laptop |
| Honest reporting of what you did *not* achieve | A glossy deck that overclaims |

---

## 2. Timeline · 时间线

| Week | Milestone | Due |
|:---:|---|---|
| 1 | Form team, sign Team Agreement, draft 3 topic ideas | End of W1 lab |
| 2 | Topic approved by instructor; dataset verified & profiled | End of W2 lab |
| 3 | Repo scaffolded; data pipeline + first baseline | End of W3 lab |
| 4 | Baseline model + metrics locked | End of W4 lab |
| 5–7 | Modelling iterations (see your track) | Weekly |
| **8** | **Midterm checkpoint — working prototype + DATA.md + 3-slide deck** | **W8 demo** |
| 9–12 | Representation / architecture improvements | Weekly |
| 13 | Application integration (agent, UI, or pipeline) | End of W13 |
| 14 | Deployed API + Docker | End of W14 |
| 15 | MLOps (tracking, data tests, drift) + full docs | End of W15 |
| 16 | **Demo Day: 5-min demo + individual defence + retrospective** | W16 |

Every week's lab ends with a **Part F capstone milestone** — see
[`labs/week-XX/lab-handout.md`](../../labs/README.md). You push to your project repo
during the lab; the instructor reviews commits, not promises.

---

## 3. Choosing a topic · 选题（师生商定）

### 3.1 The process

1. **W1 — brainstorm.** Each team writes **three** candidate topics using the
   [`project-charter-template.md`](project-charter-template.md). Three, not one: the
   first idea is usually unimplementable, and you need fallbacks.
2. **W2 — 15-minute meeting with the instructor.** Bring the three charters. The
   instructor will point at the one that is feasible and tell you why the others are
   traps. You leave the meeting with **one approved topic and a stated scope**.
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

- "We will train a model on ImageNet" — no engineering, no problem, no data work.
- Anything requiring data you do not have and cannot get by W3.
- Anything requiring labelling 100 000 samples by hand in one semester.
- A Kaggle competition where the leaderboard is the goal and the code is somebody else's notebook.
- Anything involving scraping personal data, faces of real people, or medical records without an explicit plan for consent and deletion.

---

## 4. Team structure · 三人分工

Three people is small enough that everyone must be load-bearing, and big enough that
someone *will* try to coast. The rules below exist for the second fact.

### 4.1 Roles · 角色（固定一学期）

| Role | Owns | Key artefacts |
|---|---|---|
| **Data Lead** | Acquisition, cleaning, versioning, labelling, licensing, data tests | `DATA.md`, `src/data/`, `tests/test_data.py` |
| **Model Lead** | Baseline → improvements, ablation experiments, metric choice, experiment tracking | `src/models/`, `experiments/`, `MODEL_CARD.md` |
| **Product Lead** | API/UI, deployment, documentation, demo, CI | `app.py`, `Dockerfile`, `README.md`, demo deck |

Fixed for the semester — rotating roles mid-project loses more momentum than it teaches.
Breadth is enforced a different way, in §4.2 and in the individual defence.

### 4.2 Cross-review is mandatory · 交叉审查强制

Specialisation creates silos, and silos let people hide. Therefore:

- **Every PR needs a review from someone who did not write it.** No self-merging.
- **Each member must review at least 2 PRs from each of the other two members** by W15.
  These count toward the individual grade (see `rubric-individual.md`).
- **Every member must be able to explain the whole system**, not just their part. The
  individual defence in W16 asks questions outside your role on purpose.

### 4.3 Working agreements · 协作约定

Fill in [`team-agreement-template.md`](team-agreement-template.md) in Week 1 and commit
it. It forces the conversation you will otherwise have in Week 14 at midnight:

- Meeting time and channel
- What happens when someone misses a milestone (say it out loud now)
- How you resolve a technical disagreement (default: build the cheap one first, measure)
- Branching and commit-message convention

---

## 5. Repository requirements · 仓库规范

Minimum structure. Not a suggestion — the grader looks for these paths:

```
your-project/
├── README.md              # what it does, how to run it, what the numbers are
├── requirements.txt       # or environment.yml — pinned versions
├── DATA.md                # provenance, licence, size, splits, known flaws  [template]
├── MODEL_CARD.md          # intended use, metrics, limitations, failure modes  [template]
├── RETROSPECTIVE.md       # what worked, what didn't, what you'd do differently
├── AI_USE.md              # which AI tools you used and for what  (see §6)
├── src/
│   ├── data/              # loading, cleaning, splitting
│   ├── models/            # training, evaluation
│   └── app/               # serving
├── tests/                 # at minimum: data tests + one model smoke test
├── experiments/           # tracked runs, ablation results
└── Dockerfile
```

**Reproducibility bar:** the grader will clone your repo and run the command in your
README. If it fails on a clean machine, that is −14 points on the team rubric before
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
- **You must be able to explain every line you committed.** In the individual defence,
  "I'm not sure, Copilot wrote that" scores zero on that question and triggers an
  academic-integrity review.

**Not allowed:**
- Committing code or text you have not read.
- Submitting another team's repo, a Kaggle notebook, or a GitHub project as your own.
- Using AI to generate your retrospective or peer evaluations. These are graded on
  specificity, and generic text is detectable and scores poorly.

---

## 7. Deliverables · 最终交付清单

Submitted by the end of Week 16:

| # | Deliverable | Owner | Evidence |
|:---:|---|---|:---:|
| 1 | Public GitHub repo, clean-machine installable | Product Lead | README + clone test |
| 2 | `DATA.md` — provenance, licence, splits, flaws | Data Lead | file |
| 3 | `MODEL_CARD.md` — metrics, intended use, limitations | Model Lead | file |
| 4 | Reproducible training script + tracked experiments | Model Lead | `experiments/` |
| 5 | Automated tests (data + model smoke) | Data Lead | `tests/` |
| 6 | Deployed service (Docker, working API or UI) | Product Lead | live URL / image |
| 7 | 5-minute demo + 6-slide deck | whole team | Demo Day |
| 8 | `RETROSPECTIVE.md` | each member individually | file |
| 9 | `AI_USE.md` | whole team | file |
| 10 | Weekly milestone commits, W1–W16 | whole team | git history |

---

## 8. How the 35% is calculated · 35 分怎么算

```
Capstone grade (35 points)
  = Team score      (out of 100) × 0.70 × 35%
  + Individual score(out of 100) × 0.30 × 35%
```

with two modifiers:

- **Peer-evaluation coefficient.** If your teammates rate your contribution
  substantially below the team norm, your individual score is multiplied by a
  coefficient as low as 0.6. Details in `rubric-individual.md` §3.
- **Late milestone penalty.** Milestones are due at the end of each lab.
  −2 points per late milestone on the team score, capped at −20. The cap exists
  because a project that ships late should still beat one that never ships.

See [`rubric-team.md`](rubric-team.md) and [`rubric-individual.md`](rubric-individual.md)
for the full rubrics. Milestone-by-milestone expectations are in
[`milestones.md`](milestones.md).

---

## 9. Templates · 模板

| File | Use it when | |
|---|---|---|
| [`project-charter-template.md`](project-charter-template.md) | W1–W2, three copies per team | 选题提案 |
| [`team-agreement-template.md`](team-agreement-template.md) | W1, once per team | 团队协议 |
| [`templates/DATA.md`](templates/DATA.md) | W2, updated continuously | 数据文档 |
| [`templates/MODEL_CARD.md`](templates/MODEL_CARD.md) | W4 onward | 模型卡 |
| [`templates/RETROSPECTIVE.md`](templates/RETROSPECTIVE.md) | W16, per person | 个人复盘 |
