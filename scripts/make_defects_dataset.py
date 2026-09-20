#!/usr/bin/env python
"""Generate data/raw/defects.csv - the Week 3 dataset for course 52015CC3BV.

The file is synthetic but fully reproducible: one fixed seed, no downloads, no
network. It deliberately contains the cleaning traps the Week 3 lab is about,
so that students must find them with a stated criterion instead of by eye:

  1. missing values, concentrated in one class  -> a proxy-feature hint
  2. duplicate rows on the natural key (batch_id, timestamp)
  3. two units mixed inside one column (C and F)
  4. sensor-fault outliers in one column
  5. label noise (~2%), swapped in equal numbers into and out of class 3 so the
     class-3 share stays exactly as designed
  6. a repeated group key: one batch contributes ~10 rows, so a plain random
     split puts near-duplicates on both sides of the line

Run:
    python scripts/make_defects_dataset.py

Outputs:
    data/raw/defects.csv            the dataset handed to students
    outputs/w3_dataset_facts.json   measured facts every document quotes
"""

from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parent.parent
OUT_CSV = ROOT / "data" / "raw" / "defects.csv"
OUT_FACTS = ROOT / "outputs" / "w3_dataset_facts.json"

SEED = 42
N_ROWS = 12_480
N_DUP = 812                      # duplicate rows on the natural key
N_LABEL_NOISE = 250              # ~2 % of rows carry a wrong label

# class 3 is the rare defect: 512 / 12480 = 4.1026 % -> reported as 4.1 %
CLASS_SHARES = {0: 0.3400, 1: 0.2800, 2: 0.2200, 3: 0.0410, 4: 0.1190}

FEATURES = [
    "age", "temperature_c", "pressure_kpa", "line_speed", "tension_n",
    "thickness_mm", "humidity_pct", "vibration_mm_s",
    "material_code", "operator_shift",
]
COLUMNS = ["batch_id", "timestamp", *FEATURES, "label"]

# per-class offsets: a modest, learnable signal - data sets the ceiling
CLASS_SIGNAL = {
    0: dict(temperature_c=0.0, pressure_kpa=0.0, tension_n=0.0,
            thickness_mm=0.0, vibration_mm_s=0.0),
    1: dict(temperature_c=7.5, pressure_kpa=14.0, tension_n=-9.0,
            thickness_mm=0.05, vibration_mm_s=0.35),
    2: dict(temperature_c=-6.0, pressure_kpa=-18.0, tension_n=11.0,
            thickness_mm=-0.04, vibration_mm_s=-0.25),
    3: dict(temperature_c=14.0, pressure_kpa=27.0, tension_n=-16.0,
            thickness_mm=0.11, vibration_mm_s=0.80),
    4: dict(temperature_c=-3.0, pressure_kpa=8.0, tension_n=6.0,
            thickness_mm=-0.02, vibration_mm_s=0.15),
}

BASE = dict(
    age=(6.5, 3.2),
    temperature_c=(78.0, 6.0),
    pressure_kpa=(312.0, 24.0),
    line_speed=(42.0, 5.0),
    tension_n=(121.0, 18.0),
    thickness_mm=(1.86, 0.12),
    humidity_pct=(46.0, 9.0),
    vibration_mm_s=(3.2, 0.9),
)

MATERIAL_CODES = ["A1", "A2", "B1", "B2", "C1"]
# how a code is written when it is written the wrong way
CODE_VARIANTS = {"A1": "a1", "A2": "A-2", "B1": "b1", "B2": "B-2", "C1": "c1"}


def class_counts() -> dict[int, int]:
    """Integer class counts that sum exactly to N_ROWS."""
    counts = {c: int(round(N_ROWS * s)) for c, s in CLASS_SHARES.items()}
    drift = N_ROWS - sum(counts.values())
    counts[0] += drift                     # absorb rounding in the largest class
    assert sum(counts.values()) == N_ROWS
    return counts


