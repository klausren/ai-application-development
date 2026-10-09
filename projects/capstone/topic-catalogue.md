# Capstone Topic Catalogue · 选题参考库

> **Read this before you brainstorm. It is a source of leads, not a menu.**
> 21 seeds across 5 tracks, difficulty-labelled, each with a real data lead and a real user.
>
> **在动手想题目之前先读这一页。它是「线索库」，不是「菜单」。**
> 21 个种子，5 个方向，标注难度，每个都给一条真实的数据线索和一个真实用户。

| | |
|---|---|
| **Who this is for** | 2026-2027 学年第 1 学期 · `52015CC3BV` AI Application Development · 留软工 24401 · 约 50 人 |
| **When you use it** | Before W6, *before* you write `proposals/01.md … 03.md` |
| **What it does not do** | It does not choose for you, and it does not replace your three proposals. |
| **Companion files** | [`project-charter-template.md`](project-charter-template.md) · [`milestones.md`](milestones.md) · [`rubric-project.md`](rubric-project.md) |

---

## 0. Three rules · 三条铁律

**① Copying a seed verbatim loses you marks.** Dimension A (12 pts) asks for *a specific user and
a specific pain*. If your canteen-recognition proposal says "visually impaired students" but you
never talked to one, the instructor will find out in the W6 sign-off. Take the **shape** of a seed;
supply **your own** user, your own interview, your own numbers.
**逐字照抄种子 = A 项直接掉分。**「目标用户」必须是你能说出访谈对象的人。

**② One seed ≠ one project.** You have three dials. Turn at least one of them:

| Dial | Example (from seed V1, waste sorting) |
|---|---|
| **Change the user** | 保洁员 → 宿舍楼管（只关心有害垃圾）→ 校咖啡店（只关心杯盖/纸杯） |
| **Change the data** | TrashNet 6 类 → 只用本校自采 4 类 → 自采 + 反光/弱光专项子集 |
| **Add a constraint** | 加「不确定就拒识」→ 加「P95 < 300 ms」→ 加「只用 ≤ 2 M 参数的模型」 |

**③ Your three proposals must be three different bets.** Do not submit "image classification",
"image classification with a different dataset", "image classification but bigger". A good trio:
one vision (or audio) + one text + one tabular. That way, when the W6 sign-off kills your first choice, you
still have two live options.
**三份提案必须是三个方向**，理想组合 = 一个视觉/音频 + 一个文本 + 一个表格。

> ⚠️ **All numeric targets in this catalogue are reference magnitudes, not your commitment.**
> Look at the actual class distribution first, then write your own number **before you model**.
> A target written after you see the results is capped at 10/12 on dimension A.
> 本清单里的数字目标值只是**量级参考**，不是你的承诺；你必须自己看过数据分布再定，
> 并且**在开始建模之前**写下来。

---

## 1. Difficulty scale · 难度标尺

You have **4–6 hours a week** and roughly **32 out-of-class hours** for this project. "Moderate"
here means: *one person can finish it in 16 weeks and still write an honest test.*

| | Meaning · 含义 | What it costs you |
|:---:|---|---|
| **★☆☆** | Data ready-made, standard task, one improvement axis. · 数据现成、任务标准、一个改进轴。 | Fast to start — but **easy projects score low on C and D** unless you buy depth with rigour (better splits, better failure analysis), not with a bigger model. |
| **★★☆** | **The recommended band.** Data ready-made or self-collectable, 1–2 improvement axes, a clear baseline, and a failure mode you can actually analyse. · **推荐区间。** | Normal. This is what the brief is written for. |
| **★★★** | Requires a self-built dataset, external annotation, or designing the *evaluation* itself. · 需自建数据集／外部标注，或评价方案本身要设计。 | Doable, but **you must have the data in hand by W6** and your cut list must be written in W6. |

**Distribution of the 21 seeds:** ★☆☆ 3 · **★★☆ 13** · ★★★ 5. Thirteen of twenty-one sit in the
moderate band — that is deliberate.

### Compute badges · 算力徽章

| | Meaning |
|:---:|---|
| 💻 | CPU only is enough (tabular, small text classification). 纯 CPU 可完成。 |
| 🖥️ | One consumer GPU **or** free Colab/Kaggle notebook (most CV, audio, BERT fine-tuning). 单卡或免费额度。 |
| ⚠️ | Needs more than you have. **Do not pick these.** 算力超出，不要选。 |

---

## 2. Quick-pick table · 速选表

Scan this, shortlist three, then read the full card.

| # | Track | Topic (EN) | 中文题名 | 难度 | 算力 | 数据是否现成 | 主要坑 |
|:---:|:---:|---|---|:---:|:---:|:---:|---|
| **V1** | Vision | Campus waste-sorting assistant | 校园垃圾分类助手 | ★★☆ | 🖥️ | 部分（自采） | 自采背景单一 |
| **V2** | Vision | Greenhouse leaf-disease triage | 校植物园叶片病害初筛 | ★★☆ | 🖥️ | ✅ | 公开集是实验室照，现场会崩 |
| **V3** | Vision | Lab meter reading | 实验室仪表自动读数 | ★★★ | 🖥️ | 自采 | 是回归不是分类 |
| **V4** | Vision | ASL fingerspelling for a service desk | 静态手语指拼识别 | ★★☆ | 🖥️ | 自采 + 公开 | 随机切分会虚高 |
| **T1** | Text | Bilingual campus-service intent router | 中英双语校园事务意图分类 | ★★☆ | 💻🖥️ | ✅ | 类别要收敛到 8–12 |
| **T2** | Text | Regulation Q&A by retrieval | 校园规章检索式问答 | ★★☆ | 💻 | ✅ | 必须做引用与拒答 |
| **T3** | Text | Notice → structured fields | 校园通知信息抽取 | ★★★ | 🖥️ | 自建（公开来源） | 标注 1 000 条是硬活 |
| **T4** | Text | Duplicate question clustering | 学生提问去重聚类 | ★☆☆ | 💻 | 自建 | 太容易，靠"严谨"取胜 |
| **C1** | LLM/RAG | Course assistant over this repo | 本课程资料助教（RAG） | ★★★ | 💻🖥️ | ✅ | API 费用；缺评测集 |
| **C2** | LLM/RAG | Lecture transcript → structured notes | 讲稿转结构化纪要 | ★★☆ | 💻 | ✅ | 录音须同意 |
| **C3** | LLM/RAG | Receipt field extraction, strict JSON | 票据字段抽取 | ★★☆ | 💻 | 自采 + 公开 | 票据含个人信息 |
| **C4** | LLM/RAG | Prompt-injection robustness tester | 提示注入鲁棒性测试 | ★★☆ | 💻 | 自建 | 要防"变安全了但也变笨了" |
| **D1** | Tabular | The course's own messy steel table 🟢 | 课程自带工艺数据缺陷分类（保底） | ★☆☆ | 💻 | ✅✅ | 与实验 2/3 重叠 |
| **D2** | Tabular | At-risk student early warning (OULAD) | 学业预警 | ★★☆ | 💻 | ✅ | 别用 accuracy |
| **D3** | Tabular | Machine-failure early warning | 设备故障预警 | ★★☆ | 💻 | ✅ | 极度不均衡 |
| **D4** | Forecasting | Building electric-load forecasting | 楼宇用电负荷预测 | ★★☆ | 💻 | ✅ | 时序切分不能随机 |
| **D5** | Forecasting | Bike-share demand forecasting | 共享单车需求预测 | ★☆☆ | 💻 | ✅ | 太容易，需加约束 |
| **A1** | Audio | Keyword spotting for a hands-free lab | 免手操作的关键词唤醒 | ★★☆ | 🖥️ | ✅ | 误唤醒率才是真指标 |
| **A2** | Audio | Classroom noise-event detection | 教室噪音事件检测 | ★★☆ | 🖥️ | ✅ | 事件级评估≠帧级 |
| **A3** | Audio | Lecture speech → readable, segmented notes | 讲课语音转写并自动分段 | ★★★ | 🖥️ | 自采 | 分段评测要自己设计 |
| **A4** | Audio | Abnormal-sound detection (normal-only) | 异常声检测（只用正常样本训练） | ★★★ | 🖥️ | 自采 + 公开 | 无标签，评价难 |

