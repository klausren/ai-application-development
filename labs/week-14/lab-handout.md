# Lab 14 · Model Deployment & API Engineering
> **AI Application Development** · Week 14 Lab (75 min, 课时 3–4) · English with Chinese summary at the end · 中文摘要见文末

| | |
|---|---|
| **Week / 周次** | 14 |
| **Duration** | 75 min lab + 15 min quiz & wrap-up |
| **Module** | 4 · AI Application Engineering |
| **Stack** | FastAPI, Pydantic, uvicorn, joblib/torch.save, Docker (optional) |
| **Deliverables** | `lab-14/` folder: `app.py`, `schema.py`, `client.py`, `Dockerfile`, load-test results |
| **Weight** | Lab participation & quizzes = 20% of final grade (this lab is 1/16 of that) |

## 1. Learning Objectives · 学习目标

By the end of this lab you will be able to:

- **Know** the difference between *training* a model and *serving* it, and why the boundary matters
- **Know** what belongs in an API contract (input schema, output schema, error semantics)
- **Do** wrap a trained model in a FastAPI service with validation and a health endpoint
- **Do** measure latency (p50 / p95) under concurrent load and report the numbers
- **Do** containerise the service (or document precisely why you could not)

## 2. Before You Start · 课前准备

- [ ] Week 13 lab committed
- [ ] `pip install fastapi "uvicorn[standard]" httpx` works
- [ ] Have **one trained artifact** ready: `model.joblib` (sklearn) or `model.pt` (PyTorch) — reuse Week 4 or Week 9

## 3. Lab Tasks · 实验任务

### Part A — Serialise once, load once (10 min)

```python
import joblib; joblib.dump(pipe, "model.joblib")     # sklearn
# or
torch.save(model.state_dict(), "model.pt")           # PyTorch — save the WEIGHTS, not the object
```

> **Checkpoint A** — artifact size and load time recorded.
> **Pitfall**: `torch.save(model)` pickles the class definition too; the file breaks if you rename the class. Save `state_dict` and rebuild the architecture at load time.

### Part B — A real API with a contract (25 min)

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

class PredictRequest(BaseModel):
    text: str = Field(min_length=1, max_length=5000)

class PredictResponse(BaseModel):
    label: str
    confidence: float
    model_version: str

app = FastAPI(title="Sentiment API", version="1.0.0")

@app.get("/health")
def health(): return {"status": "ok", "model_version": MODEL_VERSION}

@app.post("/predict", response_model=PredictResponse)
def predict(req: PredictRequest): ...
```

Load the model **at startup**, not per request:

```python
@app.on_event("startup")
def load(): global MODEL; MODEL = joblib.load("model.joblib")
```

> **Checkpoint B** — interactive docs at `http://127.0.0.1:8000/docs` work; screenshot included.
> **Pitfall**: loading the model inside the endpoint makes every request pay the load cost. Load once at startup.

### Part C — Errors are part of the contract (15 min)

Send five bad requests: empty string, wrong type, 10 MB payload, missing field, malformed JSON.

> **Checkpoint C** — table of the five cases: status code returned, and whether the message is useful to a client developer.
> **Think**: a 500 with a stack trace tells the client nothing and leaks your internals. Return 4xx with an actionable message.

### Part D — Load test and report real numbers (20 min)

```python
import asyncio, httpx, time
async def hammer(n=200, concurrency=16): ...
```

Measure p50 and p95 latency at concurrency 1, 8, 32. Build a small table.

> **Checkpoint D** — latency table + one sentence: at what concurrency does it fall over, and what is the first thing you would fix?
> **Pitfall**: measuring with `time.time()` around a synchronous loop tests your client, not your server. Use concurrency.

### Part E — Containerise (5 min)

Write a `Dockerfile` (even if you cannot run Docker today):

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD ["uvicorn", "app:app", "--host", "0.0.0.0", "--port", "8000"]
```

> **Checkpoint E** — Dockerfile committed. If you could not run it, write one sentence on what blocked you.

## 5. Deliverables Checklist · 交付清单

- [ ] `lab-14.ipynb` (or source files) run / start without errors
- [ ] Every **Checkpoint** executed, with evidence (output, screenshot or log)
- [ ] Results collected into **one summary table**
- [ ] Written interpretation present — code alone is not a deliverable
- [ ] Pushed to GitHub with **≥ 2 meaningful commits**

## 6. Grading Rubric · 评分标准 (100 pts)

| Criterion | Pts | What "full marks" looks like |
|---|:---:|---|
| Artifact serialisation (Part A) | 10 | model saved correctly (state_dict for PyTorch), size + load time recorded |
| FastAPI service (Part B) | 30 | health + predict endpoints, Pydantic schemas, model loaded at startup |
| Error semantics (Part C) | 20 | five bad requests handled with appropriate status codes and useful messages |
| Load test (Part D) | 25 | p50/p95 measured at three concurrency levels, bottleneck identified |
| Dockerfile (Part E) | 5 | committed and syntactically valid |
| Exit ticket | 10 | three questions answered |

Late policy: −10% per day, max 3 days, then 0.

## 7. Submission · 提交方式

```bash
git add .
git commit -m "feat: complete lab 14"
git push origin main
```

## 8. Exit Ticket · 课后反思

1. What surprised you most today?
2. What would break first if real users hit your system tomorrow?
3. One question you still have.

## 9. 中文摘要

本周把模型变成服务，是「能跑」和「能用」的分界线。

五个要点：
1. **训练和服务是两件事**：`joblib.dump`（sklearn）或 `torch.save(model.state_dict())`（PyTorch）——**存权重不存整个对象**，否则改个类名文件就废了。
2. **模型在启动时加载一次**，不要在每个请求里加载，否则每个请求都要付一次 IO 成本。
3. **API 契约要显式**：用 Pydantic 定义输入/输出 schema，字段加校验（长度、类型）。FastAPI 会自动生成 `/docs` 交互文档。
4. **错误也是契约的一部分**：客户端传错参数要返回 4xx + 可操作的错误信息；500 + 堆栈既没用又泄漏内部实现。
5. **压测要并发**：串行循环测的是客户端不是服务端。报告 p50/p95 延迟，找出崩溃的并发数。

本周交付物是一个能被别人 curl 的服务——这是 capstone 的技术底座。
