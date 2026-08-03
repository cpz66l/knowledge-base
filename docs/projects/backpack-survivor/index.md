# Backpack Survivor（背包幸存者）

> 状态：V0.2 合并升级收益兑现已记录，准备进入第 27 课数值调参台与首轮平衡
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
- 用 `RunResult`、`GameSession.EndRun()` 和 `ResultView` 把胜利/失败、结果快照、结算面板、重开/退出和环形 XP HUD 接成单局收尾闭环。
- 用 `AdjacencyRuleBook`、`AdjacencyEffectResolver` 和 `BackpackWeaponActivator` 让 `DualWield` 从候选邻接效果变成真实战斗收益，并让 UI 显示真实有效效果。
- 用 `LootEntry` 源头字段、长期物品池、三类自动武器、`FireRateBoost` 和 TMP 字体资产链，把 Demo 从最小构筑兑现推进到内容面铺开。
- 用普通/精英敌人分池、WaveStage 奖励参数、宝箱品质曲线和 GLB 闪白材质替换，把 Demo 推进到终局压力强化。
- 用 `GoldOrb`、`GameSession.TotalGold` 和 `RunHudView.goldText` 把金币掉落、散落飞行、磁吸拾取、局内统计和 HUD 显示接成闭环。
- 用 Item.ScoreValue、InventoryGrid.GetTotalScoreValue()、InventoryUIController.totalValueText 和 RunResult.BackpackValue 把单件价值、背包总价值和结算页价值快照接成闭环。
- 用 BaseScoreValue / BaseEffectValue、等级推导当前收益、ItemTooltipView 和可调攻速上限，把合并升级从视觉等级推进到价值、效果和战斗收益兑现。

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
| 第 20 课 | [胜负结算与重开闭环](run-result-and-restart-loop.md) | 已记录；课程记录描述已实现终局结果快照、结算面板、重开/退出按钮、击杀统计、环形 XP HUD 和血条 Slider 显示化修复，本环境完成静态审阅 |
| 第 21 课 | [构筑最小兑现](build-payoff-dual-wield.md) | 已记录；课程记录描述已实现邻接规则事实源、有效效果解析器、双持防三持、双持额外激活和 UI 真实有效效果投影，本环境完成静态审阅 |
| 第 22 课 | [内容面铺开](content-expansion-fire-rate-boost.md) | 已记录；课程记录描述已实现 `LootEntry` 源头字段、长期物品池、三类自动武器、`FireRateBoost` 和 TMP 中文字体修复，本环境完成静态审阅 |
| 第 23 课 | [精英宝箱与终局压力强化](elite-chests-endgame-pressure.md) | 已记录；课程记录描述已实现普通/精英分池、宝箱品质曲线、终局压力强化和 GLB 闪白修复，本环境完成静态审阅 |
| 第 24 课 | [金币掉落与局内经济 HUD](gold-drops-and-economy-hud.md) | 已记录；课程记录描述已实现金币掉落、`GoldOrb`、散落飞行、局内金币统计和 HUD 显示，本环境完成静态审阅 |
| 第 25 课 | [背包价值与物品价值显示](backpack-value-and-item-value-display.md) | 已记录；课程记录描述已实现单件物品价值、背包总价值、唯一物品去重和结算页背包价值快照，本环境完成静态审阅 |
| 第 26 课 | [合并升级收益兑现](merge-upgrade-reward-payoff.md) | 已记录；课程记录描述已实现合并升级后的价值 / 效果收益、FireRateBoost 升级收益、物品 Tooltip 和伤害数字显示修正，本环境完成静态审阅 |

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
- 第 20 课课程记录描述了 `RunResult`、`GameSession.EndRun()`、`OnRunEnded`、`ResultView`、击杀统计、重开/退出按钮、环形 XP HUD 和血条 Slider 显示化修复。本环境只读复核了项目工作区相关脚本、`.meta` 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode 或验证真实结算、按钮、场景重载或 Build 行为。当前还发现 `EditorBuildSettings.asset` 指向 `Run1.unity`，而实际检查到的场景文件是 `01-Run.unity`，重开路径需在 Unity 中复核。
- 第 21 课课程记录描述了 `AdjacencyRuleBook`、`AdjacencyEffectResolver`、`BackpackWeaponActivator.TryActivateItem()`、`ActivateDualWieldWeapons()` 和 `InventoryUIController` 改用真实有效效果投影。本环境只读复核了项目工作区相关脚本、`.meta`、`BS.Inventory.asmdef` 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode 或验证真实双持、三持防护、UI 高亮和战斗收益。
- 第 22 课课程记录描述了 `LootEntry` 扩展为背包物品源头数据、`Item` 保存价值与效果数值、入包/丢弃往返保真、长期掉落表、三类自动武器、`FireRateBoost` 聚合封顶和 TMP 中文字体修复。本环境只读复核了外部 Unity 工程相关脚本、`.meta`、掉落表资产、`01-Run.unity` 武器槽位、TMP Settings、字体 SDF、DamageNumber 与 ItemView 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 23 课课程记录描述了普通/精英敌人分池、`WaveStage` 同时下发敌人和宝箱参数、15 分钟终局压力曲线、宝箱品质权重曲线和 GLB 受击闪白修复。本环境只读复核了外部 Unity 工程相关脚本、`.meta`、敌人 Prefab、掉落资产和 `01-Run.unity` 阶段配置，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 24 课课程记录描述了金币掉落、`GoldOrb`、金币散落飞出、局内金币统计和 HUD 显示。本环境只读复核了外部 Unity 工程相关脚本、`GoldDrop.asset`、`GoldOrb.prefab`、`.meta` 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 25 课课程记录描述了单件物品价值、背包总价值、唯一物品去重和结算页背包价值快照。本环境只读复核了外部 Unity 工程相关脚本、ItemView.prefab、.meta 和  1-Run.unity 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 26 课课程记录描述了合并升级后的价值 / 效果收益、FireRateBoost 升级收益、物品 Tooltip 和伤害数字显示修正。本环境只读复核了外部 Unity 工程相关脚本、ItemTooltipView.cs、.meta 和  1-Run.unity 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。

