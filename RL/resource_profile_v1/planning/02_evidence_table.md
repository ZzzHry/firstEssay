# 主张—证据映射

|编号|主张|来源|强度|可用于|风险/状态|
|---|---|---|---|---|---|
|E1|资源档补全在某历史实例参与整数证明|stage13 SUMMARY、原始 robust180 记录|evidence-backed（历史）|动机、P0|本轮未重放；单例不能推总体|
|E2|部分实例不触发档位查询|stage13 BASELINE/SUMMARY|evidence-backed（历史）|适用边界、完整测试集|此类不能预期查询调度提速|
|E3|大块 PP 困难可能压过档位调度收益|stage13 SUMMARY 的 80/2 例|plausible-inference|风险、分层分析|需非重叠耗时诊断|
|E4|已有候选策略改善不是 RL 改善|RL/adaptive_v1 SUMMARY|evidence-backed（历史）|基线区别|其框架不含完整后处理|
|E5|未知档位保留能避免遗漏整数可行解|resource_dp.py、完整档位数学定义|evidence-backed（实现＋推导）|正确性契约|新策略尚未实现，必须 Oracle 检查|
|E6|DP 兼容性特征有选择价值|H1|hypothesis|P2、消融|强规则可能已足够|
|E7|长期回报优于单步效益|H2|hypothesis|P3/P4|须与同信息 bandit 对照|
|E8|新种子、未见产品上有收益|H3|hypothesis|P5|禁止开发/测试泄漏|
|E9|CG 列选择、稳定化、启发式选择已有学习研究|L1–L3|evidence-backed（文献）|创新边界|不构成完整相关工作综述|
|E10|本方法已具有 RL 性能优势|无|unsupported|不得写入结果|NOT RUN|

历史路径均相对仓库根目录。实际文件与 SHA-256 见上一级 EVIDENCE_INDEX.json；本表不是重新运行的测试报告。
