# Contributing to AI Application Development

First of all — thank you. This repo exists because open courseware helped its author build this course, and every contribution pays that forward.

## 🎯 What This Repo Needs Most

| Contribution | Where | Impact |
|---|---|---|
| **Typo / broken link / notebook bug fixes** | PR to any file | ⚡ Quick win, always merged fast |
| **Lab notebook solutions or extra exercises** | `labs/week-XX/` | Directly helps students |
| **New week materials** (slides, plans, scripts — EN or CN) | `lectures/`, `lesson-plans/`, … | ⭐ High impact |
| **Teaching feedback** ("my students struggled with X") | [Discussions](https://github.com/klausren/ai-application-development/discussions) | Shapes future weeks |
| **Translations** (the course is EN + CN; other languages welcome) | anywhere | ⭐ High impact |

## 📝 Ground Rules

1. **License compatibility** — by contributing, you agree your work is released under this repo's [CC BY-NC-SA 4.0](LICENSE). Don't submit material you can't license that way.
2. **Respect third-party copyright** — don't commit slides/PDFs from courses without an open license (that's why CS224n PDFs live behind a downloader script, not in git). If in doubt, link instead of bundle. See [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).
3. **Bilingual by default** — new teaching materials should ship in English (the language of instruction); Chinese versions are welcome but optional per file.
4. **Keep the weekly structure** — 90 min lecture + 75 min lab + 15 min quiz. Deviations are fine but document why in the PR.

## 🔧 Mechanics

```bash
git fork & clone
git checkout -b feat/week-05-lab
# make changes
git commit -m "feat(labs): week-05 starter notebook"   # conventional commits preferred
git push origin feat/week-05-lab
# open a PR against main
```

- Small PRs win. One topic per PR.
- Notebooks must run top-to-bottom (`Restart & Run All`) before submitting.
- If you touch `scripts/download_cs224n.sh`, run it once locally and confirm the PDF magic-byte check still passes.

## 💬 Questions?

Open a [Discussion](https://github.com/klausren/ai-application-development/discussions) — teaching questions are first-class citizens here, not noise.
