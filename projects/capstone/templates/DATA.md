# DATA.md · 数据文档模板

> Start this in Week 2, update it every week. Graded under team rubric §B (18 pts).
> **The "Known flaws" section is the one graders read first** — a dataset described
> without flaws is a dataset you have not looked at.
>
> W2 起填写，每周更新。**「已知缺陷」是评分人最先看的一节** —— 一份没有缺陷描述的数据
> 说明，只能说明你还没认真看过数据。

---

## 1. Provenance · 来源

| | |
|---|---|
| **Name** | |
| **Source** | *(exact URL, or describe collection)* |
| **Licence** | *(link. "public" / "found online" is not acceptable)* |
| **Citation** | *(papers, or "collected by us")* |
| **Access date** | |
| **Version / snapshot** | *(how do we know it won't change under us?)* |

**Human subjects / personal data** ☐ none ☐ present — describe consent, anonymisation and deletion plan:

## 2. Contents · 内容

| | |
|---|---|
| **Total rows / files** | |
| **Columns (or schema)** | |
| **Target / label** | |
| **Class distribution** | *(a table, not a sentence)* |
| **File formats & sizes** | |
| **Language / domain** | |

```python
# Paste the output of your Week-2 health check here, updated at each milestone
df.info()
df.describe()
df.isna().sum()
```

## 3. Collection & labelling · 采集与标注

| | |
|---|---|
| **How were samples collected?** | |
| **Who labelled them?** | *(authors? crowdworkers? us? an existing annotation?)* |
| **Labelling protocol** | *(the exact instruction given to annotators)* |
| **Inter-annotator agreement** | *(if ≥2 annotators — report it, or say you didn't measure it)* |
| **AI assistance in labelling** | ☐ none ☐ used: *(which tool, what fraction, how validated)* |

## 4. Preprocessing · 预处理

List **every** step, in order. If it happened in a notebook cell you can't re-run, that
is a problem — move it into `src/data/`.

1.
2.
3.

| Step | Why | Code |
|---|---|---|
| | | `src/data/clean.py::` |

## 5. Split · 划分

| | |
|---|---|
| **Strategy** | ☐ random ☐ stratified ☐ grouped ☐ time-based ☐ other |
| **Why this strategy** | *(one sentence. "because sklearn does it" is not a reason)* |
| **Train / val / test** | |
| **Seed** | |
| **Leakage checks run** | ☐ duplicate rows across splits ☐ near-duplicates ☐ group leakage ☐ temporal leakage |

> A random split on time-ordered data is wrong. Grouped splitting when the same entity
> appears in both train and test is mandatory, not optional.

## 6. Known flaws · 已知缺陷

Be specific and quantify. This section is worth more than it looks.

| Flaw | How much | How it affects the model | What we did |
|---|---|---|---|
| *(e.g. class imbalance)* | *(e.g. 6:1)* | *(e.g. accuracy will look great and mean nothing)* | *(e.g. macro-F1, class weights)* |
| | | | |
| | | | |

## 7. Intended use & restrictions · 用途与限制

- **Approved uses:**
- **Prohibited uses:** *(e.g. "not for clinical decisions"; "not for any real hiring decision")*
- **Representation gaps:** *(who is missing from this data?)*

## 8. Maintenance · 维护

| | |
|---|---|
| **Owner** | *(Data Lead)* |
| **Last updated** | |
| **Next review** | |
