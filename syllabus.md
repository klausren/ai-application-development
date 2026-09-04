# Syllabus · AI Application Development 课程大纲

| | |
|---|---|
| **Course Title** | AI Application Development · AI 应用开发 |
| **Course Type** | Major Core Course · 专业必修 |
| **Credits** | 4 |
| **Total Hours** | 64 periods — 180 min per week: Lecture 90 min + Lab 75 min + Quiz & Wrap-up 15 min |
| **Target Students** | Junior software engineering majors (international class) · 大三软件工程专业留学生 |
| **Language** | English (with Chinese support) |
| **Prerequisites** | Python programming, data structures, database principles, probability & statistics |
| **Primary Stack** | PyTorch, scikit-learn, Hugging Face Transformers, FastAPI |

## Weekly Schedule 每周安排

Every week is a 180-minute integrated session: **90 min lecture (课时 1–2) + 75 min hands-on lab (课时 3–4) + 15 min quiz & wrap-up**.
Lab guides live in [`labs/week-XX/lab-handout.md`](labs/README.md).

| Week | Topic (EN) | 主题（中文） | Lab (课时 3–4, 75 min) · 实验 |
|:---:|---|---|---|
| 1 | Introduction & Development Environment Setup | 导论与开发环境搭建 | Environment check & first ML program (Iris) |
| 2 | Data Handling Fundamentals for AI | AI 数据处理基础 | EDA & data cleaning on Titanic |
| 3 | Machine Learning Foundations | 机器学习基础 | sklearn workflow: Pipeline + GridSearchCV |
| 4 | ML Applications & Model Evaluation | 机器学习应用与模型评估 | Metrics, thresholds, overfitting & Ridge |
| 5 | Neural Network Fundamentals | 神经网络基础 | NumPy MLP by hand → PyTorch; activations |
| 6 | Training Deep Networks in Practice | 深度网络训练实践 | Optimizer / regularization ablation + TensorBoard |
| 7 | CNNs & Computer Vision | 卷积神经网络与计算机视觉 | Convolution visualisation, CNN, transfer learning |
| 8 | CV Applications & Midterm Project | CV 应用与期中项目 | Project lab: DATA.md, baseline, error analysis |
| 9 | NLP Fundamentals | 自然语言处理基础 | Tokenisation, BoW vs TF-IDF, similarity |
| 10 | Word Embeddings & Sequence Models | 词向量与序列模型 | Embeddings, padding, RNN vs LSTM |
| 11 | Transformers & Pre-trained Models | Transformer 与预训练模型 | Attention viz, DistilBERT fine-tuning, cost comparison |
| 12 | LLMs, Prompt Engineering & RAG | 大语言模型、Prompt 工程与 RAG | Prompt matrix + build & evaluate a RAG pipeline |
| 13 | Generative AI Applications & AI Agents | 生成式 AI 应用与 AI Agent | ReAct agent with tools + Gradio demo |
| 14 | Model Deployment & API Engineering | 模型部署与 API 工程 | FastAPI service, error contract, load test |
| 15 | MLOps & Production Practices | MLOps 与生产实践 | MLflow tracking, data tests, drift detection |
| 16 | Capstone Project Presentations | Capstone 项目展示 | Demo day: 5-min demo, peer review, retrospective |

## Assessment 考核方式

| Item | Format | Weight |
|---|---|:---:|
| Assignments ×3 | Individual | 30% |
| Midterm Project | Team (2–3) | 15% |
| Capstone Project | Team (2–3) | 35% |
| Lab Participation & Quizzes | Individual | 20% |

- Assignment 1: ML Pipeline Project (released W4, due W6)
- Assignment 2: Computer Vision Project (released W7, due W9)
- Assignment 3: NLP Project (released W10, due W12)
- Midterm Project presentations in Week 8; Capstone released W13, presented W16.

## Textbooks 教材

1. Géron, A. — *Hands-On Machine Learning with Scikit-Learn, Keras & TensorFlow*
2. Stevens, Antiga et al. — *Deep Learning with PyTorch*
3. Hugging Face — *Natural Language Processing with Transformers*
