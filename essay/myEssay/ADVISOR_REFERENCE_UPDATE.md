# 导师指定文献与流程图更新（2026-11-08）

五篇指定文献均已实际引用。Guo2025 原已收录，新增其余四篇后共 38 篇，未超过 40 篇，因此未删除原文献。平台用的 system/input/references.bib 同步更新。

|引用键|核对后的卷期信息|DOI|
|---|---|---|
|Wang2024RL|Neurocomputing 569, 127145, 2024|10.1016/j.neucom.2023.127145|
|Xu2023Failure|Mathematics 11(6), 1557, 2023|10.3390/math11061557|
|Guo2025|IEEE TCSS 12(5), 2848–2863, 2025；原已收录|10.1109/TCSS.2025.3540070|
|Qin2025Hybrid|IEEE TASE 22, 712–723, 2025|10.1109/TASE.2024.3418898|
|Wang2021Markov|Neurocomputing 435, 283–294, 2021|10.1016/j.neucom.2020.12.103|

完整题名、作者顺序和出版日期的 Crossref 注册元数据保存在 data/advisor_references/metadata.json。Qin 一篇在导师清单中标2024，注册题录的 published-print 和卷22对应2025，本稿采用卷期年2025；本轮未取得明确的 published-online 日期，2024可能来自早期在线记录，不能只凭 DOI 含2024就确认在线年。资产定价论文第一作者为 Jia Wang，区别于强化学习论文的 Jiacun Wang。清单中的34、33、30、28等引用次数不写入卷期页码。

交叉核对的主来源：

- [强化学习论文出版社摘要](https://www.sciencedirect.com/science/article/pii/S0925231223012687)：混合拆卸线、多技能工人、强化学习分配；本稿仅概括研究范围。
- [离散头脑风暴论文](https://www.mdpi.com/2227-7390/11/6/1557)及[版本记录](https://www.mdpi.com/2227-7390/11/6/1557/notes)：2023, 11(6),1557。
- [共享资源论文作者机构题录/摘要](https://researchwith.montclair.edu/en/publications/modeling-and-optimization-of-multiproduct-humanrobot-collaborativ/)：2025,12(5),2848–2863。
- [Qin论文 Crossref 注册题录](https://api.crossref.org/works/10.1109%2FTASE.2024.3418898)：卷22、712–723、2025。IEEE正文入口当前受限，不声称已读全文。
- [资产定价论文作者机构题录/摘要](https://researchwith.njit.edu/en/publications/a-markov-regime-switching-model-for-asset-pricing-and-ambiguity-m/)：2021,435,283–294。

部分出版社直连出现403/429，公开题录及可访问主来源摘要支持本文采用的主题描述。本轮没有声称完成五篇全文精读，也没有归纳未读性能数据。

## 引用安排与关联边界

强化学习论文放在引言混合布局相关研究，本文方法和实验仍不包含强化学习。头脑风暴论文用于随机任务/拆卸失败研究；Qin论文用于多产品人机协作研究；共享资源论文保留已有协调背景。

股票市场论文与本课题关联较弱，按要求引用于“不同领域的不确定性具有不同含义”的边界讨论，明确其金融场景。不称其为拆卸线论文，也不将其用于支撑本文疲劳模型、算法或实验优势。建议导师定稿时再次确认这条跨领域引用的必要性。

四篇新文献均实际出现在正文，五个必需引用键和40条上限进入已有检查。文献重建脚本已接入新增题录，避免再生成时丢失条目。

## 图片和验证范围

流程图原始 PNG 从 essay/add 同名复制到 img，清理旧 PDF/SVG/TIFF，保留 Mermaid 逻辑参考。重绘脚本仅生成性能图，保留用户提供的 Fig.1–4。数学模型、算法和实验数据不变；本轮不重跑优化实验。新图不适用旧 Python 矢量图的字体审计。

编译、引文和来源哈希检查及当前页面预览见 qa/advisor_update/，交付字节清单见 SHA256.v2.json。
