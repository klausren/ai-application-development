# Team Agreement · 团队协议

> Fill in during the Week 1 lab, commit it, and mean it.
> The point of this document is to have the awkward conversation in Week 1, when it is
> cheap, instead of in Week 14, when it is not.
>
> W1 实验课上写完并提交。这份文件的意义在于：把尴尬的对话放在第一周（那时还便宜），
> 而不是第十四周（那时已经很贵）。

---

## 1. Team · 组员

| Name | Student ID | Role | GitHub handle | Contact |
|---|---|---|---|---|
| | | Data Lead | | |
| | | Model Lead | | |
| | | Product Lead | | |

**Team name / repo name:**

## 2. Logistics · 协作方式

| | |
|---|---|
| **Weekly meeting time** | |
| **Channel** | *(WeChat / Slack / Discord — one place, not four)* |
| **Response expectation** | *(e.g. "reply within 24 h on weekdays")* |
| **Shared doc / board** | |

## 3. Roles · 分工

| Role | Owns | Not their job alone |
|---|---|---|
| **Data Lead** | acquisition, cleaning, `DATA.md`, `tests/test_data.py` | choosing the metric |
| **Model Lead** | baseline → improvements, ablation, `MODEL_CARD.md` | deciding what data to collect |
| **Product Lead** | API/UI, Docker, README, demo | writing the model |

**Everyone, regardless of role:**

- Reviews at least 2 PRs from each teammate before W15 *(graded)*
- Can explain the whole system in the W16 individual defence *(graded)*
- Pushes something substantive most weeks *(graded)*

## 4. When things go wrong · 出问题怎么办

These are the questions teams avoid. Answer them now.

| Situation | Our agreement |
|---|---|
| Someone misses a milestone | *(e.g. "tell the group before the deadline, not after; two misses → we raise it with the instructor")* |
| Someone goes quiet for a week | |
| We disagree on a technical choice | *(default suggestion: build the cheaper one first and measure — data beats opinions)* |
| The work turns out to be unevenly split | |
| Someone wants to change the topic after W4 | |
| A member has to leave the team (illness, withdrawal) | |

## 5. Technical conventions · 技术规范

| | |
|---|---|
| **Branching** | *(e.g. `main` protected, work on `feat/<thing>`)* |
| **PR rule** | *(e.g. "no self-merging; one reviewer who didn't write it")* |
| **Commit style** | *(e.g. `feat:` / `fix:` / `docs:` — see the lab handouts)* |
| **Environment** | *(conda / venv; `requirements.txt` pinned)* |
| **Code review turnaround** | *(e.g. "within 24 h")* |

## 6. AI tooling · AI 工具约定

| | |
|---|---|
| Which AI tools will we use? | |
| What for? | *(boilerplate? debugging? labelling? — be specific)* |
| Rule we all follow | *(e.g. "nobody commits code they haven't read")* |

## 7. Signatures · 签字

By committing this file, all three of us agree to the above.

- ______________  Date: ______
- ______________  Date: ______
- ______________  Date: ______
