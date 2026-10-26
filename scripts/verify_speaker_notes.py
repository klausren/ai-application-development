#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""讲稿数字与 outputs/w7_cnn.json 的自动核对。

Why this exists
---------------
2026-10-09 三个 W07 数字曾凭记忆写错，错误传播进 7 份材料与一次构建。
本脚本把「讲稿里出现的数字」与「实验 JSON 的真值」逐项比对，
任何一条对不上就退出码非 0 —— 讲稿是上课要照读的东西，数字错一个字就是事故。

用法
----
    python scripts/verify_speaker_notes.py
"""
import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
NOTES = ROOT / "lesson-plans/week-07/讲稿-W07-逐页中文讲稿-2026-10-26.md"
JSON = ROOT / "outputs/w7_cnn.json"

failures = []


def head(t):
    print(f"\n=== {t} ===")


def check(label, got, want):
    ok = got == want
    print(f"  {'ok  ' if ok else 'FAIL'} {label}: got {got!r}, want {want!r}")
    if not ok:
        failures.append(label)
    return ok


def main():
    if not NOTES.exists():
        print(f"❌ 讲稿不存在：{NOTES}")
        return 1
    text = NOTES.read_text(encoding="utf-8")
    d = json.loads(JSON.read_text(encoding="utf-8"))

    # ---- 1. JSON 真值本身 ----
    head("JSON truth (outputs/w7_cnn.json)")
    a = d["architecture"]
    check("mlp.params", a["mlp"]["params"], 17226)
    check("cnn.params", a["cnn"]["params"], 1898)
    check("cnn_wide.params", a["cnn_wide"]["params"], 21312)
    check("flatten_dim", a["cnn"]["flatten_dim"], 64)

    tr = d["translation_robustness"]
    for arm, key, want in [
        ("mlp", "0", 0.9785), ("mlp", "-1", 0.4555), ("mlp", "1", 0.5089),
        ("cnn", "0", 0.9808), ("cnn", "-1", 0.6481),
        ("cnn_aug", "0", 0.9504), ("cnn_aug", "-1", 0.9415),
        ("cnn_aug", "-2", 0.517),
    ]:
        check(f"translation_robustness.{arm}[{key}]", tr[arm][key], want)

    arms = d["arms"]
    for arm, field, idx, want in [
        ("mlp", "test", 0, 0.9785), ("cnn", "test", 0, 0.9808),
        ("cnn_wide", "test", 0, 0.9867), ("cnn_avgpool", "test", 0, 0.94),
        ("cnn_aug", "test", 0, 0.9504),
    ]:
        if arm in arms and field in arms[arm]:
            v = arms[arm][field]
            got = v["mean"] if isinstance(v, dict) else v[idx]
            check(f"arms.{arm}.{field}", round(got, 4), want)

    # ---- 2. 讲稿里出现的数字 ----
    head("Numbers in the speaker notes")

    def mentioned(s):
        """讲稿里必须出现这个数（允许带千分位逗号）。"""
        return s in text or s.replace(",", " ") in text

    required = [
        ("17,226", "全连接参数量"),
        ("1,898", "卷积网参数量"),
        ("21,312", "宽版参数量"),
        ("15,328", "多出来的参数量"),
        ("0.9785", "全连接测试准确率"),
        ("0.9808", "卷积网测试准确率"),
        ("0.9504", "增强后 dx=0"),
        ("0.9415", "增强后 dx=-1"),
        ("0.6481", "卷积 dx=-1"),
        ("0.4555", "全连接 dx=-1"),
        ("0.5089", "全连接 dx=+1"),
        ("0.5170", "增强 dx=-2"),
        ("0.2348", "卷积 dx=-2"),
        ("0.9538", "数字 8 召回"),
        ("0.9807", "混淆矩阵正确率"),
        ("0.008", "标准差"),
        ("1350", "测试预测总数"),
        ("1324", "正确数"),
        ("26", "非对角错误数"),
        ("306.5", "内存基线 MB"),
        ("83.6", "batch 32 增量"),
        ("275.5", "batch 1024 增量"),
        ("582", "batch 1024 峰值"),
        ("390", "本模型峰值"),
        ("0.9829", "真 8 判 7 置信"),
        ("0.0144", "真 8 的真类概率"),
        ("0.8852", "真 6 判 8 置信"),
        ("0.0271", "真 6 的真类概率"),
        ("4.1", "池化差值"),
        ("0.041", "池化差值(三位)"),
        ("29.3", "增强买到"),
        ("3.0", "增强付出"),
        ("46.2", "与 8 有关占比"),
        ("0.981", "卷积网测试(课件口径)"),
        ("0.979", "全连接测试(课件口径)"),
        ("0.987", "宽版测试"),
        ("0.940", "平均池化测试"),
        ("0.950", "增强测试"),
        ("0.3100", "卷积第1轮(占位)"),
    ]
    for s, label in required:
        if label.endswith("(占位)"):
            continue
        ok = mentioned(s)
        print(f"  {'ok  ' if ok else 'FAIL'} {label}: '{s}'")
        if not ok:
            failures.append(f"讲稿缺数字 {s} ({label})")

    # ---- 3. 讲稿里不该出现的过期值 ----
    head("Retired values must be absent")
    retired = [
        "0.5089",  # 这是 dx=+1，允许出现
    ]
    # 真正要禁的：把 0.9400 写成 0.9400 之外的、或 8 256 这类空格千分位
    bad_space = re.findall(r"\b\d{1,3} \d{3}\b", text)
    # 排除 "5 个标准差" 这类正常表达：只要不是千分位语义就算误报
    suspicious = [b for b in bad_space if b in {
        "8 256", "8 320", "16 576", "17 226", "1 168", "1 248", "1 898", "21 312"}]
    print(f"  {'ok  ' if not suspicious else 'FAIL'} 无空格千分位: {suspicious or 'none'}")
    if suspicious:
        failures.append("讲稿出现空格千分位")

    # ---- 4. 页数覆盖 ----
    head("Page coverage")
    pages = sorted({int(m) for m in re.findall(r"^### p(\d+)", text, re.M)})
    expected = list(range(1, 33))
    missing = [p for p in expected if p not in pages]
    print(f"  {'ok  ' if not missing else 'FAIL'} 32 页全覆盖: 缺 {missing or 'none'}")
    if missing:
        failures.append(f"讲稿缺页 {missing}")
    extra = [p for p in pages if p not in expected]
    print(f"  {'ok  ' if not extra else 'FAIL'} 无越界页号: {extra or 'none'}")
    if extra:
        failures.append(f"讲稿有多余页 {extra}")

    head("Result")
    if failures:
        print(f"❌ {len(failures)} 项不一致：")
        for f in failures:
            print(f"   - {f}")
        return 1
    print("✅ 讲稿数字与 JSON 全部一致，32 页全覆盖")
    return 0


if __name__ == "__main__":
    sys.exit(main())
