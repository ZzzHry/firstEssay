# 事实与边界

## 仓库事实

F1. `sub/stage13/BASELINE.md` 冻结的是整线分解。正式入口 `sub/stage11/run_plan_v2.py` 调用 `worker_v2.py`，分解链包含 `balanced_bound.py → demand_balanced.py → cg_balanced.py`。历史参数为 CPLEX 22.1.1、单线程、seed 11、MIP gap 0；本轮未重新验证许可证或运行环境。

F2. `sub/stage13/SUMMARY.md` 报告：120 任务 6 线、资源比例 80%、seed 34，在 CG 未完整收敛后经 31 次资源档查询证明整数利润 1009.98；同组 seed 32/33 查询数为 0。80 任务 2 线困难例查询 18 次后仍未闭合，且落后于 Compact。均为历史结果，本轮未重跑。

F3. `RL/adaptive_v1/SUMMARY.md` 中四种策略均是规则，不是训练出的 RL。部分候选策略减少调用却增加总时间。其不带资源 DP 的实验引擎不能充当当前完整生产分解基线。

F4. `demand_balanced.py` 当前从上界 DP 的一个路径中，按尝试次数、line、index 选择未解决档位。重复查询时间上限是 `min(2*2**min(attempts,8), remaining)`，实际参数允许配置。`profile_pp.py` 重新建立精确资源计数 MILP，并非恢复先前的 CPLEX 搜索状态。

F5. `resource_dp.py` 的未知上界按正无穷处理。上界 DP 输出 `feasible=True, value=None` 表示尚有未被排除的资源组合，但尚无有限有效 UB（内部按正无穷）；既不证明原问题可行，也不证明不可行。没有列仅表示没有已知局部整数 witness。

## 文献事实（仅定位，不构成完整查新）

L1. Chi 等，NeurIPS 2022，已研究 RL 选择 CG 列：[原始论文页面](https://papers.neurips.cc/paper_files/paper/2022/hash/3ecfe5c632afb7d96a2337b18ff99b1f-Abstract-Conference.html)。不能把“CG 加 RL”本身作为新贡献。

L2. Shen 等，ICML 2024，研究预测对偶与自适应稳定化：[PMLR](https://proceedings.mlr.press/v235/shen24e.html)。泛化的学习价格调整已有先例。

L3. Xu、Shen、Liu 的 RLHH 预印本（2023）研究 RL 选择低层启发式，也以整数解质量为目标：[作者预印本](https://arxiv.org/abs/2310.09686)。不能声称首次用整数质量指导学习型 CG。本计划引用版本为预印本，不据此确认最终出版信息。

上述页面于 2026-11-11 查询；NeurIPS 直开超时后通过同一原始站点检索摘要核对。

## 数学定义与待验证设计

M1. 档位 `(h,r)` 表示整线方案恰好使用 h 个人工配置和 r 个机器人配置，包含协作模式的两种资源消耗；不是资源上限。

M2. 在现有整线列域、完整覆盖所有可能合法档位、每线恰选一个原模型可行方案、利润可加且仅共享 H/R 容量跨线耦合的前提下，各档位的局部整数利润界可由二维 DP 组合为原整数问题的界。实现与重放仍须独立验证。

M3. 学习预测只能影响查询顺序，不能成为数学上界、不可行性证书或删除允许档位的理由。

H1. 兼容性信息可能使查询优于最大局部缺口规则。H2. 档位查询可能存在延迟收益，RL 可能优于上下文老虎机。H3. 收益可能推广到未见产品与规模。三者均为待检验假设。

## 禁止升级的结论

不声称已经训练 RL；不承诺必然提速；不把历史单次运行当显著性证据；不把资源档 DP 的整数闭合写成 CG-LP 收敛；不把截断 incumbent 当定价上界；不把未知档位删除；不把 600 秒截止写成实际运行 3600 秒；不宣称严格有理证明。
