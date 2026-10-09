"""Week 8 authoritative experiment: a text pipeline, and the padding/mask bug.

Protocol (FIXED — re-run every downstream document if you change this file):
  corpus     data/raw/course-text-corpus.jsonl      (748 passages, 6 classes = weeks 1-6)
             built by scripts/build_text_corpus.py from this repository's own
             Week 1-6 materials, so the run is offline and the licence is ours
  split      70 / 15 / 15, stratified by week, random_state = seed
  tokeniser  lowercase, regex [a-z][a-z'-]*   ;  vocab from TRAIN only,
             min_freq=2, capped at 6000, <pad>=0 <unk>=1
  model      Embedding(64, padding_idx=0) -> LSTM(hidden 96, batch_first) -> Linear(6)
  optimiser  Adam(lr=1e-3), batch_size=64, 30 epochs, max_len=96
  seeds      42, 43, 44, 45, 46

The four pooling / packing arms differ in ONE thing — how the sequence is turned
into a document vector:

  packed            sort-free pack_padded_sequence, take the final hidden state
  last_step         no packing, take out[:, -1, :]                  <- the bug
  mean_masked       no packing, average only the real timesteps
  mean_unmasked     no packing, average every timestep including padding

What the run actually shows (do NOT rewrite this into "the LSTM is accurate" —
that is not the point):
  * `last_step` reads the padding vector for every document shorter than the
    longest one in its batch and collapses — 96% of the test documents are
    shorter than max_len, so almost all of them are reading junk
  * `mean_unmasked` is the quiet version of the same mistake: a few points lost,
    nothing crashes, and it is easy to ship
  * the damage is concentrated in SHORT documents — exactly the ones a reporter
    would never look at
  * averaging the real timesteps BEATS the final hidden state here
  * every arm overfits hard (train ~0.99 against test ~0.42), and adding Week
    6's regularisation does not rescue it: the binding constraint is 523
    training passages, not the model's capacity
  * the confusion is systematic, not random: weeks that share vocabulary
    (W1/W2, both PyTorch basics) sit near chance while the largest class wins

Also measured, for the tokenisation half of CU(8): whitespace vs character
tokenisation on this repository's own Chinese text, which is where "分词" stops
being cosmetic.

Writes outputs/w8_sequence.json.
"""

from __future__ import annotations

import json
import os
import random
import re
import statistics as st
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from sklearn.metrics import confusion_matrix, f1_score
from sklearn.model_selection import train_test_split

SEED = 42
SEEDS = (42, 43, 44, 45, 46)
SWEEP_SEEDS = (42, 43, 44)
EPOCHS = 30
BATCH = 64
LR = 1e-3
EMB = 64
HID = 96
MIN_FREQ = 2
MAX_VOCAB = 6000
MAX_LEN = 96
N_CLASS = 6
WORD = re.compile(r"[a-z][a-z'-]*")

ROOT = Path(__file__).resolve().parent.parent
CORPUS = ROOT / "data/raw/course-text-corpus.jsonl"
OUT = ROOT / "outputs/w8_sequence.json"

BUCKETS = [(20, 29), (30, 49), (50, 99), (100, 10_000)]


# ------------------------------------------------------------------ corpus ---
def load_corpus():
    rows = [json.loads(l) for l in CORPUS.read_text(encoding="utf-8").splitlines()
            if l.strip()]
    X = [WORD.findall(r["text"].lower()) for r in rows]
    y = [r["week"] - 1 for r in rows]
    return rows, X, y


def build_vocab(train_tokens):
    freq = {}
    for doc in train_tokens:
        for t in doc:
            freq[t] = freq.get(t, 0) + 1
    kept = [t for t, c in freq.items() if c >= MIN_FREQ]
    kept.sort(key=lambda t: (-freq[t], t))
    kept = kept[:MAX_VOCAB - 2]
    return {t: i + 2 for i, t in enumerate(kept)}, freq


def encode(doc, vocab, max_len):
    ids = [vocab.get(t, 1) for t in doc][:max_len]
    return ids or [1]


def pad_batch(docs, max_len):
    """Right-pad with 0; returns (tensor, true lengths)."""
    enc = [encode(d, VOCAB, max_len) for d in docs]
    lengths = torch.tensor([len(e) for e in enc])
    T = int(lengths.max())
    x = torch.zeros(len(enc), T, dtype=torch.long)
    for i, e in enumerate(enc):
        x[i, :len(e)] = torch.tensor(e)
    return x, lengths


