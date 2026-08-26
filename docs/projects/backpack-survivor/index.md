# Backpack Survivor（背包幸存者）

> 状态：项目中使用
>
> 当前进度：V0.3.11 已整理至第 46 课；V0.2 正式 Windows 演示包已由用户验收，V0.3 已完成内容深度、反馈包装、敌人变化、设置能力、本地留存和 Release 文案整理
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
- 用 FireRateBoost 基础值、等级倍率、2.0x 攻速上限、伤害源头取整、波次敌人血量和宝箱距离 HUD，把 15 分钟 Demo 推进到首轮平衡验证。
- 用 `RotationState`、本地方向 / 世界方向转换、正反向邻接匹配和拖拽 ghost 刷新，把旋转从宽高表现推进到真实邻接规则语义。
- 用 `WeaponItemStatResolver`、武器实例伤害倍率、Tooltip 规则复用和 `InventoryGrid.TryMerge()` 语义刷新，把武器稀有度 / 等级差异兑现到真实伤害和 UI 解释。
- 用 `DamageBoost`、攻击芯片乘区和真实激活武器过滤，把 `AttackDamageChip` 从 Tooltip 数值推进到实际伤害收益。
- 用 `ItemIconResolver`、透明物品图标、等级星星和邻接接边，把背包格子从开发期文字显示推进到更可读的 Demo 表现。
- 用 `MainMenuController`、`EditorBuildSettings.asset` 和 `ResultView` 返回主菜单逻辑，把项目从直接进入测试场推进到主菜单、Run、结算、回流的 Demo 启动闭环。
- 用 Tab 背包开关、装备散落飞行、`LootEntry.level` 等级保真、`TargetRegistry.Clear()` / `LootChest.ResetRuntimeState()` 和 URP Lit 地面材质，把 Demo 的演示包装和重开稳定性继续收口。
- 用玩法说明面板、外部试玩反馈和主动瞄准高度平面修正，把 V0.2 从功能验收推进到完整 15 分钟试玩验收。
- 用 Profiler 快扫证据包、Build 试玩反馈、显式运行时视觉材质和 `MaterialPropertyBlock`，把性能疑点与 Build 颜色异常分开处理。
- 用 Windows Build Profile、Player Settings、场景顺序、输入资产引用和独立 exe 验收，把项目推进到 V0.2 正式演示包。

V0.3 已开始围绕构筑深度继续扩展：

- 用 `LevelUpOptionDefinition`、`LevelUpOptionGenerator`、权重、等级门槛和选择次数记录，把升级系统从固定三选一扩展成可维护候选池。
- 用 `PlayerRunStats` 统一承接伤害、暴击、射程、拾取、经济、生命和武器上限等本局升级属性，并接到真实消费侧。
- 用 `BackpackItemModifier` 和 `BackpackEffectCollector` 把数值类邻接效果从 `BackpackWeaponActivator` 中拆出，让攻速、伤害、暴击等单武器收益走统一汇总链路。
- 用 `BackpackGlobalModifier` 和 `BackpackPassiveCollector` 把机械臂、护甲、磁吸核心等“放入背包即生效”的全局被动收益与邻接收益分层。
- 用瞄准镜暴击邻接、机械臂武器上限、护甲免伤、磁吸核心拾取范围和 Tooltip 说明验证 V0.3 架构可继续扩内容。
- 用内容池扩展、`scoreValue / effectValue` 价值分层、`Item.Id` 优先图标解析和同类武器槽位上限，把构筑规则落到可感知内容和数值投放。
- 用 `SfxPlayer` cue 表、`WeaponSfxId`、通用 `SfxId`、场景 BGM 和跨场景 UI 点击音，把反馈系统从零散音效升级为可扩展音频链路。
- 用 `GameSettings`、`SettingsService`、`SettingsPanelView`、`PlayerPrefs`、音量倍率和分辨率 / 窗口模式，把设置菜单从 UI 控件扩展为可持久化、可跨场景生效的基础选项系统。
- 用 `EnemyMovement`、分离力、障碍避让、低频错峰采样和方向平滑，把敌群移动从直接追击推进到开放竞技场局部 steering。
- 用 `RangedEnemyAI`、`ProjectilePoolProvider`、`EnemySpawner` 和 `WaveDirector` 把远程敌人接入正式波次混编，让中后期战斗加入走位压力。
- 用 `SaveData`、`SaveService`、`RunResult` 和 `MainMenuRecordView` 补第一版本地 JSON 战绩存档，让总局数、胜场、最高背包价值、局外金币和传说带出数据跨重启保留。
- 用 V0.3 Release 文案和阶段复盘，把构筑深度、反馈包装、敌人变化、局外留存和发布验证整理成作品集表达材料。
- 记录 `PickUpMagnet` 多掉落物重复订阅背包变化的性能挂账，后续由 Profiler 和掉落量级决定是否引入共享被动缓存服务。

