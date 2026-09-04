#!/usr/bin/env python3
"""Week 1 Lab - Environment Check Script
AI Application Development / AI 应用开发

Run me after installing everything:
    python env-check.py

I will check every package we use this semester.
All green = you are ready. Any RED line = see the Setup Guide FAQ.
"""

import sys

print("=" * 60)
print("  AI Application Development - Week 1 Environment Check")
print("=" * 60)
print(f"Python version : {sys.version.split()[0]}  (need >= 3.10)")
print(f"Interpreter    : {sys.executable}")
print("-" * 60)

checks = [
    # (module name, import name, min version or None)
    ("numpy",        "numpy",       "1.24"),
    ("pandas",       "pandas",      "2.0"),
    ("matplotlib",   "matplotlib",  "3.7"),
    ("seaborn",      "seaborn",     None),
    ("scikit-learn", "sklearn",     "1.3"),
    ("torch",        "torch",       "2.0"),
    ("jupyterlab",   "jupyterlab",  None),
]

fail = 0

def ver_key(v):
    try:
        return tuple(int(x) for x in v.split(".")[:3])
    except ValueError:
        return (0, 0, 0)

for name, mod, minv in checks:
    try:
        m = __import__(mod)
        v = getattr(m, "__version__", "installed")
        if minv and ver_key(v) < ver_key(minv):
            print(f"  [WARN] {name:14} {v}  (recommended >= {minv})")
        else:
            print(f"  [ OK ] {name:14} {v}")
    except ImportError:
        print(f"  [FAIL] {name:14} NOT INSTALLED  ->  pip install {name}")
        fail += 1

print("-" * 60)

# GPU / accelerator check (informational, not required)
try:
    import torch
    if torch.cuda.is_available():
        print(f"  Accelerator   : CUDA GPU ({torch.cuda.get_device_name(0)})")
    elif getattr(torch.backends, "mps", None) and torch.backends.mps.is_available():
        print("  Accelerator   : Apple Silicon MPS (metal performance shaders)")
    else:
        print("  Accelerator   : CPU only - fine for this course's labs")
except ImportError:
    print("  Accelerator   : unknown (torch not installed)")

# tiny functional test - actually trains a model
try:
    from sklearn.datasets import load_iris
    from sklearn.linear_model import LogisticRegression
    X, y = load_iris(return_X_y=True)
    acc = LogisticRegression(max_iter=200).fit(X, y).score(X, y)
    print(f"  Smoke test    : trained LogisticRegression on Iris, acc = {acc:.3f}")
except Exception as e:
    print(f"  Smoke test    : FAILED ({e})")
    fail += 1

print("=" * 60)
if fail == 0:
    print("  ALL CHECKS PASSED - see you in the lab!")
else:
    print(f"  {fail} problem(s) found - check the Setup Guide FAQ,")
    print("  then ask in the class group or office hours.")
print("=" * 60)