🟢 = data is already in this repository, no download, no licence question.

---

## 3. Your track → the 16-week spine · 方向与周次主线的对应

`milestones.md` is written on a **text/sequence** spine (W7 CNN → W8 sequence → W9 transfer →
W10 Transformer → W11 LLM → W12 RAG). If your project is not text, **substitute the equivalent
step in your own domain.** The rule that never changes:

> **One change at a time, measured against the same split and the same metric.**
> 一次只改一处，同一切分、同一指标对照。

| W | Text / sequence (default) | Vision | Tabular / forecasting | Audio |
|:---:|---|---|---|---|
| 4 | MLP on TF-IDF features | MLP on flattened pixels | MLP on scaled features | MLP on summary features |
| 5 | Optimiser × LR grid | Optimiser × LR grid | GBDT vs MLP head-to-head | Optimiser × LR grid |
| 6 | Regularisation arms (dropout / wd / early stop) | + augmentation as the 7th arm | + feature selection as an arm | + mixup / spec-augment arm |
| 7 | Small CNN over embeddings | **CNN classification + confusion matrix** | Feature engineering + ablation | CNN on log-mel spectrograms |
| 8 | Tokenise → embed → LSTM | Custom `Dataset`, grouped split, augmentation | Cross-validation + **grouped split** | Waveform → spectrogram → sequence model |
| 9 | Fine-tune a pretrained encoder | **Fine-tune ResNet/EfficientNet** | Boosting vs MLP, cost compared | Fine-tune a pretrained audio model |
| 10 | Transformer vs the W8 LSTM | Swap the backbone, one change | Swap the feature set, one change | Transformer vs CNN, one change |
| 11 | LLM API, strict JSON, retry log | LLM as a labelling/augmentation **assistant** (disclose it) | LLM as a feature or synthetic-row generator (use with care) | LLM transcript as an evaluation aid |
| 12 | **RAG chain** with citations | **Operating point**: threshold + abstention | **Operating point**: threshold + cost | **Operating point**: threshold + false-alarm budget |

**W11 note for non-LLM projects.** You still owe a W11 push. "LLM as a *labelling assistant*" is a
legitimate, disclosable use — and it is a genuine finding either way: if the LLM's labels are worse
than yours, that is a result worth five lines in `DATA.md`.
**非 LLM 方向也要交 W11**：把「大模型辅助标注」当作那一周的推进点，并把结果如实写进 `DATA.md`。

---

## 4. The 21 seeds · 21 个种子

Notation · 记号：`[核]` licence verified at source this term · `[查]` commonly declared, **you must
paste the source link yourself** · `[?]` licence unclear or research-only → treat as a risk.

---

### Track V · Computer Vision · 视觉

#### V1 · Campus waste-sorting assistant · 校园垃圾分类助手
`★★☆` · `🖥️`

| | |
|---|---|
| **User** | 宿舍楼保洁员与楼管（每栋楼 1 人，可访谈；他们每天要手工分拣错投的垃圾） |
| **Problem** | Given a phone photo of one item held over a bin, the system names the correct bin (recyclable / food / hazardous / other) so that a resident can sort correctly without reading a poster. |
| **In → Out** | 224×224×3 phone photo → 4 classes + confidence |
| **Data** | TrashNet (2 527 images, 6 classes) **[核]** repo MIT · <https://github.com/garythung/trashnet> **＋ 自采本校 4 类 ≥ 800 张**（需楼管书面许可与投稿人同意） |
| **Dumb baseline** | Always predict "other" (majority class) ≈ 33% |
| **Metric & target** | macro-F1 ≥ 0.75 (4 classes, imbalanced) **＋** P95 latency < 300 ms on phone-sized input |
| **Spine fit** | W7 CNN → W9 fine-tune → W10 backbone swap → W12 abstention → W13 serving |
| **Top risk** | 自采照片背景单一（都在白墙前）→ 现场照片分布不一致。**在 W7 就补拍 150 张"真实场景"照专门做域外测试**。 |
| **Out of scope** | 不做语音播报；不做投放点导航；不做有害垃圾分类细则 |
| **Stretch** | 量化导出 + 部署 URL；对不确定样本返回"不确定，请询问楼管" |

#### V2 · Greenhouse leaf-disease triage · 校植物园叶片病害初筛
`★★☆` · `🖥️`

| | |
|---|---|
| **User** | 校植物园／农业实训基地管理员（现在靠拍照发微信群问农技员，平均等 1–2 天） |
| **Problem** | Given a phone photo of one attached leaf, the system returns the most likely disease class and a confidence, so that the grower can decide whether to isolate the plant today. |
| **In → Out** | 224×224×3 leaf photo → 1 of 10 disease/healthy classes (+ top-3) |
| **Data** | PlantVillage, 54 303 images, 38 classes — **[核] CC0 1.0** (Mohanty et al. 2016; `spMohanty/PlantVillage-Dataset`) **＋ 自采现场照 ≥ 300 张** |
| **Dumb baseline** | Always predict the majority class (healthy) — check its share first |
| **Metric & target** | **两个数字一起报**：① 公开集随机切分 macro-F1 ≥ 0.95；② **现场自采子集 macro-F1 ≥ 0.70**。只报 ① 的提案会被追问。 |
| **Spine fit** | W7 CNN → W9 fine-tune → W10 backbone swap |
| **Top risk** | **这是本项目最有价值的地方**：PlantVillage 全部是实验室单叶、统一背景拍摄，模型学到的是背景而不是病斑（Mohanty et al., *Front. Plant Sci.* 2016 已量化这一崩塌）。把它写进 `DATA.md` 的 "known flaws"，并用自采现场照证明你测过了。 |
| **Out of scope** | 不做农药推荐；不做多叶/整株图像；不做 38 类全量 |
| **Stretch** | 按"拍摄会话/植株"分组切分再跑一次，量化随机切分虚高了多少 |

