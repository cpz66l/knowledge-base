# Backpack Survivor（背包幸存者）

> 状态：V0.2 战斗反馈快包已记录，准备进入胜负结算与重开闭环
>
> 首次记录：2026-07-20
>
> Unity 版本：Unity6.3

## 项目目标

通过一个可持续扩展的幸存者类项目，把 C#、Unity 组件设计、战斗系统、UI、数据配置和工程验证串成完整实践，而不是只保留互相孤立的知识文章。

## 已完成里程碑

V0.1 已建立战斗核心原型：

- 统一可受伤对象契约。
- 建立通用生命值组件。
- 用危险区、敌人近战和投射物复用同一条伤害管线。
- 完成敌人追击、自动索敌、枪口转向、主动/自动双武器和投射物命中闭环。
- 用刷怪器形成持续战斗，并让敌人和投射物进入对象池复用周期。
- 通过第 5 课修复 `Start` 订阅在对象复用后丢失、生命值未重置等生命周期问题。

V0.2 已开始扩展掉落与背包构筑：

- 用 `LootTableData` 建立掉落表配置。
- 用 `LootRoller` 记录权重随机和保底计数。
- 用 `LootManager` 将敌人死亡、对象池取出和掉落物表现串成一条链路。
- 用 `PickUpMagnet` 和 `DropItem.OnCollected` 将掉落物推进到拾取与临时收货口。
- 用 `BS.Inventory` 纯 C# 程序集和 `InventoryGrid` 建立背包占格数据内核。
- 用 `InventorySystem` 与 UGUI 将拾取自动入包、网格显示、拖拽预览和非法回滚串成闭环。
- 用两级掉落表、`ICollectable`、`IInteractable` 和局部物理查询区分货币自动拾取与装备手动拾取。
- 用 `LootChest`、`ChestSpawner`、`MapBounds` 和散落协程把交互拾取扩展到宝箱搜刮。
- 用丢弃、R 键旋转和请求-确认拾取修复背包交互债务，为合并升级做准备。
- 用同名同级合并、物品标签、方向接口和邻接扫描建立背包构筑规则雏形。
- 用背包位置优先级和 `BackpackWeaponActivator` 将背包武器物品映射到玩家身边自动武器实体。
- 用 `GameSession`、`RunTimer`、`GameState` 和 `RunHudView` 建立单局时间、胜负、暂停、经验显示和基础 HUD。
- 用 `LevelProgress`、`LevelUpChoiceView` 和 `PlayerRunStats` 把经验成长、升级暂停、三选一选择和本局倍率消费接成闭环。
- 用 `WaveDirector`、`WaveStage` 和波次 HUD 建立 15 分钟压力曲线，并让刷怪参数按本局时间调度。
- 用 `DamageFlashView`、`DamageNumberView`、`SfxPlayer` 和 `CameraShakePlayer` 把命中、受伤、升级、开箱等战斗事实翻译成闪色、数字、音效和震屏反馈。

## 实践记录

