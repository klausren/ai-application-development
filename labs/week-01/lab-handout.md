# Lab 00 · Environment Setup, GPU Verification & Reproducibility
> **AI Application Development (52015CC3BV)** · School of Software (软件学院), Dalian Neusoft University of Information · Week 1 Lab (80 min) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 1 |
| **CU** | CU(1) · Module 1 (W1–4) |
| **Duration** | 80 min lab + 10 min quiz & wrap-up |
| **Module** | 1 · AI Application Development Foundations |
| **Stack** | Python 3.11, conda, PyTorch, Git |
| **Dataset** | None — this lab trains no model |
| **Deliverables** | `check_env.txt`, `seed_demo.py`, `report.md`, `environment.yml`, record repo link |
| **Weight** | Formative: in-class labs (实验 0–13) = 15 marks of the course (this lab is 1/14 of them) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** the six-step AI application pipeline and where the model sits inside it
- **Know** the three pillars of reproducibility: **seed, config, version**
- **Do** create an isolated conda environment and verify PyTorch, its version and its compute device
- **Do** run the same training script twice with a fixed seed and prove the two runs are bit-identical
- **Do** build a personal record repository whose layout you will reuse for the next 15 weeks

## 2. Before You Start · 课前准备

```bash
conda --version
python --version          # 3.10 or 3.11 expected
git --version
```

- [ ] conda (or Miniconda) is installed and `conda --version` prints a version string
- [ ] You can open a terminal in this course folder
- [ ] You have a GitHub account (or a university GitLab account) and can log in from the terminal
- [ ] You have read the Week 1 slides, Part 4 (reproducibility and AI boundaries)

> **If conda is missing** — install Miniconda first, then restart the terminal. Do not try to continue with the system Python; the rest of the term depends on this step.

## 3. Lab Tasks · 实验任务

### Part A — Build the environment and verify the GPU (20 min)

```bash
conda create -n ai-app python=3.11 -y
conda activate ai-app
# CPU-only build (works everywhere):
conda install pytorch torchvision -c pytorch -y
# If you have an NVIDIA GPU, install the CUDA build instead:
# conda install pytorch torchvision pytorch-cuda=12.1 -c pytorch -c nvidia -y
```

Now write `check_env.py` and run it:

```python
import sys, torch, platform

print("python :", sys.version.split()[0])
print("torch  :", torch.__version__)
print("device :", "cuda" if torch.cuda.is_available() else "cpu")
if torch.cuda.is_available():
    print("gpu    :", torch.cuda.get_device_name(0))
    print("vram   :", round(
        torch.cuda.get_device_properties(0).total_memory / 1e9, 2), "GB")
```

```bash
python check_env.py | tee check_env.txt
```

> **Checkpoint A** — `check_env.txt` exists and shows three things: the Python version, the PyTorch version, and the compute device.
> **Pitfall**: `ModuleNotFoundError: No module named 'torch'` almost always means the *kernel or interpreter* is wrong, not that the package is missing. Confirm `which python` points inside your `ai-app` environment before reinstalling anything.

### Part B — Two runs with one seed (15 min)

Create `seed_demo.py`:

```python
import random, numpy as np, torch

def set_seed(s):
    random.seed(s); np.random.seed(s)
    torch.manual_seed(s); torch.cuda.manual_seed_all(s)

def draw(seed=None):
    if seed is not None:
        set_seed(seed)
    return torch.rand(4).tolist()

print("run1 :", draw(42))   # identical to run2
print("run2 :", draw(42))   # <- fixed seed: same
print("no-seed:", draw())   # <- unfixed: random
```

```bash
python seed_demo.py | tee -a check_env.txt
```

> **Checkpoint B** — `run1` and `run2` must match **bit for bit**. Paste the three real lines into your report. Do not edit them by hand; if they differ, find the unfixed random source and say so.

### Part C — Break it on purpose (10 min)

Remove the two `draw(42)` seeds — call `draw()` three times instead — and run again.

> **Checkpoint C** — record what changes. Then answer, in your own words and in two or three sentences: *why does this course require a fixed seed?* Use the difference you actually measured. Copying the slide wording earns nothing.

### Part D — Export and version the environment (10 min)

```bash
conda env export --no-builds > environment.yml
conda list | grep -E "torch|numpy|python" > packages.txt
```

> **Checkpoint D** — `environment.yml` exists and its `torch` line matches the version printed in Part A. A classmate must be able to rebuild your environment from this file.

### Part E — Build the record repository (15 min)

```bash
mkdir ai-course-labs && cd ai-course-labs
git init && git branch -M main
printf '__pycache__/\n.ipynb_checkpoints/\n.DS_Store\n' > .gitignore
mkdir -p w01-lab0
cp ../check_env.py ../check_env.txt ../seed_demo.py ../environment.yml w01-lab0/
```

Write the `README.md` for the repo (course code, your name, the directory convention, the naming rule) and the first record:

