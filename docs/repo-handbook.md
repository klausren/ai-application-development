# Git Repository Handbook · 仓库使用手册

> **AI Application Development · 52015CC3BV** · School of Software (软件学院), Dalian Neusoft University of Information
> Individual work — one repository per student · 个人独立完成，一人一套仓库
> Updated 2026-10-09

---

## 0. The short version · 一句话版

| | |
|---|---|
| **Where do I submit?** 交到哪里 | Push to **GitHub**. There is nothing to upload anywhere else. ／ 推到 **GitHub** 就算交了，不需要再上传到任何平台。 |
| **What counts as "on time"?** 什么算按时 | The **commit hash**, once pushed. ／ 以**推送上去的 commit hash** 为准。 |
| **How many repos?** 几个仓库 | **Two** — one for lab records, one for your capstone project. ／ **两个**：一个记实验，一个放大作业。 |
| **Do I need to add the instructor?** 要加老师吗 | Not if both repos are public. `klausren` if you make them private. ／ 两个仓库都是公开的就不用；设为私有则加 `klausren`。 |

---

## 1. You have two repositories · 你有两个仓库

**English.** They do different jobs and have different layouts. Do not merge them into one —
the lab folder is a weekly record, the project repo is a growing product.

**中文。** 两个仓库用途不同、结构不同，**不要合并**。记录仓库是「每周交一次」的流水账，
项目仓库是「一直长大」的产品。

| | **Record repo** 记录仓库 | **Project repo** 项目仓库 |
|---|---|---|
| **Purpose** 用途 | Lab records — one folder per week 每周实验记录 | Your capstone, built over W6–W16 大作业项目 |
| **Repository name** 仓库名 | **`ai-course-labs`** *(fixed — do not rename)* | `<student-id>-ai-app` *(suggested)* |
| **Visibility** 可见性 | Public *(recommended)* | **Public** *(required)* |
| **One folder per week** 每周目录 | `w01-lab0/`, `w02-lab1/` … `w05-lab4/` | not applicable 不适用 |
| **Graded as** 计入 | 随堂实验 15 分 (with attendance and reviews) | 终结性 50 分 (individual project) |
| **Collected** 收集方式 | From your repo, every lab 每次实验课从仓库收 | Weekly standup + `git log` 每周站会读 `git log` |

> ⚠️ **One repo per person.** There is no group repository. Three students, three separate
> repositories — you may discuss ideas, but every line you commit must be your own.
> ／ **一人一套仓库，没有小组仓库。** 全班三个人就是三套独立仓库。可以讨论思路，
> 但**你提交的每一行都必须是你自己的**。

---

## 2. One-time setup · 一次性设置

You should already have done this in Week 1 (Lab 00). If you are on a new machine, redo it.

### 2.1 Tell Git who you are · 让 Git 知道你是谁

```bash
git config --global user.name  "Your Name"
git config --global user.email "you@university.edu"   # the SAME email as your GitHub account
git config --global init.defaultBranch main
git config --global --list                            # verify
```

**English.** Skipping this makes your very first commit fail with `*** Please tell me who you are`.
Use the same email as your GitHub account — that is what links commits to your profile.

**中文。** 不配这个，第一次提交就会报 `*** Please tell me who you are`。
**邮箱必须和 GitHub 账号一致**，否则提交不会算到你名下。

### 2.2 Authenticate · 配置推送凭证

**English.** GitHub no longer accepts your account password in the terminal. Pick one:

- **Easiest:** install **GitHub Desktop** and sign in — it handles credentials for you.
- **Or** create a **Personal Access Token**: GitHub → Settings → Developer settings →
  Personal access tokens → Tokens (classic) → Generate new token → tick **`repo`** →
  copy it once and **use it as the password** when Git asks.

**中文。** GitHub 已不接受账号密码。二选一：装 **GitHub Desktop** 登录（最省事）；
或建 **Personal Access Token**（勾 `repo` 权限），推送时**当密码用**。Token 只显示一次，记得存好。

### 2.3 Make sure the instructor can see the repo · 确保老师能看到仓库

**English.** The project repo is **public by design** — anyone with the URL can read it, so
nothing else is needed. If you prefer a **private** repo, you must invite the instructor:

> Repo → **Settings** → **Collaborators** → *Add people* → **`klausren`**

**中文。** 项目仓库按规定是**公开的**，有链接就能看，不需要额外操作。
如果你坚持用**私有仓库**，必须邀请老师：**Settings → Collaborators → 添加 `klausren`**。

---

## 3. The weekly workflow · 每周工作流

Five steps. The last one **is** your submission.

```bash
cd ai-course-labs                 # 1. go to your record repo 进入记录仓库
git pull                          # 2. pick up anything you pushed from elsewhere 先拉一下
mkdir -p w05-lab4                 # 3. this week's folder 建本周目录
#    ... do the lab, save your files into w05-lab4/ ... 做实验，文件存进该目录
git status                        # 4. see exactly what is about to be committed 看清楚要提交什么
git add w05-lab4/                 # 5. stage it 暂存
git commit -m "feat(w05): lab 4 training loop and 3x3 optimizer x lr grid"
git push origin main              # 6. PUSH — this is the submission 推送＝提交
git log --oneline -1              # 7. copy this hash for the standup 复制这行 hash 用于站会
```

