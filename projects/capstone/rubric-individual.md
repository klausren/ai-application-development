# Individual Rubric · 个人评分标准（100 分 → 折算 30%）

> The team rubric grades the artefact. **This one grades you.**
> Two people in the same team can differ by more than 10 final points on this portion.
>
> 小组分评的是作品，本表评的是**你个人**。同一个组里两个人的这部分成绩最多可以差出
> 10 分以上（占总评 3 分）。

---

## Overview 总览

| § | Dimension | Pts | Evidence used |
|:---:|---|:---:|---|
| 1 | Contribution Trace 贡献可追溯性 | 35 | git history, PRs, reviews, issues |
| 2 | Individual Defence 个人答辩 | 30 | W16 one-on-one, 5 min |
| 3 | Peer Evaluation 同行互评 | 20 | teammate ratings with written evidence |
| 4 | Retrospective 个人复盘 | 15 | `RETROSPECTIVE.md` |
| | **Subtotal** | **100** | |
| | **× Peer coefficient** (§5) | ×0.6 – 1.0 | applied to the subtotal |

---

## 1. Contribution Trace · 贡献可追溯性（35 分）

Graded from the git history. **Commits are the record; claims are not.**

| Band | Pts | What the history shows |
|---|:---:|---|
| **Excellent** | 31–35 | Substantive commits spread across **≥ 12 of the 16 weeks**, in your own role area. PRs are reviewable (scoped, with a description). You reviewed **≥ 2 PRs from each teammate** with comments that changed something. You opened or resolved issues. Spikes outside your role exist (a Data Lead trying a model, a Product Lead writing a data test). |
| **Good** | 26–30 | Steady commits across 9–11 weeks. PRs reviewed, though reviews may be light ("LGTM"). Mostly within your role. |
| **Adequate** | 20–25 | Commits cluster in 5–8 weeks or around milestones. Some weeks empty. Little cross-review. |
| **Insufficient** | 0–19 | Commits only in the final two weeks. One giant "final" commit. No reviews of others' work. Or your commits are documentation-only while all code comes from teammates. |

**Hard rules:**

- **Activity gap:** more than **3 consecutive weeks** with no commit from you triggers an
  automatic email check-in. Two triggers → this section capped at 20.
- **Review requirement:** fewer than 2 reviews of each teammate's work → **−6**.
- **Commit quality:** 40 commits that say `fix`, `update`, `asdf` are worth less than
  10 that say `fix: drop duplicate patient IDs before split (leakage risk)`.

### What counts as a substantive commit

| Counts | Does not count |
|---|---|
| Code in `src/`, tests, CI config | Only typo fixes in README |
| Data cleaning or labelling code | Only formatting/import reordering |
| Experiment scripts and configs | Only merge commits |
| Review comments that led to a change | Only changes to `.gitignore` |
| `DATA.md` / `MODEL_CARD.md` sections | Reverting your own broken commit |

---

## 2. Individual Defence · 个人答辩（30 分）

**Week 16, after the team demo. Five minutes, one-on-one with the instructor, no
teammates in the room.**

Format:

1. **2 min** — you explain the part you owned (what you built, the key decision, and
   what you would do differently).
2. **3 min** — instructor questions, deliberately including **two questions outside your
   role**. This is intentional: the course is called AI *Application* Development, and
   you must be able to reason about the whole system.

| Band | Pts | Performance |
|---|:---:|---|
| **Excellent** | 27–30 | Explains own work fluently, including *why* — you can defend a decision that didn't work out and say what you learned. Handles out-of-role questions with reasonable reasoning even when unsure. Can reproduce a result from memory. |
| **Good** | 23–26 | Solid on own work; out-of-role answers are partial but honest ("I didn't write that, but here's how I understand it"). |
| **Adequate** | 18–22 | Can describe own work but not justify it; vague on out-of-role questions. |
| **Insufficient** | 0–17 | Cannot explain code under your own name. Cannot state the project's main metric or main failure mode. |

**Zero rule:** *"I'm not sure, the AI wrote that"* or *"my teammate did it"* about code
committed under your name scores **0 on that question** and triggers an academic-integrity
review. Three such answers → this section is 0 and the case is referred.

**Rescue clause:** if your peer coefficient (§5) drops you, a strong defence is grounds
to request a review of that coefficient. A good defence can restore up to half the
deduction. This exists so that a quiet contributor who does real work is not sunk by a
personality conflict.

---

## 3. Peer Evaluation · 同行互评（20 分）

Submitted confidentially at W15 and W16 (two rounds, so early problems surface while
there is still time to fix them).