# ------------------------------------------------------------------- model ---
class TextLSTM(nn.Module):
    def __init__(self, vocab_size, pooling, dropout=0.0):
        super().__init__()
        self.pooling = pooling
        self.emb = nn.Embedding(vocab_size, EMB, padding_idx=0)
        self.rnn = nn.LSTM(EMB, HID, batch_first=True)
        self.head = nn.Linear(HID, N_CLASS)
        self.drop = nn.Dropout(dropout)             # dropout=0 -> identity

    def forward(self, x, lengths):
        e = self.drop(self.emb(x))
        if self.pooling == "packed":
            packed = nn.utils.rnn.pack_padded_sequence(
                e, lengths, batch_first=True, enforce_sorted=False)
            _, (h, _) = self.rnn(packed)
            z = h[-1]
        else:
            out, _ = self.rnn(e)
            if self.pooling == "last_step":
                z = out[:, -1, :]
            elif self.pooling == "mean_unmasked":
                z = out.mean(1)
            else:                                   # mean_masked
                mask = (x != 0).unsqueeze(-1).float()
                z = (out * mask).sum(1) / mask.sum(1).clamp(min=1)
        return self.head(self.drop(z))


def set_seed(s):
    random.seed(s)
    np.random.seed(s)
    torch.manual_seed(s)


@torch.no_grad()
def predict(model, X, y, max_len, batch=128):
    model.eval()
    preds = []
    order = sorted(range(len(X)), key=lambda i: -len(X[i]))   # pack-friendly
    for i in range(0, len(order), batch):
        idx = order[i:i + batch]
        x, ln = pad_batch([X[j] for j in idx], max_len)
        preds.extend(model(x, ln).argmax(1).tolist())
    out = [0] * len(X)
    for pos, j in enumerate(order):
        out[j] = preds[pos]
    return out


def train(arm, seed, max_len=MAX_LEN, epochs=EPOCHS, want_curve=False,
          dropout=0.0, wd=0.0):
    set_seed(seed)
    rows, X, y = load_corpus()
    idx = np.arange(len(y))
    tr, rest = train_test_split(idx, test_size=0.30, stratify=y, random_state=seed)
    va, te = train_test_split(rest, test_size=0.50, stratify=[y[i] for i in rest],
                              random_state=seed)
    Xtr = [X[i] for i in tr]; ytr = [y[i] for i in tr]
    Xte = [X[i] for i in te]; yte = [y[i] for i in te]

    global VOCAB
    VOCAB, _ = build_vocab(Xtr)
    model = TextLSTM(len(VOCAB) + 2, arm, dropout=dropout)
    opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=wd)
    g = torch.Generator().manual_seed(seed)
    hist = {"train_acc": [], "val_acc": []}

    for ep in range(epochs):
        model.train()
        perm = torch.randperm(len(Xtr), generator=g).tolist()
        for i in range(0, len(perm), BATCH):
            sel = perm[i:i + BATCH]
            x, ln = pad_batch([Xtr[j] for j in sel], max_len)
            opt.zero_grad()
            nn.functional.cross_entropy(model(x, ln),
                                        torch.tensor([ytr[j] for j in sel])).backward()
            opt.step()
        if want_curve and (ep % 3 == 0 or ep == epochs - 1):
            p = predict(model, Xtr, ytr, max_len)
            hist["train_acc"].append(round(float(np.mean(np.array(p) == np.array(ytr))), 4))
            p = predict(model, [X[i] for i in va], [y[i] for i in va], max_len)
            hist["val_acc"].append(round(float(np.mean(
                np.array(p) == np.array([y[i] for i in va]))), 4))

    pred = predict(model, Xte, yte, max_len)
    yt = np.array(yte)
    yp = np.array(pred)
    acc = float((yt == yp).mean())

    # accuracy per true-length bucket: where does the damage actually land?
    bucket = {}
    lens = [len(X[i]) for i in te]
    for lo, hi in BUCKETS:
        sel = [k for k, L in enumerate(lens) if lo <= L <= hi]
        if sel:
            bucket[f"{lo}-{hi if hi < 10_000 else 'max'}"] = {
                "n": len(sel),
                "acc": round(float((yt[sel] == yp[sel]).mean()), 4),
            }
    short_share = round(float(np.mean([L < max_len for L in lens])), 4)

    # the specific failure we want students to be able to explain
    if arm == "last_step":
        eq = [k for k, L in enumerate(lens) if L >= max_len]
        lt = [k for k, L in enumerate(lens) if L < max_len]
        tail = {
            "docs_at_or_above_max_len": len(eq),
            "acc_at_or_above_max_len": round(float((yt[eq] == yp[eq]).mean()), 4) if eq else None,
            "docs_below_max_len": len(lt),
            "acc_below_max_len": round(float((yt[lt] == yp[lt]).mean()), 4) if lt else None,
        }
    else:
        tail = None

    return {
        "arm": arm, "seed": seed, "max_len": max_len,
        "vocab_size": len(VOCAB) + 2,
        "params": sum(p.numel() for p in model.parameters()),
        "test_acc": round(acc, 4),
        "test_macro_f1": round(float(f1_score(yt, yp, average="macro")), 4),
        "by_length": bucket,
        "share_shorter_than_max_len": short_share,
        "long_doc_split": tail,
        "confusion": confusion_matrix(yt, yp, labels=list(range(N_CLASS))).tolist(),
        "predictions": yp.tolist(),
        "test_idx": [int(i) for i in te],
        "curve": hist if want_curve else None,
    }


