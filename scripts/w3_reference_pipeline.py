#!/usr/bin/env python
"""Reference run of the Week 3 lab pipeline, cleaning drill included.

This is the single source of truth for every number the Week 3 documents quote:
the split sizes after cleaning, the training-only medians and percentiles, the
class counts, and the shapes the handout asserts.

Run:
    python scripts/w3_reference_pipeline.py

Outputs:
    outputs/w3_reference_run.json
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd
import torch
from torch.utils.data import DataLoader, Dataset, Subset

ROOT = Path(__file__).resolve().parent.parent
CSV = ROOT / "data" / "raw" / "defects.csv"
OUT = ROOT / "outputs" / "w3_reference_run.json"

SEED = 42
VAL_FRAC = TEST_FRAC = 0.15
TEMP_C_MAX_PLAUSIBLE = 120.0          # above this the row was recorded in F
THICKNESS_PLAUSIBLE_MAX = 5.0         # above this the sensor faulted


class DefectDataset(Dataset):
    """DataFrame -> PyTorch dataset: two methods only."""

    def __init__(self, x: np.ndarray, y: np.ndarray, transform=None):
        self.x = torch.tensor(x, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.long)
        self.transform = transform

    def __len__(self):
        return len(self.y)

    def __getitem__(self, i):
        x = self.x[i]
        if self.transform is not None:
            x = self.transform(x)
        return x, self.y[i]


def stratified_split(labels: np.ndarray, seed: int):
    g = torch.Generator().manual_seed(seed)
    y = torch.tensor(labels, dtype=torch.long)
    idx = torch.arange(len(y))
    parts = []
    for cls in y.unique().tolist():
        c = idx[y == cls]
        c = c[torch.randperm(len(c), generator=g)]
        n_tr = int(len(c) * (1 - VAL_FRAC - TEST_FRAC))
        n_va = int(len(c) * VAL_FRAC)
        parts.append((c[:n_tr], c[n_tr:n_tr + n_va], c[n_tr + n_va:]))
    return (torch.cat([p[0] for p in parts]).numpy(),
            torch.cat([p[1] for p in parts]).numpy(),
            torch.cat([p[2] for p in parts]).numpy())


def leakage_contrast(df: pd.DataFrame, train_idx: np.ndarray, test_idx: np.ndarray,
                     labels: np.ndarray) -> dict:
    """How visible is a full-data statistic compared with a training-only one?

    The honest answer on this dataset is 'barely visible', and that is the
    lesson: leakage does not announce itself. We measure the gap so the deck
    can quote it instead of asserting it.
    """
    tr = df.iloc[train_idx]
    out: dict = {"full_vs_train": {}, "rare_class_3": {}, "test_set_trace": {}}

    for col in ("age", "pressure_kpa", "humidity_pct", "thickness_mm"):
        full, train = df[col], tr[col]
        out["full_vs_train"][col] = {
            "median": {"full": round(float(full.median()), 4),
                       "train": round(float(train.median()), 4)},
            "mean": {"full": round(float(full.mean()), 4),
                     "train": round(float(train.mean()), 4)},
            "p99": {"full": round(float(full.quantile(0.99)), 4),
                    "train": round(float(train.quantile(0.99)), 4)},
        }
        for stat in ("median", "mean", "p99"):
            a, b = out["full_vs_train"][col][stat]["full"], out["full_vs_train"][col][stat]["train"]
            out["full_vs_train"][col][stat]["rel_pct"] = (
                round(abs(a - b) / abs(b) * 100, 3) if b else 0.0)

    # the same comparison, restricted to the rare class: fewer rows, bigger drift
    rare = df[df["label"] == 3]
    rare_train_idx = train_idx[labels[train_idx] == 3]
    for col in ("age", "tension_n", "vibration_mm_s"):
        full_med = float(rare[col].median())
        train_med = float(rare.loc[rare_train_idx, col].median())
        full_mean = float(rare[col].mean())
        train_mean = float(rare.loc[rare_train_idx, col].mean())
        out["rare_class_3"][col] = {
            "n_full": int(len(rare)), "n_train": int(len(rare_train_idx)),
            "median_full": round(full_med, 4), "median_train": round(train_med, 4),
            "median_rel_pct": round(abs(full_med - train_med) / abs(train_med) * 100, 3),
            "mean_full": round(full_mean, 4), "mean_train": round(train_mean, 4),
            "mean_rel_pct": round(abs(full_mean - train_mean) / abs(train_mean) * 100, 3),
        }

    # standardising with full-data statistics moves the test set closer to zero
    for col in ("age", "pressure_kpa", "temperature_c"):
        x = df[col].astype(float)
        trv, tev = x.iloc[train_idx], x.iloc[test_idx]
        z_train = float(((tev - trv.mean()) / trv.std()).mean())
        z_full = float(((x - x.mean()) / x.std()).iloc[test_idx].mean())
        out["test_set_trace"][col] = {
            "train_scaled_mean": round(z_train, 5),
            "full_scaled_mean": round(z_full, 5),
        }
    return out


def main() -> None:
    facts: dict = {"seed": SEED}

    df = pd.read_csv(CSV)
    facts["raw_shape"] = list(df.shape)
    facts["raw_class_counts"] = {int(k): int(v) for k, v in
                                 df["label"].value_counts().sort_index().items()}
    facts["raw_dup_on_key"] = int(
        df.duplicated(subset=["batch_id", "timestamp"]).sum())

    # ---------- clean 1: de-duplicate (no statistic needed) -------------------
    n_before = len(df)
    df = df.drop_duplicates(subset=["batch_id", "timestamp"], keep="first").reset_index(drop=True)
    facts["dedup_rows_removed"] = n_before - len(df)
    facts["shape_after_dedup"] = list(df.shape)

    # ---------- clean 2: unify the unit (domain rule, not a statistic) --------
    mask_f = df["temperature_c"] > TEMP_C_MAX_PLAUSIBLE
    facts["unit_rows_fixed"] = int(mask_f.sum())
    facts["temperature_max_before_unify"] = round(float(df["temperature_c"].max()), 2)
    df.loc[mask_f, "temperature_c"] = (
        df.loc[mask_f, "temperature_c"] - 32.0) * 5.0 / 9.0
    facts["temperature_max_after_unify"] = round(float(df["temperature_c"].max()), 2)

    # ---------- clean 3: unify the category coding ----------------------------
    codes_before = sorted(df["material_code"].unique().tolist())
    facts["material_codes_before"] = codes_before
    df["material_code"] = df["material_code"].str.upper().str.replace("-", "", regex=False)
    facts["material_codes_after"] = sorted(df["material_code"].unique().tolist())

    # ... then encode it: a string column makes `astype("float32")` fail outright
    code_map = {c: i for i, c in enumerate(facts["material_codes_after"])}
    facts["material_code_map"] = code_map
    df["material_code"] = df["material_code"].map(code_map).astype("int64")

    facts["shape_before_split"] = list(df.shape)

    # ---------- split (must come before anything that learns) ----------------
    labels = df["label"].values
    train_idx, val_idx, test_idx = stratified_split(labels, SEED)
    facts["split_sizes"] = {
        "train": int(len(train_idx)), "val": int(len(val_idx)),
        "test": int(len(test_idx)),
    }

    def shares(index: np.ndarray) -> dict:
        s = pd.Series(labels[index]).value_counts(normalize=True).sort_index()
        return {int(k): round(float(v), 4) for k, v in s.items()}

    facts["split_class_shares"] = {
        "train": shares(train_idx), "val": shares(val_idx), "test": shares(test_idx),
    }
    facts["rare_class_train_count"] = int((labels[train_idx] == 3).sum())

    # how visible the leak would be - measured here, quoted by the deck
    facts["leakage_contrast"] = leakage_contrast(df, train_idx, test_idx, labels)

    # ---------- clean 4: statistics that must be TRAINING-ONLY ---------------
    tr = df.iloc[train_idx]
    medians = {c: round(float(tr[c].median()), 4)
               for c in ("age", "pressure_kpa", "humidity_pct")}
    facts["train_medians"] = medians
    facts["missing_before_impute"] = {
        c: int(df[c].isna().sum()) for c in ("age", "pressure_kpa", "humidity_pct")}

    lo = float(tr["thickness_mm"].quantile(0.01))
    hi = float(tr["thickness_mm"].quantile(0.99))
    facts["train_thickness_clip"] = {"lo": round(lo, 4), "hi": round(hi, 4)}
    facts["outlier_rows_clipped"] = int((df["thickness_mm"] > THICKNESS_PLAUSIBLE_MAX).sum())

    # a full-data median would be leakage: record both so the deck can compare
    facts["full_data_medians_would_be"] = {
        c: round(float(df[c].median()), 4)
        for c in ("age", "pressure_kpa", "humidity_pct")}

    for c, v in medians.items():
        df[c] = df[c].fillna(v)
    df["thickness_mm"] = df["thickness_mm"].clip(lo, hi)
    facts["missing_after_impute"] = int(df[["age", "pressure_kpa", "humidity_pct"]].isna().sum().sum())
    facts["thickness_max_after_clip"] = round(float(df["thickness_mm"].max()), 4)

    # ---------- Dataset / DataLoader -----------------------------------------
    feat = df.drop(columns=["batch_id", "timestamp", "label"])
    facts["feature_columns"] = list(feat.columns)
    facts["n_features"] = int(feat.shape[1])
    assert feat.shape[1] == 10, feat.shape

    ds = DefectDataset(feat.values.astype("float32"), df["label"].values)
    facts["len_ds"] = len(ds)
    facts["ds0_x_shape"] = list(ds[0][0].shape)
    facts["ds0_y_dtype"] = str(ds[0][1].dtype)

    train_loader = DataLoader(Subset(ds, train_idx), batch_size=8, shuffle=True)
    xb, yb = next(iter(train_loader))
    facts["batch_shape"] = list(xb.shape)
    facts["batch_label_shape"] = list(yb.shape)

    counts = torch.bincount(torch.tensor(labels[train_idx]), minlength=5)
    facts["train_class_counts"] = [int(v) for v in counts.tolist()]
    facts["train_class_shares"] = [round(float(v), 4) for v in
                                   (counts / counts.sum()).tolist()]
    weights = (1.0 / counts.float())
    facts["balanced_weights"] = [round(float(v), 6) for v in weights.tolist()]

    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(facts, indent=2, ensure_ascii=False) + "\n")

    print(f"wrote {OUT}\n")
    print(f"raw shape                 {facts['raw_shape']}")
    print(f"dedup removed             {facts['dedup_rows_removed']}  -> {facts['shape_after_dedup']}")
    print(f"unit rows fixed           {facts['unit_rows_fixed']}  "
          f"max {facts['temperature_max_before_unify']} -> {facts['temperature_max_after_unify']}")
    print(f"codes  {facts['material_codes_before']} -> {facts['material_codes_after']}")
    print(f"split                     {facts['split_sizes']}")
    print(f"train class counts        {facts['train_class_counts']}")
    print(f"train medians (training)  {facts['train_medians']}")
    print(f"full-data medians         {facts['full_data_medians_would_be']}   <-- what leakage looks like")
    print(f"clip from training        1%={facts['train_thickness_clip']['lo']}  "
          f"99%={facts['train_thickness_clip']['hi']}   clipped {facts['outlier_rows_clipped']} rows")
    print(f"missing after impute      {facts['missing_after_impute']}")
    print(f"n_features                {facts['n_features']}")
    print(f"len(ds) {facts['len_ds']}   ds[0] x {facts['ds0_x_shape']} y {facts['ds0_y_dtype']}")
    print(f"batch shape               {facts['batch_shape']}")
    print(f"balanced weights          {facts['balanced_weights']}")


if __name__ == "__main__":
    main()
