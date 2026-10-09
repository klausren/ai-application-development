"""Week 7 authoritative experiment: CNNs for computer vision.

Protocol (FIXED — re-run every downstream document if you change this file):
  dataset    sklearn.datasets.load_digits   (8x8, 10 classes, 1797 samples, offline)
  split      70 / 15 / 15, stratified, random_state = seed        (n_train ~= 1258)
  optimiser  Adam(lr=1e-3), batch_size=64, epochs=120, no weight decay
  seeds      42, 43, 44, 45, 46                 (every arm is repeated; mean +- sd)

Architectures (5 arms):
  mlp        flatten 64 -> 128 -> 64 -> 10       (Week 6's network, now on the full split)
  cnn        conv(1->8,3,pad1) ReLU maxpool2 -> conv(8->16,3,pad1) ReLU maxpool2 -> FC 10
  cnn_avg    same, but average pooling instead of max pooling
  cnn_wide   conv(1->16) ... conv(16->32) ... -> FC 128 -> 10
  cnn_aug    cnn + random +/-1 px shift on the TRAINING batch only

Additional measurements, all in outputs/w7_cnn.json:
  * parameter count per architecture
  * translation robustness: test accuracy under a zero-filled test-time shift
  * confusion matrix over all 5 seeds + the individual misclassified digits
  * receptive field per stage, and the output-shape formula checked against real tensors
  * gradient accumulation: true batch 128 vs 4 x 32 (scaled) vs 4 x 32 (unscaled)
  * peak process memory vs batch size, measured in subprocesses

What the run actually shows (do NOT rewrite this into "the CNN is more accurate —
that is not what the numbers say"):
  * on 8x8 digits the CNN matches the MLP's accuracy with ~9x fewer parameters
  * the MLP degrades faster than the CNN when the test image is translated
  * the second convolution already covers the whole 8x8 field, so the architecture
    cannot extract any more translation invariance than it does
  * 4 x 32 gradient accumulation reproduces the true batch-128 run exactly, and
    forgetting to scale the loss by 1/accum does not
  * at this model size nothing ever comes close to running out of memory

Writes outputs/w7_cnn.json.
"""

from __future__ import annotations

import json
import os
import random
import statistics as st
import subprocess
import sys

import numpy as np
import torch
import torch.nn as nn
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

SEED = 42
SEEDS = (42, 43, 44, 45, 46)
EPOCHS = 120
BATCH = 64
LR = 1e-3
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "outputs", "w7_cnn.json")

# (kind, out_channels, kernel, stride, padding)
CNN_STAGES = [("conv", 8, 3, 1, 1), ("pool", 8, 2, 2, 0),
              ("conv", 16, 3, 1, 1), ("pool", 16, 2, 2, 0)]
CNN_WIDE_STAGES = [("conv", 16, 3, 1, 1), ("pool", 16, 2, 2, 0),
                   ("conv", 32, 3, 1, 1), ("pool", 32, 2, 2, 0)]


# ------------------------------------------------------------------ helpers --
def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def get_data(seed):
    """70/15/15 stratified split. Identical recipe to Week 6 so the two weeks'
    MLP numbers are comparable."""
    X, y = load_digits(return_X_y=True)
    X = (X / 16.0).astype(np.float32)
    Xtr, Xrest, ytr, yrest = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=seed)
    Xva, Xte, yva, yte = train_test_split(
        Xrest, yrest, test_size=0.50, stratify=yrest, random_state=seed)
    t = lambda a: torch.tensor(a)
    return (t(Xtr), torch.tensor(ytr), t(Xva), torch.tensor(yva),
            t(Xte), torch.tensor(yte))


class MLP(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(64, 128), nn.ReLU(),
                                 nn.Linear(128, 64), nn.ReLU(),
                                 nn.Linear(64, 10))

    def forward(self, x):
        return self.net(x.view(x.shape[0], -1))