| 课次 | 内容 | 状态 |
|---|---|---|
| 第 1 课 | [伤害管线与危险区](damage-pipeline-and-hazard-zone.md) | 已实现，待补充 Unity 版本与更完整边界测试 |
| 第 2 课 | [敌人追击、近战与死亡流程](enemy-ai-and-melee.md) | 已应用；Kimi 外部检查代码与 Unity 场景 |
| 第 3 课 | [目标注册表、自动武器与投射物](target-registry-and-auto-weapon.md) | 已应用；池化边界在第 5 课继续修复 |
| 第 4 课 | [主动武器与 WeaponBase 提炼](active-weapons-and-weapon-base.md) | 已应用；主动/自动武器共用投射物管线 |
| 第 5 课 | [刷怪器与对象池](spawner-and-object-pooling.md) | 已应用；敌人与投射物完成池化复用 |
| 第 7 课 | [掉落系统与保底机制](loot-drop-and-pity.md) | 已记录；静态检查发现零权重表空引用边界待修正 |
| 第 8 课 | [拾取与磁吸](pickup-and-magnet.md) | 已记录；静态事件退订、Unity 假 null 和批量拾取副作用待验证 |
| 第 9 课 | [背包纯数据网格](inventory-data-grid.md) | 已记录；纯 C# 数据层已完成本环境编译与最小运行测试，asmdef 资产配置待 Unity 工程复核 |
| 第 10 课 | [背包 UI 与拖拽](inventory-ui-and-drag.md) | 已记录；课程记录描述已实现自动入包、拖拽预览和非法回弹，本环境完成静态审阅 |
| 第 11 课 | [掉落分层与交互拾取](loot-layering-and-interaction.md) | 已记录；课程记录描述已实现两级掉落、经验球自动拾取和装备交互拾取，本环境完成静态审阅 |
| 第 12 课 | [容器搜刮与宝箱系统](container-looting-and-chests.md) | 已记录；课程记录描述已实现宝箱交互、击杀生成、地图边界和散落协程，本环境完成静态审阅 |
| 第 13 课 | [背包交互补丁](inventory-interaction-patches.md) | 已记录；课程记录描述已修复提示框射线、丢弃、R 键旋转和请求-确认拾取，本环境完成静态审阅 |
| 第 14 课 | [合并升级与邻接联动](merge-upgrade-and-adjacency.md) | 已记录；课程记录描述已实现同名同级合并、标签、接口边、邻接扫描和接口点 UI，本环境完成静态审阅 |
| 第 15 课 | [背包武器激活](backpack-weapon-activation.md) | 已记录；课程记录描述已实现背包武器实体激活、左上优先级、激活角标和拖拽延迟重绘，本环境完成静态审阅 |
| 第 16 课 | [单局框架与基础 HUD](run-session-and-basic-hud.md) | 已记录；课程记录描述已实现单局状态、倒计时、经验显示、暂停恢复和胜负入口，本环境完成静态审阅 |
| 第 17 课 | [经验成长与三选一](level-progression-and-choice.md) | 已记录；课程记录描述已实现等级成长、升级选择、运行时倍率和消费侧接入，本环境完成静态审阅 |
| 第 18 课 | [波次导演与 15 分钟节奏](wave-director-and-run-pacing.md) | 已记录；课程记录描述已实现波次导演、阶段表、刷怪参数调度和波次 HUD，本环境完成静态审阅 |
| 第 19 课 | [战斗反馈快包](combat-feedback-pack.md) | 已记录；课程记录描述已实现受击闪色、池化伤害数字、短音效入口、玩家受伤反馈和 Cinemachine 震屏，本环境完成静态审阅 |

阶段总结：[V0.1 阶段复盘](../../reviews/2026/backpack-survivor-v0.1-review.md)。

## 当前验证证据

