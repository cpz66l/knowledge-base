# C# 工程实践路线

> 状态：学习中。此页只建立工程能力目录，不提前补写“最佳实践”结论。

## 学习顺序

1. MonoBehaviour 与纯 C# 类的职责划分
2. 数据、状态、依赖与模块边界
3. 日志、断言、异常和失败流程
4. 命名空间、目录结构与程序集
5. 可测试性、单元测试与回归验证
6. Editor、Build、IL2CPP 与平台差异

## 已有入口

- [C# 工程能力清单](../../checklists/csharp-engineering.md)
- [Unity 专题](../../unity/index.md)
- [Unity 项目能力清单](../../checklists/unity-project.md)
- [项目复盘模板](../../reviews/project-review-template.md)

## 已有实践证据

- [Backpack Survivor：伤害管线与危险区](../../projects/backpack-survivor/damage-pipeline-and-hazard-zone.md)：接口边界、事件发布、伤害数据包、Trigger 缓存和防御式处理。
- [Backpack Survivor：敌人追击、近战与死亡流程](../../projects/backpack-survivor/enemy-ai-and-melee.md)：组件依赖、条件状态分支、跨对象查找缓存和一次性死亡事件闭环。
- [Backpack Survivor：目标注册表、自动武器与投射物](../../projects/backpack-survivor/target-registry-and-auto-weapon.md)：静态注册表、生命周期对称、热路径缓冲区和灰盒实现的演进边界。
- [Backpack Survivor：主动武器与 WeaponBase 提炼](../../projects/backpack-survivor/active-weapons-and-weapon-base.md)：真实重复之后的继承提炼、输入状态位和重构边界。
- [Backpack Survivor：刷怪器与对象池](../../projects/backpack-survivor/spawner-and-object-pooling.md)：接口化池化契约、状态复位、防重复归还和初始化顺序。
- [Backpack Survivor：背包纯数据网格](../../projects/backpack-survivor/inventory-data-grid.md)：纯 C# 数据层、asmdef 隔离、二维数组占格、事件驱动 UI 投影和冗余状态取舍。
- [Backpack Survivor：合并升级与邻接联动](../../projects/backpack-survivor/merge-upgrade-and-adjacency.md)：查询/命令分离、规则表驱动、候选效果与最终结算边界。
- [Backpack Survivor：背包武器激活](../../projects/backpack-survivor/backpack-weapon-activation.md)：全量重算与配置表映射、实例身份标记、事件驱动 UI 的延迟重绘补偿。
- [Backpack Survivor：单局框架与基础 HUD](../../projects/backpack-survivor/run-session-and-basic-hud.md)：状态主人、纯 C# 计时器、事件快照、暂停恢复和胜负入口。
- [Backpack Survivor：经验成长与三选一](../../projects/backpack-survivor/level-progression-and-choice.md)：纯 C# 等级状态、奖励数据边界、升级选择状态和运行时倍率消费。
- [Backpack Survivor：波次导演与 15 分钟节奏](../../projects/backpack-survivor/wave-director-and-run-pacing.md)：时间事实源、执行器/导演拆分、阶段门闸和高频日志清理。
- [Backpack Survivor：战斗反馈快包](../../projects/backpack-survivor/combat-feedback-pack.md)：表现层消费伤害事件、场景 Provider、短音效入口和反馈分支独立降级。
- [Backpack Survivor：胜负结算与重开闭环](../../projects/backpack-survivor/run-result-and-restart-loop.md)：终局结果快照、统一结束入口、结算 UI 投影和场景重载风险边界。
- [Backpack Survivor：构筑最小兑现](../../projects/backpack-survivor/build-payoff-dual-wield.md)：候选效果/有效效果分层、规则事实源上移、按效果类型处理互斥和 UI/战斗共用真实结果。
- [Backpack Survivor：金币掉落与局内经济 HUD](../../projects/backpack-survivor/gold-drops-and-economy-hud.md)：静态掉落事件进入 `GameSession`，再用 `OnGoldChanged` 把局内金币快照投影到 HUD，并记录序列化字段改名风险。
- [Backpack Survivor：背包价值与物品价值显示](../../projects/backpack-survivor/backpack-value-and-item-value-display.md)：数据层价值查询、唯一物品去重、RunResult.BackpackValue 终局快照和 UI 纯投影边界。
- [Backpack Survivor：合并升级收益兑现](../../projects/backpack-survivor/merge-upgrade-reward-payoff.md)：基础值 / 当前值拆分、合并命令与收益公式分离、运行时值不污染配置、Tooltip 投影和伤害显示语义修正。
- [Backpack Survivor：数值调参台与首轮平衡](../../projects/backpack-survivor/balance-tuning-and-first-playtest.md)：规则层 / 表现层伤害语义对齐、直接波次血量注入、静态宝箱列表查询边界和高杠杆数值旋钮。
- [Backpack Survivor：旋转邻接方向修正](../../projects/backpack-survivor/rotation-adjacency-direction-fix.md)：四状态旋转、本地 / 世界方向转换、规则字段成对匹配、失败回滚和运行时效果投影边界。
- [Backpack Survivor：武器稀有度与等级差异](../../projects/backpack-survivor/weapon-rarity-and-level-scaling.md)：Resolver 翻译层、运行时 `Item` 到战斗倍率的事实源、战斗 / Tooltip 共用规则和语义性 `OnChanged` 刷新。
- [Backpack Survivor：攻击芯片效果实装](../../projects/backpack-survivor/attack-damage-chip-effect.md)：按效果类型扩展规则链、按真实激活武器过滤收益、按武器实例聚合倍率和刷新前重置运行时状态。
- [Backpack Survivor：物品图标与背包可读性](../../projects/backpack-survivor/item-icons-and-backpack-readability.md)：表现资源与纯数据层隔离、UI 装饰层射线边界、运行时尺寸驱动布局和配置缺失兜底。
- [Backpack Survivor：主菜单与场景流](../../projects/backpack-survivor/main-menu-and-scene-flow.md)：场景流入口、按钮事件镜像订阅、`Time.timeScale` 恢复、Build Settings 静态配置复核和返回主菜单语义演进。
- [Backpack Survivor：场景氛围与演示包装](../../projects/backpack-survivor/scene-atmosphere-and-demo-polish.md)：运行时等级往返保真、static 本局状态显式 Reset、池化对象飞行协程归零和 UI 开关临时态保护。
- [Backpack Survivor V0.1 阶段复盘](../../reviews/2026/backpack-survivor-v0.1-review.md)：交付范围、设计主线、技术债务和下一阶段计划。

## 最小产出

- 一张模块依赖图
- 一个可脱离场景测试的纯 C# 模块
- 一次 Build 环境验证
- 一份真实工程问题复盘
