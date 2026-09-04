# Labs · 实验指导书

Every week's **课时 3–4 (75 min)** is a hands-on lab. This folder holds the student-facing materials.

每个教学周的**后两个课时（75 分钟）**是动手实验，本目录存放面向学生的实验材料。

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

Every `lab-handout.md` follows the same nine sections, so students always know where to look:

| § | Section | Purpose |
|:---:|---|---|
| 1 | Learning Objectives | Know / Do split — what you'll understand vs what you'll be able to build |
| 2 | Before You Start | Environment & reading checklist, plus offline fallbacks for downloads |
| 3 | Lab Tasks | Parts A–E, each with a **time budget**, a **Checkpoint**, and a **Pitfall** |
| 4 | — | (interpretation is written inside the task cells) |
| 5 | Deliverables Checklist | the exact things being graded |
| 6 | Grading Rubric | 100 points, pre-announced |
| 7 | Submission | git commands; commit hash = timestamp |
| 8 | Exit Ticket | 3 reflection questions answered in the notebook |
| 9 | 中文摘要 | Chinese summary of the week's key ideas |

Design rules applied throughout:

- **Checkpoints, not instructions.** Each part ends with a verifiable output, so students can't drift for 20 minutes without noticing.
- **Pitfalls are named explicitly.** Every lab lists the one or two bugs that actually happen (kernel mismatch, `BCEWithLogitsLoss` + sigmoid, padding without packing, test-set tuning).
- **Offline fallbacks.** Any lab needing a download (MNIST, CIFAR-10, HuggingFace models) documents what to do if the network fails — the lab still runs.
- **Honest comparisons.** Deep-learning weeks always require comparing against the simpler baseline from an earlier week, and answering "was it worth it?"

## Weekly Index 周次索引

| Week | Lab | Module | Stack |
|:---:|---|:---:|---|
| 01 | Environment Setup & Your First ML Program | ML Foundations | numpy, pandas, sklearn, git |
| 02 | EDA & Data Cleaning on Titanic | ML Foundations | numpy, pandas, seaborn |
| 03 | The scikit-learn Workflow | ML Foundations | Pipeline, GridSearchCV |
| 04 | Model Evaluation, Overfitting & Regularization | ML Foundations | metrics, Ridge/Lasso |
| 05 | Neural Network Fundamentals (NumPy → PyTorch) | Deep Learning | torch.nn |
| 06 | Training Deep Networks in Practice | Deep Learning | torchvision, TensorBoard |
| 07 | CNNs & Computer Vision | Deep Learning | Conv2d, ResNet-18 |
| 08 | CV Application & Midterm Project Lab | Deep Learning | team project |
| 09 | NLP Fundamentals | NLP & LLM | CountVectorizer, TF-IDF |
| 10 | Word Embeddings & Sequence Models | NLP & LLM | nn.Embedding, LSTM |
| 11 | Transformers & Pre-trained Models | NLP & LLM | HuggingFace Trainer |
| 12 | LLM Prompt Engineering & RAG | NLP & LLM | local LLM, TF-IDF retriever |
| 13 | Generative AI Applications & AI Agents | AI Engineering | Gradio, ReAct loop |
| 14 | Model Deployment & API Engineering | AI Engineering | FastAPI, Docker |
| 15 | MLOps & Production Practices | AI Engineering | MLflow, pytest, drift |
| 16 | Capstone Demo Day | AI Engineering | everything |

## Grading 评分

Labs & quizzes together are **20% of the final grade**, split evenly across the 16 labs.
Each lab is graded out of 100 (rubric in its handout); late work loses 10% per day, up to 3 days.

实验与随堂小测合计占期末成绩 **20%**，16 次实验平均分配。每次实验按指导书内的 Rubric 评 100 分，晚交每天扣 10%，最多 3 天。
