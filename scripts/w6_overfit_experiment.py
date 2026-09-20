"""Week 6 authoritative experiment: overfitting and regularisation.

Protocol (FIXED — re-run every downstream document if you change this file):
  dataset    sklearn.datasets.load_digits   (8x8, 10 classes, 1797 samples, offline)
  split      70 / 15 / 15, stratified, random_state = seed
  train set  deliberately small: n_train = 80  -> 17,226 params vs 80 samples
  model      64 -> 128 -> 64 -> 10 MLP, ReLU
  optimiser  Adam(lr=1e-3), batch_size=32, epochs=400
  seeds      42, 43, 44, 45, 46  (every arm is repeated; we report mean +- sd)

Arms (6):
  baseline        no regularisation
  early_stop      stop when val loss has not improved for 20 epochs, restore best weights
  weight_decay    Adam(weight_decay=1e-2)
  dropout         Dropout(p=0.3) after each hidden layer
  augment         Gaussian input noise (sigma=0.15) + random +/-1 px shift,
                  training batch only
  combined        weight_decay + dropout + augment

What the run actually shows (do NOT rewrite this into "regularisation improves
accuracy" — that is not what the numbers say):
  * train accuracy saturates at 1.000 while the best validation epoch is ~97/400
  * validation LOSS rises monotonically after that epoch in every arm
  * validation ACCURACY barely moves -> accuracy hides the degradation
  * weight decay's clean win is suppressing the rise in validation loss
  * augmentation and the combined arm actively hurt on this task

Writes outputs/w6_regularisation.json.
"""

from __future__ import annotations

import json
import os
import random
import statistics as st

import numpy as np
import torch
import torch.nn as nn
from sklearn.datasets import load_digits
from sklearn.model_selection import train_test_split

SEED = 42
SEEDS = (42, 43, 44, 45, 46)
N_TRAIN = 80
HIDDEN = (128, 64)
EPOCHS = 400
BATCH = 32
LR = 1e-3
PATIENCE = 20
WD = 1e-2
P_DROPOUT = 0.3
NOISE_SIGMA = 0.15

OUT = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                   "outputs", "w6_regularisation.json")


def set_seed(seed):
    random.seed(seed)
    np.random.seed(seed)
    torch.manual_seed(seed)


def get_data(seed):
    """70/15/15 stratified split; shrink the training split to N_TRAIN."""
    X, y = load_digits(return_X_y=True)
    X = (X / 16.0).astype(np.float32)              # 0..15 -> 0..1
    Xtr, Xrest, ytr, yrest = train_test_split(
        X, y, test_size=0.30, stratify=y, random_state=seed)
    Xva, Xte, yva, yte = train_test_split(
        Xrest, yrest, test_size=0.50, stratify=yrest, random_state=seed)

    rng = np.random.RandomState(seed)
    keep = rng.choice(len(Xtr), size=N_TRAIN, replace=False)
    Xtr, ytr = Xtr[keep], ytr[keep]

    t = lambda a, typ: torch.tensor(a, dtype=typ)
    return (t(Xtr, torch.float32), t(ytr, torch.long),
            t(Xva, torch.float32), t(yva, torch.long),
            t(Xte, torch.float32), t(yte, torch.long))


def make_model(dropout=0.0):
    """MLP with hidden sizes HIDDEN, ReLU, optional Dropout after each block."""
    layers, prev = [], 64
    for h in HIDDEN:
        layers.append(nn.Linear(prev, h))
        layers.append(nn.ReLU())
        if dropout:
            layers.append(nn.Dropout(dropout))
        prev = h
    layers.append(nn.Linear(prev, 10))
    return nn.Sequential(*layers).float()


def augment(xb, generator):
    """Gaussian noise + random +/-1 px shift. Applied to the training batch only."""
    n = xb.shape[0]
    img = xb.view(n, 8, 8)
    idx = torch.arange(8).view(1, 8).expand(n, 8)
    shift = torch.randint(-1, 2, (n, 1), generator=generator)
    col = ((idx + shift) % 8).unsqueeze(1).expand(n, 8, 8)
    img = torch.gather(img, 2, col)
    shift_r = torch.randint(-1, 2, (n, 1), generator=generator)
    row = ((idx + shift_r) % 8).unsqueeze(2).expand(n, 8, 8)
    img = torch.gather(img, 1, row)
    xb = img.reshape(n, 64)
    noise = torch.randn(xb.shape, generator=generator) * NOISE_SIGMA
    return (xb + noise).clamp(0.0, 1.0)


@torch.no_grad()
def evaluate(model, X, y):
    model.eval()
    out = model(X)
    loss = nn.functional.cross_entropy(out, y).item()
    acc = (out.argmax(1) == y).float().mean().item()
    return loss, acc