**English.** Run `git status` every time before `git add`. It is the only way to notice the
things you did *not* mean to commit — `__pycache__/`, `.ipynb_checkpoints/`, a 200 MB dataset.

**中文。** **每次 `git add` 前都跑一次 `git status`。** 这是你发现"本来不想提交的东西"
（`__pycache__/`、`.ipynb_checkpoints/`、一个 200MB 的数据集）的唯一机会。

---

## 4. What goes where · 目录结构

### 4.1 Record repo · 记录仓库

```
ai-course-labs/
├── README.md            # course code, your name, the layout, the naming rule
├── .gitignore           # from commit #1 — never add it later
├── environment.yml      # environment snapshot (conda export)
├── AI_USE.md            # term-long AI trace, numbered #01 #02 #03 ...
├── w01-lab0/            # one folder per week, same pattern every time
│   ├── check_env.txt
│   ├── seed_demo.py
│   └── report.md
├── w02-lab1/
├── w05-lab4/            # ← this week
│   ├── lab-05.ipynb
│   ├── train_sweep.py
│   ├── grid_results.json
│   └── curves.png
└── ...
```

### 4.2 Project repo · 项目仓库

Required minimum — the grader looks for these exact paths.

```
<student-id>-ai-app/
├── README.md            # what it does, how to run it, what the numbers are
├── requirements.txt     # or environment.yml — pinned versions
├── PROJECT_PLAN.md      # weekly slot, scope, cut list, biggest risk
├── proposals/01.md …    # three real candidate topics
├── DATA.md              # provenance, licence, size, splits, known flaws
├── MODEL_CARD.md        # intended use, metrics, limitations, failure modes
├── DEVLOG.md            # one entry per week, W6 onward
├── RETROSPECTIVE.md     # W16
├── AI_USE.md            # which AI tools, used for what
├── src/
│   ├── data/            # loading, cleaning, splitting
│   ├── models/          # training, evaluation
│   └── app/             # serving (or predict.py at the root)
├── tests/               # at minimum: data tests + one model smoke test
├── experiments/         # tracked runs, ablation results
└── Dockerfile           # optional (stretch) — but it must build if present
```

> **Reproducibility bar.** The grader will **clone your repo and run the command in your
> README**. If it fails on a clean machine, that is −14 points before anything else is assessed.
> ／ **可复现底线**：老师会**克隆你的仓库、跑你 README 里那条命令**。
> 在干净机器上跑不通，先扣 14 分，再谈其他。

---

## 5. Commit messages · 提交信息规范

**Format · 格式**: `<type>(w<week>): <what changed>`

| Type | Use it for 用于 | Example |
|---|---|---|
| `feat` | a new working thing 新功能跑通 | `feat(w05): lab 4 3x3 optimizer x lr grid` |
| `fix` | a bug fix 修 bug | `fix(w05): add missing optimizer.zero_grad()` |
| `docs` | documentation only 只改文档 | `docs(w05): lab 4 report and README` |
| `exp` | an experiment run 一次实验运行 | `exp(w05): adam lr=1e-3 vs momentum` |
| `refactor` | restructure, same behaviour 重构不改行为 | `refactor(w06): split train.py into modules` |

**English.** Each lab needs **≥ 2 meaningful commits** — one for the work, at least one more
for the fixes and the write-up. A single commit at the end of the night is not a development
record, and the rubric grades the record.

**中文。** 每次实验**至少 2 个有意义的提交**：一个交工作，至少再一个交修正与写作。
最后一晚攒成一个提交，不算开发记录——而评分正是评这个记录。

---

## 6. Deadline and timestamp · 截止与时间戳

**English.**

- **The commit hash is your timestamp.** Not the file's modified time, not "I finished it on
  Sunday but pushed on Thursday."
- **It counts when it reaches GitHub.** A commit sitting on your laptop is invisible.
- **Push first, then leave history alone.** Do not `git commit --amend` or `git rebase` a commit
  you have already pushed — it rewrites the record and the timestamp stops meaning anything.
- **A week with no commit is a week with no progress**, however much work happened locally.

**中文。**

- **commit hash 就是你的时间戳。** 不是文件修改时间，也不是"我周日就做完了，周四才推"。
- **推上 GitHub 才算数。** 躺在你电脑上的提交是看不见的。
- **推完就别动历史。** 已经推上去的提交**不要 `--amend`、不要 `rebase`**，
  那会改写记录，时间戳随即失效。
- **一周没有提交＝一周没有进度**，本地做多少都一样。