## 下一步

- 第 6 课工程 hygiene 资料尚未入库，后续收到后再补。
- 第 27 课推进数值调参台与首轮平衡，重点处理弹夹 / FireRateBoost 基础值、等级倍率、攻速上限、敌人血量成长和伤害显示格式。
- 基础芯片更多邻接、物品/规则配置进一步数据化、最终评分模型、金币结算字段、Tooltip 生效收益区分和真实冷却遮罩继续挂账。
- 为 `TargetRegistry` 增加场景/Play Mode 清理、按阵营计数和失效目标处理。
- 补做低帧率、多 Collider、命中缓冲区满载、刷怪点合法性、跨池归还、批量拾取、拖拽中断、交互拾取失败、宝箱生成、宝箱品质样本、精英生成比例、金币掉落/飞行/磁吸/HUD、金币重开清零、丢弃回捡、ItemView / TotalValueText 射线、唯一物品总价值、拖拽/合并后的总价值刷新、`BackpackValue` 结算快照、合并升级收益、Tooltip 显示/隐藏/射线、FireRateBoost 升级收益、伤害数字格式、邻接扫描、背包武器激活、暂停恢复、胜负入口、升级选择、倍率消费、多级连升队列、波次切换、胜负后刷怪停止、终局刷怪压力、GLB 闪白视觉、结算面板显示、ResultView 订阅位置、Restart 场景重载、Build Settings 场景路径、QuitButton Build 行为、XP 圆环和 HUD Slider Navigation 测试。
- 使用 Profiler 验证预热量、扩容次数、索敌、物理查询、UI 重绘、经验球吸附、金币吸附、宝箱生成、散落协程、邻接扫描、背包武器激活刷新、HUD 刷新、Tooltip、升级面板、波次 HUD、结算面板、终局刷怪压力、伤害数字池、闪白材质替换、音效播放、Cinemachine 震屏和 GC Alloc。
