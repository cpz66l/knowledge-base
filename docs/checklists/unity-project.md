# Unity 项目能力检查清单

> 用于检查 Unity 知识是否已经落到可运行项目中。未学习的系统保持未勾选。

---

## 核心系统

- [x] 能解释当前项目中关键 MonoBehaviour 的生命周期顺序
- [ ] 能正确选择 Prefab、ScriptableObject 和普通 C# 对象
- [ ] 资源加载和释放有明确的所有者
- [x] UI 不依赖无必要的每帧轮询
- [ ] 场景切换时静态状态、事件和异步任务得到处理

## 数据与依赖

- [ ] 配置数据与运行时状态区分清楚
- [ ] 模块依赖方向能够用一张图说明
- [ ] 不依赖大量隐式全局单例完成通信
- [x] 事件订阅和取消订阅能够成对追踪
- [x] Inspector 引用、运行时查找和资源加载的选择有理由

## 验证与发布

- [x] 核心流程有最小测试或可重复验证步骤
- [x] 使用 Profiler 检查过至少一个真实场景
- [ ] 记录目标平台和关键性能预算
- [x] Build 后验证过功能，而不只在 Editor 中运行
- [x] 项目问题已经写入复盘，而不是只保留在记忆中

## 实践证据

- 项目：[Backpack Survivor](../projects/backpack-survivor/index.md)
- 当前证据：[伤害管线](../projects/backpack-survivor/damage-pipeline-and-hazard-zone.md)、[敌人 AI](../projects/backpack-survivor/enemy-ai-and-melee.md)、[自动武器](../projects/backpack-survivor/target-registry-and-auto-weapon.md)、[主动武器](../projects/backpack-survivor/active-weapons-and-weapon-base.md)、[刷怪器与对象池](../projects/backpack-survivor/spawner-and-object-pooling.md)、[掉落系统](../projects/backpack-survivor/loot-drop-and-pity.md)、[拾取与磁吸](../projects/backpack-survivor/pickup-and-magnet.md)、[背包纯数据网格](../projects/backpack-survivor/inventory-data-grid.md)、[背包 UI 与拖拽](../projects/backpack-survivor/inventory-ui-and-drag.md)、[掉落分层与交互拾取](../projects/backpack-survivor/loot-layering-and-interaction.md)、[容器搜刮与宝箱系统](../projects/backpack-survivor/container-looting-and-chests.md)、[背包交互补丁](../projects/backpack-survivor/inventory-interaction-patches.md)、[合并升级与邻接联动](../projects/backpack-survivor/merge-upgrade-and-adjacency.md)、[背包武器激活](../projects/backpack-survivor/backpack-weapon-activation.md)、[单局框架与基础 HUD](../projects/backpack-survivor/run-session-and-basic-hud.md)、[经验成长与三选一](../projects/backpack-survivor/level-progression-and-choice.md)、[波次导演与 15 分钟节奏](../projects/backpack-survivor/wave-director-and-run-pacing.md)、[战斗反馈快包](../projects/backpack-survivor/combat-feedback-pack.md)、[胜负结算与重开闭环](../projects/backpack-survivor/run-result-and-restart-loop.md)、[构筑最小兑现](../projects/backpack-survivor/build-payoff-dual-wield.md)、[内容面铺开](../projects/backpack-survivor/content-expansion-fire-rate-boost.md)、[精英宝箱与终局压力强化](../projects/backpack-survivor/elite-chests-endgame-pressure.md)、[金币掉落与局内经济 HUD](../projects/backpack-survivor/gold-drops-and-economy-hud.md)、[背包价值与物品价值显示](../projects/backpack-survivor/backpack-value-and-item-value-display.md)、[合并升级收益兑现](../projects/backpack-survivor/merge-upgrade-reward-payoff.md)、[数值调参台与首轮平衡](../projects/backpack-survivor/balance-tuning-and-first-playtest.md)和[旋转邻接方向修正](../projects/backpack-survivor/rotation-adjacency-direction-fix.md)，已形成 V0.1 战斗闭环并推进 V0.2 掉落、拾取、背包、宝箱、交互失败处理、构筑规则、武器激活、单局骨架、基础成长循环、波次节奏、15 分钟压力曲线、基础战斗反馈、单局收尾闭环、DualWield 战斗收益兑现、FireRateBoost 内容面扩展、普通/精英分池、宝箱品质曲线、终局压力强化、金币局内经济 HUD、单件 / 背包价值显示、终局背包价值快照、合并升级当前收益、Tooltip 信息分层、伤害数字显示修正、FireRateBoost 首轮平衡、波次血量成长、宝箱距离 HUD、首轮 15 分钟试玩验证、四状态旋转、本地 / 世界接口转换和旋转邻接方向修正。
- 新增证据：[武器稀有度与等级差异](../projects/backpack-survivor/weapon-rarity-and-level-scaling.md)记录了 `WeaponItemStatResolver`、背包武器实例倍率、Tooltip 规则复用和合并升级后的语义刷新，已把 `Item.Rarity / Item.Level` 纳入激活武器伤害解释链。
- 新增证据：[攻击芯片效果实装](../projects/backpack-survivor/attack-damage-chip-effect.md)记录了 `DamageBoost`、攻击芯片伤害乘区、真实激活武器过滤、倍率封顶和旧状态重置。
- 新增证据：[物品图标与背包可读性](../projects/backpack-survivor/item-icons-and-backpack-readability.md)记录了 `ItemIconResolver`、透明图标、等级星星、邻接接边、矩形适配和图标射线边界。
- 新增证据：[主菜单与场景流](../projects/backpack-survivor/main-menu-and-scene-flow.md)记录了 MainMenu 场景、制作者声明、Build Settings 顺序、CanvasScaler 适配和结算返回主菜单。
- 新增证据：[场景氛围与演示包装](../projects/backpack-survivor/scene-atmosphere-and-demo-polish.md)记录了装备散落、Tab 背包、丢弃回捡等级保真、静态状态重置和 URP Lit 地面 / 阴影链路。
- 新增证据：[完整 15 分钟通关验收](../projects/backpack-survivor/full-run-acceptance.md)记录了用户完整链路试玩、外部试玩理解门槛、主菜单玩法说明和主动瞄准高度平面修正。
- 新增证据：[Profiler 快扫与低风险优化](../projects/backpack-survivor/profiler-sweep-and-low-risk-optimization.md)记录了用户 Profiler 快扫、Build 后期无明显卡顿、BUG-025 颜色修复和大体积捕获忽略策略。
- 新增证据：[Build 与演示包](../projects/backpack-survivor/build-and-demo-package.md)记录了用户正式 Windows exe 独立验收、Build Profile、Player Settings、场景顺序和输入资产引用复核。
- 新增证据：[升级候选池模块](../projects/backpack-survivor/level-up-option-pool.md)记录了升级候选池、权重、等级门槛、选择次数、`PlayerRunStats` 扩展和真实消费侧接入。
- 新增证据：[邻接效果架构升级](../projects/backpack-survivor/adjacency-effect-architecture.md)记录了 `BackpackItemModifier`、`BackpackEffectCollector`、数值类邻接收益汇总和用户实机回归。
- 新增证据：[背包构筑效果扩展](../projects/backpack-survivor/backpack-build-effects-extension.md)记录了 `CritBoost`、`BackpackGlobalModifier`、`BackpackPassiveCollector`、机械臂 / 护甲 / 磁吸核心和 Tooltip 回归；[性能优化记录](../projects/backpack-survivor/performance-optimization-log.md)新增 `PickUpMagnet` 背包被动重复汇总挂账。
- 新增证据：[内容池扩展与价值平衡](../projects/backpack-survivor/content-pool-and-value-balance.md)记录了五档内容池、`scoreValue / effectValue` 分层、`Item.Id` 优先图标解析、宝箱投放和同类武器槽位上限。
- 新增证据：[基础音频系统与 BGM](../projects/backpack-survivor/audio-system-and-bgm.md)记录了 `SfxPlayer` cue 表、武器音效分型、通用短音效、BGM 和跨场景按钮音。
- 新增证据：[设置菜单与基础选项](../projects/backpack-survivor/settings-menu-and-basic-options.md)记录了 `GameSettings`、`SettingsService`、`SettingsPanelView`、`PlayerPrefs`、音量倍率、分辨率和窗口模式。
- 新增证据：[敌人寻路与群体移动优化](../projects/backpack-survivor/enemy-movement-steering.md)记录了 `EnemyMovement`、局部分离力、障碍避让、低频错峰采样、方向平滑和绕行方向记忆。
- 新增证据：[远程敌人与波次混编](../projects/backpack-survivor/ranged-enemies-and-wave-mix.md)记录了 `RangedEnemyAI`、远程投射物复用、`ProjectilePoolProvider`、敌人配置扩展和波次近远混编。
- 新增证据：[本地存档与最高纪录](../projects/backpack-survivor/local-save-and-records.md)记录了 `SaveData`、`SaveService`、`RunResult`、`MainMenuRecordView`、JSON 存档和坏档回退。
- 新增证据：[V0.3 Release 文案与发布验收](../projects/backpack-survivor/v0.3-release-notes.md)记录了 V0.3.0 Windows Demo 更新说明、运行方式、操作说明、已知边界和发布前验证口径。
- 项目记录：[Bug 记录簿](../projects/backpack-survivor/bug-log.md)和[性能优化记录](../projects/backpack-survivor/performance-optimization-log.md)用于集中查询问题家族和优化决策。
- 生命周期证据：[Unity 生命周期](../unity/lifecycle.md)与第 5 课记录了 `Awake` / `Start`、`OnEnable` / `OnDisable`、池化取出/归还和事件订阅修复；用户转述 Kimi 已检查代码与 Unity 场景。
- 复盘证据：[Backpack Survivor V0.1 阶段复盘](../reviews/2026/backpack-survivor-v0.1-review.md)。
- 复盘证据：[Backpack Survivor V0.3 阶段复盘](../reviews/2026/backpack-survivor-v0.3-review.md)记录了 V0.3 内容深度、敌人变化、本地留存、Release 口径和下一阶段方向；阶段数据来自用户复盘，本环境未重新统计外部项目。
- 尚缺证据：系统化 Profiler 前后对照数据（含终局波次压力、战斗反馈、结算面板和 GC Alloc）、目标平台关键性能预算、多 Collider、低帧率、缓冲区满载、切场景静态状态 Play Mode 复测、跨池归还、完整调用顺序矩阵、掉落概率/保底单元测试、批量拾取副作用测试、拖拽中断回滚、宝箱生成、宝箱品质权重样本、精英生成比例样本、金币掉落/飞行/磁吸/HUD、金币重开清零、GoldOrb 池化与磁吸状态复位、GLB 闪白视觉确认、丢弃回捡、交互失败反馈、合并升级、邻接扫描、背包武器激活、DualWield 真实激活、三把手枪防三持、validEffects UI 高亮、暂停恢复、胜负入口、升级选择、倍率消费、多级连升队列、波次切换、Wave HUD 文案/颜色、胜利/失败后的刷怪停止、波次压力与对象池峰值、伤害数字位置/回池、SfxPlayer 资源接线、玩家受击震屏强度、结算面板显示、BackpackValue 结算快照、Restart 场景重载、QuitButton Build 行为、XP 圆环、HUD Slider Navigation、ItemView / TotalValueText 纯展示射线、唯一物品总价值、拖拽/合并后的总价值刷新、合并升级当前价值 / 效果、Tooltip 显示 / 隐藏 / 射线、FireRateBoost 升级收益、伤害数字格式、ItemView 覆盖层 UI、LevelUpChoiceView 接线和实际 `.asmdef` / `.meta` / Prefab / Canvas / Input Actions / Layer 资产复核、FireRateBoost Play Mode 射速变化、2.0x 攻速封顶、伤害显示 / 真实扣血一致性、波次血量 TTK 样本、ChestDistanceText 射线、宝箱距离目标引导、15 分钟重复试玩样本、LootChest 静态列表重开清理 Play Mode 复测、TMP Player Build 中文显示、旋转接口四方向 Play Mode 复测、正反向邻接触发样本、丢弃再拾取旋转态取舍验证、掉落经济正式概率和当前环境对正式 exe 的复测。
- 第 29 课仍缺：Play Mode 武器稀有度 / 等级伤害样本、Lv.2 / Lv.3 合并后即时刷新、DualWield 第二把武器倍率、Legendary 配置、Resolver / Tooltip / `TryMerge` 回归测试和 Profiler / Player Build 复核。
- 第 30 / 31 课仍缺：Play Mode 攻击芯片伤害样本、DamageBoost 叠加封顶、移除芯片后倍率回落、图标 Sprite 显示、透明图标射线、旋转后接边 / 星星重排、金色接边 alpha 修正确认和 Player Build 复核。
- 下一项改进：把 V0.3.7-V0.3.11 压缩成作品集 / 面试表达，并继续为敌群规模、远程敌人站位、本地存档坏档、Release Build、Profiler 前后对照和目标平台性能预算补齐可重复验证。
