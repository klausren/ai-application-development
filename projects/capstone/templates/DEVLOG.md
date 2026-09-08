# DEVLOG.md · 每周开发日志模板

> One short entry per week, committed alongside the milestone. The format is fixed
> so you can fill it in two minutes.
>
> 每周一条，与里程碑一起提交。格式固定，两分钟就能填完——这是门槛，故意设得很低。

---

```markdown
# DEVLOG · 每周开发日志

> Personal development log. Written by me, for me — and for the instructor who
> reads it to know whether the project is real.
>
> 个人开发日志。我写给我自己，也写给评审人——他们靠这个判断项目是不是在真正推进。

## W1 (2026-MM-DD)
- Did:
- Result:
- Next:
- Blocked:

## W2 (2026-MM-DD)
- Did:
- Result:
- Next:
- Blocked:

## W3 (2026-MM-DD)
...
```

---

## Format per entry · 每周条目的格式

Each entry is **four lines**, in this order. Fill them in. If a line is genuinely empty
("nothing this week"), write "—" so the pattern is unbroken — the unbroken pattern is
itself a signal that you are paying attention.

| Field | What goes here |
|---|---|
| **Did** | 1–2 things you actually committed this week (file / function / experiment). Not "studied". |
| **Result** | The number, the screenshot, the "didn't work, here's why" — concrete. |
| **Next** | One specific thing for next week. If you can't name it, that's the answer. |
| **Blocked** | What's in the way. Empty is fine. Naming it lets someone help. |

**Three rules that matter more than they look:**

1. **Commit the entry the same day as the milestone.** Back-filling in W16 is detectable
   and scores 0 on the affected section (`rubric-defence.md` §2).
2. **"Studied" / "researched" is not "did".** A name of a file, a function, a number.
3. **"Nothing this week" is itself a useful entry** — it means the entry is honest,
   which is the whole point.

---

## Worked example · 填写示例

```markdown
## W6 (2026-09-21)
- Did: dropout sweep 0.1 / 0.3 / 0.5; AdamW vs Adam on the W5 model
- Result: dropout 0.3 helped (+0.014), AdamW did not (−0.003), lr 3e-4 helped (+0.012) — table in `experiments/ablation.md`
- Next: freeze the W5+v1 config, start the error-analysis notebook
- Blocked: waiting on the licence clarification for the Chinese CV dataset (asked Tuesday)
```

A grader reading this knows: you worked, you measured, you made a decision, you have a
plan, and one thing is actually outside your control. That is what "is this project real"
looks like.
