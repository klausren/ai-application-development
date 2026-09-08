# Project Plan · 个人项目计划

> Fill in during the Week 1 lab, commit it, and **mean it**. This is the conversation
> you would otherwise have with yourself in Week 14 at midnight — have it now, when
> it is cheap.
>
> W1 实验课上写完并提交。这份文件的意义在于：把尴尬和重要的对话放在第一周（那时还便宜），
> 而不是第十四周（那时已经很贵）。所有问题都要**你自己回答**——这恰恰是个人项目最难的
> 地方：没有队友逼你诚实。

---

## 1. You · 你的信息

| | |
|---|---|
| **Name** | |
| **Student ID** | |
| **GitHub handle** | |
| **Email / contact** | |
| **Project repo** | |

---

## 2. The week you'll actually work · 你真正能用的时间

Be honest. "All weekend" is not a schedule; it is a hope.

| | |
|---|---|
| **Fixed weekly slot** | *(e.g. Sun 14:00–18:00, Tue 20:00–22:00)* |
| **Total hours per week** | *(realistic, not aspirational — the course assumes 4–6)* |
| **Other courses / obligations that compete for this slot** | |
| **Plan if I fall one week behind** | *(e.g. "trim the stretch list, talk to the instructor before W8")* |
| **Plan if I fall three weeks behind** | *(this is the cliff — write the answer now)* |

---

## 3. Scope and the cut list · 范围与"不做的事"

Writing down what you will **not** build is the single highest-leverage thing in this
document. It is also the thing you will most want to amend in Week 14 — at which point
the amendment is just a confession.

**This project WILL:**

- ______________
- ______________
- ______________

**This project will NOT (the cut list):**

- ______________
- ______________
- ______________

**MVP vs stretch** (see the brief, §3.5). Tick what is MVP; circle what is stretch.

| Layer | In plan? |
|---|---|
| Reproducible training + one-command eval | ☐ MVP ☐ stretch |
| Working CLI or Gradio/API interface | ☐ MVP ☐ stretch |
| `DATA.md`, `MODEL_CARD.md`, `DEVLOG.md` | ☐ MVP ☐ stretch |
| Ablation table (≥ 3 rows) | ☐ MVP ☐ stretch |
| `Dockerfile` that builds and runs | ☐ MVP ☐ stretch |
| Deployed public URL | ☐ MVP ☐ stretch |
| Experiment tracking (MLflow / W&B) | ☐ MVP ☐ stretch |
| Data tests in `tests/` | ☐ MVP ☐ stretch |
| A second, genuinely different model compared head-to-head | ☐ MVP ☐ stretch |

---

## 4. Three risks and your plan for each · 三个风险

What will go wrong, and what will you do when it does?

| Risk | Likelihood (H/M/L) | What I'll do about it |
|---|:---:|---|
| *(e.g. dataset turns out to be only 400 rows)* | | |
| *(e.g. my baseline already gets 99% accuracy — no room to improve)* | | |
| *(e.g. I start late and miss W4)* | | |
| *(e.g. my Mac can't run the model I want)* | | |

---

## 5. Working alone, on purpose · 独立工作

The hardest part of an individual project is not the modelling. It is the part where
no one is watching.

| | |
|---|---|
| **What will I do when I have not pushed for a week?** | *(book a slot, write in DEVLOG anyway, anything but "do nothing for another week")* |
| **What will I do when I am stuck for two days?** | *(re-read the error trace, reproduce in a notebook, then ask the instructor — with the trace attached, not "it doesn't work")* |
| **What will I do when I am tempted to over-scope?** | *(look at §3 cut list; if it isn't on it, it isn't happening)* |
| **Who is one person I will ask for a 15-minute gut check once a month?** | *(classmate / former classmate / the instructor)* |

---

## 6. Technical conventions · 技术规范

| | |
|---|---|
| **Branching** | *(e.g. `main` protected, work on `feat/<thing>`)* |
| **Commit style** | *(e.g. `feat:` / `fix:` / `docs:` — say why, not what)* |
| **Environment** | *(conda / venv; `requirements.txt` pinned)* |
| **Seed management** | *(where you set the seed; whether you report variance)* |
| **Data location** | *(e.g. `data/raw/` gitignored, pointer in `DATA.md`)* |

---

## 7. AI tooling · AI 工具约定

| | |
|---|---|
| Which AI tools will I use? | |
| What for? | *(boilerplate? debugging? labelling? — be specific)* |
| Rule I will follow | *(e.g. "I will not commit code I have not read")* |
| What I will NOT use AI for | *(final design choices, evaluation, writing the retrospective — list at least one)* |

---

## 8. Instructor sign-off · 教师意见（W2 面談后填写）

☐ **Approved** ☐ Approved with changes: ______________ ☐ Topic rejected — use proposal __

**Scope agreed:** ______________
**Cut list agreed:** ______________
**Check-in week (default W4, W8, W12):** ______________
