# 分解粒度对比：工作站与整线

本目录为 RL 前插入的独立探索实验，不修改论文或旧算法。最终结果见 RESULTS.md，理论条件见 CONVERGENCE_ANALYSIS_ZH.md。

## 方法与可比范围

- **station_root**：现有 code/dwcg/solve.py，重建式工作站两阶段精确 CG。最后对生成列池求整数解，原始约束与独立数据检查均通过后接受 LB。若 CG 超时，使用已保存池尝试恢复，另保留最后一次完整轮有效 UB。
- **line_root**：现有 sub/stage9/cg_balanced.py，整线两阶段 CG，pricing=rebuild，无资源档位后处理。每线短经济初始化 .5 秒，正常循环内已有受限 IP 恢复。
- **line_full**：现有 sub/stage9/balanced_bound.py，论文当前完整整线方法：warm 定价、整数恢复、按需档位补全和有效经济界。
- **compact**：原始紧凑 MILP 单线程 CPLEX。

station_root/line_root 均使用重建式 PP，帮助观察粒度差异；但初始化、恢复频率、定价预算调度也存在固有实现差异，不能把全部墙钟差距严格归因于分块。line_full 是完整方案比较，更不能作为仅改变分块的纯消融。本次不将 B&P 搜索与根 CG 混比。

## 协议

五个已知开发输入，同一个冻结 JSON 给四种方法。两小例 20 秒、中例和困难例 30 秒总预算，均预留5秒收尾；station_root 另在算法预算内保留2秒整数恢复。CPLEX 单线程、seed11、MIP gap0；同实例内循环轮换方法顺序，串行执行。

父进程从启动 worker 前计时到 worker 结束，涵盖导入、建模、求解、原始整数验证、压缩及摘要落盘。深度独立审计在性能运行结束后进行，时间另计。watchdog 是预算外3秒的安全终止机制；Windows/native 不提供绝对硬实时保证。完整源文件哈希及每次运行 accounting 均保存。

每个结构只选一个开发输入，没有重复随机种子或稳定性统计，属于机制 pilot。保留困难反例和超时；不把30秒未证转换为3600秒实测结果。受限整数池不可行不等于原问题不可行。

## 运行与复核

```powershell
& .\experiments\.venv\Scripts\python.exe sub/decomposition_compare/run.py --output <新的不存在目录>
& .\experiments\.venv\Scripts\python.exe sub/decomposition_compare/audit.py <上述目录>
```

输出已有目录即拒绝覆盖。certificate.json.zlib 保存原结果与列池；summary.json 为摘要；validation/results.csv 和 convergence.csv 分别记录对照表和分阶段收敛轨迹。

pilot_20261111 保留了首批运行：line_root 缺少 stage3 模块搜索路径导致5次 adapter_error，其他方法结果也完整保留；该批不能用于完整四方法比较。修复仅在新增 runner 的导入路径，并让异常返回非零退出码，随后 final_20261111 全部重新运行。旧模型及求解算法未改。

原生日志逐文件无损归档到 evidence/solver_logs.zip，成员原字节 SHA-256 见 NATIVE_LOG_INDEX.json；本地原日志保留，Git 不逐个重复存储数千个小文件。在新的检出目录需要阅读原日志时，可将该归档解压到 evidence 目录恢复原相对路径。运行结果、证书、输入、失败记录均单独上传。
