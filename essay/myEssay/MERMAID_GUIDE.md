# 算法流程图修改与编译

当前正文使用用户提供的 `img/algorithm_flowchart.png`，从 `essay/add/` 同名复制，按全栏宽显示。`img/algorithm_flowchart.mmd` 保留为逻辑参考，不代表新图片的绘图源。

后续替换时，保存为同名 PNG，然后在本目录运行 `./build.ps1`。正文调用为：

```latex
\includegraphics[width=\textwidth]{img/algorithm_flowchart.png}
```

若使用 Mermaid 重新绘制，可导出 PNG 覆盖同名图；若导出 PDF，应同时修改正文扩展名。不要仅把 PNG 扩展名改为 PDF。`scripts/make_revision_figures.py` 现在仅重建性能图，不覆盖用户提供的 Fig. 1–4。

流程图是概览，完整定价、整数见证及有效界闭合的判断以正文和伪代码为准。OR 只对应执行模式选择，不引入拆卸路径互斥。