def run_arm(name, seed, *, wd=0.0, dropout=0.0, aug=False, early=False,
            collect_curve=False):
    set_seed(seed)
    Xtr, ytr, Xva, yva, Xte, yte = get_data(seed)
    model = make_model(dropout)
    opt = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=wd)
    g = torch.Generator().manual_seed(seed)

    n = Xtr.shape[0]
    hist = {"train_acc": [], "val_acc": [], "val_loss": []}
    best = {"val_loss": float("inf"), "epoch": 0, "state": None,
            "val_acc": 0.0, "train_acc": 0.0}
    bad = 0

    for ep in range(1, EPOCHS + 1):
        model.train()
        perm = torch.randperm(n, generator=g)
        for i in range(0, n, BATCH):
            sel = perm[i:i + BATCH]
            xb, yb = Xtr[sel], ytr[sel]
            if aug:
                xb = augment(xb, g)
            opt.zero_grad()
            loss = nn.functional.cross_entropy(model(xb), yb)
            loss.backward()
            opt.step()

        tr_loss, tr_acc = evaluate(model, Xtr, ytr)
        va_loss, va_acc = evaluate(model, Xva, yva)
        hist["train_acc"].append(round(tr_acc, 4))
        hist["val_acc"].append(round(va_acc, 4))
        hist["val_loss"].append(round(va_loss, 4))

        if va_loss < best["val_loss"] - 1e-4:
            best.update(val_loss=va_loss, epoch=ep, val_acc=va_acc,
                        train_acc=tr_acc,
                        state={k: v.clone() for k, v in model.state_dict().items()})
            bad = 0
        else:
            bad += 1
            if early and bad >= PATIENCE:
                break

    if early and best["state"] is not None:
        model.load_state_dict(best["state"])
    te_loss, te_acc = evaluate(model, Xte, yte)

    final_tr, final_va = hist["train_acc"][-1], hist["val_acc"][-1]
    final_vl = hist["val_loss"][-1]
    kept_tr, kept_va = ((best["train_acc"], best["val_acc"]) if early
                        else (final_tr, final_va))
    kept_vl = best["val_loss"] if early else final_vl

    row = {
        "arm": name, "seed": seed,
        "epochs_run": len(hist["train_acc"]),
        "params": sum(p.numel() for p in model.parameters()),
        "train_acc": round(kept_tr, 4), "val_acc": round(kept_va, 4),
        "gap": round(kept_tr - kept_va, 4),
        "val_loss_best": round(best["val_loss"], 4),
        "val_loss_best_epoch": best["epoch"],
        "val_loss_final": round(final_vl, 4),
        "val_loss_rise": round(final_vl - best["val_loss"], 4),
        "test_acc": round(te_acc, 4), "test_loss": round(te_loss, 4),
    }
    if collect_curve:
        row["curve"] = {k: v[::20] for k, v in hist.items()}   # every 20 epochs
        row["curve_last_train"] = hist["train_acc"][-1]
    return row


def agg(rows, key):
    vals = [r[key] for r in rows]
    return {"mean": round(st.mean(vals), 4),
            "sd": round(st.stdev(vals), 4) if len(vals) > 1 else 0.0}


def main():
    arms = [("baseline", {}),
            ("early_stop", {"early": True}),
            ("weight_decay", {"wd": WD}),
            ("dropout", {"dropout": P_DROPOUT}),
            ("augment", {"aug": True}),
            ("combined", {"wd": WD, "dropout": P_DROPOUT, "aug": True})]
    keys = ("train_acc", "val_acc", "gap", "val_loss_best", "val_loss_final",
            "val_loss_rise", "val_loss_best_epoch", "test_acc", "epochs_run")

    per_arm, curves = {}, {}
    for name, kw in arms:
        rows = []
        for s in SEEDS:
            rows.append(run_arm(name, s, **kw))
        per_arm[name] = {"rows": rows,
                         "stats": {k: agg(rows, k) for k in keys}}
        # one representative seed-42 curve for the deck (every 20 epochs)
        curves[name] = run_arm(name, SEED, collect_curve=True, **kw)["curve"]

    payload = {
        "protocol": {
            "dataset": "sklearn.datasets.load_digits (8x8, 10 classes, 1797 samples)",
            "split": "70/15/15 stratified, random_state = seed",
            "n_train": N_TRAIN, "hidden": list(HIDDEN),
            "params": sum(p.numel() for p in make_model().parameters()),
            "optimizer": "Adam", "lr": LR, "batch": BATCH, "epochs": EPOCHS,
            "patience": PATIENCE, "weight_decay": WD,
            "dropout_p": P_DROPOUT, "noise_sigma": NOISE_SIGMA,
            "seeds": list(SEEDS),
        },
        "arms": per_arm,
        "curves_seed42_every20ep": curves,
    }
    os.makedirs(os.path.dirname(OUT), exist_ok=True)
    with open(OUT, "w") as fh:
        json.dump(payload, fh, indent=1, ensure_ascii=False)

    print(f"{'arm':<13}{'train':>14}{'val':>14}{'gap':>14}"
          f"{'vLoss@best':>14}{'vLoss@400':>14}{'test':>14}{'ep':>6}")
    for name, _ in arms:
        s = per_arm[name]["stats"]
        f = lambda k: f"{s[k]['mean']:.3f}±{s[k]['sd']:.3f}"
        print(f"{name:<13}{f('train_acc'):>14}{f('val_acc'):>14}{f('gap'):>14}"
              f"{f('val_loss_best'):>14}{f('val_loss_final'):>14}"
              f"{f('test_acc'):>14}{s['epochs_run']['mean']:>6.0f}")
    print("\nwrote", OUT)


if __name__ == "__main__":
    main()
