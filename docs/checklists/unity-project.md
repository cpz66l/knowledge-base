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
- [ ] 使用 Profiler 检查过至少一个真实场景
- [ ] 记录目标平台和关键性能预算
- [ ] Build 后验证过功能，而不只在 Editor 中运行
- [x] 项目问题已经写入复盘，而不是只保留在记忆中

## 实践证据

- 项目：[Backpack Survivor](../projects/backpack-survivor/index.md)
- 当前证据：[伤害管线](../projects/backpack-survivor/damage-pipeline-and-hazard-zone.md)、[敌人 AI](../projects/backpack-survivor/enemy-ai-and-melee.md)、[自动武器](../projects/backpack-survivor/target-registry-and-auto-weapon.md)、[主动武器](../projects/backpack-survivor/active-weapons-and-weapon-base.md)、[刷怪器与对象池](../projects/backpack-survivor/spawner-and-object-pooling.md)、[掉落系统](../projects/backpack-survivor/loot-drop-and-pity.md)、[拾取与磁吸](../projects/backpack-survivor/pickup-and-magnet.md)、[背包纯数据网格](../projects/backpack-survivor/inventory-data-grid.md)、[背包 UI 与拖拽](../projects/backpack-survivor/inventory-ui-and-drag.md)、[掉落分层与交互拾取](../projects/backpack-survivor/loot-layering-and-interaction.md)、[容器搜刮与宝箱系统](../projects/backpack-survivor/container-looting-and-chests.md)、[背包交互补丁](../projects/backpack-survivor/inventory-interaction-patches.md)、[合并升级与邻接联动](../projects/backpack-survivor/merge-upgrade-and-adjacency.md)、[背包武器激活](../projects/backpack-survivor/backpack-weapon-activation.md)、[单局框架与基础 HUD](../projects/backpack-survivor/run-session-and-basic-hud.md)、[经验成长与三选一](../projects/backpack-survivor/level-progression-and-choice.md)、[波次导演与 15 分钟节奏](../projects/backpack-survivor/wave-director-and-run-pacing.md)、[战斗反馈快包](../projects/backpack-survivor/combat-feedback-pack.md)、[胜负结算与重开闭环](../projects/backpack-survivor/run-result-and-restart-loop.md)、[构筑最小兑现](../projects/backpack-survivor/build-payoff-dual-wield.md)、[内容面铺开](../projects/backpack-survivor/content-expansion-fire-rate-boost.md)、[精英宝箱与终局压力强化](../projects/backpack-survivor/elite-chests-endgame-pressure.md)、[金币掉落与局内经济 HUD](../projects/backpack-survivor/gold-drops-and-economy-hud.md)、[背包价值与物品价值显示](../projects/backpack-survivor/backpack-value-and-item-value-display.md)、[合并升级收益兑现](../projects/backpack-survivor/merge-upgrade-reward-payoff.md)、[数值调参台与首轮平衡](../projects/backpack-survivor/balance-tuning-and-first-playtest.md)和[旋转邻接方向修正](../projects/backpack-survivor/rotation-adjacency-direction-fix.md)，已形成 V0.1 战斗闭环并推进 V0.2 掉落、拾取、背包、宝箱、交互失败处理、构筑规则、武器激活、单局骨架、基础成长循环、波次节奏、15 分钟压力曲线、基础战斗反馈、单局收尾闭环、DualWield 战斗收益兑现、FireRateBoost 内容面扩展、普通/精英分池、宝箱品质曲线、终局压力强化、金币局内经济 HUD、单件 / 背包价值显示、终局背包价值快照、合并升级当前收益、Tooltip 信息分层、伤害数字显示修正、FireRateBoost 首轮平衡、波次血量成长、宝箱距离 HUD、首轮 15 分钟试玩验证、四状态旋转、本地 / 世界接口转换和旋转邻接方向修正。
- 新增证据：[武器稀有度与等级差异](../projects/backpack-survivor/weapon-rarity-and-level-scaling.md)记录了 `WeaponItemStatResolver`、背包武器实例倍率、Tooltip 规则复用和合并升级后的语义刷新，已把 `Item.Rarity / Item.Level` 纳入激活武器伤害解释链。
- 生命周期证据：[Unity 生命周期](../unity/lifecycle.md)与第 5 课记录了 `Awake` / `Start`、`OnEnable` / `OnDisable`、池化取出/归还和事件订阅修复；用户转述 Kimi 已检查代码与 Unity 场景。
- 复盘证据：[Backpack Survivor V0.1 阶段复盘](../reviews/2026/backpack-survivor-v0.1-review.md)。
- 尚缺证据：Profiler 前后数据（含终局波次压力、战斗反馈、结算面板和 GC Alloc）、目标平台 Build、多 Collider、低帧率、缓冲区满载、切场景静态状态、跨池归还、完整调用顺序矩阵、掉落概率/保底单元测试、批量拾取副作用测试、拖拽中断回滚、宝箱生成、宝箱品质权重样本、精英生成比例样本、金币掉落/飞行/磁吸/HUD、金币重开清零、GoldOrb 池化与磁吸状态复位、GLB 闪白视觉确认、丢弃回捡、交互失败反馈、合并升级、邻接扫描、背包武器激活、DualWield 真实激活、三把手枪防三持、validEffects UI 高亮、暂停恢复、胜负入口、升级选择、倍率消费、多级连升队列、波次切换、Wave HUD 文案/颜色、胜利/失败后的刷怪停止、波次压力与对象池峰值、伤害数字位置/回池、SfxPlayer 资源接线、玩家受击震屏强度、结算面板显示、BackpackValue 结算快照、Restart 场景重载、Build Settings 场景路径、QuitButton Build 行为、XP 圆环、HUD Slider Navigation、ItemView / TotalValueText 纯展示射线、唯一物品总价值、拖拽/合并后的总价值刷新、合并升级当前价值 / 效果、Tooltip 显示 / 隐藏 / 射线、FireRateBoost 升级收益、伤害数字格式、ItemView 覆盖层 UI、LevelUpChoiceView 接线和实际 `.asmdef` / `.meta` / Prefab / Canvas / Input Actions / Layer 资产复核、FireRateBoost Play Mode 射速变化、2.0x 攻速封顶、伤害显示 / 真实扣血一致性、波次血量 TTK 样本、ChestDistanceText 射线、宝箱距离目标引导、15 分钟重复试玩样本、LootChest 静态列表重开清理、TMP Player Build 中文显示、旋转接口四方向 Play Mode 复测、正反向邻接触发样本、丢弃再拾取旋转态取舍验证和掉落经济正式概率。
- 第 29 课仍缺：Play Mode 武器稀有度 / 等级伤害样本、Lv.2 / Lv.3 合并后即时刷新、DualWield 第二把武器倍率、Legendary 配置、Resolver / Tooltip / `TryMerge` 回归测试和 Profiler / Player Build 复核。
- 下一项改进：进入第 30 课攻击芯片效果实装，并为武器倍率、合并升级收益、Tooltip、伤害数字格式、金币 HUD、背包价值、精英生成比例、宝箱品质分布、终局压力、DualWield、FireRateBoost、波次血量、宝箱距离 HUD、旋转邻接、15 分钟重复试玩、升级选择、倍率消费、波次切换、基础 HUD、战斗反馈资源接线、暂停恢复、结算重开和拖拽取消补齐可重复验证。