Each member rates each teammate — **not themselves** — on four items, 1–5:

1. **Technical contribution** — did their work move the project forward?
2. **Reliability** — did they do what they said, by when they said?
3. **Collaboration** — did they communicate, review, and unblock others?
4. **Initiative** — did they take on work, or wait to be assigned?

**Every rating below 3 or above 4 must be accompanied by a specific written example.**
Ratings without evidence are discarded — this blocks both revenge-scoring and
everyone-gets-a-5 collusion.

| Average rating | Pts |
|---|:---:|
| 4.5 – 5.0 | 20 |
| 4.0 – 4.4 | 17–18 |
| 3.5 – 3.9 | 14–15 |
| 3.0 – 3.4 | 11–12 |
| 2.0 – 2.9 | 5–8 |
| below 2.0 | 0–3, plus a mandatory meeting with the instructor |

---

## 4. Retrospective · 个人复盘（15 分）

`RETROSPECTIVE.md`, written by you alone. Graded on **specificity** — generic text scores
poorly on purpose, because it is the easiest thing to fake.

Answer all four (see [`templates/RETROSPECTIVE.md`](templates/RETROSPECTIVE.md)):

1. What did you personally own, and how did it turn out?
2. What was the single biggest technical mistake, and what did it cost?
3. What would you do differently if you restarted at W1 — concretely?
4. What did you learn from each teammate? *(One specific thing per person.)*

| Band | Pts | Quality |
|---|:---:|---|
| **Excellent** | 14–15 | Concrete and self-critical. Names the actual mistake and its cost ("we lost a week because we split before deduplicating"). Teammate credit is specific ("Mia taught me grouped splitting — I had never used it"). Shows changed judgement, not just a list of tasks. |
| **Good** | 11–13 | Honest and specific on most points; one or two answers are generic. |
| **Adequate** | 8–10 | Describes what happened without evaluating it. "We should communicate better." |
| **Insufficient** | 0–7 | Generic filler, AI-generated text, or missing. Copy-pasting the team retrospective halves this score. |

---

## 5. Peer Coefficient · 同行互评系数

Applied to the subtotal when teammates' ratings indicate a real contribution gap.

Let `Pᵢ` = your average peer rating, `P̄` = the team's average. Ratio `r = Pᵢ / P̄`:

| Ratio `r` | Coefficient | Meaning |
|:---:|:---:|---|
| r ≥ 0.95 | **1.0** | Full credit |
| 0.85 ≤ r < 0.95 | **0.90** | Contributed, noticeably less than others |
| 0.75 ≤ r < 0.85 | **0.80** | Materially less |
| r < 0.75 | **0.60** | Substantially less — instructor meeting required |

**Worked example.** Two students in the same team:

| | Subtotal (§1–4) | Ratio | Coefficient | Individual score | → of 10.5 pts |
|---|---|:---:|:---:|:---:|:---:|
| Ana | 88 | 1.02 | 1.0 | 88.0 | 9.24 |
| Ben | 84 | 0.71 | 0.6 | 50.4 | 5.29 |

Ben's team did well, but Ben's own grade drops by **3.95 points of the final course
grade**. That is the intended size of the penalty: enough to matter, not enough to be
unrecoverable if the rest of the course is strong.

**Safeguards against abuse:**

- Ratings without written evidence are discarded (§3).
- The coefficient is computed from the **average of two rounds** (W15 + W16), so one bad
  week cannot sink you.
- The defence rescue clause (§2) can restore up to half the deduction.
- A team that rates everyone 5/5 while the git history shows one person doing
  everything will have **all three** ratings re-examined against commit data.

---

## 6. Academic integrity · 学术诚信

| Situation | Consequence |
|---|---|
| Code committed under your name that you cannot explain | 0 on the relevant defence question; review triggered |
| Copying another team's repo or a public notebook without attribution | Team score 0 for the project; referred |
| Fabricated or selectively deleted results | Team score 0; referred |
| Undisclosed AI-generated code | −15 on the team score, −10 on the individual score |
| Plagiarised retrospective or peer evaluation | 0 on that section |

Attribution is always cheaper than concealment. Using someone's code and saying so in
`AI_USE.md` costs nothing; hiding it costs the project.

---

## Student checklist · 学生自检

- [ ] I have commits in at least 12 of 16 weeks
- [ ] I have reviewed ≥ 2 PRs from each teammate
- [ ] I can explain every line I committed
- [ ] I can state the project's main metric and its biggest failure mode from memory
- [ ] I wrote my own retrospective, naming a real mistake
- [ ] I rated my teammates honestly, with written examples
