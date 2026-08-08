# 性能优化记录

> 学习状态：项目中使用，持续维护
>
> 验证状态：本页整理用户项目性能决策记录；第 35 课 Profiler 快扫和 Build 试玩来自用户实践证据，本次只读复核外部项目证据包、脚本和忽略规则，未重新运行 Profiler。
>
> 对应项目：[Backpack Survivor](index.md)
>
> 关联专题：[性能优化](../../performance/index.md)、[优化小 Tips](../../performance/perf-tips.md)
>
> 日期：2026-08-08

## 记录定位

性能优化记录不只保存“做了什么优化”，也保存“为什么不优化”。项目规模还小时，很多看起来更高级的结构会增加复杂度，却没有可证明收益。正式记录应保留判断依据、证据等级和后续触发条件。

当前下一条编号从 `OPT-003` 开始。

## 决策索引

| 编号 | 标题 | 归属课程 | 决策 |
|---|---|---|---|
| OPT-000A | 距离判断用 `sqrMagnitude` 替代 `magnitude` | 第 8 课 | 高频半径判断避免开方，关联[拾取与磁吸](pickup-and-magnet.md) |
| OPT-000B | 对象池消除 `Instantiate/Destroy` 的 GC 峰值 | 第 5 课 | 敌人、投射物、伤害数字、掉落物等短生命周期对象优先池化 |
| OPT-000C | 子弹碰撞用 `SphereCastNonAlloc` | 第 4 课 | 投射物命中路径复用缓冲，后续仍需满载边界测试 |
| OPT-000D | 决定不做 HashSet 优化 | 第 9 课 | 48 格背包规模下，数组 / 列表扫描更简单，未证明 HashSet 有收益 |
| OPT-000E | 玩家引用缓存而非每帧查找 | 第 2 / 8 课 | 高频访问引用应在启动或注入时缓存 |
| OPT-000F | 背包 UI 全量重绘而非局部刷新 | 第 10 课 | 当前格子数量小，全量重绘可读性和正确性优先；规模上去再做脏标记 |
| OPT-001 | `ItemView` 每次生成做一次全场景查找 | 第 31 课前后 | 表现层资源查找应缓存或显式注入，避免重复场景查询 |
| OPT-002 | Profiler 快扫后决定不做大重构 | 第 35 课 | Editor/Profiler 尖刺未在 Build 中形成阻断卡顿，当前只做低风险修复 |

## 重点复盘

### OPT-000D · 不做 HashSet 优化

背包格子数量有限时，直接扫描更容易维护，也更容易和拖拽、旋转、合并、回滚等规则保持一致。只有当 Profiler 或规模证明查找成为热点时，才值得引入更复杂的数据结构。

### OPT-000F · 小规模背包 UI 保持全量重绘

全量重绘不是天然低级方案。对小规模 UI 来说，先保证状态一致和回滚正确，比提前维护局部脏标记更重要。后续如果图标、接边、星星和 Tooltip 的重绘成本上升，再用 Profiler 决定是否拆分。

### OPT-002 · Profiler 快扫后不做大重构

第 35 课看到的尖刺主要归因于 EditorLoop、Live Display 或资源预加载/纹理上传。用户 Build 试玩到约 `6000` 分没有明显卡顿，因此不基于 Editor 感觉重构波次、背包或武器系统。

本次真正处理的是低风险交付问题：保存 Profiler 轻量证据、忽略大体积捕获、修复 Build 颜色异常和清理部分运行时调试日志。

## 后续触发条件

| 待评估项 | 触发条件 | 可能动作 |
|---|---|---|
| `HazardZone` 每帧遍历 `targetsInZone` | 危险区目标数量上升且 Profiler 指向该路径 | 分桶、事件驱动或降低 tick 频率 |
| `TargetRegistry` 线性找最近目标 | 敌群规模上升且索敌成为 CPU 热点 | 空间划分、按阵营缓存或限制查询频率 |
| 背包 UI 全量重绘 | 图标、接边、星星、Tooltip 组合后 UI 重建成本明显 | 局部刷新、脏格队列、视图复用 |
| TMP / 图标首次展开上传 | Player Build 中复现首次打开面板卡顿 | 预热字体、图集或关键面板 |
| 伤害数字 / 掉落物池扩容 | 终局波次出现 GC Alloc 或 Instantiate 峰值 | 提高预热量、记录峰值、调整归还策略 |

## 如何验证

| 结论 | 证据等级 | 说明 |
|---|---|---|
| OPT-000A～OPT-002 来自用户项目性能记录 | B | 来自用户放入 Inbox 的 `性能优化记录.md` |
| 第 35 课 Build 试玩约 `6000` 分无明显卡顿 | B | 来自用户实践记录和外部项目 Profiler 证据 README |
| 外部项目 `Docs/ProfilerEvidence/README.md` 静态记录了 EditorLoop、资源上传和 Live Display 观察结论 | C | 本环境只读查看外部项目证据包 |
| `.gitignore` 静态可见 `BackpackSurvivor/ProfilerCaptures/` 被忽略 | C | 本环境只读查看外部项目 `.gitignore` |
| 当前环境亲自采样 Profiler 或对比优化前后数据 | D | 本次未运行 Unity Profiler |

## 维护规则

- 新优化记录从 `OPT-003` 开始。
- 每条记录尽量包含：场景、观测指标、决策、代价、证据等级和后续触发条件。
- 只有“优化前后数据 + 同一场景复测”齐全时，才写成已验证优化收益。
- “决定不优化”也要记录原因，避免后续重复消耗精力。

## 相关内容

- [Profiler 快扫与低风险优化](profiler-sweep-and-low-risk-optimization.md)
- [Build 与演示包](build-and-demo-package.md)
- [性能优化](../../performance/index.md)
- [优化小 Tips](../../performance/perf-tips.md)
- [Bug 记录簿](bug-log.md)

> 标签：`Unity` `性能优化` `Profiler` `对象池` `GC` `Build 验证` `项目实践`
