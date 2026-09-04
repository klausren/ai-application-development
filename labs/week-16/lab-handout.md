# Lab 16 · Capstone Demo Day
> **AI Application Development** · Week 16 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 16 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 4 · AI Application Engineering |
| **Stack** | Everything from Weeks 1–15 |
| **Deliverables** | Final repo + 5-minute demo + 1-page retrospective |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Do** demonstrate a working end-to-end AI application to an audience
- **Do** defend your technical choices under questions (metrics, baselines, failure modes)
- **Do** evaluate peer projects with structured, useful feedback
- **Do** write an honest retrospective: what you would do differently with the same 8 weeks

> There is no new material this week. This lab is about **finishing and defending** what you built.

## 2. Before You Start · 课前准备

- [ ] Repository is public and `README.md` explains how to run it in ≤5 commands
- [ ] Demo works on the machine you will present from (test it, do not assume)
- [ ] Every team member can explain the part they did not write

## 3. Lab Tasks · 实验任务

### Part A — Demo readiness check (15 min)

Run through this list; fix anything that fails **before** you present:

1. `git clone` into a fresh folder and follow your own README — does it work?
2. Does the app start in under 60 seconds?
3. What happens if the network drops during the demo? (Have a cached/fallback path.)
4. Is there a **live** demo, not just slides?

> **Checkpoint A** — all four answered in writing, with the fixes you made.
> **Pitfall**: "it worked yesterday" is not a demo plan. Rehearse on the actual machine, with the actual projector and network.

### Part B — The 5-minute demo (30 min each team; you present + watch others)

Suggested structure:

| Min | Content |
|---|---|
| 0:00–0:45 | The problem and who has it |
| 0:45–1:30 | **Live demo** (not a screenshot) |
| 1:30–3:00 | How it works: data → model → serving |
| 3:00–4:00 | Results: your metric vs your baseline |
| 4:00–4:45 | **The biggest failure** and what you learned from it |
| 4:45–5:00 | What you would build next |

> **Checkpoint B** — you presented. Slides/demo files committed to the team repo.
> **Grading note**: teams that honestly present a failure consistently score higher than teams that claim everything worked.

### Part C — Peer review (10 min)

For two other teams, write:

1. **One thing that genuinely worked** (be specific — what exactly?)
2. **One thing you would question** (a metric choice? a data source? a claim?)
3. **One concrete suggestion** they could implement this week

> **Checkpoint C** — two peer reviews submitted, each with all three parts.

### Part D — Retrospective (10 min)

One page, individually:

1. What was the single biggest technical obstacle, and how did you get past it?
2. What would you do differently if you restarted today with what you now know?
3. Which week's material turned out to be most useful in practice? (Be honest — the instructor uses this to tune next year's syllabus.)

> **Checkpoint D** — `RETROSPECTIVE.md` committed to your personal fork of the team repo.

### Part E — Final submission (5 min)

Confirm: repo public · README complete · licence stated · all members contributed commits · LMS link submitted.

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-16.ipynb` (or source files) run / start without errors
- [ ] Every **Checkpoint** executed, with evidence (output, screenshot or log)
- [ ] Results collected into **one summary table**
- [ ] Written interpretation present — code alone is not a deliverable
- [ ] Pushed to GitHub with **≥ 2 meaningful commits**

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Demo readiness (Part A) | 20 | fresh-clone test done, fallback prepared, all four questions answered |
| 5-minute demo (Part B) | 40 | live demo delivered on time, structure followed, failure slide included |
| Peer reviews (Part C) | 20 | two reviews submitted, each specific and actionable |
| Retrospective (Part D) | 10 | honest, specific, committed |
| Final submission (Part E) | 10 | repo public, README complete, contributions documented |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add .
git commit -m "feat: complete lab 16"
git push origin main
```

## 8. Exit Ticket · 课后反思

1. What surprised you most today?
2. What would break first if real users hit your system tomorrow?
3. One question you still have.

## 9. 中文摘要

本周没有新知识，只有一件事：**把做了 8 周的东西讲清楚、守得住**。

五个要点：
1. **README 要在新目录里验证一遍**——`git clone` 到空文件夹，按自己的 README 走一遍，跑不通就现在改。
2. **必须现场演示**，不能只放截图。断网怎么办、启动超过 60 秒怎么办，提前想好退路。
3. **结构建议**：问题 → 现场演示 → 技术链路 → 指标 vs 基线 → **最大的失败**（必答）→ 下一步。
4. **敢讲失败的团队分数更高**：能说清「哪里不行、为什么」说明你真的理解了系统。
5. **队友互评要具体**：「做得好」没用，「你们用 macro-F1 而不是 accuracy 处理不平衡数据，这个选择很对」才有用。

最后一周的 RETROSPECTIVE.md 我会认真看——你们说哪周最有用，明年我就调整哪周。
