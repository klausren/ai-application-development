# -*- coding: utf-8 -*-
"""Week 8 deck spec — Sequence Models and Text Data (CU(8)).

Every number here is copied from outputs/w8_sequence.json and
outputs/w8_corpus_facts.json.  Single source of truth — do not hand-edit a
number without re-running:

    python scripts/build_text_corpus.py
    python scripts/w8_sequence_experiment.py

Slide schema: see RENDERERS in scripts/build_deck.py.
"""

# --------------------------------------------------------------- constants ---
N_PASSAGES = 748          # corpus size (own Week 1-6 materials)
N_CLASSES = 6
VOCAB_FULL = 3142         # full corpus vocabulary
VOCAB_TRAIN = 1592        # mean vocabulary actually seen by the model (train only)

PER_CLASS = [105, 97, 114, 119, 128, 185]      # W1..W6 passages
PER_CLASS_TEST = [80, 75, 85, 90, 95, 140]     # 5-seed test rows
RECALL = [0.1750, 0.1867, 0.4235, 0.4778, 0.4211, 0.6643]

LEN_MIN, LEN_MED, LEN_P95, LEN_MAX, LEN_MEAN = 20, 35, 87, 285, 42.1

PARAMS_MEAN = 164691      # 166,278 at seed 42; 164,691 mean over seeds
SHARE_SHORT = 0.9558      # share of test docs shorter than max_len = 96

# (test_acc_mean, test_acc_sd, macro_f1_mean, macro_f1_sd)
ARMS = {
    "packed":         (0.4248, 0.0360, 0.3843, 0.0422),
    "last_step":      (0.2407, 0.0040, 0.0711, 0.0095),
    "mean_masked":    (0.5027, 0.0449, 0.4774, 0.0482),
    "mean_unmasked":  (0.3929, 0.0684, 0.3315, 0.0935),
    "mean_masked_reg": (0.4672, 0.0595, 0.4433, 0.0625),
}

# bucket -> (n, packed, last_step)
BY_LENGTH = {
    "20-29":   (38, 0.4211, 0.1579),
    "30-49":   (41, 0.3902, 0.1707),
    "50-99":   (29, 0.4483, 0.4138),
    "100-max": (5, 0.6000, 0.4000),
}

LONG_SPLIT = {"at_ge": (5, 0.4000), "below": (108, 0.2315)}

MAXLEN_X = ["48", "96", "192"]
MAXLEN_PACKED = [0.4572, 0.4454, 0.4454]
MAXLEN_LAST = [0.2891, 0.2389, 0.2478]

CURVE_X = ["0", "3", "6", "9", "12", "15", "18", "21", "24", "27", "30"]
CURVE_TRAIN = [0.2849, 0.2696, 0.4857, 0.6386, 0.7400, 0.8375,
               0.8853, 0.8967, 0.9675, 0.9866, 0.9885]
CURVE_VAL = [0.2143, 0.2411, 0.2589, 0.2500, 0.3036, 0.3393,
             0.3571, 0.3036, 0.3661, 0.4196, 0.4196]

CONFUSION = [
    [14, 12, 10, 22, 8, 14],
    [16, 14, 13, 11, 13, 8],
    [12, 4, 36, 13, 7, 13],
    [7, 4, 16, 43, 10, 10],
    [6, 10, 9, 11, 40, 19],
    [8, 8, 11, 11, 9, 93],
]

# CJK tokenisation demo (this repo's own Chinese textbook text)
CJK_WS = {"vocab": 372, "singleton": 0.9946, "oov": 0.9973, "tokens": 375}
CJK_CH = {"vocab": 880, "singleton": 0.2170, "oov": 0.0254, "tokens": 14860}

N_MISCLASSIFIED = 14

SCRUB = 262          # week / lab / CU identifiers replaced before writing
DROPPED_CJK = 96
DROPPED_SHORT = 2928
DROPPED_DUPE = 7
SHA256 = "87e41aac89ef59903abca15eea4250e68eb9d29537c1cd78d251ad497a16b4b1"

PROTO = "自有语料 748 段 · 6 类 · Embedding(64)→LSTM(96)→Linear(6) · Adam 1e-3 · batch 64 · 30 轮 · 5 种子"
PROTO_EN = "748 passages · 6 classes · Embedding(64)→LSTM(96)→Linear(6) · Adam 1e-3 · batch 64 · 30 epochs · 5 seeds"

ARMS_X = ["packed", "last_step", "mean_masked", "mean_unmasked"]


def _pct(v):
    return f"{v * 100:.1f}%"


def zh(t, e):
    return {"zh": t, "en": e}