class CNN(nn.Module):
    """Two conv+pool blocks, then one linear layer. `stages` fixes the channel
    counts so the wide variant shares the same code; `in_size` is 8 for every
    real arm and only larger for the memory probe."""

    def __init__(self, stages=CNN_STAGES, fc=None, pool=nn.MaxPool2d, in_size=8):
        super().__init__()
        self.stages = stages
        self.in_size = in_size
        layers, cin = [], 1
        self.shapes = []
        size = in_size
        for kind, cout, k, s, p in stages:
            if kind == "conv":
                layers += [nn.Conv2d(cin, cout, k, stride=s, padding=p), nn.ReLU()]
                size = (size + 2 * p - k) // s + 1
                cin = cout
            else:
                layers.append(pool(k, stride=s))
                size = (size - k) // s + 1
            self.shapes.append((cin, size, size))
        self.body = nn.Sequential(*layers)
        self.flat = cin * size * size
        self.head = nn.Linear(self.flat, fc or 10)

    def forward(self, x):
        x = self.body(x.view(-1, 1, self.in_size, self.in_size))
        return self.head(x.view(x.shape[0], -1))


def make_model(arm):
    if arm == "mlp":
        return MLP()
    if arm == "cnn":
        return CNN()
    if arm == "cnn_avg":
        return CNN(pool=nn.AvgPool2d)
    if arm == "cnn_wide":
        return CNN(stages=CNN_WIDE_STAGES, fc=128)
    if arm == "cnn_aug":
        return CNN()
    raise ValueError(arm)


def shift_batch(imgs, dx, dy):
    """Zero-filled translation of an (n,1,8,8) batch. Used both as the training
    augmentation and as the test-time perturbation."""
    out = torch.roll(imgs, shifts=(dy, dx), dims=(2, 3))
    if dy > 0:
        out[:, :, :dy, :] = 0
    elif dy < 0:
        out[:, :, dy:, :] = 0
    if dx > 0:
        out[:, :, :, :dx] = 0
    elif dx < 0:
        out[:, :, :, dx:] = 0
    return out


@torch.no_grad()
def evaluate(model, X, y, dx=0, dy=0):
    model.eval()
    if dx or dy:
        X = shift_batch(X.view(-1, 1, 8, 8), dx, dy).view(X.shape[0], 64)
    out = model(X)
    return (out.argmax(1) == y).float().mean().item(), out


# -------------------------------------------------------------------- train --
PROBE_SHIFTS = (-2, -1, 0, 1, 2)
ACCUM_MODES = ("none", "naive", "exact", "unscaled")