#### V3 · Lab meter reading · 实验室仪表自动读数
`★★★` · `🖥️`

| | |
|---|---|
| **User** | 实验中心值班老师（每天早晚两次手工抄 12 块表的读数，抄错要重跑实验） |
| **Problem** | Given a phone photo of one meter face, the system returns the numeric reading and flags low confidence, so that the duty technician can log readings in seconds instead of walking the room twice. |
| **In → Out** | 仪表照片 → 数值（回归 / 字符序列，**不是分类**） |
| **Data** | 自采 ≥ 1 500 张（可合成增强：曝光、倾斜、反光、部分遮挡）+ 公开数字 OCR 数据做预训练 |
| **Dumb baseline** | Always output the middle of the range (or 7-segment template matching) — report its MAE |
| **Metric & target** | MAE ≤ 2% of full scale **and** 完全正确率 ≥ 0.85（两个数字，因为"接近"和"正确"是两件事） |
| **Spine fit** | W7 CNN regression → W8 sequence (CRNN) → W10 attention → W12 confidence threshold |
| **Top risk** | 数据要自己造 → 必须在 W6 就拍完第一批 300 张，否则换 V1/V2 |
| **Out of scope** | 不做实时视频流；不做跨表数据关联；不做读数入库 |
| **Stretch** | 低置信度样本返回"看不清，请重拍"并记录拒识率 |

#### V4 · ASL fingerspelling for a service desk · 静态手语指拼识别
`★★☆` · `🖥️`

| | |
|---|---|
| **User** | 校学生事务大厅值班员（聋人学生来办业务时靠纸笔，一次沟通 20 分钟） |
| **Problem** | Given a webcam frame of one static fingerspelled letter, the system outputs the letter so that a service-desk clerk can read a spelled-out name in real time. |
| **In → Out** | 224×224×3 hand image → 1 of 26 letters (+ "unknown") |
| **Data** | **自采为主**：≥ 3 名同学（**含至少 1 名手小的同学**），每人每字母 ≥ 15 张，共 ≥ 1 200 张，签署同意书 · 公开 ASL Alphabet 数据集 **[?]** 仅作对照，许可需自行确认 |
| **Dumb baseline** | Random letter ≈ 3.8%；或者 Always "E"（最常见字母） |
| **Metric & target** | **留一人交叉验证（leave-one-signer-out）macro-F1 ≥ 0.70**，并对照随机切分的虚高数字 |
| **Spine fit** | W7 CNN → W8 grouped split → W9 fine-tune → W10 backbone swap |
| **Top risk** | **随机切分会骗你**：同一个人同一字母的多张照片几乎重复，随机切分后准确率虚高。这正是评分表 B 项要求的 **grouped split**，本项目的核心就是证明你懂这件事。 |
| **Out of scope** | 不做连续手语翻译；不做双手动作；不做动态手势 |
| **Stretch** | 加一个 "unknown" 类别 + 拒识阈值，报误识率与拒识率的权衡曲线 |

---

### Track T · Text · 文本

#### T1 · Bilingual campus-service intent router · 中英双语校园事务意图分类
`★★☆` · `💻🖥️` · **最适合作为首选**

| | |
|---|---|
| **User** | 国际学生事务办公室 1 名老师（每天重复回答约 40 条微信/邮件问题，其中约七成是同样的 10 件事） |
| **Problem** | Given one free-text question (English or Chinese), the system assigns it to one of 10 service intents, so that the office can auto-answer the top intents and route the rest to the right staff member. |
| **In → Out** | 一段中/英文问题 → 10 个意图之一 + 置信度 |
| **Data** | CLINC150, 23 700 utterances, 150 intents — **[查] CC BY 3.0** <https://github.com/clinc/oos-eval> · **＋ 自建校园意图 400–600 条**（语料来源：本班同学真实提问，去标识） |
| **Dumb baseline** | Keyword rules on 10 trigger words ≈ 40–50% |
| **Simple baseline** | TF-IDF + logistic regression |
| **Metric & target** | macro-F1 ≥ 0.85 on a held-out set **＋** 低置信度转人工的召回 ≥ 0.90（out-of-scope 问题必须能被识别出来） |
| **Spine fit** | W8 LSTM → W9 fine-tune BERT/ERNIE → W10 Transformer → W11 LLM head-to-head → W12 threshold → W13 API。**全 16 周主线原生覆盖，几乎不用替换。** |
| **Top risk** | 类别数贪多。10 个意图够用，30 个就做不完。 |
| **Out of scope** | 不做多轮对话；不做账号/成绩查询；不做语音输入 |
| **Stretch** | 把 LLM 作为第二个方案对照（成本/时延一起报）；加"未知意图"检测 |

#### T2 · Regulation Q&A by retrieval · 校园规章检索式问答
`★★☆` · `💻`

| | |
|---|---|
| **User** | 大一新生与国际学生（要在几百页《学生手册》里找一个具体条款） |
| **Problem** | Given a natural-language question, the system returns the exact clause(s) from the handbook with page references, so that a student can get an authoritative answer without reading 200 pages. |
| **In → Out** | 问题 → 条款原文 + 出处（页码/章节号）+ 相似度 |
| **Data** | 《学生手册》《学籍管理规定》等**学校公开文件**（注明来源与版本）· 方法训练可用 SQuAD 2.0 **[查] CC BY-SA 4.0** · 自建评测集 200 题（含 40 题"手册里没有"） |
| **Dumb baseline** | TF-IDF / BM25 检索 top-3，不排序不拒答 |
| **Metric & target** | 条款级 Recall@3 ≥ 0.80 **＋** 「手册里没有」类问题的正确拒答率 ≥ 0.85 |
| **Spine fit** | W8 嵌入 → W9 预训练表示 → W10 Transformer 重排 → W12 检索失效分析（**原生**） |
| **Top risk** | 没有"无答案"问题 → 系统永远能编一个答案出来。**40 条无答案题是这份工作的核心。** |
| **Out of scope** | 不做生成式回答；不做多语言翻译；不覆盖院系自定的细则 |
| **Stretch** | 加一个 cross-encoder 重排器，对照 BM25 报 nDCG |

#### T3 · Notice → structured fields · 校园通知信息抽取
`★★★` · `🖥️`

