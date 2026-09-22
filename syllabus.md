# Syllabus · AI Application Development 课程大纲

> 本大纲与学校提交的《课程标准 / 教案 / 教学日历 / 考试大纲》（课程代码 **52015CC3BV**）保持一致，是课件仓库的口径源。

| | |
|---|---|
| **Course Code 课程编号** | 52015CC3BV |
| **Course Title** | AI Application Development · AI 应用开发 |
| **Department 开课单位** | 软件学院 · 软件与大数据技术系 · School of Software |
| **Course Type 课程类别** | 理论课（必修／限选）· Undergraduate |
| **Credits 学分** | 4 |
| **Hours 学时** | 总计 **64**（理论 48 + 实践 16）· 每周 4 学时，一次课 |
| **Weekly Rhythm** | 180 min per week: 讲授 90 min（复习导入 10 + 新课讲授 80）+ 随堂实验 80 min + 小结与作业 10 min |
| **Target Students** | 软件工程（来华项目）/ 2024 级 / 本科 · 授课班级：留软工 24401 |
| **Language** | English-taught (bilingual slides + Chinese summaries) · 英文授课、双语课件 |
| **Prerequisites 先修课** | 程序设计基础（Python 或 Java）、数据结构、高等数学／线性代数基础、机器学习基础 |
| **Primary Stack 技术栈** | Python · PyTorch · Hugging Face Transformers · FastAPI |
| **Primary Textbook 教材** | 《动手学深度学习（PyTorch 版）》（阿斯顿·张、李沐 等，人民邮电出版社） |

## Modules 模块与里程碑

| 模块 | 名称 | 周次 | 里程碑评审 |
|:---:|---|:---:|:---:|
| **模块一** | AI 应用开发基础与 PyTorch 入门 | W1–4 | W4（4 分） |
| **模块二** | 深度学习核心技术与模型训练 | W5–8 | W8（4 分） |
| **模块三** | 现代 AI 应用：迁移学习、大模型与 RAG | W9–12 | W12（4 分） |
| **模块四** | 工程化、部署与综合项目 | W13–16 | W16（4 分） |

## Weekly Schedule 每周安排

Every week is a 180-minute integrated session: **90 min lecture** (10 min review + 80 min new
content) **+ 80 min hands-on lab + 10 min wrap-up**. This is the split in the official 教案
(教学进程): 复习与导入 10 → 新课讲授 80 → 随堂实验 80 → 小结与作业布置 10.
Lab guides live in [`labs/week-XX/lab-handout.md`](labs/README.md).

| Week | CU | Topic (EN) | 主题（中文） | Lab · 实验 |
|:---:|:---:|---|---|---|
| 1 | CU1 | Introduction to AI Application Development | AI 应用开发导论与岗位认知 | 实验 0：环境搭建与 GPU 验证 · 固定种子跑两次 · 建实验记录仓库 |
| 2 | CU2 | PyTorch Fundamentals: Tensors and Autograd | PyTorch 基础：张量与自动求导 | 实验 1：不用 nn.Module，仅用张量 + autograd 实现线性回归 |
| 3 | CU3 | Data Preparation and Pipelines | 数据准备与管道构建 | 实验 2：自定义 Dataset/DataLoader + 数据卡片 Data Card |
| 4 | CU4 | Neural Networks and Modelling with nn.Module | 神经网络与 nn.Module 建模 | 实验 3：nn.Module 搭 MLP + 有/无激活、宽度深度对照 |
| 5 | CU5 | Training Loop, Loss and Optimizer | 训练循环、损失函数与优化器 | 实验 4：3 种优化器 × 3 组学习率对照 |
| 6 | CU6 | Evaluation, Overfitting and Regularization | 模型评估、过拟合与正则化 | 实验 5：早停 / 权重衰减 / Dropout / 增强 的泛化改善量化 |
| 7 | CU7 | CNNs for Computer Vision | 卷积神经网络与计算机视觉应用 | 实验 6：CNN 图像分类 + 混淆矩阵与错分分析 |
| 8 | CU8 | Sequence Models and Text Data | 序列模型与文本数据处理 | 实验 7：分词 → 词表 → 嵌入 → LSTM → 分类 |
| 9 | CU9 | Transfer Learning and Pretrained Models | 迁移学习与预训练模型 | 实验 8：预训练微调 vs 实验 6 从零训练对照 |
| 10 | CU10 | Attention and Transformers | 注意力机制与 Transformer | 实验 9：Transformer 文本分类 vs 实验 7 的 LSTM |
| 11 | CU11 | Large Language Models and Prompt Engineering | 大语言模型与提示工程 | 实验 10：大模型接口 + 严格 JSON 输出与重试策略 |
| 12 | CU12 | Retrieval-Augmented Generation (RAG) | 检索增强生成（RAG）应用 | 实验 11：检索 → 生成 → 引用 链路与失效分析 |
| 13 | CU13 | Model Deployment and Inference Serving | 模型部署与推理服务 | 实验 12：导出模型 + 封装 HTTP 接口 + P50/P95 时延 |
| 14 | CU14 | MLOps: Tracking, Versioning and Monitoring | MLOps：实验管理、版本与监控 | 实验 13：实验追踪 + 参数-指标对照表 + 监控面板 |
| 15 | CU15 | Responsible AI: Fairness, Explainability and Safety | 负责任 AI：公平性、可解释性与安全 | 研讨：《AI 应用伦理与安全评审表》 |
| 16 | CU16 | Capstone Acceptance and Course Review | 综合项目验收与课程总结 | 项目最终验收与答辩 |