# ------------------------------------------------------------------- spec ----
SPEC = {
    "week": 8,
    "slides": [

        # =========================================================== 01 cover
        {"type": "cover",
         "kicker": zh("模块二 · 第 8 周 · 深度学习核心技术与模型训练", "MODULE 02 · WEEK 08 · CORE DEEP LEARNING"),
         "title": zh("序列模型与文本数据处理", "Sequence Models and Text Data"),
         "title_sub": zh("从一段文本到一个张量，再从一个张量回到一个判断",
                         "From a passage to a tensor, and back to a decision"),
         "subtitle": zh(f"CU(8) · 实验 7 · {PROTO}",
                        f"CU(8) · Lab 7 · {PROTO_EN}"),
         "chips": [
             (zh("4 学时", "4 hours"), 1),
             (zh("实验 7", "Lab 7"), 1),
             (zh("M8 期中检查点 ★", "M8 midterm checkpoint ★"), 1.5),
         ],
         "lecturer": zh("任政 · 软件学院 · 软件与大数据技术系",
                        "Zheng Ren · School of Software")},

        # =========================================================== 02 contents
        {"type": "contents",
         "count": zh("30", "30"),
         "count_label": zh("页 · 5 个部分", "slides · 5 parts"),
         "tagline": zh("这一周的主角不是 LSTM，是**那个把变长文本变成定长张量的人**。"
                       "填充与掩码写错一次，模型照样训练、照样出准确率——只是那个准确率是假的。",
                       "The protagonist this week is not the LSTM. It is **the person who turns "
                       "variable-length text into a fixed-length tensor.** Get padding and masking "
                       "wrong and the model still trains and still reports an accuracy — just a fake one."),
         "timing": zh("90 讲授（复习 10 + 新课 80）\n80 实验\n10 小结与作业",
                      "90 lecture (10 review + 80 new)\n80 lab\n10 wrap-up"),
         "parts": [
             {"title": zh("把一段文本变成一个张量", "From text to a tensor"),
              "title_en": zh("Part 1", "Part 1"),
              "desc": zh("分词 → 词表 → 编码 → 填充，四步各自会在哪里出错",
                         "tokenise → vocabulary → encode → pad, and where each step breaks")},
             {"title": zh("填充与掩码", "Padding and masking"),
              "title_en": zh("Part 2", "Part 2"),
              "desc": zh("一个安静的 bug：模型读到了填充向量，指标却看不出来",
                         "A quiet bug: the model reads a pad vector and the metric cannot see it")},
             {"title": zh("训练曲线与真正的瓶颈", "Curves and the real bottleneck"),
              "title_en": zh("Part 3", "Part 3"),
              "desc": zh("它过拟合了；正则化救不回来——瓶颈在数据量",
                         "It overfits; regularisation does not rescue it — the bottleneck is data")},
             {"title": zh("它错在哪", "Where it goes wrong"),
              "title_en": zh("Part 4", "Part 4"),
              "desc": zh("6×6 混淆矩阵、准确率与宏 F1 的分裂、具体样本",
                         "A 6×6 confusion matrix, the accuracy/macro-F1 split, concrete samples")},
             {"title": zh("接下来，以及 M8", "Next, and M8"),
              "title_en": zh("Part 5", "Part 5"),
              "desc": zh("RNN→Transformer 的伏笔、指标选择的思政落点、期中检查点",
                         "the RNN→Transformer hook, the metric-choice ethics point, the midterm")},
         ]},

        # ======================================================== Part 1 (03-07)
        {"type": "section", "num": "01",
         "title": zh("把一段文本变成一个张量", "From Text to a Tensor"),
         "title_en": zh("Part 1 · tokenise → vocabulary → encode → pad",
                        "Part 1 · tokenise → vocabulary → encode → pad"),
         "lead": zh("LSTM 不认识字。它只认识 shape=(batch, seq_len) 的整数张量。"
                    "**本周 80% 的错误不发生在模型里，发生在这四步里。**"
                    "所以先把管线走通，再谈门控。",
                    "An LSTM does not read. It reads an integer tensor of shape "
                    "(batch, seq_len). **Eighty percent of this week's bugs live in these four "
                    "steps, not in the model.** Wire the pipeline first; the gates come second."),
         "pillars": [
             {"title": zh("分词", "Tokenise"), "sub": zh("按什么切？", "split on what?")},
             {"title": zh("词表", "Vocabulary"), "sub": zh("只从训练集建", "built from train only")},
             {"title": zh("编码", "Encode"), "sub": zh("未知词给谁", "who gets <unk>")},
             {"title": zh("填充", "Pad"), "sub": zh("补到多长", "pad to what length")},
         ]},

        {"type": "cards",
         "title": zh("四步链路：每一步都有一个典型错误", "Four steps, one classic bug each"),
         "right": zh(PROTO, PROTO_EN),
         "subtitle": zh("先看清链路，再写代码。每一步的失败都会以「准确率不高」的形式出现在最后，"
                        "而不在你出错的那一行。",
                        "See the chain before writing it. Every step's failure surfaces as "
                        "「low accuracy」 at the end, never at the line you broke."),
         "cols": 2, "gap": 0.7, "top": 3.3, "h": 6.6,
         "cards": [
             {"accent": "1E4FA8",
              "title": zh("① 分词 Tokenise", "1 · Tokenise"),
              "body": [zh("把字符串切成 token 序列。", "Split the string into a token sequence."),
                       zh("英文：小写 + 正则 [a-z][a-z'-]*，把 don't、state-of-the-art 当一个 token。",
                          "English: lowercase + the regex [a-z][a-z'-]*, so don't and state-of-the-art stay whole."),
                       zh("中文：**空白切分几乎必错**，见后面那一页。",
                          "Chinese: **splitting on whitespace is almost always wrong** — see the next-but-one page.")],
              "tag": zh("先想清楚再切", "decide before you split")},
             {"accent": "3D7BD9",
              "title": zh("② 词表 Vocabulary", "2 · Vocabulary"),
              "body": [zh("**只用训练集建词表。** 用全量数据建词表＝把测试集信息漏进训练。",
                          "**Build the vocabulary from the training split only.** Using all data hands test information to training."),
                       zh("min_freq=2 过滤只出现一次的词；上限 6000。",
                          "min_freq=2 drops words seen once; cap at 6000."),
                       zh("本周词表均值只有 " + str(VOCAB_TRAIN) + " 个词。",
                          "This week's mean vocabulary is only " + str(VOCAB_TRAIN) + " words.")],
              "tag": zh("数据泄漏高发区", "leakage hotspot")},
             {"accent": "059669",
              "title": zh("③ 编码 Encode", "3 · Encode"),
              "body": [zh("<pad>=0，<unk>=1，其余从 2 开始。",
                          "<pad>=0, <unk>=1, real words from 2 up."),
                       zh("padding_idx=0 让 <pad> 的嵌入向量**永远不被更新**。",
                          "padding_idx=0 keeps the <pad> embedding **frozen** — it never receives gradient."),
                       zh("这一步决定了后面掩码能不能对上。",
                          "This choice is what masking later keys off.")],
              "tag": zh("0 号位置是约定的", "index 0 is reserved")},
             {"accent": "D97706",
              "title": zh("④ 填充 Pad", "4 · Pad"),
              "body": [zh("一个 batch 里的样本必须等长。短文档补零。",
                          "One batch needs equal lengths, so short documents get zeros."),
                       zh("补到 batch 内最长，还是全库最长（max_len="
                          + str(int(LEN_P95)) + " 的对齐档 96）？这里选了后者。",
                          "Pad to the batch max, or to a global max_len (96)? We chose the global one."),
                       zh("**" + _pct(SHARE_SHORT) + " 的测试文档达不到这个长度**——这就是下一部分的全部麻烦。",
                          "**" + _pct(SHARE_SHORT) + " of test documents never reach that length** — which is exactly the next part's problem.")],
              "tag": zh("代价马上兑现", "the bill arrives here")},
         ]},

        {"type": "code",
         "title": zh("分词与建表——只从训练集", "Tokenise and build the vocabulary — train split only"),
         "right": zh("可运行", "runnable"),
         "subtitle": zh("这两块代码是本周所有实验的共同起点。注意词表是在 `train` 上统计的，"
                        "`test` 只做查表。",
                        "These two blocks are the shared starting point for every arm this week. "
                        "The vocabulary is counted on train; test only looks words up."),
         "top": 3.3, "h": 10.2,
         "blocks": [
             {"title": zh("分词 + 建词表", "Tokenise + vocabulary"),
              "size": 10.5,
              "code": {
                  "zh": [
                      "import re, collections",
                      "",
                      "TOKEN = re.compile(r\"[a-z][a-z'-]*\")",
                      "",
                      "def tokenise(text):",
                      "    return TOKEN.findall(text.lower())",
                      "",
                      "def build_vocab(texts, min_freq=2, cap=6000):",
                      "    freq = collections.Counter()",
                      "    for t in texts:            # texts = TRAIN only",
                      "        freq.update(tokenise(t))",
                      "    words = [w for w, c in freq.most_common()",
                      "             if c >= min_freq][:cap]",
                      "    # 0 = <pad>, 1 = <unk>, real words from 2",
                      "    return {\"<pad>\": 0, \"<unk>\": 1,",
                      "            **{w: i + 2 for i, w in enumerate(words)}}",
                  ],
                  "en": [
                      "import re, collections",
                      "",
                      "TOKEN = re.compile(r\"[a-z][a-z'-]*\")",
                      "",
                      "def tokenise(text):",
                      "    return TOKEN.findall(text.lower())",
                      "",
                      "def build_vocab(texts, min_freq=2, cap=6000):",
                      "    freq = collections.Counter()",
                      "    for t in texts:            # texts = TRAIN only",
                      "        freq.update(tokenise(t))",
                      "    words = [w for w, c in freq.most_common()",
                      "             if c >= min_freq][:cap]",
                      "    # 0 = <pad>, 1 = <unk>, real words from 2",
                      "    return {\"<pad>\": 0, \"<unk>\": 1,",
                      "            **{w: i + 2 for i, w in enumerate(words)}}",
                  ]}},
             {"title": zh("编码 + 填充", "Encode + pad"),
              "size": 10.5,
              "code": {
                  "zh": [
                      "import torch",
                      "",
                      "def encode(text, vocab, max_len):",
                      "    ids = [vocab.get(w, 1) for w in tokenise(text)]",
                      "    ids = ids[:max_len]",
                      "    ids += [0] * (max_len - len(ids))   # pad",
                      "    return torch.tensor(ids)",
                      "",
                      "",
                      "def encode_batch(texts, vocab, max_len=96):",
                      "    ids = [encode(t, vocab, max_len) for t in texts]",
                      "    x = torch.stack(ids)                # (B, 96)",
                      "    # 每个样本真实长度 —— 掩码就靠它",
                      "    lens = torch.tensor([",
                      "        min(len(tokenise(t)), max_len) for t in texts",
                      "    ])",
                      "    return x, lens",
                  ],
                  "en": [
                      "import torch",
                      "",
                      "def encode(text, vocab, max_len):",
                      "    ids = [vocab.get(w, 1) for w in tokenise(text)]",
                      "    ids = ids[:max_len]",
                      "    ids += [0] * (max_len - len(ids))   # pad",
                      "    return torch.tensor(ids)",
                      "",
                      "",
                      "def encode_batch(texts, vocab, max_len=96):",
                      "    ids = [encode(t, vocab, max_len) for t in texts]",
                      "    x = torch.stack(ids)                # (B, 96)",
                      "    # the true length of each sample - masking keys off this",
                      "    lens = torch.tensor([",
                      "        min(len(tokenise(t)), max_len) for t in texts",
                      "    ])",
                      "    return x, lens",
                  ]}},
         ],
         "note": zh("**lens 一定要留下来。** 少了它，你就只剩两种池化可选，而这两种正好是本周最差的两个。",
                    "**Keep `lens`.** Throw it away and you are left with exactly the two pooling "
                    "choices that turned out to be this week's worst.")},

        {"type": "table",
         "title": zh("本周语料：一份为了「不许作弊」而专门构造的数据集",
                                  "This week's corpus: built so that it cannot cheat"),
         "right": zh(PROTO, PROTO_EN),
         "subtitle": zh("任务只有一句话：**给一段英文段落，说出它出自第几周。** "
                        "语料来自本课程第 1–6 周自己的讲义、实验单与教材，不下载任何外部数据。",
                        "One task, one sentence: **given an English passage, name the week it came from.** "
                        "The corpus is this course's own Week 1–6 lecture notes, lab sheets and textbook — nothing is downloaded."),
         "top": 3.4, "h": 8.4, "bold_first": True,
         "widths": [7.4, 7.4, 7.4, 7.227],
         "cols": [zh("项目", "Item"), zh("数值", "Value"), zh("说明", "What it means"), zh("为什么这样设计", "Why")],
         "rows": [
             [zh("段落总数", "Passages"), zh(f"{N_PASSAGES}", f"{N_PASSAGES}"),
              zh("训练 523 / 验证 112 / 测试 113", "train 523 / val 112 / test 113"),
              zh("按周分层切分 70/15/15", "stratified by week, 70/15/15")],
             [zh("类别数", "Classes"), zh(f"{N_CLASSES}", f"{N_CLASSES}"),
              zh("W1 105 · W2 97 · W3 114 · W4 119 · W5 128 · W6 185",
                 "W1 105 · W2 97 · W3 114 · W4 119 · W5 128 · W6 185"),
              zh("**类别天然不平衡，最少的类只有最多的 57%**",
                 "**naturally imbalanced — the smallest class is 57% of the largest**")],
             [zh("词表", "Vocabulary"), zh(f"{VOCAB_FULL}", f"{VOCAB_FULL}"),
              zh(f"模型实际只见 {VOCAB_TRAIN} 个（只从训练集统计）",
                 f"the model sees {VOCAB_TRAIN} (counted on train only)"),
              zh("训练集之外的词一律 <unk>", "anything outside train becomes <unk>")],
             [zh("段落长度（词）", "Length (words)"),
              zh(f"中位 {LEN_MED} · 95 分位 {LEN_P95} · 最长 {LEN_MAX}",
                 f"median {LEN_MED} · p95 {LEN_P95} · max {LEN_MAX}"),
              zh(f"均值 {LEN_MEAN} 词", f"mean {LEN_MEAN} words"),
              zh("**长度差异大，填充必然发生**", "**wide spread — padding is unavoidable**")],
             [zh("反泄漏清洗", "Anti-leakage scrub"), zh(f"{SCRUB}", f"{SCRUB}"),
              zh("把 Week N / CU(N) / Lab N / 日期替换成占位符",
                 "Week N / CU(N) / Lab N / dates replaced with placeholders"),
              zh("否则答案的字面就写在题面里", "otherwise the label is literally in the text")],
             [zh("语料指纹", "Corpus fingerprint"), zh(SHA256[:12] + "…", SHA256[:12] + "…"),
              zh("SHA-256，可用 `build_text_corpus.py` 重建",
                 "SHA-256; rebuild with build_text_corpus.py"),
              zh("**可复现**：同一份语料，任何机器上结果一致",
                 "**reproducible**: same corpus, same numbers anywhere")],
         ],
         "note": zh(f"这份语料是**本课程自己的文本**（CC BY-NC-SA 4.0），因此零第三方许可风险、零下载、完全离线。"
                    f"代价是它很小——{N_PASSAGES} 段对于 6 分类来说太少了，**这正是 Part 3 那个「正则化救不回来」的根因**。",
                    f"The corpus is **this course's own text** (CC BY-NC-SA 4.0): no third-party licence risk, no download, fully offline. "
                    f"The price is size — {N_PASSAGES} passages is far too few for 6 classes, **which is the root cause of Part 3's 「regularisation does not rescue it」**.")},

        {"type": "compare",
         "title": zh("中文为什么不能按空白分词——一个可以量化的答案",
                                 "Why Chinese cannot be split on whitespace — a measurable answer"),
         "right": zh("本课程中文教材实测", "measured on this course's Chinese textbook"),
         "subtitle": zh("同一份中文文本，两种切分方式，看**词表外（OOV）比例**。"
                        "OOV 高的那一种，模型等于在猜。</",
                        "The same Chinese text, two segmentation schemes, compared on **out-of-vocabulary rate**. "
                        "The high-OOV scheme leaves the model guessing."),
         "top": 3.4, "h": 9.4,
         "columns": [
             {"title": zh("按空白切分（错的）", "Whitespace (wrong)"),
              "accent": "B91C1C",
              "items": [
                  zh(f"375 个训练片段 → 词表只有 {CJK_WS['vocab']} 个「词」",
                     f"375 train segments → a vocabulary of only {CJK_WS['vocab']}"),
                  zh(f"其中**单例词（只出现一次）占 {_pct(CJK_WS['singleton'])}**",
                     f"**{_pct(CJK_WS['singleton'])} of them are singletons**"),
                  zh(f"测试集 {CJK_WS['tokens']} 个 token 里，**{_pct(CJK_WS['oov'])} 是词表外**",
                     f"of {CJK_WS['tokens']} test tokens, **{_pct(CJK_WS['oov'])} are out of vocabulary**"),
                  zh("等价于：**整段文本只被识别成一个 <unk>**",
                     "In effect: **the whole passage collapses into a single <unk>**"),
                  zh("模型在任何中文任务上都学不到东西", "no Chinese task can be learned this way"),
              ]},
             {"title": zh("按字符级切分（对的）", "Character level (right)"),
              "accent": "059669",
              "items": [
                  zh(f"同样的 375 段 → 词表 {CJK_CH['vocab']} 个字符",
                     f"the same 375 segments → {CJK_CH['vocab']} characters"),
                  zh(f"单例占比降到 **{_pct(CJK_CH['singleton'])}**（差 {CJK_CH['singleton'] / CJK_WS['singleton']:.2f} 倍的量级）",
                     f"singleton share drops to **{_pct(CJK_CH['singleton'])}** (a different order of magnitude)"),
                  zh(f"测试集 token 数变成 {CJK_CH['tokens']}（每字一个）",
                     f"test tokens become {CJK_CH['tokens']} (one per character)"),
                  zh(f"OOV 只有 **{_pct(CJK_CH['oov'])}**",
                     f"OOV is only **{_pct(CJK_CH['oov'])}**"),
                  zh("代价：序列变长、语义单位变碎——**这是选择，不是免费**",
                     "The price: longer sequences, coarser units — **a trade, not a free win**"),
              ]},
         ],
         "note": zh(f"OOV 从 **{_pct(CJK_WS['oov'])}** 降到 **{_pct(CJK_CH['oov'])}**，差 {CJK_WS['oov'] / CJK_CH['oov']:.0f} 倍。"
                    f"工程上的正确做法通常是先上分词器（jieba 等），分词器不可用时退回字符级——"
                    f"**但绝不能什么都不做就按空格切。**",
                    f"OOV falls from **{_pct(CJK_WS['oov'])}** to **{_pct(CJK_CH['oov'])}**, a factor of "
                    f"{CJK_WS['oov'] / CJK_CH['oov']:.0f}. In practice you reach for a segmenter (jieba, etc.) "
                    f"and fall back to character level — **but you never just split on spaces and hope.**")},

        # ======================================================== Part 2 (08-12)
        {"type": "section", "num": "02",
         "title": zh("填充与掩码", "Padding and Masking"),
         "title_en": zh("Part 2 · the quiet bug", "Part 2 · the quiet bug"),
         "lead": zh(f"**{_pct(SHARE_SHORT)} 的测试文档短于 max_len=96。** "
                    f"也就是说，如果你在循环结束后直接取最后一个时间步的隐状态，"
                    f"**你读到的是填充向量，不是句子。** "
                    f"这个错误不会让程序崩，只会让准确率悄悄掉一半。",
                    f"**{_pct(SHARE_SHORT)} of test documents are shorter than max_len=96.** "
                    f"So if you take the hidden state at the final timestep, **you are reading the pad "
                    f"vector, not the sentence.** Nothing crashes. The accuracy just quietly halves."),
         "pillars": [
             {"title": zh("填充", "Pad"), "sub": zh("补零到定长", "zeros to fixed length")},
             {"title": zh("掩码", "Mask"), "sub": zh("告诉模型哪些是真词", "which positions are real")},
             {"title": zh("打包", "Pack"), "sub": zh("让 RNN 提前停下", "let the RNN stop early")},
             {"title": zh("池化", "Pool"), "sub": zh("怎么把序列压成一个向量", "sequence → one vector")},
         ]},

        {"type": "code",
         "title": zh("同一个 LSTM，两种读法——差别在最后三行",
                                 "One LSTM, two readings — the difference is the last three lines"),
         "right": zh("这是本周唯一必须看懂的对照", "the single comparison you must understand"),
         "subtitle": zh("上半：取 `out[:, -1, :]`——**取到的是第 96 个位置，不是最后一个真词**。"
                        "下半：`pack_padded_sequence` 让 LSTM 在真词结束处停下。",
                        "Top: `out[:, -1, :]` — **that is position 96, not the last real token.** "
                        "Bottom: `pack_padded_sequence` stops the LSTM where the real tokens end."),
         "top": 3.3, "h": 11.0,
         "blocks": [
             {"title": zh("✗ 错：读到填充向量", "✗ Wrong: reads the pad vector"),
              "size": 10.5,
              "code": {
                  "zh": [
                      "class TextLSTM(nn.Module):",
                      "    def __init__(self, vocab_size, hidden=96):",
                      "        super().__init__()",
                      "        self.emb = nn.Embedding(vocab_size, 64,",
                      "                                padding_idx=0)",
                      "        self.lstm = nn.LSTM(64, hidden,",
                      "                            batch_first=True)",
                      "        self.fc = nn.Linear(hidden, 6)",
                      "",
                      "    def forward(self, x, lens):",
                      "        e = self.emb(x)          # (B, 96, 64)",
                      "        out, _ = self.lstm(e)    # (B, 96, 96)",
                      "        # ✗ 第 96 个位置 = 填充",
                      "        return self.fc(out[:, -1, :])",
                  ],
                  "en": [
                      "class TextLSTM(nn.Module):",
                      "    def __init__(self, vocab_size, hidden=96):",
                      "        super().__init__()",
                      "        self.emb = nn.Embedding(vocab_size, 64,",
                      "                                padding_idx=0)",
                      "        self.lstm = nn.LSTM(64, hidden,",
                      "                            batch_first=True)",
                      "        self.fc = nn.Linear(hidden, 6)",
                      "",
                      "    def forward(self, x, lens):",
                      "        e = self.emb(x)          # (B, 96, 64)",
                      "        out, _ = self.lstm(e)    # (B, 96, 96)",
                      "        # ✗ position 96 is padding",
                      "        return self.fc(out[:, -1, :])",
                  ]}},
             {"title": zh("✓ 对：打包后取末隐状态", "✓ Right: pack, then take the last hidden state"),
              "size": 10.5,
              "code": {
                  "zh": [
                      "from torch.nn.utils.rnn import (",
                      "    pack_padded_sequence,",
                      "    pad_packed_sequence,",
                      ")",
                      "",
                      "# 必须在包里按长度降序",
                      "def forward(self, x, lens):",
                      "    e = self.emb(x)",
                      "    order = torch.argsort(lens, descending=True)",
                      "    inv = torch.argsort(order)",
                      "    packed = pack_padded_sequence(",
                      "        e[order], lens[order].cpu(),",
                      "        batch_first=True, enforce_sorted=True)",
                      "    out, (h, _) = self.lstm(packed)",
                      "    # h[-1] 是每个样本『最后一个真词』的隐状态",
                      "    return self.fc(h[-1][inv])",
                  ],
                  "en": [
                      "from torch.nn.utils.rnn import (",
                      "    pack_padded_sequence,",
                      "    pad_packed_sequence,",
                      ")",
                      "",
                      "# the pack requires descending length order",
                      "def forward(self, x, lens):",
                      "    e = self.emb(x)",
                      "    order = torch.argsort(lens, descending=True)",
                      "    inv = torch.argsort(order)",
                      "    packed = pack_padded_sequence(",
                      "        e[order], lens[order].cpu(),",
                      "        batch_first=True, enforce_sorted=True)",
                      "    out, (h, _) = self.lstm(packed)",
                      "    # h[-1] is each sample's LAST REAL token",
                      "    return self.fc(h[-1][inv])",
                  ]}},
         ],
         "note": zh("两段代码**参数量完全相同**（166 278），训练轮数相同，数据相同。"
                    "唯一的差别是「第 96 个位置」还是「最后一个真词」。下一页看这个差别值多少。",
                    "Both blocks have **exactly the same parameter count** (166,278), the same epochs, "
                    "the same data. The only difference is 「position 96」 versus 「the last real token」. "
                    "The next page prices it.")},

        {"type": "table",
         "title": zh("四种池化方式的总账：同一模型，差 26 个点",
                                 "Four pooling choices, one model, a 26-point spread"),
         "right": zh("5 种子均值 ± 1 sd", "mean ± 1 sd over 5 seeds"),
         "subtitle": zh("四个臂只改「怎么把 (B,96,96) 压成 (B,96)」这一步。参数量、数据、轮数、优化器全部相同。",
                        "The four arms differ only in how (B,96,96) becomes (B,96). Same parameters, data, epochs, optimiser."),
         "top": 3.4, "h": 7.6, "bold_first": True,
         "widths": [7.0, 5.4, 5.4, 5.4, 6.227],
         "cols": [zh("臂", "Arm"), zh("测试准确率", "Test acc"), zh("宏 F1", "Macro F1"),
                  zh("与最优差", "Gap to best"), zh("一句话", "In one line")],
         "rows": [
             [zh("mean_masked（最优）", "mean_masked (best)"),
              zh(f"{ARMS['mean_masked'][0]:.4f} ± {ARMS['mean_masked'][1]:.4f}",
                 f"{ARMS['mean_masked'][0]:.4f} ± {ARMS['mean_masked'][1]:.4f}"),
              zh(f"{ARMS['mean_masked'][2]:.4f}", f"{ARMS['mean_masked'][2]:.4f}"),
              zh("—", "—"),
              zh("按真实长度求均值", "average over real positions only")],
             [zh("packed", "packed"),
              zh(f"{ARMS['packed'][0]:.4f} ± {ARMS['packed'][1]:.4f}",
                 f"{ARMS['packed'][0]:.4f} ± {ARMS['packed'][1]:.4f}"),
              zh(f"{ARMS['packed'][2]:.4f}", f"{ARMS['packed'][2]:.4f}"),
              zh("−7.8 个点", "−7.8 points"),
              zh("正规做法，但只读末状态", "textbook, but reads one state")],
             [zh("mean_unmasked", "mean_unmasked"),
              zh(f"{ARMS['mean_unmasked'][0]:.4f} ± {ARMS['mean_unmasked'][1]:.4f}",
                 f"{ARMS['mean_unmasked'][0]:.4f} ± {ARMS['mean_unmasked'][1]:.4f}"),
              zh(f"{ARMS['mean_unmasked'][2]:.4f}", f"{ARMS['mean_unmasked'][2]:.4f}"),
              zh("−11.0 个点", "−11.0 points"),
              zh("把填充也算进均值", "padding folded into the mean")],
             [zh("last_step（最差）", "last_step (worst)"),
              zh(f"{ARMS['last_step'][0]:.4f} ± {ARMS['last_step'][1]:.4f}",
                 f"{ARMS['last_step'][0]:.4f} ± {ARMS['last_step'][1]:.4f}"),
              zh(f"{ARMS['last_step'][2]:.4f}", f"{ARMS['last_step'][2]:.4f}"),
              zh("−26.2 个点", "−26.2 points"),
              zh("读到的是填充向量", "reads the pad vector")],
         ],
         "note": zh(f"**最差与最优差 0.2620，接近 26 个点。** 请特别注意 `last_step` 的宏 F1 只有 "
                    f"{ARMS['last_step'][2]:.4f}——6 分类随机基线是 1/6 ≈ 0.1667，"
                    f"**它已经低于随机。** 而它的准确率是 {ARMS['last_step'][0]:.4f}，"
                    f"看上去只是「效果不好」，不像崩了。这就是 Part 4 要讲的指标问题。",
                    f"**The spread is 0.2620 — nearly 26 points.** Note `last_step`'s macro F1 of "
                    f"{ARMS['last_step'][2]:.4f}: the 6-class chance level is 1/6 ≈ 0.1667, "
                    f"**so it is below chance.** Its accuracy, {ARMS['last_step'][0]:.4f}, merely looks "
                    f"「mediocre」 rather than broken. That is Part 4's metric problem.")},

        {"type": "compare",
         "title": zh("掩码：一个「写了就等于没写」的错误",
                                 "Masking: the error that looks like it was never written"),
         "right": zh("mean_unmasked vs mean_masked", "mean_unmasked vs mean_masked"),
         "subtitle": zh("两个臂都做「对时间维求平均」，代码几乎逐字相同。差别只有一个布尔参数。",
                        "Both arms average over the time axis; the code is nearly character-identical. "
                        "The difference is one boolean."),
         "top": 3.4, "h": 9.2,
         "columns": [
             {"title": zh("✗ 不掩码", "✗ Unmasked"),
              "accent": "B91C1C",
              "items": [
                  zh(f"测试准确率 **{ARMS['mean_unmasked'][0]:.4f}**",
                     f"test accuracy **{ARMS['mean_unmasked'][0]:.4f}**"),
                  zh(f"宏 F1 **{ARMS['mean_unmasked'][2]:.4f}**",
                     f"macro F1 **{ARMS['mean_unmasked'][2]:.4f}**"),
                  zh("每篇短文档的向量里，**大部分位置是填充向量**",
                     "for a short document, **most positions in the average are pad vectors**"),
                  zh(f"文档越短被稀释得越狠：20–29 词桶只有 {BY_LENGTH['20-29'][1]:.4f}",
                     f"the shorter the document the worse: the 20–29 bucket gets {BY_LENGTH['20-29'][1]:.4f}"),
                  zh("标准差最大（±0.0684）——**结果不稳定**",
                     "largest spread (±0.0684) — **unstable**"),
              ]},
             {"title": zh("✓ 掩码", "✓ Masked"),
              "accent": "059669",
              "items": [
                  zh(f"测试准确率 **{ARMS['mean_masked'][0]:.4f}**（+{(ARMS['mean_masked'][0] - ARMS['mean_unmasked'][0]) * 100:.1f} 个点）",
                     f"test accuracy **{ARMS['mean_masked'][0]:.4f}** (+{(ARMS['mean_masked'][0] - ARMS['mean_unmasked'][0]) * 100:.1f} points)"),
                  zh(f"宏 F1 **{ARMS['mean_masked'][2]:.4f}**（+{(ARMS['mean_masked'][2] - ARMS['mean_unmasked'][2]) * 100:.1f} 个点）",
                     f"macro F1 **{ARMS['mean_masked'][2]:.4f}** (+{(ARMS['mean_masked'][2] - ARMS['mean_unmasked'][2]) * 100:.1f} points)"),
                  zh("`(h * mask).sum(1) / mask.sum(1)`——**一行**",
                     "`(h * mask).sum(1) / mask.sum(1)` — **one line**"),
                  zh(f"20–29 词桶回到 {BY_LENGTH['20-29'][1]:.4f}",
                     f"the 20–29 bucket returns to {BY_LENGTH['20-29'][1]:.4f}"),
                  zh("标准差收窄到 ±0.0449", "spread narrows to ±0.0449"),
              ]},
         ],
         "note": zh("注意哪一个桶涨得最多：**最短的那一桶**。这符合机制——文档越短，填充占的比例越大，"
                    "不掩码的伤害越重。**这就是「掩码不是优化，是正确性」的证据。**",
                    "Look at which bucket gains most: **the shortest one.** That matches the mechanism — "
                    "the shorter the document, the larger the pad share, the heavier the damage. "
                    "**Masking is not an optimisation; it is correctness.**")},

        {"type": "cards",
         "title": zh("解剖那个安静的 bug：按长度分桶，伤害就露出来了",
                                 "Autopsy of the quiet bug: bucket by length and the damage shows"),
         "right": zh(f"max_len = 96 · {_pct(SHARE_SHORT)} 文档未达此长度",
                     f"max_len = 96 · {_pct(SHARE_SHORT)} of docs fall short"),
         "subtitle": zh("同一个 `last_step` 臂，同一个准确率，按文档长度切开看。"
                        "如果错误是随机的，各桶应该差不多——它们不是。",
                        "Same arm, same headline accuracy, split by document length. "
                        "If the error were random the buckets would look alike. They do not."),
         "cols": 2, "gap": 0.7, "top": 3.3, "h": 6.5,
         "cards": [
             {"accent": "B91C1C",
              "title": zh("最短的桶塌得最狠", "The shortest bucket collapses"),
              "body": [zh(f"20–29 词：packed {BY_LENGTH['20-29'][1]:.4f} vs last_step **{BY_LENGTH['20-29'][2]:.4f}**",
                          f"20–29 words: packed {BY_LENGTH['20-29'][1]:.4f} vs last_step **{BY_LENGTH['20-29'][2]:.4f}**"),
                       zh(f"30–49 词：{BY_LENGTH['30-49'][1]:.4f} vs **{BY_LENGTH['30-49'][2]:.4f}**",
                          f"30–49 words: {BY_LENGTH['30-49'][1]:.4f} vs **{BY_LENGTH['30-49'][2]:.4f}**"),
                       zh("50–99 词：两者终于接近（0.4483 vs 0.4138）",
                          "50–99 words: they finally converge (0.4483 vs 0.4138)"),
                       zh("**越长越没事，正好是填充比例的镜像。**",
                          "**the longer the document, the smaller the harm — a mirror of the pad share.**")],
              "tag": zh("机制对上了", "mechanism fits")},
             {"accent": "1E4FA8",
              "title": zh("长度分界线上还有一条硬证据", "A second, harder line at the boundary"),
              "body": [zh(f"长度 ≥ 96 的文档：{LONG_SPLIT['at_ge'][0]} 篇，准确率 **{LONG_SPLIT['at_ge'][1]:.4f}**",
                          f"documents at or above 96 words: {LONG_SPLIT['at_ge'][0]}, accuracy **{LONG_SPLIT['at_ge'][1]:.4f}**"),
                       zh(f"长度 < 96 的文档：{LONG_SPLIT['below'][0]} 篇，准确率 **{LONG_SPLIT['below'][1]:.4f}**",
                          f"documents below 96 words: {LONG_SPLIT['below'][0]}, accuracy **{LONG_SPLIT['below'][1]:.4f}**"),
                       zh("长度够的文档没有填充位置，`[-1]` 就真的指向句末——**它们基本正常**。",
                          "Long enough documents have no padded positions, so `[-1]` really is the end — **they behave normally.**"),
                       zh("**这排除了「只是数据太难」的解释。**",
                          "**This rules out 「the task is just hard」.**")],
              "tag": zh("同一条 bug，两组证据", "one bug, two lines of evidence")},
         ]},

        # ======================================================== Part 3 (13-17)
        {"type": "section", "num": "03",
         "title": zh("训练曲线与真正的瓶颈", "Curves and the Real Bottleneck"),
         "title_en": zh("Part 3 · it overfits, and that is not the main problem",
                        "Part 3 · it overfits, and that is not the main problem"),
         "lead": zh("最好的一臂只有 **0.5027**。第一反应是「正则化不够」。"
                    "这一部分用三条证据说明：**它确实过拟合了，但正则化救不回来——因为瓶颈是那 523 个训练段落。**",
                    "The best arm reaches only **0.5027**. The reflex is 「add regularisation」. "
                    "Three pieces of evidence say: **yes it overfits, but regularisation does not rescue it — "
                    "the bottleneck is the 523 training passages.**"),
         "pillars": [
             {"title": zh("过拟合", "Overfitting"), "sub": zh("训练 0.99 / 验证 0.42", "train 0.99 / val 0.42")},
             {"title": zh("正则化", "Regularisation"), "sub": zh("试过了，没救回来", "tried it, did not work")},
             {"title": zh("序列长度", "Sequence length"), "sub": zh("扫过 48/96/192", "swept 48/96/192")},
             {"title": zh("数据量", "Data"), "sub": zh("523 段太少", "523 passages is too few")},
         ]},

        {"type": "chart",
         "title": zh("训练与验证：一条冲到 0.99，一条停在 0.42",
                                 "Train against validation: one runs to 0.99, one parks at 0.42"),
         "right": zh("packed 臂 · 种子 42", "packed arm · seed 42"),
         "subtitle": zh("11 个采样点（每 3 轮记一次，共 30 轮）。两条线的距离就是过拟合的量。",
                        "11 sampled points (every 3 epochs, 30 total). The distance between the lines is the overfitting."),
         "categories": CURVE_X,
         "series": [
             {"name": zh("训练准确率", "Train accuracy"), "values": CURVE_TRAIN,
              "color": "D97706", "smooth": False, "emphasis": True},
             {"name": zh("验证准确率", "Validation accuracy"), "values": CURVE_VAL,
              "color": "1E4FA8", "smooth": False, "emphasis": True},
         ],
         "x_label": zh("训练轮次", "epoch"),
         "y_label": zh("准确率", "accuracy"),
         "x": 2.22, "y": 3.4, "w": 19.0, "h": 11.0, "y_max": 1.0,
         "notes": [
             zh(f"第 30 轮：训练 {CURVE_TRAIN[-1]:.4f}，验证 {CURVE_VAL[-1]:.4f}，**差 {CURVE_TRAIN[-1] - CURVE_VAL[-1]:.4f}**。",
                f"At epoch 30: train {CURVE_TRAIN[-1]:.4f}, val {CURVE_VAL[-1]:.4f}, **a gap of {CURVE_TRAIN[-1] - CURVE_VAL[-1]:.4f}**."),
             zh("训练第 24 轮就到 0.9675，验证只有 0.3661——**模型在背训练集**。",
                "By epoch 24 train is already 0.9675 while val is 0.3661 — **the model is memorising.**"),
             zh("验证曲线**从未下降**，所以这不是「训练过头」，而是「容量用错了地方」。",
                "The validation curve **never falls**, so this is not 「trained too long」; it is capacity spent in the wrong place."),
             zh("这正是第 6 周讲过的形状——**同一张脸，换了数据集**。",
                "This is exactly the shape from Week 6 — **the same face, a different dataset.**"),
         ]},

        {"type": "table",
         "title": zh("扫 max_len：48 / 96 / 192，切掉或者补多都没用",
                                 "Sweeping max_len: 48, 96, 192 — neither truncating nor padding helps"),
         "right": zh("3 种子（42–44）", "3 seeds (42–44)"),
         "subtitle": zh("一个自然的猜测是「96 太长/太短」。扫一遍就知道：这不是长度问题。",
                        "A natural guess is 「96 is too long or too short」. Sweep it and the guess dies."),
         "top": 3.4, "h": 7.2, "bold_first": True,
         "widths": [6.4, 5.8, 5.8, 5.8, 5.627],
         "cols": [zh("max_len", "max_len"), zh("packed 准确率", "packed acc"),
                  zh("last_step 准确率", "last_step acc"), zh("packed 标准差", "packed sd"),
                  zh("解读", "Reading")],
         "rows": [
             [zh("48（更短，切掉长文）", "48 (shorter, truncates)"),
              zh(f"{MAXLEN_PACKED[0]:.4f}", f"{MAXLEN_PACKED[0]:.4f}"),
              zh(f"{MAXLEN_LAST[0]:.4f}", f"{MAXLEN_LAST[0]:.4f}"),
              zh(f"{0.0135:.4f}", "0.0135"),
              zh("packed 略好，last_step 也涨——**符合机制**",
                 "packed a little better; last_step rises too — **as the mechanism predicts**")],
             [zh("96（本周默认）", "96 (this week's default)"),
              zh(f"{MAXLEN_PACKED[1]:.4f}", f"{MAXLEN_PACKED[1]:.4f}"),
              zh(f"{MAXLEN_LAST[1]:.4f}", f"{MAXLEN_LAST[1]:.4f}"),
              zh(f"{0.0285:.4f}", "0.0285"),
              zh("基准", "baseline")],
             [zh("192（更长，补更多）", "192 (longer, pads more)"),
              zh(f"{MAXLEN_PACKED[2]:.4f}", f"{MAXLEN_PACKED[2]:.4f}"),
              zh(f"{MAXLEN_LAST[2]:.4f}", f"{MAXLEN_LAST[2]:.4f}"),
              zh(f"{0.0357:.4f}", "0.0357"),
              zh("**完全没涨**——补更多零不产生信息",
                 "**no gain at all** — more zeros carry no information")],
         ],
         "note": zh(f"packed 在三个长度上分别是 {MAXLEN_PACKED[0]:.4f} / {MAXLEN_PACKED[1]:.4f} / "
                    f"{MAXLEN_PACKED[2]:.4f}——**基本不动**（波动在标准差以内）。"
                    f"与此同时 last_step 在三种长度上都远低于它。"
                    f"**结论：调 max_len 不是杠杆；但选错池化方式，调什么长度都白搭。**",
                    f"packed lands at {MAXLEN_PACKED[0]:.4f} / {MAXLEN_PACKED[1]:.4f} / {MAXLEN_PACKED[2]:.4f} — "
                    f"**essentially flat** (within one standard deviation). last_step stays far below it at every length. "
                    f"**Conclusion: max_len is not the lever; the pooling bug survives every length you try.**")},

        {"type": "compare",
         "title": zh("正则化救不回来——这是本周最重要的诚实结论",
                                 "Regularisation does not rescue it — this week's most important honest result"),
         "right": zh("沿用第 6 周的手段", "Week 6's tools, applied to the best arm"),
         "subtitle": zh("把第 6 周最有效的两样东西（Dropout 0.3 + 权重衰减 1e-3）加到本周最好的一臂上。"
                        "如果瓶颈是容量，应该涨；如果瓶颈是数据，不该涨。",
                        "Week 6's two most effective tools (Dropout 0.3 + weight decay 1e-3) added to this week's best arm. "
                        "If capacity is the bottleneck it should rise; if data is, it should not."),
         "top": 3.4, "h": 9.2,
         "columns": [
             {"title": zh("mean_masked（基准最优）", "mean_masked (baseline best)"),
              "accent": "1E4FA8",
              "items": [
                  zh(f"测试准确率 **{ARMS['mean_masked'][0]:.4f} ± {ARMS['mean_masked'][1]:.4f}**",
                     f"test accuracy **{ARMS['mean_masked'][0]:.4f} ± {ARMS['mean_masked'][1]:.4f}**"),
                  zh(f"宏 F1 **{ARMS['mean_masked'][2]:.4f} ± {ARMS['mean_masked'][3]:.4f}**",
                     f"macro F1 **{ARMS['mean_masked'][2]:.4f} ± {ARMS['mean_masked'][3]:.4f}**"),
                  zh("无 Dropout，无权重衰减", "no Dropout, no weight decay"),
                  zh("参数量 166 278", "166,278 parameters"),
                  zh("**这是本周的最好成绩，就到这里了**",
                     "**this is this week's ceiling**"),
              ]},
             {"title": zh("+ Dropout 0.3 + wd 1e-3", "+ Dropout 0.3 + wd 1e-3"),
              "accent": "B91C1C",
              "items": [
                  zh(f"测试准确率 **{ARMS['mean_masked_reg'][0]:.4f} ± {ARMS['mean_masked_reg'][1]:.4f}**",
                     f"test accuracy **{ARMS['mean_masked_reg'][0]:.4f} ± {ARMS['mean_masked_reg'][1]:.4f}**"),
                  zh(f"宏 F1 **{ARMS['mean_masked_reg'][2]:.4f} ± {ARMS['mean_masked_reg'][3]:.4f}**",
                     f"macro F1 **{ARMS['mean_masked_reg'][2]:.4f} ± {ARMS['mean_masked_reg'][3]:.4f}**"),
                  zh(f"准确率 **下降 {(ARMS['mean_masked'][0] - ARMS['mean_masked_reg'][0]) * 100:.1f} 个点**",
                     f"accuracy **drops {(ARMS['mean_masked'][0] - ARMS['mean_masked_reg'][0]) * 100:.1f} points**"),
                  zh(f"宏 F1 下降 {(ARMS['mean_masked'][2] - ARMS['mean_masked_reg'][2]) * 100:.1f} 个点",
                     f"macro F1 drops {(ARMS['mean_masked'][2] - ARMS['mean_masked_reg'][2]) * 100:.1f} points"),
                  zh("标准差反而变大（±0.0595）——**更不稳了**",
                     "spread actually widens (±0.0595) — **less stable**"),
              ]},
         ],
         "note": zh(f"第 6 周这两招是有效的（那里的数据够、模型大）。本周它们**同时压低了准确率和宏 F1**，"
                    f"还把方差放大了。这正是我们要教的东西：**同一个技术手段，在「容量瓶颈」和「数据瓶颈」下的正确答案是相反的。**"
                    f"判断依据不是手段本身，是你先诊断出瓶颈在哪。",
                    f"In Week 6 these two worked (enough data, a big model). Here they **lower both accuracy and macro F1** "
                    f"and widen the spread. That is the lesson: **the same technique has opposite correct answers under a "
                    f"capacity bottleneck and under a data bottleneck.** You pick by diagnosing the bottleneck first, not by taste.")},

        {"type": "chart",
         "title": zh("瓶颈是数据：类别越大，召回越高",
                                 "The bottleneck is data: the bigger the class, the better the recall"),
         "right": zh("packed 臂 · 5 种子合计", "packed arm · pooled over 5 seeds"),
         "subtitle": zh("同一个模型、同一批特征，**只按类别大小排序**，召回率就大致跟着排好了（Spearman ρ = 0.77）。"
                        "这是「模型在学先验，而不是在学内容」的直接证据。",
                        "Same model, same features — **sort the six classes by size** and recall tracks it closely (Spearman rho = 0.77). "
                        "Direct evidence that the model is learning the prior, not the content."),
         "categories": [
             f"W1 · n={PER_CLASS_TEST[0]}", f"W2 · n={PER_CLASS_TEST[1]}",
             f"W3 · n={PER_CLASS_TEST[2]}", f"W4 · n={PER_CLASS_TEST[3]}",
             f"W5 · n={PER_CLASS_TEST[4]}", f"W6 · n={PER_CLASS_TEST[5]}",
         ],
         "series": [
             {"name": zh("各类召回率", "Per-class recall"), "values": RECALL,
              "color": "1E4FA8", "smooth": False, "emphasis": True},
         ],
         "x_label": zh("类别（按测试样本数排列）", "class (ordered by test size)"),
         "y_label": zh("召回率", "recall"),
         "x": 2.22, "y": 3.4, "w": 19.0, "h": 11.0, "y_max": 0.75,
         "notes": [
             zh(f"最小的两类（n={PER_CLASS_TEST[0]}、{PER_CLASS_TEST[1]}）召回 **{RECALL[0]:.4f} / {RECALL[1]:.4f}**。",
                f"The two smallest classes (n={PER_CLASS_TEST[0]}, {PER_CLASS_TEST[1]}) recall **{RECALL[0]:.4f} / {RECALL[1]:.4f}**."),
             zh(f"最大的类（n={PER_CLASS_TEST[5]}）召回 **{RECALL[5]:.4f}**，是 W1 的 {RECALL[5] / RECALL[0]:.1f} 倍。",
                f"The largest class (n={PER_CLASS_TEST[5]}) recalls **{RECALL[5]:.4f}** — {RECALL[5] / RECALL[0]:.1f}× W1."),
             zh(f"有两处小逆序：W2（n=75）略高于 W1（n=80），W5（n=95）略低于 W4（n=90）。",
                f"There are two small inversions: W2 (n=75) edges above W1 (n=80), and W5 (n=95) dips just below W4 (n=90)."),
             zh("**所以「加正则化」不会有用：欠的是样本，不是约束。**",
                "**So regularisation cannot help: what is missing is samples, not constraints.**"),
         ]},

        # ======================================================== Part 4 (18-22)
        {"type": "section", "num": "04",
         "title": zh("它错在哪", "Where It Goes Wrong"),
         "title_en": zh("Part 4 · recommend a number you would defend",
                        "Part 4 · recommend a number you would defend"),
         "lead": zh("0.5027 这个准确率几乎不提供信息。这一部分换成两个更好用的东西："
                    "**6×6 混淆矩阵**，和**准确率与宏 F1 的分裂**。"
                    "后者就是本周思政落点的量化版本。",
                    "0.5027 carries almost no information. This part swaps it for two things that do: "
                    "**a 6×6 confusion matrix**, and **the accuracy / macro-F1 split**. "
                    "The latter is the quantified version of this week's ethics point."),
         "pillars": [
             {"title": zh("混淆矩阵", "Confusion matrix"), "sub": zh("6×6，逐格可查", "6×6, cell by cell")},
             {"title": zh("准确率 ≠ 宏 F1", "Accuracy ≠ macro F1"), "sub": zh("差 17 个点", "a 17-point gap")},
             {"title": zh("具体样本", "Concrete cases"), "sub": zh("14 篇逐条看", "14 passages, read them")},
             {"title": zh("交付标准", "Delivery bar"), "sub": zh("四条，可检查", "four checks")},
         ]},

        {"type": "table",
         "title": zh("混淆矩阵：5 个种子、565 个测试预测之和",
                                 "Confusion matrix: 565 test predictions over 5 seeds"),
         "right": zh("packed 臂", "packed arm"),
         "subtitle": zh("行＝真实周次，列＝模型判断。对角是正确，非对角是错误。合计 565，正确 240（0.4248）。",
                        "Row = true week, column = prediction. Diagonal is correct. Total 565; correct 240 (0.4248)."),
         "top": 3.5, "h": 8.0, "bold_first": True, "body_size": 11.5, "head_size": 12,
         "widths": [5.0, 4.07, 4.07, 4.07, 4.07, 4.07, 4.077],
         "cols": [zh("真实＼预测", "true / pred"),
                  zh("W1", "W1"), zh("W2", "W2"), zh("W3", "W3"),
                  zh("W4", "W4"), zh("W5", "W5"), zh("W6", "W6")],
         "rows": [
             [zh("W1（n=80）", "W1 (n=80)")] + [zh(str(v), str(v)) for v in CONFUSION[0]],
             [zh("W2（n=75）", "W2 (n=75)")] + [zh(str(v), str(v)) for v in CONFUSION[1]],
             [zh("W3（n=85）", "W3 (n=85)")] + [zh(str(v), str(v)) for v in CONFUSION[2]],
             [zh("W4（n=90）", "W4 (n=90)")] + [zh(str(v), str(v)) for v in CONFUSION[3]],
             [zh("W5（n=95）", "W5 (n=95)")] + [zh(str(v), str(v)) for v in CONFUSION[4]],
             [zh("W6（n=140）", "W6 (n=140)")] + [zh(str(v), str(v)) for v in CONFUSION[5]],
         ],
         "note": zh(f"读法只有一句：**看非对角，而且看它是均匀的还是集中的。** "
                    f"这一张的非对角**几乎是平的**——每个格子都在 4～22 之间，"
                    f"没有任何一个「重灾区」。对角线上只有 W6 明显突出（93）。"
                    f"**一个「什么都能错一点、什么都学不精」的矩阵，诊断是数据不足，不是模型不对。**",
                    f"One reading rule: **look off-diagonal, and ask whether the mass is uniform or concentrated.** "
                    f"Here it is **almost flat** — every cell sits between 4 and 22, with no disaster zone. "
                    f"On the diagonal only W6 stands out (93). **A matrix that gets a bit of everything wrong and "
                    f"nothing right is diagnosed as too little data, not a wrong model.**")},

        {"type": "code",
         "title": zh("把错分的那几段亲自读一遍", "Read the misclassified passages yourself"),
         "right": zh("14 篇 · 种子 42", "14 passages · seed 42"),
         "subtitle": zh("打印矩阵只是第一步。第二步是把错分样本的**原文**调出来看——"
                        "你会立刻发现它们都是好句子，只是**不属于任何单独一周**。",
                        "Printing the matrix is step one. Step two is pulling the **raw text** of the misclassified "
                        "passages — and immediately seeing that they are fine sentences that simply **belong to no single week**."),
         "top": 3.3, "h": 11.0,
         "blocks": [
             {"title": zh("打印错分样本", "Print the failures"),
              "size": 10.5,
              "code": {
                  "zh": [
                      "@torch.no_grad()",
                      "def show_errors(model, loader, vocab, inv_vocab, n=10):",
                      "    model.eval()",
                      "    shown = 0",
                      "    for x, lens, y in loader:",
                      "        logits = model(x, lens)",
                      "        pred = logits.argmax(1)",
                      "        bad = (pred != y).nonzero().flatten()",
                      "        for i in bad:",
                      "            ids = x[i][x[i] != 0].tolist()",
                      "            words = ' '.join(",
                      "                inv_vocab.get(j, '<unk>') for j in ids)",
                      "            p = logits[i].softmax(0)[pred[i]].item()",
                      "            print(f'true W{y[i]+1} -> pred W{pred[i]+1}'",
                      "                  f'  conf={p:.4f}')",
                      "            print(f'   {words[:120]}...')",
                      "            shown += 1",
                      "            if shown >= n:",
                      "                return",
                  ],
                  "en": [
                      "@torch.no_grad()",
                      "def show_errors(model, loader, vocab, inv_vocab, n=10):",
                      "    model.eval()",
                      "    shown = 0",
                      "    for x, lens, y in loader:",
                      "        logits = model(x, lens)",
                      "        pred = logits.argmax(1)",
                      "        bad = (pred != y).nonzero().flatten()",
                      "        for i in bad:",
                      "            ids = x[i][x[i] != 0].tolist()",
                      "            words = ' '.join(",
                      "                inv_vocab.get(j, '<unk>') for j in ids)",
                      "            p = logits[i].softmax(0)[pred[i]].item()",
                      "            print(f'true W{y[i]+1} -> pred W{pred[i]+1}'",
                      "                  f'  conf={p:.4f}')",
                      "            print(f'   {words[:120]}...')",
                      "            shown += 1",
                      "            if shown >= n:",
                      "                return",
                  ]}},
             {"title": zh("你会读到的三类句子", "The three kinds of sentence you will find"),
              "size": 10.5,
              "code": {
                  "zh": [
                      "# 1) 短句，词表负担最重",
                      "# true W4 -> pred W3   (20 词)",
                      "\"Hidden layers transform the features",
                      " first; the output layer decides afterwards.\"",
                      "",
                      "# 2) 通用工程句子，哪一周都成立",
                      "# true W1 -> pred W2   (26 词)",
                      "\"Hyper-parameters, data paths, batch size",
                      " and split ratios live in a file ...\"",
                      "",
                      "# 3) 术语跨周复用（这里 17,226 出现在 W6 段落里）",
                      "# true W6 -> pred W4   (22 词)",
                      "\"Explain how a training set of 80 samples",
                      " against 17,226 parameters produces",
                      " overfitting ...\"",
                      "",
                      "# 结论：14 篇里没有一篇是「模型看错了」",
                      "#     它们本来就不属于单独一周",
                  ],
                  "en": [
                      "# 1) short, so the vocabulary burden is heaviest",
                      "# true W4 -> pred W3   (20 tokens)",
                      "\"Hidden layers transform the features",
                      " first; the output layer decides afterwards.\"",
                      "",
                      "# 2) a generic engineering sentence, true of any week",
                      "# true W1 -> pred W2   (26 tokens)",
                      "\"Hyper-parameters, data paths, batch size",
                      " and split ratios live in a file ...\"",
                      "",
                      "# 3) vocabulary reused across weeks (17,226 appears in a W6 passage)",
                      "# true W6 -> pred W4   (22 tokens)",
                      "\"Explain how a training set of 80 samples",
                      " against 17,226 parameters produces",
                      " overfitting ...\"",
                      "",
                      "# conclusion: none of the 14 is a modelling mistake;",
                      "#             they belong to no single week",
                  ]}},
         ],
         "note": zh(f"**这 14 篇不是模型的失败，是任务定义的边界。** "
                    f"「这一段属于哪一周」在语义上本来就没有唯一答案——尤其当段落取自跨周复用的概念时。"
                    f"**课件的正确做法是把这个发现写进报告，而不是继续调参。**",
                    f"**These 14 are not model failures; they are the task's boundary.** "
                    f"「Which week does this passage belong to」 has no unique answer — especially for "
                    f"concepts reused across weeks. **The right move is to write that finding into the report, "
                    f"not to keep tuning.**")},

        {"type": "table",
         "title": zh("准确率与宏 F1 的分裂：一个必须会认的信号",
                                 "The accuracy / macro-F1 split: a signal you must recognise"),
         "right": zh("同一批臂，两个数字", "the same arms, two numbers"),
         "subtitle": zh("6 分类的随机基线是 1/6 ≈ 0.1667。**准确率会让你以为模型在正常工作；宏 F1 会说真话。**",
                        "Six-class chance level is 1/6 ≈ 0.1667. **Accuracy lets a broken model look employed; macro F1 tells the truth.**"),
         "top": 3.4, "h": 7.6, "bold_first": True,
         "widths": [6.6, 5.6, 5.6, 5.6, 6.027],
         "cols": [zh("臂", "Arm"), zh("准确率", "Accuracy"), zh("宏 F1", "Macro F1"),
                  zh("差距", "Gap"), zh("诊断", "Diagnosis")],
         "rows": [
             [zh("mean_masked", "mean_masked"),
              zh(f"{ARMS['mean_masked'][0]:.4f}", f"{ARMS['mean_masked'][0]:.4f}"),
              zh(f"{ARMS['mean_masked'][2]:.4f}", f"{ARMS['mean_masked'][2]:.4f}"),
              zh(f"{(ARMS['mean_masked'][0] - ARMS['mean_masked'][2]) * 100:.1f} 点",
                 f"{(ARMS['mean_masked'][0] - ARMS['mean_masked'][2]) * 100:.1f} pts"),
              zh("两个数字一致——**报告可信**",
                 "the two agree — **a trustworthy report**")],
             [zh("packed", "packed"),
              zh(f"{ARMS['packed'][0]:.4f}", f"{ARMS['packed'][0]:.4f}"),
              zh(f"{ARMS['packed'][2]:.4f}", f"{ARMS['packed'][2]:.4f}"),
              zh(f"{(ARMS['packed'][0] - ARMS['packed'][2]) * 100:.1f} 点",
                 f"{(ARMS['packed'][0] - ARMS['packed'][2]) * 100:.1f} pts"),
              zh("轻微分裂，可接受", "mild split, acceptable")],
             [zh("mean_unmasked", "mean_unmasked"),
              zh(f"{ARMS['mean_unmasked'][0]:.4f}", f"{ARMS['mean_unmasked'][0]:.4f}"),
              zh(f"{ARMS['mean_unmasked'][2]:.4f}", f"{ARMS['mean_unmasked'][2]:.4f}"),
              zh(f"{(ARMS['mean_unmasked'][0] - ARMS['mean_unmasked'][2]) * 100:.1f} 点",
                 f"{(ARMS['mean_unmasked'][0] - ARMS['mean_unmasked'][2]) * 100:.1f} pts"),
              zh("分裂开始明显", "the split is now visible")],
             [zh("last_step", "last_step"),
              zh(f"{ARMS['last_step'][0]:.4f}", f"{ARMS['last_step'][0]:.4f}"),
              zh(f"{ARMS['last_step'][2]:.4f}", f"{ARMS['last_step'][2]:.4f}"),
              zh(f"**{(ARMS['last_step'][0] - ARMS['last_step'][2]) * 100:.1f} 点**",
                 f"**{(ARMS['last_step'][0] - ARMS['last_step'][2]) * 100:.1f} pts**"),
              zh(f"**宏 F1 {ARMS['last_step'][2]:.4f} 低于随机 0.1667**",
                 f"**macro F1 {ARMS['last_step'][2]:.4f} is below chance 0.1667**")],
         ],
         "note": zh(f"`last_step` 的准确率是 {ARMS['last_step'][0]:.4f}，看上去「只是不好」；"
                    f"宏 F1 是 {ARMS['last_step'][2]:.4f}，**低于随机**。两个数字的差距是 "
                    f"{(ARMS['last_step'][0] - ARMS['last_step'][2]) * 100:.1f} 个点。"
                    f"**只报准确率的报告会把一个坏掉的模型送进上线。**",
                    f"`last_step` reports {ARMS['last_step'][0]:.4f} accuracy, which reads as 「just weak」; "
                    f"its macro F1 is {ARMS['last_step'][2]:.4f} — **below chance**. The gap is "
                    f"{(ARMS['last_step'][0] - ARMS['last_step'][2]) * 100:.1f} points. "
                    f"**An accuracy-only report ships this broken model.**")},

        {"type": "checklist",
         "title": zh("错分分析的交付标准：四条，条条可检查",
                                 "The error-analysis delivery bar: four checks you can verify"),
         "right": zh("对应官方课后任务", "the official homework, operationalised"),
         "subtitle": zh("官方原话是「说明为什么模型在某些类别上表现更差」。下面是这句话的可检查版本。",
                        "The official wording is 「explain why the model does worse on some classes」. "
                        "Here is the checkable version."),
         "top": 3.4, "h": 2.9,
         "items": [
             {"badge": zh("① 混淆矩阵", "1 · Matrix"), "accent": "1E4FA8",
              "title": zh("打印矩阵本身，并写出三个总数", "Print the matrix and state three totals"),
              "desc": zh("预测总数 565、正确 240、准确率 0.4248，以及**对角线上哪一格最大**（W6 的 93）。"
                         "只写准确率不算通过。",
                         "Total 565, correct 240, accuracy 0.4248, and **which diagonal cell is largest** (W6 at 93). "
                         "Accuracy alone does not pass.")},
             {"badge": zh("② 两个指标", "2 · Two metrics"), "accent": "059669",
              "title": zh("准确率与宏 F1 同时报，并解释差距", "Report accuracy and macro F1 together, and explain the gap"),
              "desc": zh("`last_step` 的 0.2407 对 0.0711 是本周最好的教学素材："
                         "**宏 F1 低于随机 0.1667，而准确率看不出来。**",
                         "`last_step`'s 0.2407 against 0.0711 is the week's best teaching specimen: "
                         "**macro F1 below chance (0.1667) while accuracy shows nothing.**")},
             {"badge": zh("③ 具体样本", "3 · Concrete cases"), "accent": "D97706",
              "title": zh("至少 3 段错分原文 + 模型置信度", "At least 3 raw passages with model confidence"),
              "desc": zh("种子 42 一共 14 段，全部可查。要求**贴原文**，不接受「模型学得不好」这类说法。",
                         "Seed 42 yields 14; all retrievable. The rule is **quote the text** — "
                         "「the model learned poorly」 is not accepted.")},
             {"badge": zh("④ 一个可检验假设", "4 · One testable hypothesis"), "accent": "B91C1C",
              "title": zh("写出一条能被下一步推翻的猜想", "Write one guess the next step could falsify"),
              "desc": zh("例如：「把 max_len 降到 48 会让最短桶的准确率上升」。"
                         "然后**去跑它**，把结果写回报告——不管涨没涨。",
                         "For example: 「lowering max_len to 48 raises the shortest bucket」. "
                         "Then **run it** and write the outcome back — win or lose.")},
         ]},

        # ======================================================== Part 5 (23-26)
        {"type": "section", "num": "05",
         "title": zh("接下来，以及 M8", "Next, and M8"),
         "title_en": zh("Part 5 · the hook for Module 3, and the midterm checkpoint",
                        "Part 5 · the hook for Module 3, and the midterm checkpoint"),
         "lead": zh("本周的 LSTM 是**模块三全部内容的对照组**：第 9 周迁移学习、第 10 周注意力与 Transformer，"
                    "都会拿它当基准。另外，**第 8 周同时是 M8 期中检查点**——大作业在这里第一次被正式评一次。",
                    "This week's LSTM is **the control arm for all of Module 3**: W9 transfer learning and W10 "
                    "attention/Transformers are measured against it. And **Week 8 is also M8, the midterm checkpoint** — "
                    "the first formally graded review of the project."),
         "pillars": [
             {"title": zh("RNN → LSTM", "RNN → LSTM"), "sub": zh("门控解决梯度", "gates fix gradients")},
             {"title": zh("→ Attention", "→ Attention"), "sub": zh("不再顺序处理", "no more sequential scan")},
             {"title": zh("→ Transformer", "→ Transformer"), "sub": zh("本周的对照组", "this week's control")},
             {"title": zh("M8 ★", "M8 ★"), "sub": zh("期中检查点 4 分", "midterm, 4 points")},
         ]},

        {"type": "table",
         "title": zh("把本周的 LSTM 放进序列模型的谱系里",
                                 "Placing this week's LSTM in the sequence-model lineage"),
         "right": zh("周次对应官方课程地图", "weeks per the official course map"),
         "subtitle": zh("三次升级各自解决一个具体缺陷。**下周开始你会亲手把这三步走一遍**，而本周的 0.5027 就是基准线。",
                        "Three upgrades, each fixing a specific defect. **From next week you walk all three yourself**, "
                        "with this week's 0.5027 as the baseline."),
         "top": 3.4, "h": 8.8, "bold_first": True,
         "widths": [4.6, 6.2, 6.2, 6.2, 6.227],
         "cols": [zh("模型", "Model"), zh("解决了什么", "What it fixed"),
                  zh("留下了什么", "What it left"), zh("关键机制", "Key mechanism"),
                  zh("课程位置", "Where in the course")],
         "rows": [
             [zh("RNN", "RNN"),
              zh("第一次让参数跨时间共享", "first model to share parameters across time"),
              zh("长序列梯度消失/爆炸", "vanishing/exploding gradients on long sequences"),
              zh("h_t = tanh(Wx + Uh_{t-1})", "h_t = tanh(Wx + Uh_{t-1})"),
              zh("本周知识点（KT16）", "this week (KT16)")],
             [zh("LSTM / GRU", "LSTM / GRU"),
              zh("用门控把「记住什么」变成可学的", "makes 「what to remember」 learnable via gates"),
              zh("仍然必须顺序计算，无法并行", "still sequential — cannot be parallelised"),
              zh("遗忘门 / 输入门 / 输出门", "forget / input / output gates"),
              zh("**本周实验 7 用的就是它**", "**lab 7 uses exactly this**")],
             [zh("Attention", "Attention"),
              zh("取消「必须压成一个向量」的瓶颈", "removes the fixed-vector bottleneck"),
              zh("本身不含位置信息", "carries no positional information"),
              zh("Q·Kᵀ → softmax → V", "Q·Kᵀ → softmax → V"),
              zh("第 10 周（CU(10)）", "Week 10 (CU(10))")],
             [zh("Transformer", "Transformer"),
              zh("把注意力堆深，训练可完全并行", "stacks attention deeply and parallelises fully"),
              zh("数据与算力需求陡增（本周的瓶颈会更痛）",
                 "needs far more data and compute (this week's bottleneck gets worse)"),
              zh("多头 + 位置编码 + 残差", "multi-head + positional encoding + residual"),
              zh("第 10–11 周（CU(10–11)）", "Weeks 10–11 (CU(10–11))")],
         ],
         "note": zh("注意最后一行那句话：**Transformer 会把「数据不够」这个问题放大，而不是缩小。** "
                    "本周你亲眼看到 523 个训练段落能把一个 166 K 参数的 LSTM 逼到什么程度——"
                    "同一个瓶颈在第 10 周会以更贵的形式回来。**这才是本周最该带走的东西。**",
                    "Note the last row: **a Transformer amplifies the 「not enough data」 problem, not the reverse.** "
                    "You have just watched 523 training passages pin a 166K-parameter LSTM — "
                    "the same bottleneck returns in Week 10, more expensively. **That is the thing to carry out of this week.**")},

        {"type": "cards",
         "title": zh("思政落点：错误代价并不对称，指标选择就是对用户负责",
                                 "Ethics point: error costs are asymmetric, so metric choice is a duty to users"),
         "right": zh("以用户为中心", "user-centred design"),
         "subtitle": zh("把这句话从口号变成可检查的东西：**同一个模型，换一个指标，结论就反了。** "
                        "下面三张卡全部来自本周实测，不是设想。",
                        "Turn the slogan into something checkable: **the same model, a different metric, an opposite "
                        "conclusion.** All three cards below are measured this week, not hypothesised."),
         "cols": 3, "gap": 0.6, "top": 3.4, "h": 9.6,
         "cards": [
             {"accent": "B91C1C",
              "title": zh("① 准确率会放过一个坏模型", "1 · Accuracy can pass a broken model"),
              "body": [zh(f"`last_step`：准确率 {ARMS['last_step'][0]:.4f}，宏 F1 {ARMS['last_step'][2]:.4f}。",
                          f"`last_step`: accuracy {ARMS['last_step'][0]:.4f}, macro F1 {ARMS['last_step'][2]:.4f}."),
                       zh("宏 F1 低于 6 分类随机基线 0.1667。",
                          "Macro F1 sits below the 6-class chance level of 0.1667."),
                       zh("**只看准确率，这个模型会通过评审。**",
                          "**On accuracy alone, this model passes review.**"),
                       zh("代价落在少数类用户身上——他们几乎从不被正确识别。",
                          "The cost lands on minority-class users, who are almost never recognised.")],
              "tag": zh("谁承担代价", "who pays")},
             {"accent": "1E4FA8",
              "title": zh("② 类别大小决定了谁被牺牲", "2 · Class size decides who is sacrificed"),
              "body": [zh(f"W1（n={PER_CLASS_TEST[0]}）召回 {RECALL[0]:.4f}；W6（n={PER_CLASS_TEST[5]}）召回 {RECALL[5]:.4f}。",
                          f"W1 (n={PER_CLASS_TEST[0]}) recalls {RECALL[0]:.4f}; W6 (n={PER_CLASS_TEST[5]}) recalls {RECALL[5]:.4f}."),
                       zh("差距 " + f"{RECALL[5] / RECALL[0]:.1f}" + " 倍，且总体随类别大小上升（Spearman ρ = 0.77）。",
                          "A " + f"{RECALL[5] / RECALL[0]:.1f}" + "× gap, rising overall with class size (Spearman rho = 0.77)."),
                       zh("**宏 F1 存在的全部理由，就是让这件事被看见。**",
                          "**This is precisely why macro F1 exists.**"),
                       zh("用加权 F1 或准确率，这个差距会被平均数抹平。",
                          "Weighted F1 or plain accuracy averages the gap away.")],
              "tag": zh("平均值掩盖什么", "what an average hides")},
             {"accent": "059669",
              "title": zh("③ 指标是写给用户看的产品决策", "3 · A metric is a product decision"),
              "body": [zh("回看第 6 周：那里「最大化准确率」是对的，因为数据平衡、代价对称。",
                          "Recall Week 6: there, maximising accuracy was right — balanced data, symmetric costs."),
                       zh("本周「最大化准确率」是错的，因为它奖励模型猜大类的先验。",
                          "Here it is wrong, because it rewards guessing the majority prior."),
                       zh("**同一个动作，两个场景，一个对一个错。**",
                          "**Same action, two settings, one right and one wrong.**"),
                       zh("**选指标之前先问：这一次，谁的错误更贵？**",
                          "**Before picking a metric, ask: whose mistake costs more this time?**")],
              "tag": zh("这不是技术细节", "not a technicality")},
         ]},

        {"type": "cards",
         "title": zh("AI 赋能：让 AI 生成整条管道，然后你去抓它的错",
                                 "AI co-pilot: let the AI write the whole pipeline, then you catch it"),
         "right": zh("官方 AI 赋能落点", "the official AI-enabled activity"),
         "subtitle": zh("官方要求是「AI 生成文本处理管道 → 学生定位填充/掩码错误，记录修正前后的结果差异」。"
                        "这不是可选项，是**要交记录**的一步。",
                        "The official brief: 「AI generates a text-processing pipeline → students locate the "
                        "padding/masking errors and record the before/after difference」. "
                        "This is not optional — **the record is graded.**"),
         "cols": 2, "gap": 0.7, "top": 3.4, "h": 9.4,
         "cards": [
             {"accent": "1E4FA8",
              "title": zh("第一步：提问（把问题问准）", "Step 1 · Ask (and ask precisely)"),
              "body": [zh("提示词模板：**「用一个 PyTorch LSTM 做 6 分类文本任务，"
                          "输入是变长文本，给出完整的前向传播，并说明你怎么处理填充。」**",
                          "Prompt template: **「Write a complete PyTorch LSTM forward pass for a 6-class "
                          "text task with variable-length input, and explain how you handle padding.」**"),
                       zh("要求它**给出可运行代码**，不要散文解释。",
                          "Demand **runnable code**, not prose."),
                       zh("**不许先看老师给的参考实现再问**——先让 AI 出初稿。",
                          "**Do not read the reference implementation first** — get the AI's first draft.")],
              "tag": zh("先有初稿", "get a draft first")},
             {"accent": "B91C1C",
              "title": zh("第二步：找错（这是评分点）", "Step 2 · Find the bug (this is the graded part)"),
              "body": [zh("对照检查清单，逐条在 AI 代码里找：",
                          "Work down this checklist against the AI's code:"),
                       zh(f"① 有没有传 `lens` 进去？没有 → 它只能取 `[-1]`。",
                          f"① Does it accept `lens`? If not, it can only use `[-1]`."),
                       zh("② 词表是在全量数据上建的吗？→ 数据泄漏。",
                          "② Is the vocabulary built on all data? → leakage."),
                       zh("③ 用了 `padding_idx=0` 吗？没有 → 填充向量会被更新。",
                          "③ Is `padding_idx=0` set? If not, the pad embedding receives gradient."),
                       zh("④ 池化是掩码均值，还是裸 `mean`？**裸 mean 就是本周第 4 名。**",
                          "④ Is the pooling a masked mean or a bare `mean`? **A bare mean is this week's 4th place.**")],
              "tag": zh("逐条留痕", "annotate each one")},
         ],
         "note": zh("**记录表必须包含三列：AI 原代码怎么写 / 你改成了什么 / 修正前后准确率差多少。** "
                    "第三列是硬要求——**只写「我发现了 bug」不算数，要有数字。** 参考量级："
                    f"裸 mean → 掩码均值是 +{(ARMS['mean_masked'][0] - ARMS['mean_unmasked'][0]) * 100:.1f} 个点；"
                    f"`[-1]` → packed 是 +{(ARMS['mean_masked'][0] - ARMS['last_step'][0]) * 100:.1f} 个点。",
                    "**Your log needs three columns: what the AI wrote / what you changed / the accuracy "
                    "difference before and after.** The third column is mandatory — "
                    f"**「I found a bug」 does not count; a number does.** Reference magnitudes: "
                    f"bare mean → masked mean is +{(ARMS['mean_masked'][0] - ARMS['mean_unmasked'][0]) * 100:.1f} points; "
                    f"`[-1]` → packed is +{(ARMS['mean_masked'][0] - ARMS['last_step'][0]) * 100:.1f} points.")},

        # ============================================================ 27 quiz
        {"type": "quiz",
         "title": zh("随堂小测", "In-class quiz"),
         "right": zh("4 题 · 口头回答", "4 items · spoken"),
         "subtitle": zh("每题都在检验本周最容易搞错的一处。**先说答案，再说理由。**",
                        "Each item probes the week's most commonly broken step. **Answer first, then justify.**"),
         "cols": 2, "gap": 0.55, "top": 3.3, "h": 6.6,
         "questions": [
             {"tag": zh("第 1 题", "Item 1"),
              "q": zh(f"词表应该在哪一部分数据上统计？如果用了全部 {N_PASSAGES} 段会怎样？",
                      f"Which split should the vocabulary be counted on? What breaks if you use all {N_PASSAGES} passages?"),
              "options": [
                  zh("A. 全部数据，这样词表最大最全", "A. All of it — the vocabulary is largest that way"),
                  zh("B. 只用训练集；用全部＝把测试集信息漏进训练，测试准确率虚高",
                     "B. Train only; using all of it leaks test information and inflates the test accuracy"),
                  zh("C. 只用测试集，因为要和测试分布对齐", "C. Test only, to match the test distribution"),
                  zh("D. 无所谓，词表只影响速度", "D. It does not matter; the vocabulary only affects speed"),
              ]},
             {"tag": zh("第 2 题", "Item 2"),
              "q": zh(f"{_pct(SHARE_SHORT)} 的测试文档写不到 max_len=96。"
                      "此时 `out[:, -1, :]` 取到的是什么？",
                      f"{_pct(SHARE_SHORT)} of test documents never reach max_len=96. "
                      "What does `out[:, -1, :]` return?"),
              "options": [
                  zh("A. 最后一个真词的隐状态", "A. The hidden state of the last real token"),
                  zh("B. 第 96 个位置的隐状态——短文档上就是填充向量",
                     "B. The state at position 96 — a pad vector on short documents"),
                  zh("C. 全序列的平均", "C. The mean over the sequence"),
                  zh("D. 会报形状错误，跑不起来", "D. It raises a shape error and will not run"),
              ]},
             {"tag": zh("第 3 题", "Item 3"),
              "q": zh(f"`last_step` 准确率 {ARMS['last_step'][0]:.4f}，宏 F1 {ARMS['last_step'][2]:.4f}。"
                      "该怎么汇报？",
                      f"`last_step` reports {ARMS['last_step'][0]:.4f} accuracy and {ARMS['last_step'][2]:.4f} macro F1. "
                      "How do you report it?"),
              "options": [
                  zh(f"A. 准确率 {ARMS['last_step'][0]:.4f}，效果一般，继续调参",
                     f"A. Accuracy {ARMS['last_step'][0]:.4f}; mediocre, keep tuning"),
                  zh(f"B. 两个都报，并指出宏 F1 低于随机 0.1667——**这是坏掉，不是一般**",
                     f"B. Report both, and note macro F1 is below chance 0.1667 — **broken, not mediocre**"),
                  zh("C. 只报宏 F1，因为它更严格", "C. Report macro F1 only; it is the stricter one"),
                  zh("D. 两个都低，说明任务本身不可做", "D. Both are low, so the task is impossible"),
              ]},
             {"tag": zh("第 4 题", "Item 4"),
              "q": zh("本周最好的臂只有 0.5027。加 Dropout + 权重衰减之后会怎样？为什么？",
                      "The best arm reaches only 0.5027. What happens when you add Dropout + weight decay, and why?"),
              "options": [
                  zh("A. 会涨，正则化总是改善泛化", "A. It rises — regularisation always improves generalisation"),
                  zh(f"B. 会降（{ARMS['mean_masked'][0]:.4f} → {ARMS['mean_masked_reg'][0]:.4f}）——"
                     "瓶颈是数据量（523 段），不是容量，此时正则化是在削减仅有的信息",
                     f"B. It falls ({ARMS['mean_masked'][0]:.4f} → {ARMS['mean_masked_reg'][0]:.4f}) — "
                     "the bottleneck is data (523 passages), not capacity, so regularisation cuts the only signal there is"),
                  zh("C. 完全不变，因为参数量没变", "C. Unchanged; the parameter count did not change"),
                  zh("D. 会涨，但要跑满更多轮才看得出来", "D. It rises, but only after many more epochs"),
              ]},
         ]},

        # ==================================================== 28 M8 checkpoint
        {"type": "checklist",
         "title": zh("M8 · 期中检查点 ★ —— 本周同时也是大作业的第一次正式评审",
                                 "M8 · Midterm checkpoint ★ — this week is also the project's first graded review"),
         "right": zh("模块二里程碑 · 4 分", "Module 2 milestone · 4 points"),
         "subtitle": zh("M8 不是额外任务，它是**课程「阶段评审 15 分」里的一块**。"
                        "本周课内完成，**当场演示 3 分钟**，第 3 页必须讲失败。",
                        "M8 is not extra work; it is **one block of the course's 15-point staged review**. "
                        "Done in class this week, **a live 3-minute demo**, with slide 3 about failures."),
         "top": 3.4, "h": 2.8,
         "items": [
             {"badge": zh("交付 ①", "Deliver 1"), "accent": "1E4FA8",
              "title": zh("能跑的原型", "A working prototype"),
              "desc": zh("在一台干净机器上 clone 下来能跑起来。跑不起来就没有这一项——"
                         "**「在我机器上能跑」不算。**",
                         "Runs from a fresh clone. If it does not run, the item does not count — "
                         "**「works on my machine」 is not a demo.**")},
             {"badge": zh("交付 ②", "Deliver 2"), "accent": "059669",
              "title": zh("`DATA.md` v1", "`DATA.md` v1"),
              "desc": zh("数据来源、许可、多少样本、怎么切分、有没有泄漏、已知的坑。"
                         "本周刚做完的实验 7 就是最好的模板。",
                         "Source, licence, sample count, split, leakage check, known traps. "
                         "This week's lab 7 is the template.")},
             {"badge": zh("交付 ③", "Deliver 3"), "accent": "D97706",
              "title": zh("3 页幻灯片，第 3 页讲失败", "A 3-slide deck; slide 3 is about failures"),
              "desc": zh("第 1 页做什么、第 2 页数字、**第 3 页你错在哪**。"
                         "第 3 页是评分重点——**只讲成绩的幻灯片按未完成处理。**",
                         "Slide 1 what it does, slide 2 the numbers, **slide 3 where it fails.** "
                         "Slide 3 carries the marks — **an all-good-news deck is treated as incomplete.**")},
             {"badge": zh("交付 ④", "Deliver 4"), "accent": "B91C1C",
              "title": zh("3 分钟现场演示 + 提问 2 分钟", "A live 3-minute demo + 2 minutes of questions"),
              "desc": zh("**不许放录屏，不许放 PPT 动画代替运行。** 我会问「如果我改这个参数会怎样」，"
                         "你要能当场回答或者当场试。",
                         "**No screen recordings, no animations standing in for a run.** I will ask "
                         "「what happens if I change this parameter」 — answer live or try it live.")},
         ]},

        # ========================================================= 29 summary
        {"type": "summary",
         "title": zh("本周小结", "This week in four lines"),
         "right": zh("CU(8) · 实验 7", "CU(8) · Lab 7"),
         "subtitle": zh("四句话，每一句都在本周有数字支撑。",
                        "Four sentences, each with a number behind it from this week."),
         "points": [
             zh("文本任务的错误大多不在模型里，而在**分词 → 词表 → 编码 → 填充**这四步里。"
                f"中文按空白切分会使 OOV 达到 {_pct(CJK_WS['oov'])}。",
                "Most text-task bugs live in the four pipeline steps — **tokenise, vocabulary, encode, pad** — "
                f"not in the model. Splitting Chinese on whitespace drives OOV to {_pct(CJK_WS['oov'])}."),
             zh(f"填充必须配掩码。**{_pct(SHARE_SHORT)} 的测试文档短于 max_len**，"
                f"不掩码就是让模型去读填充向量；池化方式的选择值 "
                f"{(ARMS['mean_masked'][0] - ARMS['last_step'][0]) * 100:.1f} 个点。",
                f"Padding must come with masking. **{_pct(SHARE_SHORT)} of test documents fall short of max_len**, "
                f"and without a mask the model reads pad vectors; the pooling choice alone is worth "
                f"{(ARMS['mean_masked'][0] - ARMS['last_step'][0]) * 100:.1f} points."),
             zh(f"它确实过拟合（训练 0.9885 / 验证 0.4196），但**正则化救不回来**"
                f"（{ARMS['mean_masked'][0]:.4f} → {ARMS['mean_masked_reg'][0]:.4f}）——"
                f"**瓶颈是 523 个训练段落，不是容量。**",
                f"It does overfit (train 0.9885 / val 0.4196), but **regularisation does not rescue it** "
                f"({ARMS['mean_masked'][0]:.4f} → {ARMS['mean_masked_reg'][0]:.4f}) — "
                f"**the bottleneck is 523 training passages, not capacity.**"),
             zh(f"指标选择是对用户负责：各类召回从 {RECALL[0]:.4f} 到 {RECALL[5]:.4f}，"
                f"**只有宏 F1 能让这个差距可见**；准确率会放过一个低于随机的模型。",
                f"Metric choice is a duty to users: per-class recall runs from {RECALL[0]:.4f} to {RECALL[5]:.4f}, "
                f"and **only macro F1 makes that gap visible**; accuracy will pass a below-chance model."),
         ],
         "todos": [
             {"title": zh("实验 7 报告", "Lab 7 report"),
              "desc": zh("流程代码、四种池化的对照表、混淆矩阵、≥3 段错分原文、"
                         "AI 协同记录表（含修正前后数字）。",
                         "Pipeline code, the four-arm pooling table, the confusion matrix, ≥3 raw "
                         "misclassified passages, and the AI co-pilot log with before/after numbers.")},
             {"title": zh("课后预判题", "Prediction task"),
              "desc": zh("官方要求：「若换成长文本，现有方案会遇到什么问题」——"
                         "写成一页预判，下周讲评。",
                         "The official homework: 「what breaks if the text gets long」 — "
                         "one page, discussed next week.")},
             {"title": zh("M8 三件套", "M8 pack"),
              "desc": zh("原型 + `DATA.md` v1 + 3 页幻灯片（第 3 页讲失败）。"
                         "**本周课内演示，不延期。**",
                         "Prototype + `DATA.md` v1 + a 3-slide deck (slide 3 on failures). "
                         "**Demoed in class this week; no extension.**")},
         ]},

        # ========================================================= 30 closing
        {"type": "closing",
         "quote": zh("「准确率不是成绩，是一个你还没开始解释的数字。」",
                     "「Accuracy is not a result. It is a number you have not started explaining.」"),
         "quote_sub": zh("本周：0.4248 的准确率、0.0711 的宏 F1、14 段错分原文——"
                         "加起来才是一份报告。",
                         "This week: 0.4248 accuracy, 0.0711 macro F1, 14 raw misclassified passages — "
                         "together they are a report."),
         "thanks": zh("谢谢大家", "Thank you"),
         "next_label": zh("下周预告", "Next week"),
         "next": zh("第 9 周　迁移学习与预训练模型（CU(9)）："
                    "先用预训练模型重做本周这件事，看它能不能突破 0.5027；"
                    "以及一次「从零训练 vs 微调」的完整对照。",
                    "Week 9 · Transfer Learning and Pretrained Models (CU(9)): "
                    "redo this week's task with a pretrained model and see whether it breaks 0.5027 — "
                    "plus a full from-scratch versus fine-tune comparison."),
         "sign": zh("AI 应用开发 · 第 8 周课件 · 任政 · 软件学院",
                    "AI Application Development · Week 8 Lecture · Zheng Ren · School of Software")},
    ],
}


# ------------------------------------------------- quote normalisation -------
# The spec above is written with the CJK corner brackets 「 」 because they are
# unambiguous to type and to grep.  They must not survive into the English
# deck: the validator only flags Han characters, but the House style for the
# English version is ASCII quotes (and the zh version uses the Simplified
# convention “ ”).  Normalise once, here, so the rule lives in one place.
import re as _re


def _norm_quotes(obj):
    if isinstance(obj, dict):
        return {k: _norm_quotes(v) for k, v in obj.items()}
    if isinstance(obj, tuple):
        return tuple(_norm_quotes(v) for v in obj)
    if isinstance(obj, list):
        return [_norm_quotes(v) for v in obj]
    if isinstance(obj, str) and ("\u300c" in obj or "\u300d" in obj):
        if _re.search(r"[\u4e00-\u9fff]", obj):          # Chinese string
            return obj.replace("\u300c", "\u201c").replace("\u300d", "\u201d")
        return obj.replace("\u300c", "'").replace("\u300d", "'")
    return obj


SPEC = _norm_quotes(SPEC)