| | |
|---|---|
| **User** | 不懂中文的国际学生（学校官网通知是唯一信息源，靠翻译软件经常漏掉报名截止日期） |
| **Problem** | Given one Chinese notice page, the system extracts {event, audience, deadline, location, how to register} as structured fields plus an English one-line summary, so that an international student knows whether it applies and what to do. |
| **In → Out** | 通知正文 → 5 个结构化字段 + 是否需要行动（布尔） |
| **Data** | 学校官网公开通知 ≥ 1 200 条（注明来源与抓取日期；先看 `robots.txt` 与站点条款）· 手工标注 600 条为黄金集 |
| **Dumb baseline** | 正则只抽日期（正则很强，别小看它——它可能抽中 70% 的 deadline） |
| **Metric & target** | 字段级 F1 ≥ 0.85（deadline 单列报，因为它最重要）**＋** 幻觉字段率 ≤ 3% |
| **Spine fit** | W8 序列标注 → W9 预训练 → W10 Transformer → **W11 严格 JSON + 重试（原生）** |
| **Top risk** | 标注是硬活。600 条 × 5 字段 —— 用"预标注 + 人工改"能省一半时间，但**预标注用了大模型必须在 `DATA.md` 声明**。 |
| **Out of scope** | 不做全文翻译；不做通知推送；不做历史归档 |
| **Stretch** | 加"这条通知不适用你"的过滤（按 audience 字段），报误滤率 |

#### T4 · Duplicate question clustering · 学生提问去重聚类
`★☆☆` · `💻`

| | |
|---|---|
| **User** | 课程助教／答疑平台维护者（FAQ 里同一个问题有 20 种问法） |
| **Problem** | Given a batch of student questions, the system groups paraphrases together and picks a representative, so that an FAQ can be written once instead of twenty times. |
| **In → Out** | 问题列表 → 簇标签 + 每簇代表句 |
| **Data** | 自建 ≥ 1 500 条真实提问（本课程/哈工大 LCQMC 等公开 paraphrase 数据 **[查] 许可需确认**· 去标识） |
| **Dumb baseline** | 字符 3-gram Jaccard 相似度 + 阈值（**这个基线比你想的强**） |
| **Metric & target** | 成对 precision/recall F1 ≥ 0.75，外加上层评估：人工抽查 50 个簇的"纯度" ≥ 0.80 |
| **Spine fit** | W8 嵌入 → W9 预训练表示 → W10 对比学习/Transformer → W12 阈值与簇数选择 |
| **Top risk** | **太容易**。★☆☆ 的项目必须在"评价严谨性"上加码：报至少 2 种嵌入、给出阈值敏感度曲线、分析失败簇。 |
| **Out of scope** | 不做自动回答；不做多语言聚类；不做实时增量聚类 |
| **Stretch** | 用 HDBSCAN 对照 KMeans，并说明为什么簇数不是超参数而是决策 |

---

### Track C · LLM / RAG / Agent

#### C1 · Course assistant over this repo · 本课程资料助教（RAG）
`★★★` · `💻🖥️` · **数据零风险，主线原生**

| | |
|---|---|
| **User** | 本课程的学弟学妹（你的同学就是用户，访谈零成本；任课教师是需求方代表） |
| **Problem** | Given a question about this course (labs, milestones, rubric, lecture content), the system answers **with citations to the exact file and section**, so that a student can self-serve instead of posting in the group chat. |
| **In → Out** | 自然语言问题 → 答案 + 引用（文件路径 + 章节标题），或明确回答"课程资料中没有" |
| **Data** | **本仓库 `lectures/` `labs/` `projects/` `textbook/` `syllabus.md`（课程自有，许可清楚）** · 若做评测：自建 30 题 × (问题, 期望答案, 期望引用) 黄金集 |
| **Dumb baseline** | **直接问大模型、不检索**（又蠢又贴切：它会给出课程里根本没有的截止日期） |
| **Metric & target** | 30 题正确率 ≥ 0.80 **＋** 引用命中率 ≥ 0.90 **＋** 无答案题的拒答率 ≥ 0.80。三个数字缺一不可。 |
| **Spine fit** | W8 嵌入 → W9 表示 → W11 LLM 严格 JSON → **W12 RAG 原生** → W13 API |
| **Top risk** | ① 没做评测集就开始调参（调的是感觉）② API 费用失控。**在 `PROJECT_PLAN.md` 里写下预算上限**（例：≤ ¥50 或 ≤ 200 次调用） |
| **Out of scope** | 不做课程外的通用问答；**不做作业代写（明确写进边界）**；不做成绩查询 |
| **Stretch** | 加入拒答阈值实验；对照"只给检索结果给 LLM" vs "直接问 LLM"，把费用与正确率一起画出来 |

#### C2 · Lecture transcript → structured notes · 讲稿转结构化纪要
`★★☆` · `💻`

| | |
|---|---|
| **User** | 缺课的学生与非母语学生（一次 90 分钟全英文讲授，跟不下来）；教师本人（每周复盘） |
| **Problem** | Given a lecture transcript, the system produces a fixed-schema summary — key points, definitions introduced, code/commands shown, and "actions for you" — so that a student can catch up in 10 minutes. |
| **In → Out** | 讲稿文本（或音频）→ 固定 JSON 结构（≤ 6 个字段） |
| **Data** | 本课程的 `lesson-plans/` 与 `lectures/` 文本（课程自有）**＋ 自采 8–10 段录音**（**只录你自己或公开课；课堂录音须先取得师生同意**）· 人工标注 200 段作为评测集 |
| **Dumb baseline** | 只做 ASR 转写、不做任何结构化（= 一堆没有小标题的流水句） |
| **Metric & target** | 关键要点召回 ≥ 0.80 **＋** 虚构条目率 ≤ 5%（**幻觉率必须单独报，这是本项目的灵魂**） |
| **Spine fit** | W8 序列 → W11 LLM 严格 JSON + 重试（**原生**）→ W12 检索历史讲稿 |
| **Top risk** | 隐私。录音涉及他人 → 必须同意 + 去标识；`DATA.md` 要写清同意流程。 |
| **Out of scope** | 不做自动出题；不做课堂实时字幕；不做成绩相关分析 |
| **Stretch** | 把"虚构条目率"做成一张随提示词版本变化的表（这是 C 项"消融"的好素材） |

#### C3 · Receipt field extraction, strict JSON · 票据字段抽取
`★★☆` · `💻`

| | |
|---|---|
| **User** | 学生会／社团报销岗（每月约 120 张票据手工录入，最容易错在金额和日期） |
| **Problem** | Given one receipt photo, the system returns {merchant, date, total, tax_id} as strict JSON with per-field confidence, so that the treasurer can copy-paste instead of retyping. |
| **In → Out** | 票据照片 → 4 字段 JSON（schema 固定，校验失败即重试） |
| **Data** | SROIE (ICDAR 2019, 1 000 张) **[?] 研究用途，须确认** + 自采 ≥ 1 200 张（**必须去标识：遮住卡号、姓名、手机号后再入库，并在 `DATA.md` 说明**）+ 合成票据 |
| **Dumb baseline** | Tesseract OCR + 正则规则（**很强的基线，别指望轻松超过**） |
| **Metric & target** | 字段级 F1 ≥ 0.90（金额与日期单列） **＋** schema 校验通过率 ≥ 0.98（解析不了等于没做） |
| **Spine fit** | W7 CNN（图像）→ W11 LLM 严格 JSON + 重试日志（**原生**）→ W13 API |
| **Top risk** | 票据是个人金融数据。**去标识不是可选项**：写清你的遮罩流程，并把它作为 `DATA.md` 的 known flaw。 |
| **Out of scope** | 不做自动记账；不做 OCR 全文导出；不做多张票据合并 |
| **Stretch** | 报"有没有重试"两版对照：重试把校验通过率从多少提到多少 |

