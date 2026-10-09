# -*- coding: utf-8 -*-
"""Numeric single-source-of-truth check for the AI Application Development decks.

Why this exists
---------------
On 2026-10-09 three W07 numbers were written from memory rather than recomputed
from ``outputs/w7_cnn.json``.  The error propagated into 7 companion documents and
a built deck before two sub-agents independently questioned it.  See
``outputs/修订记录-W07-2026-10-09.md``.  This script is the fix: every derived
quantity is recomputed here, and the deck specs are asserted against it.

What it checks
--------------
1. Derived facts recomputed straight from the experiment JSON — never hard-coded.
2. The hard-coded constants inside ``deck_specs/week_07.py`` / ``week_08.py``
   must equal those recomputed values.
3. Published documents (specs, lesson plans, textbook, lab handouts) must not
   contain any value on the "retired" list — the specific wrong numbers that
   already shipped once.

Usage
-----
    python scripts/verify_num_sync.py          # exit 0 = in sync, 1 = drift
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))

FAILURES = []


def check(label, got, want, tol=0.0):
    ok = abs(got - want) <= tol if isinstance(want, float) else got == want
    mark = "ok  " if ok else "FAIL"
    print(f"  {mark} {label}: got {got!r}, want {want!r}")
    if not ok:
        FAILURES.append(label)
    return ok


def head(title):
    print(f"\n=== {title} ===")


# ---------------------------------------------------------------------------
# 1. W07 — recompute the confusion-matrix facts that were wrong
# ---------------------------------------------------------------------------
head("W07 · confusion matrix, recomputed from w7_cnn.json")
w7 = json.loads((ROOT / "outputs/w7_cnn.json").read_text(encoding="utf-8"))
M = w7["confusion_cnn_5seeds"]

total = sum(sum(r) for r in M)
correct = sum(M[i][i] for i in range(10))
off = [(i, j, M[i][j]) for i in range(10) for j in range(10) if i != j and M[i][j]]
n_off = sum(v for _, _, v in off)
n_digit8 = sum(v for i, j, v in off if i == 8 or j == 8)
cls8_n = sum(M[8])
cls8_correct = M[8][8]

check("total predictions", total, 1350)
check("correct", correct, 1324)
check("accuracy", round(correct / total, 4), 0.9807, tol=1e-4)
check("off-diagonal errors", n_off, 26)
check("errors involving digit 8", n_digit8, 12)
check("share involving digit 8", round(n_digit8 / n_off * 100, 1), 46.2, tol=0.05)
check("digit-8 support (row sum)", cls8_n, 130)
check("digit-8 correct", cls8_correct, 124)
check("digit-8 recall", round(cls8_correct / cls8_n, 4), 0.9538, tol=1e-4)

arms = w7["arms"]
params_cnn = arms["cnn"]["stats"]["params"]["mean"]
params_wide = arms["cnn_wide"]["stats"]["params"]["mean"]
check("cnn params", params_cnn, 1898)
check("cnn_wide params", params_wide, 21312)
check("cnn_wide / cnn ratio", round(params_wide / params_cnn, 1), 11.2, tol=0.05)

# ---------------------------------------------------------------------------
# 2. W07 spec constants must match the recomputed values
# ---------------------------------------------------------------------------
head("W07 · deck spec agrees with the JSON")
import deck_specs.week_07 as s7  # noqa: E402

check("spec MLP_VAL length", len(s7.MLP_VAL), 20)
check("spec SHIFT_MLP dx=0", s7.SHIFT_MLP[2], 0.9785)
check("spec SHIFT_CNN dx=-1", s7.SHIFT_CNN[1], 0.6481)
check("spec SHIFT_AUG dx=-1", s7.SHIFT_AUG[1], 0.9415)
check("spec SHIFT_AUG dx=0", s7.SHIFT_AUG[2], 0.9504)
mem = w7["memory_vs_batch"]
baseline = [r for r in mem if r["batch"] == 0][0]["peak_rss_mb"]
over = [round(r["over_baseline_mb"], 1) for r in mem if r["batch"] != 0]
check("spec MEM_OVER matches JSON", [round(v, 1) for v in s7.MEM_OVER], over)
check("spec MEM_X matches JSON",
      s7.MEM_X, [str(r["batch"]) for r in mem if r["batch"] != 0])
check("memory baseline", baseline, 306.5, tol=0.05)
check("memory at batch 1024", [r["peak_rss_mb"] for r in mem if r["batch"] == 1024][0],
      582.0, tol=0.05)

# ---------------------------------------------------------------------------
# 3. W08 — recompute the derived quantities
# ---------------------------------------------------------------------------
head("W08 · derived quantities, recomputed from w8_sequence.json")
w8 = json.loads((ROOT / "outputs/w8_sequence.json").read_text(encoding="utf-8"))
st = {k: v["stats"] for k, v in w8["arms"].items()}

check("mean_masked acc", st["mean_masked"]["test_acc"]["mean"], 0.5027, tol=1e-4)
check("packed acc", st["packed"]["test_acc"]["mean"], 0.4248, tol=1e-4)
check("mean_unmasked acc", st["mean_unmasked"]["test_acc"]["mean"], 0.3929, tol=1e-4)
check("last_step acc", st["last_step"]["test_acc"]["mean"], 0.2407, tol=1e-4)
check("last_step macro F1 below chance", st["last_step"]["test_macro_f1"]["mean"] < 1 / 6, True)
check("mean_masked_reg acc", st["mean_masked_reg"]["test_acc"]["mean"], 0.4672, tol=1e-4)

spread = st["mean_masked"]["test_acc"]["mean"] - st["last_step"]["test_acc"]["mean"]
check("best - worst spread", round(spread * 100, 1), 26.2, tol=0.05)

mask_gain = st["mean_masked"]["test_acc"]["mean"] - st["mean_unmasked"]["test_acc"]["mean"]
check("masking gain (points)", round(mask_gain * 100, 1), 11.0, tol=0.05)

pack_gain = st["packed"]["test_acc"]["mean"] - st["last_step"]["test_acc"]["mean"]
check("[−1] -> packed gain (points)", round(pack_gain * 100, 1), 18.4, tol=0.05)

reg_drop = st["mean_masked"]["test_acc"]["mean"] - st["mean_masked_reg"]["test_acc"]["mean"]
check("regularisation drop (percentage points)", round(reg_drop * 100, 1), 3.6, tol=0.001)

Cf = w8["confusion_packed_5seeds"]
w8_total = sum(sum(r) for r in Cf)
w8_correct = sum(Cf[i][i] for i in range(6))
recall = [round(Cf[i][i] / sum(Cf[i]), 4) for i in range(6)]
check("w8 total predictions", w8_total, 565)
check("w8 correct", w8_correct, 240)
check("w8 accuracy", round(w8_correct / w8_total, 4), 0.4248, tol=1e-4)
check("w8 per-class recalls", recall, [0.1750, 0.1867, 0.4235, 0.4778, 0.4211, 0.6643])
check("W6/W1 recall ratio", round(recall[5] / recall[0], 2), 3.80, tol=0.005)
# Recall tracks class size, but NOT perfectly: there are exactly two small
# inversions (W2 above W1, W5 below W4).  Spearman rho over n=6.
sizes = [sum(r) for r in Cf]


def _rank(v):
    order = sorted(range(len(v)), key=lambda i: v[i])
    r = [0] * len(v)
    for pos, i in enumerate(order):
        r[i] = pos + 1
    return r


rs, rr = _rank(sizes), _rank(recall)
d2 = sum((rs[i] - rr[i]) ** 2 for i in range(6))
rho = 1 - 6 * d2 / (6 * (6 * 6 - 1))
check("Spearman rho (size vs recall)", round(rho, 3), 0.771, tol=0.001)
inversions = sum(1 for i in range(5) if (sizes[i + 1] - sizes[i]) * (recall[i + 1] - recall[i]) < 0)
check("inversions in size vs recall", inversions, 2)
check("two smallest classes both below 0.20", recall[0] < 0.20 and recall[1] < 0.20, True)

# curve gap
cv = w8["detail_seed42"]["packed"]["curve"]
check("epoch-30 train", cv["train_acc"][-1], 0.9885, tol=1e-4)
check("epoch-30 val", cv["val_acc"][-1], 0.4196, tol=1e-4)
check("curve gap", round(cv["train_acc"][-1] - cv["val_acc"][-1], 4), 0.5689, tol=1e-4)

cjk = {s["scheme"]: s for s in w8["cjk_tokenisation"]["schemes"]}
ws = cjk["whitespace (no segmentation)"]
ch = cjk["character level"]
check("CJK whitespace OOV", ws["oov_rate"], 0.9973, tol=1e-4)
check("CJK character OOV", ch["oov_rate"], 0.0254, tol=1e-4)
check("CJK OOV improvement factor", round(ws["oov_rate"] / ch["oov_rate"]), 39)

cf = json.loads((ROOT / "outputs/w8_corpus_facts.json").read_text(encoding="utf-8"))
check("corpus passages", cf["n_passages"], 748)
check("corpus vocabulary", cf["vocab_full"], 3142)
check("anti-leakage scrub count", cf["scrub_counters"]["scrubbed"], 262)

# ---------------------------------------------------------------------------
# 4. W08 spec constants must match the recomputed values
# ---------------------------------------------------------------------------
head("W08 · deck spec agrees with the JSON")
import deck_specs.week_08 as s8  # noqa: E402

check("spec RECALL", s8.RECALL, recall)
check("spec CONFUSION rows", s8.CONFUSION, Cf)
check("spec ARMS mean_masked", round(s8.ARMS["mean_masked"][0], 4), 0.5027, tol=1e-4)
check("spec ARMS last_step macro F1", round(s8.ARMS["last_step"][2], 4), 0.0711, tol=1e-4)
check("spec SHARE_SHORT", s8.SHARE_SHORT, 0.9558, tol=1e-4)
check("spec CURVE_TRAIN last", s8.CURVE_TRAIN[-1], 0.9885, tol=1e-4)
check("spec CURVE_VAL last", s8.CURVE_VAL[-1], 0.4196, tol=1e-4)
check("spec max_len packed sweep", s8.MAXLEN_PACKED, [0.4572, 0.4454, 0.4454])
check("spec N_PASSAGES", s8.N_PASSAGES, 748)
check("spec SHA256 matches corpus", s8.SHA256, cf["sha256"])

# ---------------------------------------------------------------------------
# 5. Retired values must not reappear anywhere in the published documents
# ---------------------------------------------------------------------------
head("Published documents · retired values must be absent")

# Every entry is a string that WAS WRONG and already shipped once.
RETIRED = {
    # --- W07, 2026-10-09 ---
    "57.7": "W07 share of errors involving digit 8 (real value 46.2)",
    "124/135": "W07 digit-8 recall denominator (real denominator 130)",
    "10.2x": "W07 cnn_wide parameter multiple (real 11.2x)",
    "10.2 倍": "W07 cnn_wide parameter multiple (real 11.2 倍)",
    "15 个与数字 8": "W07 error count (real 12)",
    "15 of the 26 errors involve the digit 8": "W07 error count (real 12)",
    # --- W08, 2026-10-09 (second pass) ---
    "3.5 points": "regularisation drop (0.5027-0.4672 = 0.0355 -> 3.6 percentage points)",
    "3.5 个点": "regularisation drop (0.5027-0.4672 = 0.0355 -> 3.6 个百分点)",
    "唯一的逆序": "recall vs class size has TWO inversions (W2>W1, W5<W4), not one",
    "唯一一处逆序": "recall vs class size has TWO inversions, not one",
    "唯一一处对 W4 的小逆序": "recall vs class size has TWO inversions, not one",
    "only inversion": "recall vs class size has TWO inversions, not one",
    "only one inversion": "recall vs class size has TWO inversions, not one",
    "everything else is monotone": "there are two inversions",
    "其余全部单调": "there are two inversions",
    "Recall rises monotonically with class size": "recall vs size has two inversions (Spearman rho = 0.77)",
    "召回随类别大小单调上升": "recall vs size has two inversions (Spearman rho = 0.77)",
    "召回率就单调地排好了": "recall vs size has two inversions (Spearman rho = 0.77)",
}

DOC_GLOBS = [
    "scripts/deck_specs/week_07.py",
    "scripts/deck_specs/week_08.py",
    "lesson-plans/week-07/*.html",
    "lesson-plans/week-08/*.html",
    "textbook/chapter-07/*.html",
    "textbook/chapter-08/*.html",
    "labs/week-07/*.md",
    "labs/week-08/*.md",
]

docs = []
for g in DOC_GLOBS:
    docs.extend(sorted(ROOT.glob(g)))

for path in docs:
    text = path.read_text(encoding="utf-8")
    for bad, why in RETIRED.items():
        n = text.count(bad)
        if n:
            rel = path.relative_to(ROOT)
            print(f"  FAIL {rel}: {bad!r} x{n}   [{why}]")
            FAILURES.append(f"{rel}:{bad}")

if not FAILURES:
    print(f"  ok   scanned {len(docs)} documents, no retired values found")

# ---------------------------------------------------------------------------
head("Result")
if FAILURES:
    print(f"{len(FAILURES)} problem(s):")
    for f in FAILURES:
        print(f"  - {f}")
    sys.exit(1)

print(f"all checks passed across {len(docs)} documents")
sys.exit(0)
