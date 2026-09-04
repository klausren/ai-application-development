# Lab 13 · Generative AI Applications & AI Agents
> **AI Application Development** · Week 13 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 13 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 4 · AI Application Engineering |
| **Stack** | Gradio, `transformers` (local LLM) or a mock LLM, plain Python |
| **Deliverables** | `lab-13/` folder: `agent.py`, `tools.py`, `app.py`, `traces.md` |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** the agent loop: `observe → think → act → observe`, and where it can go wrong
- **Know** the difference between a *tool call* and free-form generation, and why structured output matters
- **Do** implement three tools and a ReAct-style loop that can use them
- **Do** ship a working Gradio demo a non-technical person could use
- **Do** add guardrails: step limit, JSON validation, and graceful failure

## 2. Before You Start · 课前准备

- [ ] Week 12 lab committed (you have a working LLM call path)
- [ ] `pip install gradio` works
- [ ] If no model is available, use the mock LLM from Week 12 — the agent logic is identical

## 3. Lab Tasks · 实验任务

### Part A — Three tools with real contracts (15 min)

```python
# tools.py — every tool has a name, a docstring the model reads, and typed inputs
def calculator(expr: str) -> float:
    "Evaluate an arithmetic expression. Input MUST be a valid Python arithmetic string."
    return eval(expr, {"__builtins__": {}}, {})      # note the sandboxing

def search_courses(query: str) -> str:
    "Look up course information. Returns matching catalogue entries."

def get_weather(city: str) -> str:
    "Get current weather for a city (mock data)."
```

> **Checkpoint A** — three tools, each with a docstring a model could act on, plus one input that breaks each.
> **Pitfall**: `eval()` on model output is a remote-code-execution hole. Sandbox it (as above) or use `ast.literal_eval`. Never ship a bare `eval`.

### Part B — The ReAct loop (25 min)

```python
MAX_STEPS = 6
for step in range(MAX_STEPS):
    prompt = build_prompt(history, question)
    out = llm(prompt)
    if out.startswith("ACTION:"):
        result = call_tool(parse(out))
        history.append(("observation", result))
    elif out.startswith("ANSWER:"):
        return out
```

> **Checkpoint B** — three traces saved to `traces.md`: one that finishes in 1 step, one that needs 3+, and one that **loops or fails**.
> **Pitfall**: without `MAX_STEPS`, a confused agent burns tokens forever. Every production agent has a step cap — add yours now.

### Part C — Structured output & validation (15 min)

Force the model to emit JSON and validate it before acting:

```python
import json, pydantic
class Action(pydantic.BaseModel):
    tool: str
    args: dict
Action.model_validate_json(raw)      # raises if the model hallucinated a field
```

Test with three malformed outputs (missing key, wrong type, unknown tool name).

> **Checkpoint C** — the three malformed cases and how your code handled each (raise? retry? fallback?).
> **Think**: retrying once with the error message in the prompt fixes a surprising share of failures. Measure it.

### Part D — Ship a Gradio demo (20 min)

```python
import gradio as gr
gr.ChatInterface(fn=agent_reply, title="Course Assistant").launch()
```

Add: a textbox, a "show reasoning trace" checkbox, and example prompts.

> **Checkpoint D** — a screenshot of the running UI plus the URL it printed. Try it with a question it cannot answer — what does the user see?
> **Pitfall**: a raw exception in the UI looks broken to users. Catch errors and return a friendly message.

### Part E — Wrap up (5 min)

List three things a malicious user could make your agent do, and the guardrail for each.

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-13.ipynb` (or source files) run / start without errors
- [ ] Every **Checkpoint** executed, with evidence (output, screenshot or log)
- [ ] Results collected into **one summary table**
- [ ] Written interpretation present — code alone is not a deliverable
- [ ] Pushed to GitHub with **≥ 2 meaningful commits**

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Tool contracts (Part A) | 20 | three tools, model-readable docstrings, failure inputs documented, eval sandboxed |
| ReAct loop (Part B) | 30 | loop implemented with step cap, three traces incl. one failure saved |
| Structured output (Part C) | 20 | JSON validated, three malformed cases handled and measured |
| Gradio demo (Part D) | 20 | working UI with error handling, screenshot included |
| Exit ticket | 10 | three questions answered |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add .
git commit -m "feat: complete lab 13"
git push origin main
```

## 8. Exit Ticket · 课后反思

1. What surprised you most today?
2. What would break first if real users hit your system tomorrow?
3. One question you still have.

## 9. 中文摘要

本周把 LLM 从「聊天」变成「会干活」，核心是**工具调用 + 循环控制**。

五个要点：
1. **Agent 的骨架是 ReAct 循环**：观察 → 思考 → 行动 → 再观察，直到输出答案。
2. **必须设步数上限**（`MAX_STEPS`）：智能体一旦卡住，没有上限就会无限烧 token。生产环境里这是硬性约束。
3. **工具的 docstring 是给模型看的**，写清楚输入格式和返回内容，等于在写「API 文档」。
4. **输出要结构化并校验**：让模型吐 JSON，用 Pydantic 校验后再执行。把报错信息塞回提示词重试一次，能修好相当比例的失败——**要去测量这个比例**。
5. **安全第一**：`eval()` 模型输出等于远程代码执行，必须沙箱化或用 `ast.literal_eval`。UI 里不能把异常直接抛给用户。

思考题的参考答案方向：提示词注入（外部内容伪装成指令）、越权调用工具（工具白名单）、无限循环（步数上限）。
