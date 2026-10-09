# START HERE · Capstone restarts in Week 6

> **Read this once, fully. Then act on §2 before the W6 lab.**
> 一页纸。英文授课，文末有中文要点。

---

## 1. What is changing

Up to now the milestones were *written down* but never *due*. That is on me, not on you.

**From Week 6 the clock restarts:**

- **Nothing before Week 6 is penalised.** The W1–W4 milestones are not counted and no late
  penalty applies to them. 第 6 周之前的里程碑**不追溯、不扣分**。
- **Everything from Week 6 is due, and it is collected.** Every week, in the lab, from the
  repository — not a promise.
- **The M4 milestone moves to W7** (still worth 4 points). M8 in W8 does **not** move.

Why it matters: with a late start, **the honest path is to cut scope, not to promise more.**
Your MVP is authorised to be smaller than the version printed in the project brief — see §4.

---

## 2. Due this week — before the W6 lab

Three things. All three, no exceptions.

| # | What | Where |
|:---:|---|---|
| 1 | **Three candidate topics**, one page each, using [`project-charter-template.md`](project-charter-template.md) | `proposals/01.md`, `02.md`, `03.md` in your repo |
| 2 | **`PROJECT_PLAN.md`** filled in — weekly slot, scope boundary, cut list, biggest risk | repo root |
| 3 | **`DEVLOG.md`**, first entry (one entry per week from here on) | repo root |

**Three real candidates, not one idea split three ways.** The first idea is usually
unimplementable — that is why you bring three. Read [`topic-catalogue.md`](topic-catalogue.md)
(21 seeds) for the *shape* of a project; **copying a seed verbatim loses marks on dimension A.**

---

## 3. The W6 lab: a 15-minute topic sign-off

In the lab you get **90 seconds in front of the class**. Cover exactly three things:

1. **Who is the user?** A specific person doing a specific job. "Everyone" is not a user.
2. **Where does the data come from, and is it legal?** Name the source and the licence.
   If you cannot name it, the topic is not ready.
3. **What dumb baseline will you beat?** Majority class, a rule of thumb, last week's model —
   something. If beating it is trivial, there is no project.

You leave with **one approved topic, a one-line scope, and a cut list** — the things we agreed
you will *not* build.

**Come without proposals and you write them in the room, and the class waits.** No proposal,
no topic.

**Stuck?** Use **D1** from the catalogue: `data/raw/defects.csv` in this repository — 12 480 rows,
no download, no licence risk, and it ships with a real leakage trap. Starting beats choosing
perfectly.

---

## 4. Compressed timeline

M8 in W8 and everything from W9 on is **unchanged**. Only the early weeks were compressed.

| Week | Due (pushed to your repo) | Checked by |
|:---:|---|---|
| **W6** *(week of 12 Oct)* | `PROJECT_PLAN.md` · `proposals/01–03.md` · `DATA.md` v0 · `DEVLOG.md` · first working `src/data/` | 3 real proposals; data loads ≥ 1 000 rows in one command |
| **W7** *(week of 19 Oct)* | **M4 · 4 pts** — `data_card.md` · `src/train.py` · baseline number · **target number** · ablation ≥ 3 rows | runs on a **fresh clone**; baseline + target both committed |
| **W8** *(week of 26 Oct)* | **M8 · 4 pts · midterm checkpoint ★** — running prototype · `DATA.md` v1 · 3-slide deck · main model v1 + error analysis | **live 3-minute demo** (not slides); slide 3 is about failures |
| W9–W12 | pre-trained upgrade → representation upgrade → LLM → retrieval | unchanged |
| **W12** | **M12 · 4 pts** | ≥ 5 failure cases grouped |
| W13–W15 | interface → packaging → tracking & docs freeze | unchanged |
| **W16** | **M16 · 4 pts** — `v1.0` tag · `RETROSPECTIVE.md` | 5-min demo + 8-min defence |

### Authorised smaller MVP

W6–W7 each carry about three normal weeks of work, so the scope is cut **on purpose**:

> **MVP:** one model · one reproducible command · one usable interface · one honest error analysis.
> **Explicitly not expected:** deployment URL, Docker, tracking platform, a second approach to compare.

Those still count as bonus (up to +3) if you get there. They are no longer things you are
expected to do. **Write your cut list in W6, not in W14.**

---

## 5. How the weekly rhythm works

- **Every lab ends with 15 minutes of capstone.** Not homework. Bring your repo.
- **Weekly standup, 60 seconds each, three sentences:** what you pushed (give the **commit hash**),
  what is blocking you, what is next. **No slides.** We read `git log`.
- **Commit hash is the timestamp.** A week with no commit is a week with no progress, however
  much work happened on your laptop.
- **Three consecutive weeks with no commit → a mandatory meeting.** A second trigger caps the
  development-trace section of the rubric at 18/30.

The one rule that outranks everything else:

> **Every line you commit is a line you can explain.** In the W16 defence, "the AI wrote that"
> scores zero on that question and triggers an academic-integrity review.

---

## 6. 中文要点

1. **第 6 周重新起算**：第 6 周之前的里程碑**不追究、不扣分**；从第 6 周起每周必交，按仓库提交记录收。
2. **本周课前必须交三样**：`proposals/01–03.md`（三份**真**候选）、`PROJECT_PLAN.md`、`DEVLOG.md` 第一条。
3. **第 6 周课内 15 分钟立项审定**：每人 90 秒，只讲「用户是谁 / 数据从哪来且许可是什么 / 你要打败的笨基线是什么」。没带提案就当场写。
4. **M4 顺延到第 7 周**（仍 4 分）；**M8 第 8 周不动**——它是全学期最重要的检查点，**现场真跑**，讲失败的那页最值分。
5. **范围已获准缩小**：一个模型 + 一条可复现命令 + 一个可用界面 + 一份诚实误差分析。部署 / Docker / 追踪平台**不再要求**。
6. **每周站会 60 秒，不许用 PPT**，给 commit hash。**连续三周无提交 → 强制约谈。**

---

*Questions: bring them to the lab, not to email the night before the deadline.*