#### C4 · Prompt-injection robustness tester · 提示注入鲁棒性测试器
`★★☆` · `💻`

| | |
|---|---|
| **User** | 下一届要复用这个助教系统的教师（安全评估需求是真实的） |
| **Problem** | Given a target LLM application, the system runs a fixed battery of adversarial prompts and reports which classes of attack succeed, so that the owner knows what to patch before students use it. |
| **In → Out** | 目标应用的接口 + 150 条攻击模板 → 攻击成功率表（按攻击类型分组）+ 修复建议 |
| **Data** | 自建 150 条攻击模板（4 类：越权指令 / 角色扮演绕过 / 编码混淆 / 多轮诱导）+ 50 条正常问题作为对照 |
| **Dumb baseline** | 无防护的原始系统提示词（基线 = 它的攻击成功率） |
| **Metric & target** | 攻击成功率 ASR ≤ 0.15（从未防护基线降下来） **＋ 正常问题正确率下降 ≤ 5%**（防住了但变笨了是常见失败，必须报） |
| **Spine fit** | W11 LLM 原生 → W12 失效分析（≥ 5 个失败案例分组）→ W15 负责任 AI 直接对接 |
| **Top risk** | 只测一个模型、测一次就下结论。**同一攻击跑 ≥ 5 次**，报通过率的方差。 |
| **Out of scope** | 不攻击校外系统；不做真实社工；不发布可复制的攻击载荷（只发布模板类别与聚合结果） |
| **Stretch** | 给每个攻击类别配一条"修复后的提示词"，做前后对照表 |

---

### Track D · Tabular & Forecasting · 表格与时序

#### D1 · The course's own messy steel table · 课程自带工艺数据缺陷分类 🟢
`★☆☆` · `💻` · **保底选项：数据已在本仓库，零下载、零许可风险**

| | |
|---|---|
| **User** | 轧钢产线的工艺工程师（代理用户：数据由课程提供的工艺流程日志模拟，须在提案里明确写出这一点） |
| **Problem** | Given one production batch's process log (10 features), the system predicts the defect class and flags rare-class batches, so that a line engineer can inspect the likely-bad batches first. |
| **In → Out** | 10 个工艺特征 → 5 个缺陷类别（class 3 仅占 4.1%） |
| **Data** | `data/raw/defects.csv` — 12 480 行 × 13 列，**课程自有，许可清楚**。已有事实：`outputs/w3_dataset_facts.json` |
| **Dumb baseline** | Always predict class 0 ≈ 33.9% |
| **Simple baseline** | Logistic regression on the scaled 10 features |
| **Metric & target** | **少类（class 3）召回 ≥ 0.60** + macro-F1 ≥ 0.65（**不报 accuracy**：33.9% 的多数类基线会让 accuracy 骗人） |
| **Split** | **必须按 `batch_id` 分组切分**。一个批次约 10 行 → 随机切分把近似重复放进训练与测试两边（数据自带的告警原文就在 `w3_dataset_facts.json` 里）。这是评分表 B 项「随机切分会 −5」的完美教材。 |
| **Spine fit** | W4 MLP → W5 GBDT vs MLP → W7 特征工程 → W12 阈值与代价 |
| **Top risk** | 这份数据在实验 2/3 里已经出现过 → **只靠它做项目会显得单薄**。建议在它之上加一个真正的外部数据源（如 V1/V2 或 D2），把它当"对照组"。 |
| **Known flaws to write up** | 缺值（age 3.2%）、单位混入（temperature_c 有 998 行渗入了 °F）、离群（thickness_mm 37 行）、编码不一致（material_code 749 行有 `A-2`/`a1` 变体）、标签噪声约 250 行、批次内近似重复 |
| **Out of scope** | 不做时序预测；不做产线实时接入；不做根因归因 |

#### D2 · At-risk student early warning · 学业预警
`★★☆` · `💻`

| | |
|---|---|
| **User** | 远程教育机构的学业导师（**代理用户**：OULAD 的 advisor 角色，提案里必须写明是代理，并说明你如何构造这个用户的需求） |
| **Problem** | Given the first 4 weeks of clickstream and assessment submissions, the system ranks students by risk of not passing, so that a tutor can spend a limited weekly call budget on the students who need it most. |
| **In → Out** | 点击流聚合 + 早期作业提交记录 → 每名学生一个风险分 0–1 |
| **Data** | OULAD — 32 593 students, 10.66 M VLE clicks, 22 module presentations — **[核] CC BY 4.0** <https://analyse.kmi.open.ac.uk/open_dataset>（已用 k-anonymity 匿名化） |
| **Dumb baseline** | 规则："前两周一次作业都没交 ⇒ 高风险"（**很强、很真实的基线**） |
| **Metric & target** | 在导师"每周只能打 20% 学生"的预算下：recall@20% ≥ 0.60 · precision@10% ≥ 0.70。**别用 accuracy**（不通过率约 33%，accuracy 无意义） |
| **Split** | **按 module presentation 做时间切分**，随机切分 = 未来信息泄漏 |
| **Spine fit** | W4 MLP → W5 GBDT 对照 → W7 特征工程 → W12 阈值与代价曲线 → W13 API |
| **Top risk** | 把问题当"预测成绩"。它是**资源分配**问题，指标必须写成"在有限人工预算下的命中率"。 |
| **Out of scope** | 不预测具体分数；不做自动干预；**不做任何重识别尝试**（数据已匿名，禁止尝试还原个人） |
| **Stretch** | 代价敏感阈值曲线；按 disability / 地区分层做公平性审计（直通 W15） |

#### D3 · Machine-failure early warning · 设备故障预警
`★★☆` · `💻`