def agg(rows, key):
    vals = [r[key] for r in rows]
    return {"mean": round(st.mean(vals), 4),
            "sd": round(st.stdev(vals), 4) if len(vals) > 1 else 0.0}


# ------------------------------------------------- Chinese tokenisation demo --
def cjk_demo():
    """Whitespace vs character tokenisation on this repository's own Chinese
    textbook text. Chinese has no spaces, so whitespace tokenisation produces
    one token per sentence: a vocabulary that never transfers."""
    from html.parser import HTMLParser

    class T(HTMLParser):
        BLOCK = {"p", "div", "li", "h1", "h2", "h3", "h4", "br", "td", "section"}
        def __init__(self):
            super().__init__(); self.out = []; self.skip = 0
        def handle_starttag(self, tag, a):
            if tag in ("script", "style"): self.skip += 1
            if tag in self.BLOCK: self.out.append("\n")
        def handle_endtag(self, tag):
            if tag in ("script", "style"): self.skip = max(0, self.skip - 1)
            if tag in self.BLOCK: self.out.append("\n")
        def handle_data(self, d):
            if not self.skip: self.out.append(d)

    segs = []
    for w in range(1, 7):
        p = ROOT / f"textbook/chapter-{w:02d}/zh.html"
        if not p.exists():
            continue
        h = T(); h.feed(p.read_text(encoding="utf-8"))
        for s in "".join(h.out).split("\n"):
            s = re.sub(r"\s+", "", s)
            s = re.sub(r"[^\u4e00-\u9fff]", "", s)
            if len(s) >= 12:
                segs.append(s)
    split = len(segs) // 2
    train, test = segs[:split], segs[split:]

    def stats(tok_fn, name):
        vocab = {}
        for s in train:
            for t in tok_fn(s):
                vocab[t] = vocab.get(t, 0) + 1
        n_tok = sum(len(tok_fn(s)) for s in test)
        oov = sum(1 for s in test for t in tok_fn(s) if t not in vocab)
        single = sum(1 for c in vocab.values() if c == 1)
        return {"scheme": name,
                "train_segments": len(train), "test_segments": len(test),
                "vocab_train": len(vocab),
                "singletons": single,
                "singleton_share": round(single / max(len(vocab), 1), 4),
                "test_tokens": n_tok,
                "oov_tokens": oov,
                "oov_rate": round(oov / max(n_tok, 1), 4)}

    return {
        "corpus": "textbook/chapter-01..06/zh.html (this repository's own Chinese text)",
        "segments": len(segs),
        "schemes": [stats(lambda s: s.split(), "whitespace (no segmentation)"),
                    stats(lambda s: list(s), "character level")],
    }


# -------------------------------------------------------------------- main ---
VOCAB = {}