| Item 项目 | Rule 规则 |
|---|---|
| Labs 实验 | Due **Monday 23:59** ／ 周一 23:59；late −10%/day, up to 3 days 晚交每天 −10%，最多 3 天 |
| Capstone milestones 里程碑 | Collected **in the lab** 课内收；late −2 pts each, capped at −20 |
| Silence 静默 | **Three consecutive weeks with no commit → a mandatory meeting** 连续三周无提交 → 强制约谈 |

---

## 7. What to submit this week · 本周提交（Week 5 · Lab 4）

**Four files into `w05-lab4/`.**

```bash
git add w05-lab4/
git commit -m "feat(w05): lab 4 training loop and 3x3 optimizer x lr grid"
git push origin main
```

| File | What it is |
|---|---|
| `lab-05.ipynb` | the notebook — must run top-to-bottom after `Restart & Run All` |
| `train_sweep.py` | one command that reproduces every number |
| `grid_results.json` | the nine runs as data — **this is the evidence** |
| `curves.png` | loss and accuracy curves |

> **Due Monday 12 October, 23:59.** No screenshots. A photo of your screen is not a result.
> ／ **10 月 12 日（周一）23:59 截止。不收截图**——拍屏幕不算结果。

> **Naming note.** The official lab number is **实验 4**; the file is called `lab-05.ipynb`
> because the folder follows the *week*. ／ **命名提醒**：官方编号是**实验 4**，
> 文件名却是 `lab-05.ipynb`——因为目录跟的是**周次**。两个号都对。

---

## 8. Never do this · 不要做的事

| Never 不要 | Why 为什么 |
|---|---|
| `git push --force` ／ `git push -f` | Erases commits from GitHub. The record cannot be recovered. ／ 会抹掉 GitHub 上的提交，记录无法恢复。 |
| `--amend` or `rebase` a pushed commit | Rewrites the timestamp. Your "on time" commit becomes invisible. ／ 改写时间戳，按时提交直接失效。 |
| Commit datasets or model weights 提交数据集/权重 | A 200 MB file breaks cloning for everyone, including the grader. Keep them out with `.gitignore`. |
| Commit `.env`, tokens, API keys | Once pushed, treat the key as leaked and rotate it. ／ 推上去就当已泄露，立刻换新的。 |
| Commit `.ipynb_checkpoints/`, `__pycache__/`, `.DS_Store` | Noise in every diff. They belong in `.gitignore` **from commit #1**. |
| Commit code you have not read | "The AI wrote that" scores zero on the defence question and triggers an integrity review. ／ "AI 写的"在答辩里得 0 分，并触发学术诚信审查。 |

---

## 9. Troubleshooting · 排错

| Symptom 现象 | Cause 原因 | Fix 修法 |
|---|---|---|
| `*** Please tell me who you are` | `user.name` / `user.email` not set 没配身份 | Run §2.1 ／ 按 §2.1 配置 |
| `git push` asks for a password and rejects it | GitHub no longer accepts account passwords | Use a Personal Access Token or GitHub Desktop ／ 用 Token 或 GitHub Desktop |
| `fatal: not a git repository` | You are in the wrong folder 不在仓库目录里 | `cd` into the repo first ／ 先 `cd` 进仓库 |
| `! [rejected] ... non-fast-forward` | GitHub has a commit you do not have locally | `git pull --rebase` then `git push` ／ 先拉再推 |
| The instructor cannot open your repo | It is private and you did not invite anyone | Settings → Collaborators → `klausren` ／ 加协作人 |
| `.ipynb_checkpoints/` shows up in `git status` | `.gitignore` added after the first commit | Add it now, then `git rm -r --cached` the folder ／ 补 `.gitignore`，再清缓存 |
| Your commit shows someone else's name | `user.email` differs from your GitHub account | Fix §2.1 and re-commit ／ 按 §2.1 改，重新提交 |

**Still stuck?** Post in the class group with **all three**: (1) your OS and chip,
(2) the exact command you ran, (3) the **full** error text — not a cropped screenshot.

**还没解决？** 在班级群里发**三样**：① 你的系统和芯片 ② 你敲的**原命令** ③ **完整的**报错文本（不要裁剪截图）。

---

## 10. Before you push · 提交前自检

- [ ] `git status` shows **only** the files you mean to commit ／ 只列出了你想提交的文件
- [ ] `git diff --cached` reviewed — no stray debug prints, no secrets ／ 看过 diff，没有调试残留和密钥
- [ ] The notebook runs clean after **Kernel → Restart & Run All** ／ 笔记本能整份跑通
- [ ] `README.md` states the **one command** that reproduces your result ／ README 里写了那条复现命令
- [ ] Commit message follows `<type>(w<week>): ...` ／ 提交信息符合规范
- [ ] **≥ 2 commits** this week ／ 本周至少 2 个提交
- [ ] `git push` succeeded — not just `git commit` ／ **推送成功了**，不是只提交
- [ ] `git log --oneline -1` hash copied for the standup ／ 复制好 hash 用于站会

---

*Questions: bring them to the lab, not to an email the night before the deadline.*
*有问题拿到课上问，别在截止前一晚发邮件。*