| | |
|---|---|
| **User** | 实训中心设备管理员（机床非计划停机一次平均影响 4 学时实训） |
| **Problem** | Given one machine's recent sensor window, the system flags an elevated failure risk so that maintenance can be scheduled before the next class block. |
| **In → Out** | 传感器窗口（温度/转速/扭矩/刀具磨损）→ 故障概率 |
| **Data** | AI4I 2020 Predictive Maintenance (UCI id 601, 10 000 rows) **[查] CC BY 4.0** · 或 NASA C-MAPSS（公有领域，多机多时序，可做 RUL 回归） |
| **Dumb baseline** | 规则："刀具磨损 > 200 min ⇒ 高风险"（先报它的 precision/recall） |
| **Metric & target** | 故障类 recall ≥ 0.85 **＋** 误报率 ≤ 0.15。**两个数字必须成对报**，因为漏检与误报的代价不对称。 |
| **Split** | 按机器 ID 分组，或按时间顺序 |
| **Spine fit** | W4 MLP → W5 提升树对照 → W6 类别权重作为正则臂 → W12 阈值与代价 |
| **Top risk** | 故障率约 3.4% → **accuracy 会给出 96.6% 的假象**。这正好是"指标要论证"的标准教材。 |
| **Out of scope** | 不做剩余寿命精确预测（若选 C-MAPSS 则可另做回归版）；不做传感器异常检测；不做备件管理 |
| **Stretch** | 报一条 PR 曲线 + 选点的业务理由；对照"只看规则"的成本差 |

#### D4 · Building electric-load forecasting · 楼宇用电负荷预测
`★★☆` · `💻`

| | |
|---|---|
| **User** | 后勤能源管理岗（每月电费超支，需要提前一天知道哪几个时段会冲高） |
| **Problem** | Given past hourly consumption and calendar features, the system forecasts the next 24 hours of load so that the energy manager can pre-cool rooms and shift heavy loads. |
| **In → Out** | 历史逐小时用电 + 日历/天气 → 未来 24 小时逐小时用电 |
| **Data** | UCI "Individual household electric power consumption" (2 075 259 rows, minute-level) **[查] CC BY 4.0** · 或校某栋楼自采数据（需后勤同意） |
| **Dumb baseline** | **"昨天同一时刻的值"（naive seasonal）** —— 时序任务最经典也最该有的基线 |
| **Metric & target** | 未来 24 h 逐小时 MAPE ≤ 12%（并单列高峰时段的误差，因为那是业务关心的） |
| **Split** | **纯时间顺序切分**（最后 N 天作测试集）；随机切分是错的，评分表 B 项原文点了 time-based split |
| **Spine fit** | W4 MLP → W8 序列模型（LSTM）→ W10 Transformer 对照 → W12 阈值 |
| **Top risk** | 把 MAPE 报成单一个数字。**分时段报**，并解释为什么高峰时段更重要。 |
| **Out of scope** | 不做电价优化；不做设备级分解；不做长期（季度）预测 |
| **Stretch** | 加节假日前后的误差分析；报 naive 基线的差值而不是绝对误差 |

#### D5 · Bike-share demand forecasting · 共享单车需求预测
`★☆☆` · `💻`

| | |
|---|---|
| **User** | 校园共享单车运维调度员（早高峰某些站点全空、某些站点堆满） |
| **Problem** | Given the date and hour, the system predicts rental demand per station-hour so that the dispatcher knows where to move bikes before 8 a.m. |
| **In → Out** | 日期 + 小时 + 天气 + 节假日 → 该站该小时租借量 |
| **Data** | UCI Bike Sharing Dataset (id 275, 17 379 hourly rows) **[查] CC BY 4.0** <https://archive.ics.uci.edu/dataset/275> |
| **Dumb baseline** | 同时段历史均值（hour × weekday 交叉表） |
| **Metric & target** | 逐小时 MAPE ≤ 15% **＋** 高峰时段（7–9 时、17–19 时）MAPE ≤ 20%（**高峰单列**） |
| **Split** | 时间顺序（前 80% 天作训练） |
| **Spine fit** | W4 MLP → W7 特征工程（周期编码）→ W8 序列 → W12 阈值 |
| **Top risk** | **太容易**（★☆☆）。必须在严谨性上取胜：报残差图、做按天的误差分解、说明为什么不用 RMSE。 |
| **Out of scope** | 不做站点间调度优化；不做长期扩张预测；不做多城市迁移 |
| **Stretch** | 预测"是否会出现缺车"这个二分类版本，与回归版对照 |

---

### Track A · Audio & Speech · 语音与音频

> **Why this track is under-used:** audio is *natively* a sequence, so it fits the W8 → W10 spine
> better than images do — and very few students pick it, so you will not collide.
> 音频天然是序列，比图像更贴合 W8→W10 主线；而且选的人少，不容易撞车。

#### A1 · Keyword spotting for a hands-free lab · 免手操作的关键词唤醒
`★★☆` · `🖥️`

| | |
|---|---|
| **User** | 做化学/生物实验时必须戴手套的学生（不能碰键盘，只能停下、脱手套、点鼠标） |
| **Problem** | Given 1-second microphone audio, the system detects fixed command words ("start", "stop", "next-step") and triggers the action, so that a student can control the experiment log without touching anything. |
| **In → Out** | 1 s, 16 kHz waveform → 12 个命令词中的 1 个（或"无词"） |
| **Data** | Google Speech Commands v2 (105 829 clips, 35 words) **[查] CC BY 4.0** · 取 12 个词的子集（每词 ≥ 1 000 条） |
| **Dumb baseline** | Always predict the most common word ≈ 8% |
| **Metric & target** | 12 类 macro-F1 ≥ 0.90 **＋ 误唤醒率 ≤ 1 次/小时**（在真实背景噪声下测）。两个数字都要——只报准确率等于没测。 |
| **Spine fit** | W7 CNN on log-mel → W8 序列模型 → W10 Transformer 对照 → W13 服务 |
| **Top risk** | 只在安静数据上测。**自己录 5 分钟实验室背景噪声做域外测试**，误唤醒率会立刻现形。 |
| **Out of scope** | 不做连续语音识别；不做说话人识别（**涉及生物特征，不要做**）；不做多语言 |
| **Stretch** | 报模型大小与 CPU 推理时延（要在树莓派级别的设备上说得通） |

#### A2 · Classroom noise-event detection · 教室噪音事件检测
`★★☆` · `🖥️`

| | |
|---|---|
| **User** | 教师与后勤（后排学生听不清；噪声投诉无据可依） |
| **Problem** | Given a class-period recording, the system labels time segments by noise type (speech babble, door slam, construction, HVAC hum) so that the cause of poor audibility can be located. |
| **In → Out** | 音频片段（1 s 帧）→ 5 类噪声事件 + 时间戳 |
| **Data** | ESC-50 (2 000 clips, 50 classes) **[查] CC BY-NC 3.0**（**非商业，仅课程作业，必须写进 `DATA.md`**）· UrbanSound8K **[查] CC BY-NC 3.0** · + 自采教室背景 ≥ 30 min |
| **Dumb baseline** | 瞬时音量阈值规则（**意料之外地强**，先诚实地报出它的 F1） |
| **Metric & target** | 帧级 macro-F1 ≥ 0.75 **＋ 事件级 F1 ≥ 0.60**（连续片段不能碎成几十个短事件——这是本项目最容易忽略的评测陷阱） |
| **Spine fit** | W7 CNN → W8 序列 → W10 Transformer → W12 阈值 |
| **Top risk** | 只报帧级指标。**事件级评估要你自己设计**（合并相邻帧、定义最小事件时长），并把规则写进 `evaluate.py`。 |
| **Out of scope** | 不录语音内容（**只做声学事件，不做语音转写**——这样隐私侵入小得多，是加分论点）；不做实时告警 |
| **Stretch** | 用"只训练正常噪声"的半监督版本，报 AUC 与误报率 |