- 原始学习记录描述了实际运行结果：玩家进入危险区持续掉血，离开后停止，死亡后不再受伤。
- 本知识库环境使用 .NET SDK 和最小 Unity API 桩完成了脚本编译，并通过 `Health` 扣血/死亡守卫、危险区进入/tick/退出的逻辑冒烟测试；但没有真实 Unity 物理场景、Prefab 或运行截图，因此不能代替 Unity 场景复测。
- 第 2～5 课课程记录描述了敌人追击、双武器、自动索敌、扫掠命中、刷怪和对象池的场景运行结果。
- 用户补充说明 Kimi 已检查代码与 Unity 场景；知识库将其记录为外部检查证据。本环境仍没有完整 Unity 工程与 Profiler 数据，因此不声称亲自复现了运行或性能结果。
- 第 7 课课程记录描述了掉落系统、权重随机、保底计数和掉落物超时回收。本环境完成静态审阅，未运行 Unity 场景；其中零权重表、掉落 Prefab 是否接入对象池、`FindAnyObjectByType` 成本和材质实例化仍待项目验证。
- 第 8 课课程记录描述了拾取磁吸、`DropItem.OnCollected` 静态事件和临时 `PickupLogger`。本环境完成静态审阅，未运行 Unity 场景；静态事件生命周期、Unity 假 null、批量拾取副作用和 Profiler 数据仍待验证。
- 第 9 课课程记录描述了 `BS.Inventory` 纯数据程序集、`Item`、`InventoryGrid` 和 Debug.Log 验证剧本。本环境用 .NET SDK 对整理后的纯 C# 数据层完成编译与最小运行测试；未检查实际 `.asmdef`、`.meta` 或 Unity 工程资产。
- 第 10 课课程记录描述了背包 UI、拖拽、红绿预览、非法回弹和拾取自动入包。本环境完成静态审阅和文档构建，未运行 Unity Editor、Play Mode 或检查 Prefab / Canvas 层级。
- 第 11 课课程记录描述了掉落分层、保底修正、经验球自动拾取、装备 E 键交互和提示 UI。本环境完成静态审阅和文档构建，未运行 Unity Editor、Play Mode 或检查 Prefab / Input Actions / Layer 配置。
- 第 12 课课程记录描述了宝箱 `IInteractable` 复用、击杀触发生成、地图边界、拒绝采样和掉落散落协程。本环境完成静态审阅和文档构建，未运行 Unity Editor、Play Mode 或检查 Prefab / 场景 / Layer 配置。
- 第 13 课课程记录描述了提示框射线阻挡修复、面板外丢弃、R 键旋转、`Interact()` 请求-确认和背包满反馈。本环境完成静态审阅和文档构建，未运行 Unity Editor、Play Mode 或检查 Canvas / Input Actions / 场景引用。
- 第 14 课课程记录描述了同名同级合并、`ItemTag`、`ConnectableSides`、邻接规则表、候选效果扫描和接口点 UI。本环境完成静态审阅和文档构建，未运行 Unity Editor、Play Mode 或检查 ItemView Prefab / 字体资源 / `.meta`。
- 第 15 课课程记录描述了 `BackpackWeaponActivator`、`WeaponSlot`、`GetUniqueItems` 左上优先级、激活实例标记、拖拽延迟重绘和覆盖层自适应。本环境完成静态审阅和文档构建，未运行 Unity Editor、Play Mode 或检查 `01-Run.unity` / ItemView Prefab / 字体资源 / `.meta`。
- 第 16 课课程记录描述了 `GameState`、`RunTimer`、`GameSession`、`RunHudView`、暂停恢复、经验显示和基础 HUD。本环境只读复核了项目工作区相关脚本与 `.meta` 存在，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode 或验证场景接线。
- 第 17 课课程记录描述了 `LevelProgress`、`LevelUpOption`、`LevelUpOptionGenerator`、`LevelUpChoiceView`、`PlayerRunStats`、升级选择暂停和倍率消费。本环境只读复核了项目工作区相关脚本、`.meta`、`GameInput.inputactions` 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode 或实际点击升级面板。
- 第 18 课课程记录描述了 `WaveDirector`、`WaveStage`、`EnemySpawner.ApplyWaveSettings()`、`OnWaveStageChanged`、波次 HUD 和 `TargetRegistry` 日志清理。本环境只读复核了项目工作区相关脚本、`.meta` 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode 或验证真实刷怪节奏。
- 第 19 课课程记录描述了 `DamageFlashView`、`DamageNumberView`、`DamageNumberSpawner`、`DamageNumberPoolProvider`、`SfxPlayer`、`PlayerHitFeedbackView` 和 `CameraShakePlayer`。本环境只读复核了项目工作区相关脚本、`.meta`、`Enemy.prefab`、`DamageNumber.prefab`、`manifest.json` 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode 或验证真实闪色、数字、音效、震屏和资源接线。

## 下一步

- 第 6 课工程 hygiene 资料尚未入库，后续收到后再补。
- 第 20 课推进胜负结算与重开闭环。
- 邻接效果结算器、DualWield 战斗兑现、基础芯片多邻接、物品/规则配置数据化和真实冷却遮罩继续挂账。
- 为 `TargetRegistry` 增加场景/Play Mode 清理、按阵营计数和失效目标处理。
- 补做低帧率、多 Collider、命中缓冲区满载、刷怪点合法性、跨池归还、批量拾取、拖拽中断、交互拾取失败、宝箱生成、丢弃回捡、合并升级、邻接扫描、背包武器激活、暂停恢复、胜负入口、升级选择、倍率消费、波次切换、胜负后刷怪停止、刷怪压力、战斗反馈资源接线、伤害数字位置、音效播放和震屏强度测试。
- 使用 Profiler 验证预热量、扩容次数、索敌、物理查询、UI 重绘、经验球吸附、宝箱生成、散落协程、邻接扫描、背包武器激活刷新、HUD 刷新、升级面板、波次 HUD、刷怪压力、伤害数字池、闪色材质访问、音效播放、Cinemachine 震屏和 GC Alloc。
