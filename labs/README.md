# Labs · 实验指导书

Every week's hands-on lab is an **80-minute** session — the second half of a 180-minute
integrated class: **90 min lecture + 80 min lab + 10 min wrap-up**.

每个教学周的后两个课时（**80 分钟**）是动手实验，本目录存放面向学生的实验材料。

Lab numbering follows the school's official course documents
(课程代码 **52015CC3BV** · 课程标准/教案/教学日历/考试大纲): **实验 0–13**, one per week for
**Week 1–14**. Week 15 is the Responsible-AI seminar and Week 16 is capstone acceptance, so
neither carries a lab number.

实验编号与学校《教学日历》一致：**实验 0–13**，对应 **Week 1–14**；Week 15 为伦理研讨、
Week 16 为综合验收答辩，均不单独编号。

## Structure 目录结构

```
labs/
├── README.md                 ← this index 本索引
└── week-XX/
    ├── lab-handout.md        ← the lab guide 实验指导书（本周任务、检查点、评分标准）
    ├── starter-notebook.ipynb← student notebook with TODO blanks (where available)
    ├── env-check.py          ← environment verifier (Week 1)
    └── setup-guide.html      ← installation guide with FAQ (Week 1)
```

## Lab Handout Template 指导书统一结构

Every `lab-handout.md` follows the same eight sections, so students always know where to look:

| § | Section | Purpose |
|:---:|---|---|
| 1 | Learning Objectives | Know / Do split — what you'll understand vs what you'll be able to build |
| 2 | Before You Start | Environment & reading checklist, plus offline fallbacks for downloads |
| 3 | Lab Tasks | Parts A–F, each with a **time budget**, a **Checkpoint**, and a **Pitfall** |
| 4 | Deliverables Checklist | the exact things being graded |
| 5 | Grading Rubric | 100 points, pre-announced |
| 6 | Submission | git commands; commit hash = timestamp |
| 7 | Exit Ticket | 3 reflection questions answered in the notebook |
| 8 | 中文摘要 | Chinese summary of the week's key ideas |

Design rules applied throughout:

- **Checkpoints, not instructions.** Each part ends with a verifiable output, so students can't drift for 20 minutes without noticing.
- **Pitfalls are named explicitly.** Every lab lists the bugs that actually happen — a missing `net.train()` / `net.eval()` toggle, forgetting to restore the best weights when early stopping, tuning on the test set, `CrossEntropyLoss` fed already-softmaxed logits.
- **Offline fallbacks.** Any lab needing a download (torchvision MNIST, CIFAR-10, HuggingFace models) documents what to do if the network fails — the lab still runs.
- **Honest comparisons.** Every week compares against the simpler baseline from an earlier week and answers "was it worth it?" — a well-documented negative result is a valid deliverable.

## Weekly Index 周次索引

Lab numbers follow the official calendar. **Currently published: Week 1–6 (实验 0–5)**; later
weeks land as the semester progresses.

| Week | CU | Lab | Topic | Module |
|:---:|:---:|:---:|---|:---:|
| 01 | CU1 | 实验 0 | Environment Setup, GPU Verification & Reproducibility | 一 |
| 02 | CU2 | 实验 1 | Linear Regression with Tensors and Autograd | 一 |
| 03 | CU3 | 实验 2 | Data Preparation and Pipelines | 一 |
| 04 | CU4 | 实验 3 | Modelling with `nn.Module` and Controlled Ablations | 一 |
| 05 | CU5 | 实验 4 | Training Loop, Loss and Optimizer — the 3 × 3 controlled experiment | 二 |
| 06 | CU6 | 实验 5 | Model Evaluation, Overfitting and Regularization — six arms, one honest verdict | 二 |
| 07 | CU7 | 实验 6 | CNN image classification + confusion matrix & misclassification analysis *(to be published)* | 二 |
| 08 | CU8 | 实验 7 | Tokenization → vocabulary → embeddings → LSTM → classification *(to be published)* | 二 |
| 09 | CU9 | 实验 8 | Fine-tuning a pretrained model vs Lab 06 trained from scratch *(to be published)* | 三 |
| 10 | CU10 | 实验 9 | Transformer text classification vs Lab 07's LSTM *(to be published)* | 三 |
| 11 | CU11 | 实验 10 | LLM API + strict JSON output and retry strategy *(to be published)* | 三 |
| 12 | CU12 | 实验 11 | Retrieval → generation → citation pipeline and failure analysis *(to be published)* | 三 |
| 13 | CU13 | 实验 12 | Export the model + wrap an HTTP endpoint + P50/P95 latency *(to be published)* | 四 |
| 14 | CU14 | 实验 13 | Experiment tracking + parameter–metric table + monitoring dashboard *(to be published)* | 四 |
| 15 | CU15 | — | Responsible AI seminar: *AI Application Ethics & Safety Review Form* | 四 |
| 16 | CU16 | — | Capstone acceptance and defence | 四 |

Module names 模块名称：**一** AI 应用开发基础与 PyTorch 入门（W1–4）· **二** 深度学习核心技术与模型训练（W5–8）·
**三** 现代 AI 应用：迁移学习、大模型与 RAG（W9–12）· **四** 工程化、部署与综合项目（W13–16）。

**Part F is how the labs connect to the final project** — every lab ends by pushing one
capstone milestone (and a `DEVLOG.md` entry) to your project repo, so the project is built
continuously instead of in a Week-15 panic. See
[`projects/capstone/milestones.md`](../projects/capstone/milestones.md).

## Grading 评分

Labs are graded inside the **formative 50%** of the course: **随堂实验 15 分** (covering 实验 0–13),
alongside 出勤与课堂参与 10 分、阶段评审 15 分、AI 协同记录 10 分. The summative 50% is the
individual capstone project. There is no closed-book final exam.

实验成绩计入形成性考核的「随堂实验 15 分」（覆盖实验 0–13）；终结性 50% 为个人项目成果物。
本课程为考查课，无闭卷笔试。

Each lab is graded out of 100 (rubric in its handout); late work loses 10% per day, up to 3 days.

每次实验按指导书内的 Rubric 评 100 分，晚交每天扣 10%，最多 3 天。
