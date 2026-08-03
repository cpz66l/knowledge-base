# C# 工程能力检查清单

> 本清单是学习规划，不代表相关内容已经完成。请在真正学习和实践后再勾选。

---

## 语言与设计

- [ ] 能解释值语义与引用语义，不简单等同于“栈/堆”
- [ ] 能根据需求选择 class、struct、interface 和组合
- [ ] 能使用泛型减少重复代码，同时避免过度抽象
- [ ] 能说明委托、事件、接口和直接调用的取舍
- [x] 能识别静态全局状态带来的生命周期和测试问题

对应入口：[C# 面向对象](../csharp/oop/index.md)。

## 内存与性能

- [ ] 能通过 Profiler 找到一处托管分配
- [ ] 能识别装箱、闭包、字符串和集合扩容产生的成本
- [x] 能说明对象池的适用范围和容量策略
- [ ] 能定位静态引用或事件订阅造成的对象残留
- [ ] 能记录一次优化前后的数据，而不只凭感觉判断

对应入口：[GC 与内存管理](../csharp/gc-and-memory.md)与[性能优化](../performance/index.md)。

## 异步与并发

- [ ] 能区分 Coroutine、Task、线程和 Job System 的用途
- [ ] 能避免在业务入口滥用 `async void`
- [ ] 能为长生命周期任务设计取消机制
- [ ] 能处理异步异常和对象销毁后的回调
- [ ] 知道哪些 Unity API 只能在主线程调用

对应入口：[async/await 异步](../csharp/async-await.md)。

## 工程质量

- [x] 代码按职责拆分，不把所有逻辑放进 MonoBehaviour
- [x] 使用命名空间和程序集边界控制依赖
- [x] 核心逻辑能够脱离场景进行测试
- [ ] 日志包含足够上下文，并区分普通信息和错误
- [ ] 对异常、空引用和失败流程有明确策略

## 实践证据

> 项目或 Demo：[Backpack Survivor](../projects/backpack-survivor/index.md)
>
> 验证方式：课程运行记录；用户转述 Kimi 已检查代码与 Unity 场景；知识库完成静态复核、纯 C# 数据层最小运行测试和站点构建。
>
> 已有证据：[WeaponBase 提炼](../projects/backpack-survivor/active-weapons-and-weapon-base.md)、[刷怪器与对象池](../projects/backpack-survivor/spawner-and-object-pooling.md)、[背包纯数据网格](../projects/backpack-survivor/inventory-data-grid.md)、[合并升级与邻接联动](../projects/backpack-survivor/merge-upgrade-and-adjacency.md)、[背包武器激活](../projects/backpack-survivor/backpack-weapon-activation.md)、[单局框架与基础 HUD](../projects/backpack-survivor/run-session-and-basic-hud.md)、[经验成长与三选一](../projects/backpack-survivor/level-progression-and-choice.md)、[波次导演与 15 分钟节奏](../projects/backpack-survivor/wave-director-and-run-pacing.md)、[战斗反馈快包](../projects/backpack-survivor/combat-feedback-pack.md)、[胜负结算与重开闭环](../projects/backpack-survivor/run-result-and-restart-loop.md)、[构筑最小兑现](../projects/backpack-survivor/build-payoff-dual-wield.md)、[内容面铺开](../projects/backpack-survivor/content-expansion-fire-rate-boost.md)、[精英宝箱与终局压力强化](../projects/backpack-survivor/elite-chests-endgame-pressure.md)、[金币掉落与局内经济 HUD](../projects/backpack-survivor/gold-drops-and-economy-hud.md)、[背包价值与物品价值显示](../projects/backpack-survivor/backpack-value-and-item-value-display.md)、[合并升级收益兑现](../projects/backpack-survivor/merge-upgrade-reward-payoff.md)、[V0.1 阶段复盘](../reviews/2026/backpack-survivor-v0.1-review.md)。
>
> 仍未理解或缺少证据：Profiler 前后数据、目标平台 Build、实际 `.asmdef` / `.meta` 资产复核、静态注册表跨场景清理、`GoldOrb.OnCollected` 静态事件生命周期、金币池化/磁吸状态复位、`InventoryGrid.GetTotalScoreValue()` 纯 C# 回归测试、`RunResult.BackpackValue` 终局快照实测、ItemView / TotalValueText 射线确认、ItemTooltipView 接线、合并升级当前值回归、FireRateBoost 升级收益实测、伤害数字格式确认、升级多选队列、波次阶段切换/阶段门卫实测、精英/普通池概率采样、宝箱权重统计、GLB 闪白池化恢复观察、战斗反馈资源接线、热路径日志清理复核、胜利/失败后的刷怪停止、池所有权、结算统计准确性、Build Settings 场景路径、DualWield Play Mode 结果、FireRateBoost Play Mode 结果和基础芯片数值平衡。