def train_arm(arm, seed, epochs=EPOCHS, batch=BATCH, accum=1, accum_mode="none",
              probe_shifts=()):
    """One training run, with everything the deck needs collected on the way out.

    Gradient accumulation is expressed per GROUP rather than per micro-batch, so
    the weighting can be made exact. For a group of `size` samples split into
    micro-batches of len(sel):

        none      single batch, weight 1
        exact     weight len(sel)/size   -> the group gradient IS the group mean,
                                            even when the last micro-batch is short
        naive     weight 1/accum         -> correct only while every micro-batch has
                                            the same size; biased on the epoch tail
        unscaled  weight 1               -> the bug that "forgot to scale at all"

    Trained once per (arm, seed) on purpose: the shift probe and the confusion
    matrix reuse this run instead of retraining, which is where a naive
    "train inside the sweep" loop silently costs 5x the compute.
    """
    set_seed(seed)
    Xtr, ytr, Xva, yva, Xte, yte = get_data(seed)
    model = make_model(arm)
    opt = torch.optim.Adam(model.parameters(), lr=LR)
    g = torch.Generator().manual_seed(seed)
    n = Xtr.shape[0]
    hist = {"train_acc": [], "val_acc": []}
    steps = 0
    group = batch * accum
    accum_steps = group // batch

    for ep in range(1, epochs + 1):
        model.train()
        perm = torch.randperm(n, generator=g)
        for g0 in range(0, n, group):
            chunk = perm[g0:g0 + group]
            size = len(chunk)
            opt.zero_grad()
            for m0 in range(0, size, batch):
                sel = chunk[m0:m0 + batch]
                xb, yb = Xtr[sel], ytr[sel]
                if arm == "cnn_aug":
                    dx = int(torch.randint(-1, 2, (1,), generator=g))
                    dy = int(torch.randint(-1, 2, (1,), generator=g))
                    xb = shift_batch(xb.view(-1, 1, 8, 8), dx, dy).view(-1, 64)
                loss = nn.functional.cross_entropy(model(xb), yb)
                if accum_mode == "exact":
                    w = len(sel) / size
                elif accum_mode == "naive":
                    w = 1.0 / accum_steps
                else:                              # none / unscaled
                    w = 1.0
                (loss * w).backward()
            opt.step()
            steps += 1
        tr, _ = evaluate(model, Xtr, ytr)
        va, _ = evaluate(model, Xva, yva)
        hist["train_acc"].append(round(tr, 4))
        hist["val_acc"].append(round(va, 4))

    te, logits = evaluate(model, Xte, yte)
    row = {
        "arm": arm, "seed": seed,
        "params": sum(p.numel() for p in model.parameters()),
        "train_acc": round(hist["train_acc"][-1], 4),
        "val_acc": round(hist["val_acc"][-1], 4),
        "test_acc": round(te, 4),
        "n_test": int(len(yte)),
        "n_wrong": int((logits.argmax(1) != yte).sum()),
        "opt_steps": steps,
        "curve": {"train_acc": hist["train_acc"][::6],
                  "val_acc": hist["val_acc"][::6]},
    }
    for d in probe_shifts:
        row[f"test_acc_dx{d:+d}"] = round(evaluate(model, Xte, yte, dx=d)[0], 4)

    pred = logits.argmax(1)
    conf_m = torch.zeros(10, 10, dtype=torch.long)
    for t_, p_ in zip(yte.tolist(), pred.tolist()):
        conf_m[t_][p_] += 1
    row["confusion"] = conf_m.tolist()
    probs = torch.softmax(logits, 1)
    wrong = []
    for i in range(len(yte)):
        if pred[i] != yte[i]:
            wrong.append({
                "true": int(yte[i]), "pred": int(pred[i]),
                "confidence": round(float(probs[i][pred[i]]), 4),
                "true_prob": round(float(probs[i][yte[i]]), 4),
                "pixels": [int(v) for v in (Xte[i] * 16).round().clamp(0, 15)],
            })
    wrong.sort(key=lambda w: -w["confidence"])
    row["misclassified"] = wrong
    row["n_test"] = int(len(yte))
    row["n_wrong"] = len(wrong)
    return row


def agg(rows, key):
    vals = [r[key] for r in rows]
    return {"mean": round(st.mean(vals), 4),
            "sd": round(st.stdev(vals), 4) if len(vals) > 1 else 0.0}


# ------------------------------------------------------- architecture facts --
def out_size(size, k, s, p):
    return (size + 2 * p - k) // s + 1


def receptive_field(stages, start=8):
    """RF and jump size after each stage; also the feature-map size, checked
    against a real forward pass by the caller."""
    rf, jump, size, out = 1, 1, start, []
    for kind, _c, k, s, p in stages:
        size = out_size(size, k, s, p)
        rf = rf + (k - 1) * jump
        jump = jump * s
        out.append({"kind": kind, "k": k, "s": s, "rf": rf,
                    "jump": jump, "feature_map": size})
    return out


def architecture_facts():
    """Every shape here comes from a real forward pass. The stage -> feature-map
    mapping is DERIVED from the layer list (a conv stage owns two body layers —
    conv then ReLU — a pool stage owns one) instead of hard-coding indices, which
    is how an earlier version of this check silently compared a ReLU output
    against a pooling output and reported a false failure."""
    cnn = CNN()
    body = list(cnn.body)
    recorded, i = [], 0
    h = torch.zeros(1, 1, 8, 8)
    with torch.no_grad():
        for kind, *_rest in CNN_STAGES:
            if kind == "conv":
                h = body[i](h); i += 1        # conv
                h = body[i](h); i += 1        # ReLU
            else:
                h = body[i](h); i += 1        # pool
            recorded.append(list(h.shape[1:]))
    assert i == len(body), f"layer accounting off: consumed {i} of {len(body)}"

    stages = receptive_field(CNN_STAGES)
    checks = []
    for st, real in zip(stages, recorded):
        expected = st["feature_map"]
        checks.append({"stage": st["kind"], "formula_out": expected,
                       "forward_out": real[1], "matches_forward": real[1] == expected})
    wide = receptive_field(CNN_WIDE_STAGES)
    return {
        "cnn": {
            "params": sum(p.numel() for p in cnn.parameters()),
            "feature_maps_from_real_forward": recorded,
            "stages": stages,
            "final_rf": stages[-1]["rf"],
            "rf_of_last_conv": next(s["rf"] for s in reversed(stages)
                                    if s["kind"] == "conv"),
            "flatten_dim": cnn.flat,
            "image_size": 8,
        },
        "cnn_wide": {
            "params": sum(p.numel() for p in make_model("cnn_wide").parameters()),
            "stages": wide,
            "final_rf": wide[-1]["rf"],
        },
        "mlp": {"params": sum(p.numel() for p in MLP().parameters())},
        "formula_checks": checks,
    }