#### A3 · Lecture speech → readable, segmented notes · 讲课语音转写并自动分段
`★★★` · `🖥️`

| | |
|---|---|
| **User** | 听障学生与非母语学生（ASR 全文没有标点、没有段落，读起来比听还累） |
| **Problem** | Given a raw ASR transcript of a lecture, the system restores punctuation and topic segmentation so that a reader can skim the lecture in five minutes. |
| **In → Out** | 无标点转写文本 → 加标点 + 话题分段（每段一个标题） |
| **Data** | 本课程 `lesson-plans/` 与 `lectures/` 文本（课程自有）作参考 · 自采 8–12 段讲座录音（**须同意**）· 预训练可用 LibriSpeech **[查] CC BY 4.0** |
| **Dumb baseline** | 每 200 字切一段、句末统一加句号（**真的不比它差多少，先报它的分数**） |
| **Metric & target** | 分段边界 F1 ≥ 0.70 **＋** 标点准确率 ≥ 0.85（人工评 30 段；**评测集由你自己标注 30 段，这本身是交付物**） |
| **Spine fit** | W8 序列标注 → W10 Transformer → W11 LLM 后处理对照 → W12 失效分析 |
| **Top risk** | 没有黄金分段。**先在 W7 手工分 30 段**，否则到 W12 你无法证明任何数字。 |
| **Out of scope** | 不做实时字幕；不做翻译；不做说话人分离 |
| **Stretch** | 对照"LLM 后处理"与"小模型序列标注"两条路线，把成本与时延也报出来 |

#### A4 · Abnormal-sound detection, normal-only training · 异常声检测（只用正常样本训练）
`★★★` · `🖥️`

| | |
|---|---|
| **User** | 图书馆／自习室夜间安全值守（**用声音代替摄像头：不采集人脸、不采集语音内容，隐私侵入小得多——这个论证本身就是 W15 的好素材**） |
| **Problem** | Given continuous room audio, the system raises an alert when it hears something anomalous (glass breaking, alarm, sustained mechanical rattle) that was never present during training, so that a night warden can check remotely. |
| **In → Out** | 音频帧 → 异常分数 0–1（**只用正常音频训练自编码器，异常靠重构误差暴露**） |
| **Data** | 自采正常环境声 ≥ 2 h（图书馆 3 个时段）+ 异常声：ESC-50 中的 glass break / siren / alarm **[查] CC BY-NC 3.0** + 自录若干 |
| **Dumb baseline** | 音量阈值（先报它的每小时误报次数，通常高得吓人） |
| **Metric & target** | 帧级 AUC ≥ 0.85 **＋ 每小时误报 ≤ 2 次**（后者才是业务指标；报 AUC 不报误报率等于没回答"能不能用"） |
| **Spine fit** | W7 自编码器（重构）→ W8 序列自编码器 → W10 表示学习对照 → W12 阈值与误报预算 |
| **Top risk** | 无标签 → 评测方案要自己设计（用"留出异常类"的协议：训练时完全不用异常声）。这是 ★★★ 的原因。 |
| **Out of scope** | 不录音内容、不做说话人识别、不做事件定位到具体房间；不做真实报警联动 |
| **Stretch** | 报"按房间/时段"的误报差异，讨论为什么夜间误报更多（分布漂移，直通 W14） |

---

## 5. High-risk topics · 高风险题目（不是不能做，是会撞车或踩许可）

| Topic | Why it is risky | The fix |
|---|---|---|
| **"Train a model on ImageNet"** | 无用户、无问题、无数据工作。README §3.4 明确打回。 | 换成上述任一种子，把"用户"两个字补上。 |
| **人脸 / 声纹 / 步态识别考勤** | README §3.4 明确打回：真实人脸、生物特征、无同意方案。 | 换 **A4 异常声检测**——同样解决"夜间安全"，但**不采集人脸与语音内容**，且隐私论证本身就是加分点。 |
| **"做一个疾病诊断 AI"** | 医学影像需伦理审查与授权数据，本课程无此通道。 | 换 V2 植物病害：**同一个技术骨架（细粒度图像分类 + 域外测试）**，数据合规、还有现成的"已知缺陷"可写。 |
| **中文谣言/假新闻检测（CHEF、THUNLP 等）** | CHEF 仓库 **[?] 未声明开源许可**；这类语料多数许可不明 → 直接踩 README §3.4「无许可」红线。 | 想保留任务形态，就换 **T2/T4**（有明确许可或自建 + 写清采集同意）；把"许可不明导致换题"这件事写进 W6 的 `DEVLOG.md`——它是一段真实的过程记录。 |
| **"用大模型做一个聊天机器人"** | 无法评价（没有对错标准），D 项直接垮掉。 | 加三个约束：**检索 + 引用 + 可拒答** → 立刻变成 C1，评测集也自然产生了。 |
| **爬取某网站的评论/岗位数据** | 违反站点条款或 `robots.txt`，且许可无法写进 `DATA.md`。 | 先看条款；不行就改用公开数据集，或自采（你自己生成的数据许可最清楚）。**T3 用的是学校官网公开通知，来源可写、可引用。** |
| **钢材表面缺陷（照抄 `milestones.md` 的示例）** | ① 撞车率极高（每届都有人选）② NEU-DET **[?] 无明确开源许可**。 | 若真要选：**必须**拿到自己的产线照片，或改用 **D1**（课程自带的表格版，零许可风险），并在提案里说明数据来源差异。 |
| **3D 重建 / 视频生成** | 算力超出（⚠️），单人在 16 周内无法收敛。 | 换音频/表格方向。想保留"生成"味道，用 C2（结构化生成，可评测）。 |
| **"我要做一个综合平台，包含 A、B、C 三个功能"** | 范围是三个项目，不是三个功能。W14 必崩。 | 只留一个功能做深，另两个写进 **scope boundary（明确不做）**——评分表把"砍掉的清单"算作成熟度，不是认输。 |
| **Kaggle 竞赛刷榜** | README §3.4 明确打回：排行榜是目标、代码是别人的 notebook。 | 换成本清单任一种子，把"我要比 SOTA 高"改成"我要知道**哪一处改动**带来了多少提升"。 |

---

## 6. Dataset leads · 数据集线索

**Hard rule before you use this table:** a licence claim in this table is a *lead*, not a fact.
Your `DATA.md` must contain **the licence name + the URL where you read it**. In W6 the instructor
will spot-check three of them at random.