## 实践记录

| 课次 | 内容 | 状态 |
|---|---|---|
| 第 1 课 | [伤害管线与危险区](damage-pipeline-and-hazard-zone.md) | 项目中使用；Unity 版本与更完整边界测试待补充 |
| 第 2 课 | [敌人追击、近战与死亡流程](enemy-ai-and-melee.md) | 项目中使用；Kimi 外部检查代码与 Unity 场景 |
| 第 3 课 | [目标注册表、自动武器与投射物](target-registry-and-auto-weapon.md) | 项目中使用；池化边界在第 5 课继续修复 |
| 第 4 课 | [主动武器与 WeaponBase 提炼](active-weapons-and-weapon-base.md) | 项目中使用；主动/自动武器共用投射物管线 |
| 第 5 课 | [刷怪器与对象池](spawner-and-object-pooling.md) | 项目中使用；敌人与投射物完成池化复用 |
| 第 7 课 | [掉落系统与保底机制](loot-drop-and-pity.md) | 项目中使用；静态检查发现零权重表空引用边界待修正 |
| 第 8 课 | [拾取与磁吸](pickup-and-magnet.md) | 项目中使用；静态事件退订、Unity 假 null 和批量拾取副作用待验证 |
| 第 9 课 | [背包纯数据网格](inventory-data-grid.md) | 项目中使用；纯 C# 数据层已完成本环境编译与最小运行测试，asmdef 资产配置待 Unity 工程复核 |
| 第 10 课 | [背包 UI 与拖拽](inventory-ui-and-drag.md) | 项目中使用；课程记录描述已实现自动入包、拖拽预览和非法回弹，本环境完成静态审阅 |
| 第 11 课 | [掉落分层与交互拾取](loot-layering-and-interaction.md) | 项目中使用；课程记录描述已实现两级掉落、经验球自动拾取和装备交互拾取，本环境完成静态审阅 |
| 第 12 课 | [容器搜刮与宝箱系统](container-looting-and-chests.md) | 项目中使用；课程记录描述已实现宝箱交互、击杀生成、地图边界和散落协程，本环境完成静态审阅 |
| 第 13 课 | [背包交互补丁](inventory-interaction-patches.md) | 项目中使用；课程记录描述已修复提示框射线、丢弃、R 键旋转和请求-确认拾取，本环境完成静态审阅 |
| 第 14 课 | [合并升级与邻接联动](merge-upgrade-and-adjacency.md) | 项目中使用；课程记录描述已实现同名同级合并、标签、接口边、邻接扫描和接口点 UI，本环境完成静态审阅 |
| 第 15 课 | [背包武器激活](backpack-weapon-activation.md) | 项目中使用；课程记录描述已实现背包武器实体激活、左上优先级、激活角标和拖拽延迟重绘，本环境完成静态审阅 |
| 第 16 课 | [单局框架与基础 HUD](run-session-and-basic-hud.md) | 项目中使用；课程记录描述已实现单局状态、倒计时、经验显示、暂停恢复和胜负入口，本环境完成静态审阅 |
| 第 17 课 | [经验成长与三选一](level-progression-and-choice.md) | 项目中使用；课程记录描述已实现等级成长、升级选择、运行时倍率和消费侧接入，本环境完成静态审阅 |
| 第 18 课 | [波次导演与 15 分钟节奏](wave-director-and-run-pacing.md) | 项目中使用；课程记录描述已实现波次导演、阶段表、刷怪参数调度和波次 HUD，本环境完成静态审阅 |
| 第 19 课 | [战斗反馈快包](combat-feedback-pack.md) | 项目中使用；课程记录描述已实现受击闪色、池化伤害数字、短音效入口、玩家受伤反馈和 Cinemachine 震屏，本环境完成静态审阅 |
| 第 20 课 | [胜负结算与重开闭环](run-result-and-restart-loop.md) | 项目中使用；课程记录描述已实现终局结果快照、结算面板、重开/退出按钮、击杀统计、环形 XP HUD 和血条 Slider 显示化修复，本环境完成静态审阅 |
| 第 21 课 | [构筑最小兑现](build-payoff-dual-wield.md) | 项目中使用；课程记录描述已实现邻接规则事实源、有效效果解析器、双持防三持、双持额外激活和 UI 真实有效效果投影，本环境完成静态审阅 |
| 第 22 课 | [内容面铺开](content-expansion-fire-rate-boost.md) | 项目中使用；课程记录描述已实现 `LootEntry` 源头字段、长期物品池、三类自动武器、`FireRateBoost` 和 TMP 中文字体修复，本环境完成静态审阅 |
| 第 23 课 | [精英宝箱与终局压力强化](elite-chests-endgame-pressure.md) | 项目中使用；课程记录描述已实现普通/精英分池、宝箱品质曲线、终局压力强化和 GLB 闪白修复，本环境完成静态审阅 |
| 第 24 课 | [金币掉落与局内经济 HUD](gold-drops-and-economy-hud.md) | 项目中使用；课程记录描述已实现金币掉落、`GoldOrb`、散落飞行、局内金币统计和 HUD 显示，本环境完成静态审阅 |
| 第 25 课 | [背包价值与物品价值显示](backpack-value-and-item-value-display.md) | 项目中使用；课程记录描述已实现单件物品价值、背包总价值、唯一物品去重和结算页背包价值快照，本环境完成静态审阅 |
| 第 26 课 | [合并升级收益兑现](merge-upgrade-reward-payoff.md) | 项目中使用；课程记录描述已实现合并升级后的价值 / 效果收益、FireRateBoost 升级收益、物品 Tooltip 和伤害数字显示修正，本环境完成静态审阅 |
| 第 27 课 | [数值调参台与首轮平衡](balance-tuning-and-first-playtest.md) | 项目中使用；课程记录描述已实现 FireRateBoost 回调、伤害源头取整、波次敌人血量、宝箱距离 HUD 和首轮 15 分钟试玩，本环境完成静态审阅 |
| 第 28 课 | [旋转邻接方向修正](rotation-adjacency-direction-fix.md) | 项目中使用；课程记录描述已实现四状态旋转、本地 / 世界接口转换、正反向邻接匹配、拖拽中接口刷新和丢弃原始朝向还原，本环境完成静态审阅 |
| 第 29 课 | [武器稀有度与等级差异](weapon-rarity-and-level-scaling.md) | 项目中使用；课程记录描述已实现武器稀有度 / 等级伤害差异、Tooltip 可读性和合并后即时刷新，本环境完成静态审阅 |
| 第 30 课 | [攻击芯片效果实装](attack-damage-chip-effect.md) | 项目中使用；课程记录描述已实现 DamageBoost、攻击芯片伤害乘区、真实激活武器过滤和 Tooltip 文案区分，本环境完成静态审阅 |
| 第 31 课 | [物品图标与背包可读性](item-icons-and-backpack-readability.md) | 项目中使用；课程记录描述已实现图标解析、透明图标、等级星星、邻接接边和矩形适配，本环境完成静态审阅 |
| 第 32 课 | [主菜单与场景流](main-menu-and-scene-flow.md) | 项目中使用；课程记录描述已实现主菜单、制作者声明、Build Settings 场景顺序和结算返回主菜单，本环境完成静态审阅 |
| 第 33 课 | [场景氛围与演示包装](scene-atmosphere-and-demo-polish.md) | 项目中使用；课程记录描述已实现演示包装、Tab 背包、装备散落、等级保真、静态状态重置和 Lit 地面材质，本环境完成静态审阅 |
| 第 34 课 | [完整 15 分钟通关验收](full-run-acceptance.md) | 项目中使用；用户记录完整链路验收和外部试玩理解门槛，本环境静态复核玩法说明入口与主动瞄准高度平面修正 |
| 第 35 课 | [Profiler 快扫与低风险优化](profiler-sweep-and-low-risk-optimization.md) | 项目中使用；用户记录 Build 后期无明显卡顿和 BUG-025 修复，本环境静态复核 Profiler 证据包、显式材质与 MPB 链路 |
| 第 36 课 | [Build 与演示包](build-and-demo-package.md) | 项目中使用；用户记录正式 Windows exe 独立验收通过，本环境静态复核 Build Profile、Player Settings、场景顺序、输入资产和 Build 输出 |
| 第 37 课 | [升级候选池模块](level-up-option-pool.md) | 项目中使用；用户复盘记录候选池、权重、等级门槛、选择次数和真实消费侧，本环境整理文档，未运行 Unity |
| 第 38 课 | [邻接效果架构升级](adjacency-effect-architecture.md) | 项目中使用；用户记录一轮实机试玩回归未发现问题，本环境整理文档，未运行 Unity |
| 第 39 课 | [背包构筑效果扩展](backpack-build-effects-extension.md) | 项目中使用；用户记录瞄准镜、机械臂、护甲、磁吸核心和 Tooltip 回归通过，本环境整理文档，未运行 Unity / Profiler |
| 第 40 课 | [内容池扩展与价值平衡](content-pool-and-value-balance.md) | 项目中使用；用户记录内容池、价值曲线、图标、Tooltip、宝箱和武器槽位实机回归全绿，本环境整理文档，未运行 Unity |
| 第 41 课 | [基础音频系统与 BGM](audio-system-and-bgm.md) | 项目中使用；用户记录武器音效、通用短音效、BGM、跨场景按钮音实机效果良好，本环境整理文档，未运行 Unity |
| 第 42 课 | [设置菜单与基础选项](settings-menu-and-basic-options.md) | 项目中使用；用户记录设置面板、音量倍率、分辨率、跨场景保留和 `dotnet build` 通过，本环境整理文档，未重复运行 Unity / dotnet build |
| 第 43 课 | [敌人寻路与群体移动优化](enemy-movement-steering.md) | 项目中使用；用户记录敌群移动更稳、完整跑局无大问题和 `dotnet build` 通过，本环境整理文档，未重复运行 Unity / dotnet build |
| 第 44 课 | [远程敌人与波次混编](ranged-enemies-and-wave-mix.md) | 项目中使用；用户记录远程敌人生成、射击、命中、死亡掉落和波次混编完整跑局无明显问题，本环境整理文档，未重复运行 Unity / dotnet build |
| 第 45 课 | [本地存档与最高纪录](local-save-and-records.md) | 项目中使用；用户记录 JSON 存档、重启保留、坏档兜底和弹窗遮罩验收，本环境整理文档，未重复运行 Unity / dotnet build |
| 第 46 课 | [V0.3 Release 文案与发布验收](v0.3-release-notes.md) | 发布准备；用户草稿记录 V0.3 Windows Build、设置、Profiler 快扫和实机试玩结论，本环境整理文档，未运行 Build |

