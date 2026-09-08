# Defence & Process Rubric · 答辩与过程评分标准（100 分 → 折算 30%）

> The project rubric grades the artefact. **This one grades you — your defence, your
> development trace, and how honestly you reported the work.** The artefact lives in
> `rubric-project.md`.
>
> 作品分评的是**你做出来的东西**。本表评的是**你本人**——答辩、开发轨迹与复盘。
> 作品评分见 `rubric-project.md`。

There is **no peer-evaluation coefficient** on an individual project. Your grade is
your own work, measured directly. The signals are the W16 defence, the git history,
the `DEVLOG.md`, and the retrospective — all of which are yours by construction.

---

## Overview 总览

| § | Dimension | Pts | Evidence used |
|:---:|---|:---:|---|
| 1 | Individual Defence 个人答辩 | 45 | W16, 8 min, one-on-one |
| 2 | Development Trace 开发轨迹 | 30 | git history + `DEVLOG.md` |
| 3 | Retrospective 个人复盘 | 15 | `RETROSPECTIVE.md` |
| 4 | AI Use & Academic Integrity AI 使用与学术诚信 | 10 | `AI_USE.md` + §4 below |
| | **Total** | **100** | |

---

## 1. Individual Defence · 个人答辩（45 分）

**Week 16, after the 5-minute demo. Eight minutes, one-on-one with the instructor.**

The whole project is yours, so the defence covers the whole project — not "your part".
Expect questions on data, modelling, evaluation, interface, and engineering. Two of the
questions will deliberately be outside your strongest area, on purpose.

| Format | Duration |
|---|---|
| Walk through the system end-to-end — what you built, the key decision, the one thing you'd reverse | 3 min |
| Instructor questions, covering the full stack (data, model, evaluation, interface, engineering) | 5 min |

| Band | Pts | Performance |
|---|:---:|---|
| **Excellent** | 40–45 | Explains the whole system fluently, including *why*. Can defend a decision that didn't work out and say what you learned. Handles questions outside the strongest area with reasonable reasoning even when unsure. Can reproduce a key result from memory. |
| **Good** | 34–39 | Solid on the system overall; out-of-area answers are partial but honest ("I didn't get to that part — here's how I would have approached it"). |
| **Adequate** | 27–33 | Can describe what the system does but not justify the choices; vague on questions in weaker areas. |
| **Insufficient** | 0–26 | Cannot explain code under your own name. Cannot state the project's main metric, main failure mode, or the size of the data. |

**Zero rule:** *"I'm not sure, the AI wrote that"* or *"I copied it from a tutorial"*
about code committed under your name scores **0 on that question** and triggers an
academic-integrity review. Three such answers → this section is 0 and the case is
referred (§4).

---

## 2. Development Trace · 开发轨迹（30 分）

Graded from `DEVLOG.md` and the git history. **Commits and weekly notes are the
record; claims are not.**

| Band | Pts | What the history shows |
|---|:---:|---|
| **Excellent** | 26–30 | `DEVLOG.md` has one entry per week for **≥ 14 of the 16 weeks**, each with the three lines (did / result / next) plus blocked. Substantive commits spread across **≥ 12 of the 16 weeks**. Commit messages are scoped and say *why*, not just *what* (`fix: drop duplicate patient IDs before split (leakage risk)`). Experiments live in `experiments/`, not in a 600-line cell. |
| **Good** | 22–25 | `DEVLOG.md` present for 10–13 weeks. Steady commits across 9–11 weeks. Most commit messages are meaningful. |
| **Adequate** | 18–21 | Commits cluster in 5–8 weeks or around milestones. `DEVLOG.md` present for 6–9 weeks, sometimes stub-shaped. Some weeks empty. |
| **Insufficient** | 0–17 | Commits only in the final two weeks. One giant "final" commit. `DEVLOG.md` missing or back-filled in W16. |

**Hard rules:**

- **Activity gap.** More than **3 consecutive weeks** with no commit *and* no
  `DEVLOG.md` entry triggers a mandatory check-in. A second trigger → this section
  capped at 18. The cap exists so that "it is just me" is not a reason to disappear.
- **Commit quality.** 40 commits that say `fix`, `update`, `asdf` are worth less than
  10 that say `fix: drop duplicate patient IDs before split (leakage risk)`.

### What counts as a substantive commit

| Counts | Does not count |
|---|---|
| Code in `src/`, tests, CI config | Only typo fixes in README |
| Data cleaning or labelling code | Only formatting/import reordering |
| Experiment scripts and configs | Only merge commits |
| `DATA.md` / `MODEL_CARD.md` / `DEVLOG.md` sections | Reverting your own broken commit |
| Review of a classmate's repo (optional bonus) | Only changes to `.gitignore` |

---

## 3. Retrospective · 个人复盘（15 分）

`RETROSPECTIVE.md`, written by you alone. Graded on **specificity** — generic text scores
poorly on purpose, because it is the easiest thing to fake.

Answer all four (see [`templates/RETROSPECTIVE.md`](templates/RETROSPECTIVE.md)):

1. What did you personally own, and how did it turn out?
2. What was the single biggest technical mistake, and what did it cost?
3. What would you do differently if you restarted at W1 — concretely?
4. What did the project teach you about working alone on a 16-week engineering task?

| Band | Pts | Quality |
|---|:---:|---|
| **Excellent** | 14–15 | Concrete and self-critical. Names the actual mistake and its cost ("I lost four days to a leak between split and dedup"). Shows changed judgement, not just a list of tasks. The "what would I do differently" answer is something you could *actually* start doing next week. |
| **Good** | 11–13 | Honest and specific on most points; one or two answers are generic. |
| **Adequate** | 8–10 | Describes what happened without evaluating it. "I should have started earlier." |
| **Insufficient** | 0–7 | Generic filler, AI-generated text, or missing. |

---

## 4. AI Use & Academic Integrity · AI 使用与学术诚信（10 分）

| Band | Pts | What is in `AI_USE.md` and the repo |
|---|:---:|---|
| **Excellent** | 9–10 | `AI_USE.md` lists every AI tool used, with the *kind* of work each did (boilerplate / debugging / labelling / docstring) and the *kinds* of work it did **not** do (final design decisions, evaluation, writing). A reviewer can cross-check claims against the commit history. |
| **Good** | 7–8 | Tool list present and reasonably specific. Minor gaps (one off-the-cuff use not logged). |
| **Adequate** | 5–6 | A `AI_USE.md` exists but reads like a disclaimer. Vague on what the AI actually did. |
| **Insufficient** | 0–4 | Missing, or contradicted by the code/comments, or not disclosed at all. |

| Situation | Consequence |
|---|---|
| Code committed under your name that you cannot explain | 0 on the relevant defence question; review triggered |
| Submitting someone else's repo, a Kaggle notebook, or a GitHub project as your own | Project score 0; referred |
| Fabricated or selectively deleted results | Project score 0; referred |
| Undisclosed AI-generated code | −15 on the project score, −10 on this section |
| AI-generated `DEVLOG.md` or retrospective, or back-filling them in W16 | 0 on the affected section |

Attribution is always cheaper than concealment. Using someone's code and saying so in
`AI_USE.md` costs nothing; hiding it costs the project.

---

## Student checklist · 学生自检

- [ ] I have `DEVLOG.md` entries for at least 14 of 16 weeks
- [ ] I have substantive commits in at least 12 of 16 weeks
- [ ] I can explain every line I committed
- [ ] I can state the project's main metric, biggest failure mode, and the size of the data from memory
- [ ] I wrote my own retrospective, naming a real mistake and its cost
- [ ] My `AI_USE.md` is honest and complete