Every week's lab ends with a **capstone milestone** that pushes the individual project forward.
See [`projects/capstone/milestones.md`](projects/capstone/milestones.md).

## Assessment 考核方式

本课程为**考查课**（无闭卷笔试），成績由形成性考核与终结性考核构成。

### 形成性考核 50%

| 项目 | 说明 | 分值 |
|---|---|:---:|
| 出勤与课堂参与 | 到课、课堂活动与提问 | 10 |
| 随堂实验 | 实验 0–13 的完成质量与报告 | 15 |
| 阶段评审 | 模块里程碑 W4 / W8 / W12 / W16 | 15 |
| AI 协同记录 | `AI_USE.md`：AI 出错点与你的修正 | 10 |

### 终结性考核 50%（项目成果物）

| 项目 | 说明 | 分值 |
|---|---|:---:|
| 个人表现 | 本人端到端实现 + 文档 + 开发轨迹（`DEVLOG.md`） | 90 |
| 加分项 | 超出要求的工作（如额外实验、开源贡献、性能优化） | 10 |

> 具体评分维度与分值见《大作业评分标准》。终结性 100 分量表中的**个人表现 90 分**拆成两张
> 各 100 分的评分表，按 70 / 30 折算：
>
> | 评分表 | 权重 | 折合分 |
> |---|:---:|:---:|
> | [`rubric-project.md`](projects/capstone/rubric-project.md) — 作品（仓库 / 数据 / 建模 / 评估 / 工程 / 接口 / 演示） | 70% | 63 |
> | [`rubric-defence.md`](projects/capstone/rubric-defence.md) — 答辩 / 开发轨迹 / 复盘 / AI 使用披露 | 30% | 27 |
>
> 另有**加分项 10 分**（课赛融合 / 科创融合成果、软著材料等），加分后总分不超过 100。

### Capstone 大作业

- **个人项目**（每位学生独立完成，不组队）；题目在 W2 与教师商定。
- 范围以 **MVP + stretch list** 的方式协商确定。
- 项目部分（成果物）+ 答辩与过程部分（W16 答辩 · Git 轨迹与 `DEVLOG.md` · 复盘 · AI 使用披露）。
- 因为项目是个人完成，**不设同伴评价系数**；答辩与过程部分直接以 **Git 历史与每周 `DEVLOG.md`** 为证据。

Full brief: [`projects/capstone/README.md`](projects/capstone/README.md)

## Textbooks 教材与参考资料

1. 《动手学深度学习（PyTorch 版）》—— 阿斯顿·张、李沐 等，人民邮电出版社（主教材，含 d2l 配套代码）
2. PyTorch 官方文档与教程 — <https://pytorch.org/docs/>
3. Hugging Face — *Natural Language Processing with Transformers*
