# Lab 09 · NLP Fundamentals — from raw text to a classifier
> **AI Application Development** · Week 9 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 9 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 3 · NLP & Large Language Models |
| **Stack** | scikit-learn (`CountVectorizer`, `TfidfVectorizer`), NLTK-style tokenisation |
| **Dataset** | `fetch_20newsgroups` (4 categories) |
| **Deliverables** | `lab-09.ipynb` with a vectoriser comparison table |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** the difference between Bag-of-Words, TF-IDF and n-grams, and what each loses
- **Know** why the vectoriser must be fitted **on the training split only**
- **Do** build a complete text-classification pipeline end to end
- **Do** read the highest-weighted TF-IDF features per class and explain them
- **Do** compute cosine similarity between documents and sanity-check it

## 2. Before You Start · 课前准备

- [ ] Week 8 project lab committed
- [ ] `python -c "import sklearn; print(sklearn.__version__)"` works
- [ ] Read Chapter 9 (tokenisation, BoW, TF-IDF)

```python
from sklearn.datasets import fetch_20newsgroups
cats = ["sci.space", "comp.graphics", "rec.sport.baseball", "talk.politics.guns"]
train = fetch_20newsgroups(subset="train", categories=cats, remove=("headers","footers","quotes"))
```

> **Pitfall**: if the download fails, the TA will hand you a local copy — the lab is identical. Do not skip the `remove=` argument; headers leak the answer and make your accuracy meaningless.

## 3. Lab Tasks · 实验任务

### Part A — Tokenisation by hand, then by library (10 min)

```python
text = "The rockets launched; NASA's budget didn't grow!"
print(text.lower().split())            # naive — what is wrong with this?
```

Compare naive splitting against `CountVectorizer(token_pattern=...)`. List three cases where naive splitting breaks.

> **Checkpoint A** — three concrete failure cases (punctuation, contractions, casing), written out.

### Part B — BoW vs TF-IDF vs n-grams (25 min)

```python
from sklearn.pipeline import make_pipeline
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.linear_model import LogisticRegression
```

Run four configurations, same classifier, same split:

| Run | Representation | Test acc | #features |
|---|---|---|---|
| 1 | `CountVectorizer()` | | |
| 2 | `TfidfVectorizer()` | | |
| 3 | `TfidfVectorizer(ngram_range=(1,2))` | | |
| 4 | `TfidfVectorizer(min_df=3, sublinear_tf=True)` | | |

> **Checkpoint B** — the filled table plus one sentence: why did run 4 *reduce* features but often *improve* accuracy?
> **Pitfall**: fitting the vectoriser before `train_test_split` leaks test vocabulary into training. Use a `Pipeline` so it happens inside CV.

### Part C — What did the model actually learn? (20 min)

```python
import numpy as np
feats = np.array(vec.get_feature_names_out())
for i, c in enumerate(clf.classes_):
    top = np.argsort(clf.coef_[i])[-12:]
    print(c, "->", feats[top])
```

> **Checkpoint C** — top-12 features per class, plus one sentence per class on whether the keywords look **causal** or **incidental**.
> **Think**: if `nasa` predicts `sci.space`, is the model understanding space, or memorising a proper noun?

### Part D — Similarity and its limits (15 min)

```python
from sklearn.metrics.pairwise import cosine_similarity
```

Pick 5 documents, compute pairwise cosine similarity on TF-IDF vectors, and find the nearest neighbour of each.

> **Checkpoint D** — the 5×5 heatmap plus one example where the nearest neighbour is wrong, and your explanation.
> **Pitfall**: cosine similarity on raw counts is dominated by document length. TF-IDF fixes that — say so in your answer.

### Part E — Wrap up (5 min)

One paragraph: what information does a bag of words throw away? Give one concrete example from your own results.

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-09.ipynb` runs top-to-bottom without errors (`Kernel → Restart & Run All`)
- [ ] Every **Checkpoint** cell executed, with its output visible
- [ ] Results collected into **one comparison table**
- [ ] Markdown cells contain your own interpretation, not just code
- [ ] Pushed to GitHub with **≥ 2 meaningful commits**

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Tokenisation critique (Part A) | 15 | three real failure cases identified, not generic statements |
| Representation comparison (Part B) | 30 | four runs tabulated, leakage avoided, min_df effect explained |
| Feature inspection (Part C) | 25 | top features extracted per class, causal-vs-incidental judgement made |
| Similarity analysis (Part D) | 20 | heatmap produced, one wrong nearest neighbour diagnosed |
| Exit ticket | 10 | three questions answered |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add lab-09.ipynb
git commit -m "feat: complete lab 09"
git push origin main
```

## 8. Exit Ticket · 课后反思

1. What surprised you most today?
2. Where did your model fail, and what does that failure tell you about the representation it uses?
3. One question you still have.

## 9. 中文摘要

本周把文本变成数字，并让你亲眼看到这种变换丢掉了什么。

五个要点：
1. **分词没那么简单**：大小写、标点、缩写（`didn't`）都会让朴素切分失效。
2. **BoW 只数词频，TF-IDF 惩罚到处都出现的词**——后者通常更好，因为「the」没有区分度。
3. **向量化器只能在训练集上 fit**：先 fit 再切分 = 测试集的词表泄漏进了训练，分数虚高。用 `Pipeline` 自动避免。
4. **`min_df` 提精度**：丢掉只出现一两次的词，特征变少但往往更准——噪声比信息多。
5. **看权重最高的特征**：如果某个类别靠专有名词（NASA）取胜，说明模型在「背词」而不是「理解」。

最后记住：词袋丢掉的是**词序和语义**。「狗咬人」和「人咬狗」的 BoW 向量完全相同——这正是下周词向量和第 11 周 Transformer 要解决的问题。