# ---------------------------------------------------------- memory probe -----
def _mem_probe(bs):
    """Peak RSS of one forward+backward pass at this batch size.

    macOS reports ru_maxrss in BYTES (Linux uses kilobytes), so the divisor is
    1024**2 and not 1024 — getting this wrong silently reports megabytes that are
    off by 1024x.

    The 8x8 model is far too small to move the needle, so the input is nearest
    neighbour upsampled to 32x32 — 16x the activation volume, the same order as
    a real vision model — purely to make the batch-size effect measurable.
    bs=0 measures the interpreter + torch baseline on its own so the growth can
    be reported above it rather than on top of it."""
    import resource

    def rss_mb():
        return round(resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024 ** 2, 1)

    label = "32x32 (4x nearest-neighbour upsample of the 8x8 digits)"
    if bs == 0:
        print(json.dumps({"batch": 0, "peak_rss_mb": rss_mb(),
                          "input": "interpreter + torch only"}))
        return

    m = CNN(in_size=32)
    opt = torch.optim.Adam(m.parameters(), lr=1e-3)
    x = torch.randn(bs, 1, 8, 8)
    x = x.repeat_interleave(4, dim=2).repeat_interleave(4, dim=3)
    y = torch.randint(0, 10, (bs,))
    for _ in range(3):
        opt.zero_grad()
        nn.functional.cross_entropy(m(x), y).backward()
        opt.step()
    print(json.dumps({"batch": bs, "peak_rss_mb": rss_mb(), "input": label}))


def memory_sweep():
    out = []
    for bs in (0, 32, 64, 128, 256, 512, 1024):
        r = subprocess.run([sys.executable, os.path.abspath(__file__),
                            "--mem-probe", str(bs)],
                           capture_output=True, text=True, timeout=600)
        line = [l for l in r.stdout.splitlines() if l.startswith("{")]
        if line:
            out.append(json.loads(line[-1]))
        else:
            print("mem probe failed for", bs, r.stderr[-400:], file=sys.stderr)
    base = out[0]["peak_rss_mb"] if out and out[0]["batch"] == 0 else 0.0
    for m in out:
        m["over_baseline_mb"] = round(m["peak_rss_mb"] - base, 1)
    return out


