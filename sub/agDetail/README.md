# 当前整线分解算法详细说明

请先阅读 **[ALGORITHM_DESIGN_ZH.md](ALGORITHM_DESIGN_ZH.md)**。这是一份面向理解、讲解和论文答辩的详细中文说明，覆盖问题定义、整线列、主问题、对偶定价、Phase I/II、整数恢复、资源档 DP、上下界、真实运行过程和代码导航。

建议分三次阅读：

1. 第 1–5 节：先理解“为什么分解”和“列里包含什么”。
2. 第 6–13 节：理解完整流程、检验数、上下界和整数证明。
3. 第 14–20 节：对照真实证书、参数、源码和常见问题。

本说明针对当前论文的 `sub/stage9/balanced_bound.py` 主线，不将旧工作站列 B&P 或 RL 实验当作当前论文算法。

- `evidence_summary.json`：从已有求解证书抽取的三个真实例子；保留来源及 SHA-256。
- `SOURCE_INDEX.json`：18 个关键源码文件的 SHA-256、顶层函数/类行号。
- `collect_evidence.py`：仅重新读取上述证据和索引，不调用求解器。

在项目根目录执行以下命令可以更新摘录；若源码或证据版本改变，应同步审查说明文字，而不是默认旧文字仍适用：

```powershell
& experiments/.venv/Scripts/python.exe sub/agDetail/collect_evidence.py
```

文档整理基线：Git `7aa6cec7`。本次仅编写说明、检查代码和读取历史证据，没有修改求解算法或重新执行性能实验。文中的“教学例子”明确标出，不属于论文实验结果。