```
ai-course-labs/
├── README.md          # course info, layout, naming rules
├── environment.yml    # environment snapshot (conda export)
├── w01-lab0/
│   ├── check_env.txt  # self-check output
│   ├── seed_demo.py
│   └── report.md      # three outputs + your conclusion
├── w02-lab1/          # one directory per week, same pattern
└── AI_USE.md          # term-long AI trace, numbered #01 #02 ...
```

```bash
git add . && git commit -m "feat(w01): lab 0 environment, seed experiment and record repo"
git remote add origin https://github.com/<you>/ai-course-labs.git
git push -u origin main
```

> **Checkpoint E** — `git log --oneline` shows your commit, `git status` is clean, and the repo is reachable by URL.
> **Pitfall**: GitHub rejects account passwords over HTTPS. If prompted for a password, use a Personal Access Token. Also: a `.gitignore` added *after* the first commit has already failed at its job.

### Part F — Capstone milestone · 大作业里程碑 (10 min)

> **M1 · Three topic proposals + `PROJECT_PLAN.md` + `DEVLOG.md` v0** — see [`projects/capstone/milestones.md`](../../projects/capstone/milestones.md).

**Apply this week's skill:** you just built an environment and a Git repository. Use them for the project itself — **the capstone is an individual project**, one repo per student, with a first commit today.

**Push to your project repo before the lab ends:**

- Create the project repo (public, your own account as the sole owner and contributor).
- Write `PROJECT_PLAN.md` with your weekly working slot, the scope (MVP vs stretch), three risks and a cut list.
- Write **three** topic proposals in `proposals/01.md` … `03.md`: the problem and its user, where the data comes from, a dumb baseline you expect to beat, and the biggest risk.
- Add a stub `DEVLOG.md` — one entry per week from W1 onward. Start the habit while there is almost nothing to write.

> **Checkpoint F** — the repo exists with at least one commit, three genuinely different proposals (not one idea written three times), and a plan with a realistic weekly slot and a cut list.
> **Pitfall**: a milestone pushed next week is a milestone you did not do. Late = −2 project points, each time, up to −20.

## 4. Deliverables Checklist · 交付清单

- [ ] `check_env.txt` — Python version, PyTorch version, device, and (if present) GPU name and VRAM
- [ ] `seed_demo.py` plus the three **real** output lines (`run1`, `run2`, `no-seed`)
- [ ] `report.md` — your own 2–3 sentence conclusion on why the seed must be fixed
- [ ] `environment.yml` committed, with a `torch` version matching Part A
- [ ] Record repository pushed with **≥ 2 meaningful commits** and a README describing the layout
- [ ] `AI_USE.md` started with at least one entry (see Part E layout)
- [ ] Capstone M1 pushed: `PROJECT_PLAN.md`, `proposals/01–03.md`, `DEVLOG.md` v0

## 5. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Environment verified (Part A) | 20 | version table + device result present, `environment.yml` consistent with it |
| Seed experiment (Parts B–C) | 25 | `run1` and `run2` bit-identical, the no-seed run genuinely differs, outputs are real |
| Written conclusion (Part C) | 20 | explains the *necessity* of the seed using the measured difference; no copied slide text |
| Record repository (Part E) | 20 | clean layout, README with the naming rule, ≥ 2 commits, `.gitignore` present from the start |
| AI collaboration trace | 15 | at least one entry stating **where the AI was wrong** and how you found it |

Late policy: −10% per day, max 3 days, then 0.

*Part F (the capstone milestone) is not scored here — it is graded under the Capstone Project. Missing it costs −2 project points there.*

## 6. Submission · 提交方式

Paste **two** things into the LMS box:

1. the record-repository URL, and
2. the commit hash of your Lab 00 commit.

```bash
git add .
git commit -m "feat(w01): lab 0 complete"
git push origin main
git log --oneline -1        # copy this hash
```

**A commit hash counts as your timestamp**, not the LMS upload time.

## 7. Exit Ticket · 课后反思 (answer in the last Markdown cell or at the end of `report.md`)

1. What was the single most surprising thing you observed today?
2. Which step would you do differently next time, and why?
3. One question you still have (the instructor reads these and answers the best ones next week).

## 8. 中文摘要

本实验是全学期唯一一次「不训练模型」的实验，但它决定后面 15 周是否顺利。四个任务：搭环境 → 验 GPU → 固定种子跑两次 → 建记录仓库。

三个必须理解的点：
1. **环境要隔离**：一个项目一个 conda 环境，`environment.yml` 入库，换机器能重建。
2. **可复现性三要素**：固定种子、集中配置、版本管理。缺一项，结果就无法被追溯，别人（包括三天后的你自己）复算不出来。
3. **Git 提交就是时间戳**——截止以 commit 为准，不是以平台上传时间为准；记录仓库的目录与命名从第一周就固定。

常见翻车点：kernel / 解释器选错（表现为 `import torch` 报错，其实是装的在别的环境里）；GitHub 推送用密码被拒（要用 PAT）；`.gitignore` 在第一次 commit 之后才加（等于没加）；报告里的两次输出是「手打」的而不是真跑出来的。

- [ ] **Capstone milestone M1** pushed to the project repo (Part F — graded under the Capstone, not this lab)