# -------------------------------------------------------------------- main ---
def main():
    arms = ["mlp", "cnn", "cnn_avg", "cnn_wide", "cnn_aug"]
    keys = ("train_acc", "val_acc", "test_acc", "params")
    probe_arms = ("mlp", "cnn", "cnn_aug")

    per_arm, curves, detail = {}, {}, {}
    for name in arms:
        shifts = PROBE_SHIFTS if name in probe_arms else ()
        rows = [train_arm(name, s, probe_shifts=shifts) for s in SEEDS]
        per_arm[name] = {"rows": rows,
                         "stats": {k: agg(rows, k) for k in keys}}
        curves[name] = rows[0]["curve"]                 # seed 42
        detail[name] = rows[0]                          # seed 42, full detail

    # translation robustness, averaged over the seeds already trained
    robust = {}
    for a in probe_arms:
        robust[a] = {str(d): round(st.mean(
            [r[f"test_acc_dx{d:+d}"] for r in per_arm[a]["rows"]]), 4)
            for d in PROBE_SHIFTS}

    # confusion matrix summed over all 5 seeds (more stable than one seed)
    totals = np.zeros((10, 10), dtype=int)
    for r in per_arm["cnn"]["rows"]:
        totals += np.array(r["confusion"])
    confusion_5seed = totals.tolist()

    # gradient accumulation: does the surrogate reproduce the real batch?
    accum = {}
    for name, kw in (("batch128_true", {"batch": 128, "accum": 1,
                                        "accum_mode": "none"}),
                     ("accum4x32_exact", {"batch": 32, "accum": 4,
                                          "accum_mode": "exact"}),
                     ("accum4x32_naive", {"batch": 32, "accum": 4,
                                          "accum_mode": "naive"}),
                     ("accum4x32_unscaled", {"batch": 32, "accum": 4,
                                             "accum_mode": "unscaled"})):
        rows = [train_arm("cnn", s, **kw) for s in SEEDS]
        accum[name] = {
            "rows": [{k: r[k] for k in ("seed", "test_acc", "n_wrong",
                                        "opt_steps")} for r in rows],
            "stats": {k: agg(rows, k) for k in ("test_acc", "val_acc")}}
    ref = [r["test_acc"] for r in accum["batch128_true"]["rows"]]
    for name, v in accum.items():
        v["identical_to_batch128_per_seed"] = [r["test_acc"] for r in v["rows"]] == ref
        v["n_seeds_matching"] = sum(1 for a, b in zip([r["test_acc"] for r in v["rows"]],
                                                      ref) if a == b)

    mem = memory_sweep()
    if len(mem) >= 2:
        base = mem[0]["peak_rss_mb"]
        for m in mem:
            m["ratio_over_baseline"] = (round(m["over_baseline_mb"] /
                                              max(mem[1]["over_baseline_mb"], 0.1), 2)
                                        if len(mem) > 1 else None)

    payload = {
        "protocol": {
            "dataset": "sklearn.datasets.load_digits (8x8, 10 classes, 1797 samples)",
            "split": "70/15/15 stratified, random_state = seed",
            "optimizer": "Adam", "lr": LR, "batch": BATCH, "epochs": EPOCHS,
            "seeds": list(SEEDS),
            "cnn_stages": [[k, c, kk, s, p] for k, c, kk, s, p in CNN_STAGES],
            "cnn_wide_stages": [[k, c, kk, s, p] for k, c, kk, s, p in CNN_WIDE_STAGES],
            "augmentation": "random +/-1 px shift, training batch only",
            "accumulation_modes": list(ACCUM_MODES),
        },
        "arms": per_arm,
        "curves_seed42_every6ep": curves,
        "predictions_seed42": detail,
        "confusion_cnn_5seeds": confusion_5seed,
        "translation_robustness": robust,
        "architecture": architecture_facts(),
        "grad_accumulation": accum,
        "memory_vs_batch": mem,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)

    print(f"\n{'arm':<11}{'params':>9}{'train':>15}{'val':>15}{'test':>15}")
    for a in arms:
        s = per_arm[a]["stats"]
        f = lambda k: f"{s[k]['mean']:.3f}±{s[k]['sd']:.3f}"
        print(f"{a:<11}{s['params']['mean']:>9.0f}{f('train_acc'):>15}"
              f"{f('val_acc'):>15}{f('test_acc'):>15}")
    print("\ntranslation robustness (test acc, dx):")
    for a, d in robust.items():
        print(f"  {a:<9}", {k: d[k] for k in ("-2", "-1", "0", "1", "2")})
    print("\ngradient accumulation (test acc per seed):")
    for n, v in accum.items():
        print(f"  {n:<20} {[r['test_acc'] for r in v['rows']]}"
              f"  mean {v['stats']['test_acc']['mean']:.4f}"
              f"  match={v['n_seeds_matching']}/5")
    print("\nmemory vs batch:", [(m["batch"], m["peak_rss_mb"]) for m in mem])
    print("\nwrote", OUT)


if __name__ == "__main__":
    if len(sys.argv) > 2 and sys.argv[1] == "--mem-probe":
        _mem_probe(int(sys.argv[2]))
    else:
        main()
