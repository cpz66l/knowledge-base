# 第 39 课：背包构筑效果扩展

> 状态：项目中使用 / 用户复盘记录
> 对应版本：V0.3.3
> 证据归属：用户 `inbox/V0.3.3背包构筑效果扩展复盘.md`；用户记录完成实机回归，本环境未运行 Unity Editor、Play Mode、Profiler 或 Player Build
> 关联内容：[邻接效果架构升级](adjacency-effect-architecture.md)、[性能优化记录](performance-optimization-log.md)

## 模块目标

V0.3.2 完成邻接收益汇总层后，V0.3.3 用新玩法验证这套架构，并把背包收益拆成两层：

```text
放入背包 = 被动构筑收益
摆好位置 = 邻接构筑收益
```

本模块新增：

- 瞄准镜邻接武器，提供暴击率加成。
- 背包全局被动汇总层，承接机械臂、护甲、磁吸核心。
- 不同消费侧分别读取武器上限、玩家免伤和拾取范围。
- 记录 `PickUpMagnet` 每个掉落物订阅背包变化的性能隐患。

## 邻接收益：瞄准镜暴击

`CritBoost` 链路：

```text
AdjacencyRuleBook
  武器 Up + Scope Down -> CritBoost
        ↓
AdjacencyEffectResolver
  Stackable effects 放行 CritBoost
        ↓
BackpackEffectCollector
  CritBoost 汇总到目标武器 BackpackItemModifier
        ↓
BackpackWeaponActivator
  注入 AutoWeapon / WeaponBase
        ↓
WeaponBase.Fire
  stats.CritChance + backpackCritChanceBonus
```

这个效果验证了 V0.3.2 的架构收益：新增一个数值邻接效果，不需要在 `BackpackWeaponActivator` 中再写一整套扫描逻辑。

## 全局被动收益

新增 `BackpackGlobalModifier` 表示当前背包整体提供的收益：

```text
ActiveWeaponLimitBonus
DamageReductionBonus
PickupRangeBonus
```

新增 `BackpackPassiveCollector` 输入 `InventoryGrid.GetUniqueItems()`，输出当前背包被动汇总：

| 物品 | 被动收益 | 消费侧 |
|---|---|---|
| `MechanicalArm` | 激活武器上限 +1，最多生效一个 | `BackpackWeaponActivator` |
| `Armor` | 免伤加成 | `Health.TakeDamage` |
| `MagnetCore` | 拾取范围加成 | `PickUpMagnet` |

选择“每次背包变化重新汇总”，而不是“捡到时加一次、丢弃时减一次”，因为背包物品可以拖拽、丢弃、合成和重开。重新汇总更不容易留下旧状态残留。

## 三条收益链路

### 邻接数值收益

```text
InventoryGrid.ScanAdjacency
  ↓
AdjacencyEffectResolver.ResolveValidEffects
  ↓
BackpackEffectCollector.Collect
  ↓
BackpackItemModifier
  ↓
BackpackWeaponActivator.ApplyModifierToAutoWeapon
  ↓
WeaponBase / AutoWeapon
```

用于攻速、伤害、暴击等“作用到某把武器”的收益。

### 背包全局被动收益

```text
InventoryGrid.GetUniqueItems
  ↓
BackpackPassiveCollector.Collect
  ↓
BackpackGlobalModifier
  ↓
BackpackWeaponActivator / Health / PickUpMagnet
```

用于激活武器上限、免伤、拾取范围等“作用到整局角色状态”的收益。

### 表现说明链路

```text
ItemTooltipView.Show(item)
  ↓
根据 ItemTag 显示收益说明
```

UI 不参与规则，只负责解释当前物品价值。

## 关键设计判断

| 判断 | 原因 |
|---|---|
| 机械臂做被动，不做邻接 | 它改变构筑容量，放进背包即可产生装备价值更直观 |
| 护甲不写入 `PlayerRunStats` | 护甲是当前背包状态，不是升级成长；写入 Stats 容易出现丢弃 / 合成后残留 |
| 磁吸核心和升级拾取范围分乘区 | 升级成长与背包装备来自两套系统，分乘区让两者都有体感 |
| 护甲 + 医疗邻接暂缓 | 生存流基础价值已成立，持续回血会牵涉战斗节奏和站撸风险 |

## 回归测试记录

用户复盘记录覆盖：

```text
瞄准镜邻接后暴击率提升，移走后失效
机械臂放入背包后激活武器上限 +1，多个机械臂只生效一个
护甲放入背包后受伤降低，丢掉后恢复
磁吸核心放入背包后吸附距离变远，丢掉后恢复
升级免伤 + 护甲免伤封顶正常
升级拾取范围 + 磁吸核心共同生效
重开局不残留上一局背包被动
Tooltip 能解释新增构筑物品收益
危险 using 扫描干净
```

用户反馈当前效果没有明显问题。知识库记录为用户实践证据，不等同于本环境亲自运行 Unity。

## 风险与挂账

| 风险 | 说明 | 后续动作 |
|---|---|---|
| `EffectValue` 语义分化 | 攻速、伤害、暴击、武器上限、免伤、磁吸都复用同一字段 | 后续考虑 `ItemEffectType` 或 ScriptableObject 数据化 |
| `PickUpMagnet` 重复订阅背包变化 | 每个掉落物各自订阅 `InventoryGrid.OnChanged` 并重复汇总被动 | 掉落物数量上升或 Profiler 指向尖刺时，改为共享 `BackpackPassiveRuntime` |
| Tooltip 分支变长 | 物品越来越多后，按 `ItemTag` 写描述会膨胀 | 后续拆独立 formatter 或数据化描述 |

## 面试表达

- V0.3.3 的核心不是多加几个物品，而是把背包收益拆成“单武器邻接 modifier”和“全局被动 modifier”。
- `PlayerRunStats` 保持升级成长事实源，不承接随背包变化的临时状态。
- 对低频事件先保持简单，但把未来量级风险写进性能记录，等 Profiler 证明后再优化。