项目级记录：[Bug 记录簿](bug-log.md)、[性能优化记录](performance-optimization-log.md)。

阶段总结：[V0.1 阶段复盘](../../reviews/2026/backpack-survivor-v0.1-review.md)、[V0.3 版本复盘](../../reviews/2026/backpack-survivor-v0.3-review.md)。

面试表达：[面试复盘第 01 阶段](../../reviews/2026/backpack-survivor-interview-stage-01.md)。

## 当前验证证据

- 原始学习记录描述了实际运行结果：玩家进入危险区持续掉血，离开后停止，死亡后不再受伤。
- 本知识库环境使用 .NET SDK 和最小 Unity API 桩完成了脚本编译，并通过 `Health` 扣血/死亡守卫、危险区进入/tick/退出的逻辑冒烟测试；但没有真实 Unity 物理场景、Prefab 或运行截图，因此不能代替 Unity 场景复测。
- 第 2～5 课课程记录描述了敌人追击、双武器、自动索敌、扫掠命中、刷怪和对象池的场景运行结果。
- 用户补充说明 Kimi 已检查代码与 Unity 场景；知识库将其记录为外部检查证据。后续整理中，本环境对外部 Unity 工程做过多轮静态复核，但仍不声称亲自复现了 Unity Play Mode、Profiler 或 Player Build 运行结果。
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
- 第 20 课课程记录描述了 `RunResult`、`GameSession.EndRun()`、`OnRunEnded`、`ResultView`、击杀统计、重开/退出按钮、环形 XP HUD 和血条 Slider 显示化修复。本环境只读复核了项目工作区相关脚本、`.meta` 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode 或验证真实结算、按钮、场景重载或 Build 行为。第 20 课当时发现的 `Run1.unity` Build Settings 残留已在第 32 课静态复核中确认修正为 MainMenu / `01-Run`。
- 第 21 课课程记录描述了 `AdjacencyRuleBook`、`AdjacencyEffectResolver`、`BackpackWeaponActivator.TryActivateItem()`、`ActivateDualWieldWeapons()` 和 `InventoryUIController` 改用真实有效效果投影。本环境只读复核了项目工作区相关脚本、`.meta`、`BS.Inventory.asmdef` 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode 或验证真实双持、三持防护、UI 高亮和战斗收益。
- 第 22 课课程记录描述了 `LootEntry` 扩展为背包物品源头数据、`Item` 保存价值与效果数值、入包/丢弃往返保真、长期掉落表、三类自动武器、`FireRateBoost` 聚合封顶和 TMP 中文字体修复。本环境只读复核了外部 Unity 工程相关脚本、`.meta`、掉落表资产、`01-Run.unity` 武器槽位、TMP Settings、字体 SDF、DamageNumber 与 ItemView 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 23 课课程记录描述了普通/精英敌人分池、`WaveStage` 同时下发敌人和宝箱参数、15 分钟终局压力曲线、宝箱品质权重曲线和 GLB 受击闪白修复。本环境只读复核了外部 Unity 工程相关脚本、`.meta`、敌人 Prefab、掉落资产和 `01-Run.unity` 阶段配置，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 24 课课程记录描述了金币掉落、`GoldOrb`、金币散落飞出、局内金币统计和 HUD 显示。本环境只读复核了外部 Unity 工程相关脚本、`GoldDrop.asset`、`GoldOrb.prefab`、`.meta` 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 25 课课程记录描述了单件物品价值、背包总价值、唯一物品去重和结算页背包价值快照。本环境只读复核了外部 Unity 工程相关脚本、ItemView.prefab、.meta 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 26 课课程记录描述了合并升级后的价值 / 效果收益、FireRateBoost 升级收益、物品 Tooltip 和伤害数字显示修正。本环境只读复核了外部 Unity 工程相关脚本、ItemTooltipView.cs、.meta 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 27 课课程记录描述了 FireRateBoost 基础值回调、等级倍率表、2.0x 攻速上限、伤害源头取整、波次敌人血量、宝箱距离 HUD 和首轮 15 分钟试玩。本环境只读复核了外部 Unity 工程相关脚本、掉落表资产、`ChestDistanceView.cs`、`.meta` 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 28 课课程记录描述了四状态 `RotationState`、本地方向到世界方向转换、正反向邻接匹配、拖拽 ghost 接口刷新和丢弃原始朝向还原；用户记录已通过 Unity 内测。本环境只读复核了外部 Unity 工程相关脚本与 `.meta`，并完成静态审阅和文档构建；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 29 课课程记录描述了武器稀有度 / 等级伤害差异、玩家升级倍率与武器倍率乘区、Tooltip 可读性和合并后即时刷新。本环境只读复核了外部 Unity 工程中的 `WeaponItemStatResolver.cs`、`WeaponBase.cs`、`BackpackWeaponActivator.cs`、`InventoryGrid.cs`、`ItemTooltipView.cs`、`.meta` 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 30 课课程记录描述了 `AttackDamageChip` 真实参与战斗、DamageBoost 与 FireRateBoost 分乘区、旧倍率重置和 Tooltip 文案区分；用户记录已通过实测。本环境只读复核了外部 Unity 工程中的 `AdjacencyEffectId.cs`、`AdjacencyRuleBook.cs`、`AdjacencyEffectResolver.cs`、`WeaponBase.cs`、`BackpackWeaponActivator.cs`、`ItemTooltipView.cs` 和 `01-Run.unity` 中的关键 YAML 引用，并完成静态审阅；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 31 课课程记录描述了物品图标、透明 PNG、等级星星、邻接接边、矩形适配和拖拽 / 旋转 / Tooltip 兼容；用户记录称 `dotnet build` 通过。本环境只读复核了外部 Unity 工程中的 `ItemIconResolver.cs`、`InventoryUIController.cs`、`ItemView.cs`、`ItemView.prefab`、`01-Run.unity`、图标 PNG / `.meta` 和图标 manifest；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。当前静态检查仍看到 `ItemView.cs` 金色接边 `alpha = 8f`，与课程记录“alpha 控制在 0～1”存在差异，后续需确认。
- 第 32 课课程记录描述了 MainMenu 场景、`MainMenuController`、制作者声明、CanvasScaler 适配、Build Settings 顺序和 `ResultView` 返回主菜单；用户记录称已通过实测与代码验收。本环境只读复核了外部 Unity 工程中的 `MainMenuController.cs`、`ResultView.cs`、`EditorBuildSettings.asset`、`MainMenu.unity`、主菜单图片资源和 `.meta`；未运行 Unity Editor / Play Mode 或 Player Build。
- 第 33 课课程记录描述了装备散落、Tab 背包开关、丢弃回捡等级保真、重开静态状态清理和 Lit 地面 / 阴影链路；用户记录称已通过实测与代码验收。本环境只读复核了外部 Unity 工程中的 `LootManager.cs`、`DropItem.cs`、`InventoryUIController.cs`、`GameInput.inputactions`、`LootEntry`、`Item.cs`、`InventorySystem.cs`、`TargetRegistry.cs`、`LootChest.cs`、`GameSession.cs`、`M_Ground_Quarantine_Lit.mat`、`.meta` 和 `01-Run.unity` 关键 YAML 引用；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 34 课课程记录描述了完整 15 分钟试玩验收、外部试玩反馈、主菜单玩法说明和主动射击高度平面修正；用户记录称已通过代码巡检和基础构建验证。本环境只读复核了外部 Unity 工程中的 `MainMenuController.cs`、`InputReader.cs`、`ActiveWeapon.cs`、`PlayerController.cs`、`MainMenu.unity` 和 `01-Run.unity` 关键 YAML 引用；未运行 Unity Editor / Play Mode、Profiler 或 Player Build。
- 第 35 课课程记录描述了 Profiler 快扫、Build 后期无明显卡顿、BUG-025 颜色异常修复和大体积 Profiler 捕获忽略策略；用户记录称 Build 实测约 `6000` 分无明显卡顿。本环境只读复核了外部项目 `Docs/ProfilerEvidence/README.md`、Profiler 轻量截图存在性、`.gitignore`、`Projectile.cs`、`DropItem.cs`、运行时视觉材质 Prefab 引用和脚本危险 using / 日志扫描；未运行 Unity Profiler 或 Player Build。
- 第 36 课课程记录描述了正式 Windows 演示包输出、Build Profile、Player Settings、UI Input Module 引用修复、日志清理和独立 exe 验收；用户记录称正式包独立运行验收通过。本环境只读复核了外部 Unity 工程 Windows Build Profile、`ProjectSettings.asset`、`EditorBuildSettings.asset`、MainMenu / Run 场景输入资产引用、Build 目录和 zip 文件存在性，以及 `Assets/BackpackSurvivor` `.meta` 配对情况；未运行 exe。
- 第 37 课 V0.3.1 复盘记录描述了升级候选池、权重、等级门槛、选择次数、同轮不重复、`PlayerRunStats` 扩展和真实消费侧接入；本环境整理为知识页，未运行 Unity Editor / Play Mode 或 Player Build。
- 第 38 课 V0.3.2 复盘记录描述了 `BackpackItemModifier`、`BackpackEffectCollector`、数值类邻接收益汇总和现有双持 / 芯片行为回归；用户记录一轮实机试玩未发现问题，本环境未运行 Unity Editor / Play Mode 或 Player Build。
- 第 39 课 V0.3.3 复盘记录描述了 `CritBoost`、`BackpackGlobalModifier`、`BackpackPassiveCollector`、机械臂 / 护甲 / 磁吸核心消费侧和 Tooltip 说明；用户记录实机回归通过，本环境未运行 Unity Editor、Profiler 或 Player Build。
- 第 40 课 V0.3.4 复盘记录描述了内容池扩展、五档掉落池、价值曲线、`Item.Id` 优先图标解析、Tooltip、宝箱投放和同类武器槽位；用户记录实机回归全绿，本环境未运行 Unity Editor、Profiler 或 Player Build。
- 第 41 课 V0.3.5 复盘记录描述了 `SfxPlayer` cue 表、`WeaponSfxId`、通用短音效、BGM、跨场景按钮音和胜负反馈；用户记录实机测试效果良好，本环境未运行 Unity Editor、Profiler 或 Player Build。
- 第 42 课 V0.3.6 复盘记录描述了 `GameSettings`、`SettingsService`、`SettingsPanelView`、`PlayerPrefs`、音量倍率、分辨率和窗口模式；用户记录 `dotnet build BackpackSurvivor/BackpackSurvivor.sln --no-restore` 通过，本环境未重复运行 Unity 或 dotnet build。
- 第 43 课 V0.3.7 复盘记录描述了 `EnemyMovement`、局部分离力、障碍避让、低频错峰采样、方向平滑和绕行方向记忆；用户记录实机跑局后移动明显更稳且 `dotnet build` 通过，本环境未重复运行 Unity、Profiler 或 dotnet build。
- 第 44 课 V0.3.8-V0.3.9 复盘记录描述了 `RangedEnemyAI`、`ProjectilePoolProvider`、远程敌方子弹复用、`EnemySpawner` 远程概率和 `WaveDirector` 混编；用户记录完整跑局无明显问题且 `dotnet build` 通过，本环境未重复运行 Unity、Profiler 或 dotnet build。
- 第 45 课 V0.3.10 复盘记录描述了 `SaveData`、`SaveService`、`RunResult` 扩展、`MainMenuRecordView`、JSON 持久化、坏档兜底和弹窗遮罩；用户记录重启保留和 `dotnet build` 通过，本环境未重复运行 Unity 或 dotnet build。
- 第 46 课 V0.3.11 Release 文案记录了 V0.3.0 Windows Demo 的主要更新、运行方式、操作说明、已知说明和验证结论；Build、Profiler 和试玩结论来自用户记录，本环境未运行 Build 或发布流程。

