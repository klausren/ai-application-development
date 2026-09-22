# Projects · 项目

The course has one long thread running through all 16 weeks: an **individual capstone
project** worth **50% of the final grade** — the whole of the summative assessment.
Every weekly lab ends with a capstone milestone (Part F), so the project is built
continuously rather than in a Week-15 panic.

这门课有一条贯穿 16 周的主线：**个人大作业**，占期末总评 **50%**（即终结性考核的全部）。
每周实验课的最后一节（Part F）都要求推进一次大作业，所以项目是持续做出来的，
而不是第 15 周突击出来的。

```
projects/
└── capstone/
    ├── README.md                  ← start here 主指导书
    ├── rubric-project.md          ← 作品评分 (100 → 个人表现 90 中占 70%，即 63 分)：repo / 数据 / 建模 / 评估 / 工程 / 接口 / 演示
    ├── rubric-defence.md          ← 答辩与过程 (100 → 个人表现 90 中占 30%，即 27 分)：答辩 / 开发轨迹 / 复盘 / AI 使用
    ├── milestones.md              ← 16 周里程碑
    ├── project-charter-template.md← 选题提案（W1 交三份）
    ├── project-plan-template.md   ← 个人项目计划 + 范围与不做清单（W1）
    └── templates/
        ├── DATA.md                ← 数据文档（W2 起）
        ├── MODEL_CARD.md          ← 模型卡（W4 起）
        ├── DEVLOG.md              ← 每周开发日志（W1–W16）
        └── RETROSPECTIVE.md       ← 个人复盘（W16）
```

## How the 50% splits · 50 分怎么构成

终结性考核占课程总评 **50%**，其内部按 100 分量表计 = **个人表现 90 + 加分项 10**：

```text
Summative (50 pts of the course grade)
  = Individual performance (90 / 100) × 50%
  + Bonus                  (10 / 100) × 50%

    Individual performance (90 / 100)
      = Project score      (rubric / 100) × 0.70  → 63   ← the artefact 作品
      + Defence & process  (rubric / 100) × 0.30  → 27   ← you, and how you worked 你本人
```

The defence/process portion replaces the old "peer evaluation" + "individual portion"
split that teams used. On an individual project there is no peer to evaluate you, so
the same 30% now measures: your **W16 defence**, the **git history and `DEVLOG.md`**,
the **retrospective**, and an honest **`AI_USE.md`**. Two dimensions of the same
artefact cannot differ — the project score *is* the project score.

> The 10-point bonus covers work beyond the brief (extra experiments, open-source
> contributions, performance work, competition/innovation outputs, software-copyright
> filings). It is capped at 10 and cannot lift the course grade above 100.
> See [`capstone/README.md`](capstone/README.md) §8.

## Weekly rhythm · 每周节奏

| When | What |
|---|---|
| Lab Parts A–E | this week's technical skill 本周技术 |
| **Lab Part F** | **push this week's milestone + a `DEVLOG.md` entry to the project repo 推进大作业** |
| End of lab | instructor checks commits and the log, not promises |

Weekly lab handouts: [`labs/week-XX/lab-handout.md`](../labs/README.md) → Part F.