def main():
    arms = ["packed", "last_step", "mean_masked", "mean_unmasked"]
    regularised = [("mean_masked_reg", 0.3, 1e-3)]
    per_arm = {}
    for a in arms:
        rows = [train(a, s) for s in SEEDS]
        per_arm[a] = {"rows": [{k: v for k, v in r.items()
                                if k not in ("predictions", "test_idx", "confusion",
                                             "curve")} for r in rows],
                      "stats": {k: agg(rows, k) for k in
                                ("test_acc", "test_macro_f1", "vocab_size", "params")}}
    # Week 6's regularisation, applied to the best pooling arm: does it rescue
    # the model, or is the binding constraint the 523 training passages?
    for name, p, wd in regularised:
        rows = [train("mean_masked", s, dropout=p, wd=wd) for s in SEEDS]
        per_arm[name] = {"rows": [{k: v for k, v in r.items()
                                   if k not in ("predictions", "test_idx", "confusion",
                                                "curve")} for r in rows],
                         "stats": {k: agg(rows, k) for k in
                                   ("test_acc", "test_macro_f1", "vocab_size", "params")},
                         "regularisation": {"dropout": p, "weight_decay": wd}}

    detail = train("packed", SEED, want_curve=True)
    bug = train("last_step", SEED)
    rows_text = [json.loads(l) for l in CORPUS.read_text(encoding="utf-8").splitlines()
                 if l.strip()]
    wrong = []
    for k, p in enumerate(detail["predictions"]):
        i = detail["test_idx"][k]
        true_w = rows_text[i]["week"]
        if p != true_w - 1:
            wrong.append({
                "true_week": true_w,
                "pred_week": p + 1,
                "tokens": len(WORD.findall(rows_text[i]["text"].lower())),
                "text": rows_text[i]["text"][:170],
            })
    wrong.sort(key=lambda w: w["tokens"])          # shortest first

    # confusion over all 5 seeds for the correct arm
    conf = np.zeros((N_CLASS, N_CLASS), dtype=int)
    for s in SEEDS:
        conf += np.array(train("packed", s)["confusion"])

    # max_len sweep: the bug should get worse as the padding gets longer
    sweep = {}
    for a in ("packed", "last_step"):
        sweep[a] = {}
        for ml in (48, MAX_LEN, 192):
            vals = [train(a, s, max_len=ml)["test_acc"] for s in SWEEP_SEEDS]
            sweep[a][str(ml)] = {"mean": round(st.mean(vals), 4),
                                 "sd": round(st.stdev(vals), 4)}

    payload = {
        "protocol": {
            "corpus": "data/raw/course-text-corpus.jsonl (built from this repo's own W1-6 text)",
            "n_passages": len(rows_text), "classes": N_CLASS,
            "split": "70/15/15 stratified by week, random_state = seed",
            "tokeniser": "lowercase, regex [a-z][a-z'-]*",
            "vocab": f"from train only, min_freq={MIN_FREQ}, cap {MAX_VOCAB}, <pad>=0 <unk>=1",
            "model": f"Embedding({EMB}) -> LSTM({HID}) -> Linear({N_CLASS})",
            "optimizer": "Adam", "lr": LR, "batch": BATCH, "epochs": EPOCHS,
            "max_len": MAX_LEN, "seeds": list(SEEDS),
            "sweep_seeds": list(SWEEP_SEEDS),
            "regularisation_arm": {"base": "mean_masked", "dropout": 0.3,
                                   "weight_decay": 1e-3,
                                   "why": ("Week 6's regularisation applied to the best "
                                           "pooling arm, to test whether the low accuracy is "
                                           "a capacity problem or a data problem")},
        },
        "arms": per_arm,
        "confusion_packed_5seeds": conf.tolist(),
        "length_buckets": [f"{lo}-{hi if hi < 10000 else 'max'}" for lo, hi in BUCKETS],
        "detail_seed42": {
            "packed": {k: detail[k] for k in
                       ("test_acc", "test_macro_f1", "by_length", "long_doc_split",
                        "share_shorter_than_max_len", "curve", "params", "vocab_size")},
            "last_step": {k: bug[k] for k in
                          ("test_acc", "test_macro_f1", "by_length", "long_doc_split",
                           "share_shorter_than_max_len")},
        },
        "misclassified_seed42": wrong[:14],
        "max_len_sweep": sweep,
        "cjk_tokenisation": cjk_demo(),
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(payload, indent=1, ensure_ascii=False))

    print(f"{'arm':<19}{'vocab':>7}{'params':>9}{'acc':>16}{'macroF1':>16}")
    for a in per_arm:
        s = per_arm[a]["stats"]
        f = lambda k: f"{s[k]['mean']:.3f}±{s[k]['sd']:.3f}"
        print(f"{a:<15}{s['vocab_size']['mean']:>7.0f}{s['params']['mean']:>9.0f}"
              f"{f('test_acc'):>16}{f('test_macro_f1'):>16}")
    print("\nby length (seed 42) — packed vs last_step:")
    for b in payload["length_buckets"]:
        p = detail["by_length"].get(b); q = bug["by_length"].get(b)
        print(f"  {b:>8}  n={p['n'] if p else '-':>3}  packed={p['acc'] if p else '-':>6}"
              f"  last_step={q['acc'] if q else '-':>6}")
    print("\nlong-doc split (last_step seed 42):", bug["long_doc_split"])
    print("\nmax_len sweep:", json.dumps(sweep, ensure_ascii=False))
    print("\ncjk:", json.dumps(payload["cjk_tokenisation"]["schemes"], ensure_ascii=False))
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