## 下一步

- V0.3 阶段已经形成[版本复盘](../../reviews/2026/backpack-survivor-v0.3-review.md)。下一步不建议立刻追 Boss 或大系统，优先围绕构筑内容深度、收益展示、局外金币消费出口和作品集表达继续推进。
- 第 6 课工程 hygiene 资料尚未入库，后续收到后再补。
- 物品/规则配置进一步数据化、最终评分模型、金币结算字段、Tooltip 生效收益区分、真实冷却遮罩和 `PickUpMagnet` 背包被动共享缓存继续挂账。
- 为 `TargetRegistry` 增加场景/Play Mode 清理、按阵营计数和失效目标处理。
- 补做低帧率、多 Collider、命中缓冲区满载、刷怪点合法性、跨池归还、批量拾取、拖拽中断、交互拾取失败、宝箱生成、宝箱品质样本、精英生成比例、金币掉落/飞行/磁吸/HUD、金币重开清零、ItemView / TotalValueText / ChestDistanceText 射线、合并升级收益、Tooltip、FireRateBoost / DamageBoost 样本、波次血量与 TTK、旋转邻接、图标 Sprite 显示、金色接边 alpha、15 分钟重复试玩样本、Build 目标平台回归和作品材料复核。
- 使用 Profiler 做系统化前后对照：预热量、扩容次数、索敌、物理查询、UI 重绘、图标 / 接边布局、经验球 / 金币吸附、宝箱生成、散落协程、邻接扫描、背包武器激活刷新、Tooltip、升级面板、波次 HUD、结算面板、终局刷怪压力、伤害数字池、闪白材质替换、音效播放、Cinemachine 震屏和 GC Alloc。