| Dataset | Task | Size | Licence (as declared) | Get it | Verified? |
|---|---|---|:---:|---|:---:|
| **`data/raw/defects.csv`** | tabular, 5-class | 12 480 rows | 课程自有 | already in this repo | ✅ |
| OULAD | tabular / learning analytics | 32 593 students | **CC BY 4.0** | analyse.kmi.open.ac.uk/open_dataset · UCI 349 | ✅ |
| PlantVillage | image, 38 classes | 54 303 | **CC0 1.0** | `spMohanty/PlantVillage-Dataset` · Kaggle mirrors | ✅ |
| TrashNet | image, 6 classes | 2 527 | repo **MIT** (code); dataset per citation request | `github.com/garythung/trashnet` | ✅ |
| Food-101 | image, 101 classes | 101 000 | **licence unknown** — official page states none; ETH's HF card says `unknown`; mirrors claim CC BY 4.0 | ETH `data.vision.ee.ethz.ch/cvl/food-101` | ❌ |
| CLINC150 | intent classification | 23 700 | CC BY 3.0 | `github.com/clinc/oos-eval` | ⚠️ |
| Banking77 | intent classification | 13 083 | CC BY 4.0 | HF `PolyAI/banking77` | ⚠️ |
| SQuAD 2.0 | extractive QA | 150 000 | CC BY-SA 4.0 | `rajpurkar.github.io/SQuAD-explorer` | ⚠️ |
| Google Speech Commands v2 | keyword spotting | 105 829 clips | CC BY 4.0 | TFDS `speech_commands` | ⚠️ |
| ESC-50 | audio event tags | 2 000 clips | **CC BY-NC 3.0** (non-commercial) | `github.com/karolpiczak/ESC-50` | ⚠️ |
| UrbanSound8K | audio event tags | 8 732 clips | CC BY-NC 3.0 | `urbansounddataset.weebly.com` | ⚠️ |
| LibriSpeech | ASR / speech | 1 000 h | CC BY 4.0 | openslr.org/12 | ⚠️ |
| UCI AI4I 2020 | predictive maintenance | 10 000 | CC BY 4.0 | UCI id 601 | ⚠️ |
| UCI Bike Sharing | demand forecasting | 17 379 | CC BY 4.0 | UCI id 275 | ⚠️ |
| UCI household power | load forecasting | 2 075 259 | CC BY 4.0 | UCI id 235 | ⚠️ |
| ASL Alphabet | image, 29 classes | ~87 000 | **unclear** — do not rely on it | Kaggle | ❌ |
| NEU-DET | image, 6 classes | 1 800 | **research use, no clear open licence** | Kaggle/GitHub mirrors | ❌ |
| CHEF | Chinese fact-checking | 10 000 claims | **not declared in the repo** | `github.com/THU-BPM/CHEF` | ❌ |
| SROIE (ICDAR 2019) | receipt field extraction | 1 000 | research use — confirm first | `rrc.cvc.uab.es/?ch=13` | ❌ |

⚠️ = commonly declared, **paste the source link yourself** · ❌ = treat as a risk, prefer an alternative.

> **A live example of why "a mirror is not a source".** This table originally listed Food-101 as
> CC BY 4.0, because that is what several dataset mirrors (including Hugging Face and Kaggle
> re-uploads) declare. Checked against the sources themselves on **2026-10-09**:
>
> | Where you look | What it says |
> |---|---|
> | ETH landing page | a citation format and a download link — **no licence** |
> | ETH's own dataset card on Hugging Face (`ethz/food101`) | **`license: unknown`** |
> | mirrors / re-uploads | "CC BY 4.0" — supported by neither of the above |
> | the HF `datasets` loader script | carries a *LICENSE AGREEMENT* text naming Foodspotting and "scientific fair use" — but that text is **not on the landing page** |
>
> Same dataset, four answers — and only the first two are the source. **The licence is unknown:
> treat it as a risk.** This is exactly the check dimension B (18 pts) is asking you to perform,
> and it is why "公开数据" is not an acceptable answer in the licence box.
> **这就是为什么「镜像站写的许可」不算许可。** 本表初稿把 Food-101 标成 CC BY 4.0（因为多个镜像站
> 这么写）；2026-10-09 逐处核对：ETH 官方页**没写许可**，ETH 自己的数据集卡写的是
> **`license: unknown`**。同一个数据集四个答案，只有前两个算数——**许可未知，按风险处理**。
>
> **If you use Food-101 anyway**, note two things in `DATA.md`: (a) the licence is unknown at the
> source — say so honestly instead of picking a name you found on a mirror, and keep it out of
> anything you republish; (b) the authors state the 750 training images per class **were
> deliberately not cleaned** and contain label noise — an ideal "known flaw" to write up.

**Getting datasets from inside China · 校内网络获取通道**

| Need | Do this |
|---|---|
| Hugging Face is slow/blocked | `export HF_ENDPOINT=https://hf-mirror.com` before `datasets.load_dataset(...)` — record it in `README.md` |
| Kaggle is slow | prefer the original source (UCI, GitHub, TFDS, openslr) over a Kaggle re-upload — **and the licence is usually clearer at the original source** |
| Pre-trained weights | `torchvision` / `timm` weights download from `download.pytorch.org`, which is normally reachable; if not, use the mirror and document it |
| Nothing is reachable | fall back to **D1** (in-repo) — you will still have a complete project |

---

## 7. Your Week-6 checklist · 第 6 周动作清单

Do these in order. The last three are the milestone.

- [ ] Skim the quick-pick table (§2). Shortlist **five** seeds. 速选表挑出 5 个。
- [ ] For each of the five, open the data link and **look at the raw data** — class counts, a few rows. Cross out any that you cannot open today. 逐个打开数据链接，今天打不开的直接划掉。
- [ ] Simulate the dumb baseline by hand: what would "always predict the majority class" score? If you cannot find the class counts, the dataset is not verified. 估算"多数类基线"能拿多少分。
- [ ] Narrow to **three** seeds from **three different tracks**. 收敛到 3 个、且跨 3 个方向。
- [ ] Apply the three dials (§0 rule ②) to at least one of them, so it is *yours*. 至少对其中一个转一次旋钮。
- [ ] Fill `proposals/01.md`, `02.md`, `03.md` with the [charter template](project-charter-template.md) — **one page each**. 三份提案。
- [ ] Write `PROJECT_PLAN.md`: weekly slot, MVP vs stretch, three risks, **the cut list**. 写下计划与砍单。
- [ ] Write `DEVLOG.md` v0 — one entry, even if it says "spent the lab reading a topic list". 建 `DEVLOG.md`。

**What the instructor checks at the W6 sign-off:** three genuinely different proposals,
a plan with a realistic weekly slot, and a cut list. Nothing else — but nothing less.
**W6 课内审定后教师只查三件事**：三份真正不同的提案、一个现实的每周时间槽、一份砍单。

---

*Last updated: 2026-09-22 · 任政 (Zheng Ren) · 52015CC3BV · School of Software, DNUI*
*This catalogue is a teaching aid. The licence lead column is a lead — you own the verification.*
