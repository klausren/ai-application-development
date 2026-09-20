#!/usr/bin/env python
"""Execute the Week 3 handout's code blocks verbatim and check every number
the handout claims in its comments.

Any mismatch means the handout lies to students, so this runs before every
publish. Run:
    python scripts/verify_w3_handout.py
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset, Subset, WeightedRandomSampler

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "raw" / "defects.csv"

ok = fail = 0


def check(label: str, got, want) -> None:
    global ok, fail
    good = (got == want) if not isinstance(want, float) else abs(got - want) < 5e-4
    mark = "OK  " if good else "FAIL"
    if good:
        ok += 1
    else:
        fail += 1
    print(f"{mark} {label:<52} got={got!r:<24} want={want!r}")


# ============================ Part A ========================================
df = pd.read_csv(CSV)
check("A shape", tuple(df.shape), (12480, 13))
check("A n classes", int(df["label"].nunique()), 5)

share = df["label"].value_counts(normalize=True).sort_index()
check("A smallest class share", round(float(share.min()), 4), 0.041)
assert share.min() > 0.0
assert share.min() < 0.05

key = ["batch_id", "timestamp"]
n_dup = int(df.duplicated(subset=key).sum())
check("A duplicates on key", n_dup, 812)

age_missing = (df.assign(age_missing=df["age"].isna())
                 .groupby("label")["age_missing"].mean().round(4).to_dict())
check("A age-missing rate, class 3", float(age_missing[3]), 0.25)
check("A age-missing rate, class 0", float(age_missing[0]), 0.0227)

miss = df.isna().mean().sort_values(ascending=False).head(6)
check("A top missing column", miss.index[0], "age")
check("A age missing rate", round(float(miss.iloc[0]), 3), 0.032)
check("A 2nd missing column", miss.index[1], "pressure_kpa")
check("A 3rd missing column", miss.index[2], "humidity_pct")
check("A raw temperature max", round(float(df["temperature_c"].max()), 2), 218.25)

# ============================ Part B ========================================
before = len(df)
df = df.drop_duplicates(subset=key, keep="first").reset_index(drop=True)
check("B rows after de-dup", len(df), 11668)
check("B removed == counted", before - len(df) == n_dup, True)

mask_f = df["temperature_c"] > 120
check("B rows recorded in Fahrenheit", int(mask_f.sum()), 935)
check("B max before unify", round(float(df["temperature_c"].max()), 2), 214.01)
df.loc[mask_f, "temperature_c"] = (df.loc[mask_f, "temperature_c"] - 32) * 5 / 9
check("B max after unify", round(float(df["temperature_c"].max()), 2), 108.94)
assert df["temperature_c"].max() < 120

codes_raw = sorted(df["material_code"].unique().tolist())
check("B code spellings before", len(codes_raw), 10)
df["material_code"] = df["material_code"].str.upper().str.replace("-", "", regex=False)
check("B codes after", sorted(df["material_code"].unique().tolist()),
      ["A1", "A2", "B1", "B2", "C1"])
df["material_code"] = df["material_code"].map({"A1": 0, "A2": 1, "B1": 2, "B2": 3, "C1": 4})
assert df["material_code"].notna().all()

# ============================ Part C ========================================
labels = torch.tensor(df["label"].values, dtype=torch.long)
g = torch.Generator().manual_seed(42)
idx = torch.arange(len(df))
parts = []
val_frac = test_frac = 0.15
for cls in labels.unique().tolist():
    c = idx[labels == cls]
    c = c[torch.randperm(len(c), generator=g)]
    n_tr = int(len(c) * (1 - val_frac - test_frac))
    n_va = int(len(c) * val_frac)
    parts.append((c[:n_tr], c[n_tr:n_tr + n_va], c[n_tr + n_va:]))

train_idx = torch.cat([p[0] for p in parts])
val_idx = torch.cat([p[1] for p in parts])
test_idx = torch.cat([p[2] for p in parts])
check("C split sizes", (len(train_idx), len(val_idx), len(test_idx)), (8165, 1747, 1756))
check("C classes present in train",
      sorted(torch.unique(labels[train_idx]).tolist()), [0, 1, 2, 3, 4])

train = df.iloc[train_idx]

# the handout measures the leak BEFORE imputing - the order is the lesson
full_median = float(df["age"].median())
train_median = float(train["age"].median())
rel = abs(full_median - train_median) / train_median * 100
check("C full median vs train median (%)", round(rel, 3), 0.039)
check("C full-data median (before impute)", round(full_median, 4), 6.4886)
print(f"     -> printed values would read {full_median:.4f} vs {train_median:.4f}")

med = train[["age", "pressure_kpa", "humidity_pct"]].median().round(4)
check("C train median age", float(med["age"]), 6.4861)
check("C train median pressure_kpa", float(med["pressure_kpa"]), 314.3376)
check("C train median humidity_pct", float(med["humidity_pct"]), 45.7531)

lo, hi = train["thickness_mm"].quantile([0.01, 0.99])
check("C clip lo (1st pct)", round(float(lo), 4), 1.5743)
check("C clip hi (99th pct)", round(float(hi), 4), 2.1827)

df[["age", "pressure_kpa", "humidity_pct"]] = (
    df[["age", "pressure_kpa", "humidity_pct"]].fillna(med))
df["thickness_mm"] = df["thickness_mm"].clip(lo, hi)
check("C missing after impute",
      int(df[["age", "pressure_kpa", "humidity_pct"]].isna().sum().sum()), 0)
check("C thickness max after clip", round(float(df["thickness_mm"].max()), 4), 2.1827)

# imputing pulls the full-data median onto the training median: the demo dies
# if you measure after acting instead of before
check("C post-impute medians collapse (why measure first)",
      round(float(df["age"].median()), 4) == round(train_median, 4), True)

# ============================ Part D ========================================
class DefectDataset(Dataset):
    def __init__(self, df, transform=None):
        self.y = torch.tensor(df["label"].values, dtype=torch.long)
        self.x = torch.tensor(df.drop(columns=["label"]).values.astype("float32"))
        self.transform = transform

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        x = self.x[i]
        if self.transform is not None:
            x = self.transform(x)
        return x, self.y[i]


feat = df.drop(columns=["batch_id", "timestamp"])
ds = DefectDataset(feat)
check("D n features", int(feat.drop(columns=["label"]).shape[1]), 10)
check("D len(ds)", len(ds), 11668)
check("D ds[0] x shape", tuple(ds[0][0].shape), (10,))
check("D ds[0] y dtype", str(ds[0][1].dtype), "torch.int64")

xb, yb = next(iter(DataLoader(ds, batch_size=8)))
check("D batch shape", tuple(xb.shape), (8, 10))

# ============================ Part E ========================================
train_ds = Subset(ds, train_idx)
val_ds = Subset(ds, val_idx)
test_ds = Subset(ds, test_idx)
train_loader = DataLoader(train_ds, batch_size=32, shuffle=True, num_workers=0)
xb2, yb2 = next(iter(train_loader))
check("E train batch shape", tuple(xb2.shape), (32, 10))
check("E train batches", len(train_loader), 256)


def add_noise(x):
    return x + 0.01 * torch.randn_like(x)


ds_aug = DefectDataset(feat, transform=add_noise)
check("E augmented train sample still 1-D", tuple(Subset(ds_aug, train_idx)[0][0].shape), (10,))
check("E untouched val sample is 1-D", tuple(Subset(ds, val_idx)[0][0].shape), (10,))

# ============================ Part F ========================================
y_tr = labels[train_idx]
counts = torch.bincount(y_tr, minlength=5)
check("F train class counts", counts.tolist(), [2771, 2276, 1801, 335, 982])
check("F counts sum", int(counts.sum()), 8165)
check("F rare-class train share", round(float(counts[3] / counts.sum()), 4), 0.0410)

w = (1.0 / counts.float())[y_tr]
sampler = WeightedRandomSampler(weights=w, num_samples=len(w), replacement=True)
balanced = DataLoader(train_ds, batch_size=32, sampler=sampler)
seen = torch.cat([yb for _, yb in balanced])
check("F sampler keeps training size", int(len(seen)), 8165)
# sampling is stochastic and the sampler carries no seed, so assert a band, not a point
rare_share_after = float((seen == 3).double().mean())
check("F sampler lifts the rare class towards 1/5",
      round(rare_share_after, 1), 0.2)

# ============================ summary =======================================
print()
print(f"{ok} checks passed, {fail} failed")
json.dump({"passed": ok, "failed": fail}, open("/tmp/w3_handout_verify.json", "w"))
raise SystemExit(1 if fail else 0)
