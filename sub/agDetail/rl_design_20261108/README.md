# RL 组会材料（2026-11-08）

正式交付是上一级的 `RL_DESIGN_GROUP_MEETING_20261108.pptx` 和 `RL_DESIGN_NOTES_ZH.md`。PPT 为20页、16:9，建议18–20分钟；演讲者备注逐页附解释和来源。当前没有RL训练成果，本次不修改求解器。

- `SPEAKER_NOTES.md`：逐页讲稿的文本副本。
- `build_deck.mjs`：可编辑PPT生成源代码，使用 `@oai/artifact-tool`。
- `slide_manifest.json`：页码、标题、讲稿与来源。
- `final_previews/`：从最终PPTX重新导入并渲染的20页预览。
- `QA_REPORT.md` / `qa.json`：PPTX结构检查。
- `DELIVERY_CHECK.md`：人工视觉检查及验证边界。
- `SOURCE_CHECK.json`：图表数值与历史报告的逐项比对。
- `SHA256.json`：本次交付及读取来源的哈希，与旧算法说明的哈希独立。

## 数据核对

```powershell
python sub/agDetail/rl_design_20261108/verify_materials.py
```

此脚本只读历史数据与PPTX，核对3个原生图表的数值和20份讲稿，并更新本目录检查报告；不求解实例、不训练RL、不重新判定历史证书。

## 重建PPT

使用本机 presentations 技能提供的 Node.js、Python 与 `@oai/artifact-tool`。没有采用 python-pptx 创建PPT。源码中的默认路径是当前机器的实际运行环境，也可通过环境变量覆盖：

- `PRESENTATIONS_SKILL_DIR`：presentations 技能根目录。
- `ARTIFACT_PYTHON`：运行检查器的 Python。
- `RUNTIME_NODE_MODULES`：包含 `@oai/artifact-tool` 的运行时依赖目录。
- `DECK_REVISION`：可选的新版本标识；省略时自动用时间戳，避免覆盖内部校验输出。

在本目录建立忽略的 `build/`，将其 `node_modules` 链接到运行时依赖，复制 `build_deck.mjs` 到 `build/` 后使用对应 Node 执行。构建器创建独立内部输出，结构校验后复制到上一级正式PPTX路径，因此重建前请另存用户自行编辑的PPT。之后用技能的 `render_presentation.mjs` 重新渲染**最终文件**到 `final_previews/` 并逐页复核，再运行数据检查脚本。

图表是按真实报告数值建立的原生图表，含嵌入式数值工作簿快照；没有原始Excel公式或外链需要保留。字体为本机已安装的 Microsoft YaHei。