def main() -> None:
    rng = np.random.default_rng(SEED)
    counts = class_counts()

    labels = np.concatenate(
        [np.full(n, c, dtype=np.int64) for c, n in sorted(counts.items())]
    )
    rng.shuffle(labels)

    # ---------------- 5. label noise: balanced in and out of class 3 ----------
    # so the class-3 share is untouched by the noise we inject
    rare = np.flatnonzero(labels == 3)
    other = np.flatnonzero(labels != 3)
    k = N_LABEL_NOISE // 2
    out_idx = rng.choice(rare, size=k, replace=False)
    in_idx = rng.choice(other, size=k, replace=False)
    noise_idx = np.concatenate([out_idx, in_idx])
    labels[out_idx] = rng.choice([0, 1, 2, 4], size=k)
    labels[in_idx] = 3
    assert (labels == 3).sum() == counts[3], "class-3 share must stay as designed"

    df = pd.DataFrame({"label": labels})

    # ---------------- continuous features -------------------------------------
    for name, (mu, sd) in BASE.items():
        col = rng.normal(mu, sd, size=N_ROWS)
        shift = np.array([CLASS_SIGNAL[int(l)].get(name, 0.0) for l in labels])
        df[name] = col + shift
    df["age"] = np.clip(df["age"], 0.5, 24.0)
    df["humidity_pct"] = np.clip(df["humidity_pct"], 12.0, 88.0)

    # ---------------- categorical features ------------------------------------
    df["material_code"] = rng.choice(MATERIAL_CODES, size=N_ROWS)
    df["operator_shift"] = rng.integers(1, 4, size=N_ROWS)

    # ---------------- 6. group key: ~10 rows per production batch -------------
    n_rows_per_batch = 10
    n_batches = int(np.ceil(N_ROWS / n_rows_per_batch))
    batch_ids = np.repeat(
        [f"B{b:03d}" for b in range(n_batches)], n_rows_per_batch
    )[:N_ROWS]
    df["batch_id"] = batch_ids
    start = np.datetime64("2026-06-01T06:00:00")
    offsets = rng.integers(0, 60 * 24 * 60, size=N_ROWS)      # within ~60 days
    df["timestamp"] = (start + offsets.astype("timedelta64[m]")).astype(str)
    df = df[COLUMNS]

    # ---------------- 2. duplicates on (batch_id, timestamp) -----------------
    # a duplicate copies another row of the SAME class, which is how a double
    # entry happens in practice - and it leaves the class shares intact.
    # Within each class, targets and sources come from disjoint halves of a
    # permutation, so every copied key appears exactly twice and no source is
    # ever overwritten: the duplicate count is exact, not luck.
    dup_by_class: dict[int, int] = {}
    remaining = N_DUP
    ordered = sorted(counts)
    for i, cls in enumerate(ordered):
        if i == len(ordered) - 1:
            dup_by_class[cls] = remaining
        else:
            n = int(round(N_DUP * counts[cls] / N_ROWS))
            dup_by_class[cls] = n
            remaining -= n
    assert sum(dup_by_class.values()) == N_DUP

    for cls, n in dup_by_class.items():
        perm = rng.permutation(np.flatnonzero(labels == cls))
        for tgt, src in zip(perm[:n], perm[n:2 * n]):
            df.iloc[int(tgt)] = df.iloc[int(src)].values

    n_dup_measured = int(df.duplicated(subset=["batch_id", "timestamp"]).sum())
    assert n_dup_measured == N_DUP, f"expected {N_DUP} dups, got {n_dup_measured}"

    # ---------------- 3. one column, two units --------------------------------
    n_unit_rows = int(round(0.08 * N_ROWS))         # 8 % recorded in Fahrenheit
    unit_idx = rng.choice(N_ROWS, size=n_unit_rows, replace=False)
    df.loc[unit_idx, "temperature_c"] = (
        df.loc[unit_idx, "temperature_c"] * 9 / 5 + 32
    )

    # ---------------- 4. sensor-fault outliers --------------------------------
    n_outlier_rows = int(round(0.003 * N_ROWS))     # 0.3 % stuck high
    outlier_idx = rng.choice(N_ROWS, size=n_outlier_rows, replace=False)
    df.loc[outlier_idx, "thickness_mm"] = (
        df.loc[outlier_idx, "thickness_mm"] * 40.0
    )

    # ---------------- coding inconsistency ------------------------------------
    n_variant_rows = int(round(0.06 * N_ROWS))
    variant_idx = rng.choice(N_ROWS, size=n_variant_rows, replace=False)
    df.loc[variant_idx, "material_code"] = [
        CODE_VARIANTS[c] for c in df.loc[variant_idx, "material_code"]
    ]

    # ---------------- 1. missing values, concentrated in class 3 --------------
    age_missing = np.zeros(N_ROWS, dtype=bool)
    for cls, rate in ((3, 0.25), (0, 0.0227), (1, 0.0227), (2, 0.0227), (4, 0.0227)):
        pool = np.flatnonzero(labels == cls)
        take = rng.choice(pool, size=int(round(len(pool) * rate)), replace=False)
        age_missing[take] = True
    df.loc[age_missing, "age"] = np.nan

    for name, rate in (("pressure_kpa", 0.011), ("humidity_pct", 0.006)):
        pool = rng.choice(N_ROWS, size=int(round(rate * N_ROWS)), replace=False)
        df.loc[pool, name] = np.nan

    df["label"] = df["label"].astype(int)

    # ---------------- facts every document quotes -----------------------------
    shares = df["label"].value_counts(normalize=True).sort_index()
    missing = {
        col: {
            "n": int(df[col].isna().sum()),
            "rate": round(float(df[col].isna().mean()), 4),
        }
        for col in df.columns
        if df[col].isna().any()
    }
    by_class = (
        df.assign(age_missing=df["age"].isna())
        .groupby("label")["age_missing"].mean().round(4).to_dict()
    )
    facts = {
        "seed": SEED,
        "counts_are_over": (
            "the raw table, duplicates included. After de-duplication the same "
            "defects shrink - see outputs/w3_reference_run.json: 935 unit rows, "
            "35 outlier rows. Both numbers are correct; they just describe "
            "different stages of the pipeline."
        ),
        "raw_rows": int(len(df)),
        "raw_cols": int(df.shape[1]),
        "columns": COLUMNS,
        "features": len(FEATURES),
        "feature_names": FEATURES,
        "classes": int(df["label"].nunique()),
        "class_counts": {int(k): int(v) for k, v in
                         df["label"].value_counts().sort_index().items()},
        "class_shares": {int(k): round(float(v), 4) for k, v in shares.items()},
        "rare_class": 3,
        "rare_class_share_pct": round(float(shares[3]) * 100, 1),
        "duplicate_rows_on_key": n_dup_measured,
        "duplicate_key": ["batch_id", "timestamp"],
        "unique_rows": int(len(df) - n_dup_measured),
        "missing": missing,
        "age_missing_rate_by_class": {int(k): float(v) for k, v in by_class.items()},
        "unit_mixed": {"column": "temperature_c", "rows": int(n_unit_rows),
                       "unit": "F mixed into C",
                       "max_after_mix": round(float(df["temperature_c"].max()), 2)},
        "outliers": {"column": "thickness_mm", "rows": int(n_outlier_rows),
                     "criterion": "> 5 mm (about 3 sigma x 40)",
                     "max": round(float(df["thickness_mm"].max()), 2)},
        "code_inconsistency": {"column": "material_code", "rows": int(n_variant_rows),
                               "variants": CODE_VARIANTS},
        "label_noise_rows": int(N_LABEL_NOISE),
        "rows_per_batch_mean": round(N_ROWS / n_batches, 2),
        "n_batches": int(n_batches),
        "plain_random_split_leak": (
            "one batch contributes ~10 rows, so a random split puts "
            "near-duplicates in both train and test"
        ),
    }

    OUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUT_CSV, index=False)
    OUT_FACTS.parent.mkdir(parents=True, exist_ok=True)
    OUT_FACTS.write_text(json.dumps(facts, indent=2, ensure_ascii=False) + "\n")

    print(f"wrote {OUT_CSV}  ({OUT_CSV.stat().st_size/1024:.0f} KB)")
    print(f"wrote {OUT_FACTS}")
    print()
    print(f"shape                {df.shape}")
    print(f"features             {len(FEATURES)}")
    print(f"class shares         {[f'{k}:{v:.4f}' for k, v in shares.items()]}")
    print(f"rare class 3         {shares[3]*100:.1f} %  ({int((df['label']==3).sum())} rows)")
    print(f"duplicates on key    {n_dup_measured}")
    print(f"unique rows          {facts['unique_rows']}")
    print(f"missing              { {k: v['rate'] for k, v in missing.items()} }")
    print(f"age missing by class {facts['age_missing_rate_by_class']}")
    print(f"unit-mixed rows      {n_unit_rows}   max temp after mix {facts['unit_mixed']['max_after_mix']}")
    print(f"outlier rows         {n_outlier_rows}   max thickness {facts['outliers']['max']}")
    print(f"code variants        {n_variant_rows}")
    print(f"label noise rows     {N_LABEL_NOISE}")


if __name__ == "__main__":
    main()
