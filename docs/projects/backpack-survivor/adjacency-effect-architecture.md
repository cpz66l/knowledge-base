# 第 38 课：邻接效果架构升级

> 状态：项目中使用 / 用户复盘记录
> 对应版本：V0.3.2
> 证据归属：用户 `inbox/V0.3.2邻接效果架构复盘.md`；用户记录完成一轮实机试玩回归，本环境未运行 Unity Editor、Play Mode 或 Player Build
> 关联内容：[构筑最小兑现](build-payoff-dual-wield.md)、[攻击芯片效果实装](attack-damage-chip-effect.md)

## 模块目标

V0.3.1 扩展升级系统后，V0.3.2 转向邻接系统。原先 `BackpackWeaponActivator` 已经承担基础武器激活、双持、品质 / 等级倍率、攻速芯片和伤害芯片收益汇总等职责。

本模块目标不是急着新增效果，而是先把邻接系统拆成更清楚的层级：

- 扫描：背包布局产生候选邻接效果。
- 筛选：解析真实有效效果，例如双持防三持。
- 汇总：数值类收益聚合成按物品查询的 modifier。
- 注入：激活武器并把 modifier 写入战斗侧。
- 表现：UI 只显示真实有效效果。

## 新增结构

### `BackpackItemModifier`

表示某个背包 `Item` 当前从邻接中获得的数值收益：

```text
Item
FireRateBonus
DamageBonus
HasAnyBonus
```

它只保存原始收益，不计算最终倍率，也不负责封顶。

### `BackpackEffectCollector`

负责把 `validEffects` 汇总成 modifier 表：

```text
Collect(validEffects)
  Clear old modifiers
  FireRateBoost -> Add to weapon item modifier
  DamageBoost   -> Add to weapon item modifier

TryGetModifier(item, out modifier)
```

Collector 不认识 `AutoWeapon`，不引用 `UnityEngine`，也不处理 `DualWield`。它只做数值类收益汇总。

## 最终链路

```text
InventoryGrid.ScanAdjacency(AdjacencyRuleBook.Rules)
  ↓
AdjacencyEffectResolver.ResolveValidEffects(candidateEffects)
  ↓
BackpackEffectCollector.Collect(validEffects)
  ↓
BackpackWeaponActivator.RefreshActiveWeapons()
  ↓
TryActivateItem(item)
  ↓
ApplyModifierToAutoWeapon(item, autoWeapon)
  ↓
WeaponBase / AutoWeapon
```

表现层仍走独立链路：

```text
InventoryUIController.Redraw()
  ↓
ScanAdjacency
  ↓
ResolveValidEffects
  ↓
ItemView.SetConnectors(...)
```

UI 只投影规则结果，不参与规则计算。

## 关键取舍

| 取舍 | 原因 |
|---|---|
| `DualWield` 不进 Collector | 它改变武器是否激活，不是数值 modifier |
| 封顶不放进 `BackpackItemModifier` | modifier 保存原始收益，最终倍率和封顶属于消费侧规则 |
| 低频背包刷新可接受少量对象分配 | 当前背包刷新不是每帧逻辑，先保证架构清晰；若 Profiler 证明有尖刺再复用对象 |
| 不抽复杂接口 | 先用两个轻量类解决 Activator 膨胀，避免过度工程化 |

## 回归测试记录

用户复盘记录本模块完成后做了一轮实机试玩回归，覆盖：

```text
双持不占基础名额
三手枪防三持
弹匣攻速芯片生效
攻击芯片伤害生效
双持奖励武器也能吃自己的 modifier
旋转邻接仍按方向触发
断开邻接后旧效果不残留
UI 灰边 / 金边表现不回归
```

用户反馈未发现问题。知识库记录为用户实践证据，不等同于本环境亲自运行 Unity。

## 面试表达

- 我把邻接效果分成激活类和数值类：双持改变是否激活，伤害 / 攻速改变已激活武器的数值。
- `BackpackEffectCollector` 让新增数值效果变成“扩展 modifier 字段 + 汇总 + 消费侧注入”，而不是继续在 Activator 里复制扫描逻辑。
- 重构完成后用旧玩法回归确认行为等价，而不是只看编译通过。

## 待验证

- `IsWeapon(item)` 当前仍有 Demo 阶段硬编码，后续武器类型继续扩展时应改为 `ItemDefinition.IsWeapon`、标签或 resolver。
- `activeWeaponsByItem` 如果只写入不读取，可以在后续清理，减少误导状态。

