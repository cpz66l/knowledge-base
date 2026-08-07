# 攻击芯片效果实装

> 学习状态：项目中使用
>
> 验证状态：待验证。用户记录已实测，本次未重复运行 Unity。
>
> 前置知识：[武器稀有度与等级差异](weapon-rarity-and-level-scaling.md)、[内容面铺开](content-expansion-fire-rate-boost.md)、[构筑最小兑现](build-payoff-dual-wield.md)
>
> 对应项目：[Backpack Survivor](index.md)
>
> 下一步：[第 31 课物品图标与背包可读性](item-icons-and-backpack-readability.md)
>
> 日期：2026-08-05
>
> 阶段：V0.2 掉落与背包构筑 · 第 30 课

## 学习目标

- 把 `AttackDamageChip` 从 Tooltip 数值推进成真实战斗收益。
- 用 `AdjacencyEffectId.DamageBoost` 接入既有邻接规则体系，而不是在武器逻辑里写物品特判。
- 让攻击芯片只作用于真实激活武器，避免未激活武器旁的芯片偷加当前输出。
- 在 `WeaponBase.Fire()` 中建立基础伤害、玩家升级、武器品质和攻击芯片四个乘区。
- 为可叠加攻击芯片设置背包伤害倍率上限，并在全量刷新前重置旧倍率。
- 让 Tooltip 明确区分弹匣的攻速收益、攻击芯片的伤害收益和武器本体的品质收益。

## 当前理解

第 30 课解决的是“攻击芯片已经有配置和 Tooltip，但还没有进入真实战斗”的断层。当前实现没有绕过邻接系统，而是把攻击芯片作为一种新的邻接效果接到原链路：

```text
AdjacencyRuleBook
  -> InventoryGrid.ScanAdjacency()
  -> AdjacencyEffectResolver.ResolveValidEffects()
  -> BackpackWeaponActivator.ActivateDamageBoost()
  -> WeaponBase.Fire()
```

这让攻击芯片继续由“物品标签 + 接触方向 + 有效效果 + 激活武器”共同决定。玩家必须把芯片贴到正确方向，并且芯片相邻的是当前真实激活的武器，伤害数字才会变高。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `AdjacencyEffectId.DamageBoost` | 表达攻击伤害加成这种邻接效果 |
| `AdjacencyRuleBook` | 定义手枪、步枪、霰弹枪与 `AttackDamageChip` 的方向规则 |
| `AdjacencyEffectResolver` | 继续对 `DualWield` 做互斥，同时放行 `FireRateBoost` 与 `DamageBoost` |
| `WeaponBase.backpackDamageBoostMultiplier` | 保存背包攻击芯片乘区，默认 `1f` |
| `WeaponBase.SetBackpackDamageBoostMultiplier()` | 提供写入攻击芯片倍率的入口，当前下限钳到 `1f` |
| `BackpackWeaponActivator.maxBackpackDamageBoostMultiplier` | 限制多芯片叠加后的最大伤害倍率 |
| `ActivateDamageBoost()` | 按真实激活 `AutoWeapon` 累加相邻芯片 `EffectValue` 并写回倍率 |
| `DeactivateAllWeapons()` | 刷新前重置攻速、武器品质和攻击芯片三类背包倍率 |
| `ItemTooltipView` | 区分显示“攻速”、“伤害”和“伤害提升” |

## 最小示例

### 新增 DamageBoost 效果

```csharp
public enum AdjacencyEffectId
{
    None = 0,
    DualWield,
    FireRateBoost,
    CritBoost,
    HazardResistBoost,
    BurningBullets,
    DamageBoost
}
```

效果 ID 是邻接系统内部的语言。用 enum 表达 `DamageBoost`，可以让规则表、Resolver 和战斗应用层围绕同一个标识协作，避免字符串拼写导致规则静默失效。

### 规则表加入攻击芯片方向

```csharp
new AdjacencyRule(
    ItemTag.Rifle,
    ConnectableSides.Up,
    ItemTag.AttackDamageChip,
    ConnectableSides.Down,
    AdjacencyEffectId.DamageBoost),
```

当前外部工程静态可见手枪、步枪和霰弹枪都已有 `AttackDamageChip` 规则。规则仍然由 `ItemTag + ConnectableSides + EffectId` 共同定义，不把攻击芯片做成随便贴任意边都生效的全局装备。

### Resolver 放行 DamageBoost

```csharp
public static List<AdjacencyEffect> ResolveValidEffects(List<AdjacencyEffect> candidateEffects)
{
    List<AdjacencyEffect> validEffects = new List<AdjacencyEffect>();
    if (candidateEffects == null) return validEffects;

    AddValidDualWieldEffects(candidateEffects, validEffects);
    AddValidFireRateBoostEffects(candidateEffects, validEffects);
    AddValidDamageBoostEffects(candidateEffects, validEffects);

    return validEffects;
}
```

第一版 `DamageBoost` 和 `FireRateBoost` 一样全部放行，层数控制放到应用层用倍率上限处理。这样以后如果要改成按芯片实例限用、按武器类型限层或按稀有度改上限，可以在策略层做，而不污染候选扫描。

### WeaponBase 四乘区

```csharp
protected float backpackWeaponMultiplier = 1f;
protected float backpackDamageBoostMultiplier = 1f;

float rawDamage = damage
    * stats.DamageMultiplier
    * backpackWeaponMultiplier
    * backpackDamageBoostMultiplier;
```

四个来源的语义变清楚：

```text
damage                         = 武器 prefab 基础伤害
stats.DamageMultiplier          = 玩家升级乘区
backpackWeaponMultiplier        = 武器稀有度 / 等级乘区
backpackDamageBoostMultiplier   = 攻击芯片邻接乘区
```

这比把所有伤害加成都揉进一个字段更容易调参，也更容易解释为什么“高品质武器 + 玩家升级 + 攻击芯片”会互相放大。

### 按真实激活武器应用芯片

```csharp
private void ActivateDamageBoost(List<AdjacencyEffect> validEffects)
{
    Dictionary<AutoWeapon, float> damageBonusByWeapon = new Dictionary<AutoWeapon, float>();

    foreach (AdjacencyEffect effect in validEffects)
    {
        if (effect == null) continue;
        if (effect.EffectId != AdjacencyEffectId.DamageBoost) continue;

        if (TryGetActiveAutoWeapon(effect.ItemA, out AutoWeapon autoWeaponA))
        {
            if (damageBonusByWeapon.ContainsKey(autoWeaponA))
                damageBonusByWeapon[autoWeaponA] += effect.ItemB.EffectValue;
            else
                damageBonusByWeapon[autoWeaponA] = effect.ItemB.EffectValue;
        }
        else if (TryGetActiveAutoWeapon(effect.ItemB, out AutoWeapon autoWeaponB))
        {
            if (damageBonusByWeapon.ContainsKey(autoWeaponB))
                damageBonusByWeapon[autoWeaponB] += effect.ItemA.EffectValue;
            else
                damageBonusByWeapon[autoWeaponB] = effect.ItemA.EffectValue;
        }
    }
}
```

核心边界是 `TryGetActiveAutoWeapon()`。邻接扫描只说明“背包里存在这条连接”，战斗应用还必须确认哪一侧是真实激活武器。未激活武器旁边的芯片不应该绕过激活上限给当前武器加伤害。

## 项目中的应用

### 攻击芯片不是玩家升级

`PlayerRunStats` 表达本局升级成长；攻击芯片表达背包布局收益。把芯片倍率写进 `AutoWeapon` 的背包乘区后，每次背包变化都能通过全量刷新重新计算，不需要反向扣回 `PlayerRunStats`，也不容易残留旧状态。

### DamageBoost 与 FireRateBoost 分乘区

`FireRateBoost` 改攻击间隔，`DamageBoost` 改单发伤害。它们都会影响 DPS，但调参手段和玩家体感不同：

```text
FireRateBoost -> AutoWeapon.SetBackpackFireRateMultiplier()
DamageBoost   -> WeaponBase.SetBackpackDamageBoostMultiplier()
```

分开以后，攻速和伤害可以各自封顶、各自做 Tooltip、各自做后续平衡。

### 刷新前必须清旧倍率

`BackpackWeaponActivator` 采用“先全关，再按当前背包重算”的策略。新增 `DamageBoost` 后，关闭阶段必须同步重置：

```text
SetBackpackFireRateMultiplier(1f)
SetBackpackWeaponMultiplier(1f)
SetBackpackDamageBoostMultiplier(1f)
```

否则拿走攻击芯片后，旧布局的伤害倍率可能继续留在武器实例上。

### Tooltip 区分三类伤害语义

第 29 课已经让武器 Tooltip 显示“伤害提升”，第 30 课继续把芯片文案拆清楚：

```text
Magazine：攻速 +xx%
AttackDamageChip：伤害 +xx%
Pistol / Rifle / Shotgun：伤害提升 +xx%
```

玩家看到的不是泛泛的“效果”，而是能直接指导摆放决策的属性名。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 攻击芯片只显示不生效 | 只更新 Tooltip，没有接入邻接效果和武器乘区 | 按 EffectId -> RuleBook -> Resolver -> Activator -> WeaponBase 顺序接线 |
| 未激活武器旁的芯片也加成 | 只看 validEffects，不看 `activeWeaponsByItem` | 应用层必须先 `TryGetActiveAutoWeapon()` |
| 拿走芯片后伤害不回落 | 新倍率没进入刷新重置流程 | `DeactivateAllWeapons()` 同步重置攻击芯片倍率 |
| DamageBoost 污染玩家升级 | 把背包布局收益写进 `PlayerRunStats` | 保持玩家升级乘区和背包芯片乘区分离 |
| 攻速和伤害难以单独调参 | 把 FireRateBoost / DamageBoost 混进同一字段 | 分别维护攻速倍率和伤害倍率 |
| 规则表方向写错 | 邻接边没有成对接触 | 按实际接触边写，例如武器 `Up` 对芯片 `Down` |
| Tooltip 信息太泛 | 统一写“效果 +xx%” | 根据 `ItemTag` 写“攻速”或“伤害” |

## 如何验证

### 当前已记录证据

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 30 课攻击芯片已通过用户实测，不邻接不加伤害、贴对方向后伤害数字变高、拿走后倍率回落 | B | 来自用户放入 Inbox 的课程记录 |
| 用户记录显示 DamageBoost 与 FireRateBoost 分别影响伤害和攻速，且能与玩家升级、武器稀有度 / 等级乘区共同工作 | B | 来自用户课程验收记录 |
| 外部工程静态可见 `AdjacencyEffectId.DamageBoost` 与攻击芯片规则 | C | 本环境只读查看 `AdjacencyEffectId.cs` 与 `AdjacencyRuleBook.cs` |
| `AdjacencyEffectResolver` 静态可见 `AddValidDamageBoostEffects()` | C | 本环境只读查看外部 Unity 工程脚本 |
| `WeaponBase.cs` 静态可见 `backpackDamageBoostMultiplier`、setter 和四乘区 `rawDamage` | C | 本环境只读查看外部 Unity 工程脚本 |
| `BackpackWeaponActivator.cs` 静态可见 `maxBackpackDamageBoostMultiplier = 2f`、`ActivateDamageBoost()` 和刷新前倍率重置 | C | 本环境只读查看外部 Unity 工程脚本 |
| `ItemTooltipView.cs` 静态可见 `Magazine` 显示攻速、`AttackDamageChip` 显示伤害、武器显示伤害提升 | C | 本环境只读查看外部 Unity 工程脚本 |
| 当前环境未运行 Unity Editor / Play Mode、Profiler 或 Player Build | D | 未启动 Unity，未亲自复测真实画面、伤害数字、性能或 Build |

### 待补验证

- 用 Play Mode 录制攻击芯片贴合前后同一武器的真实伤害数字。
- 复核拿走攻击芯片、拖动换位、合并升级后倍率是否立即回落或刷新。
- 复核多个攻击芯片叠加时是否被 `maxBackpackDamageBoostMultiplier` 正确封顶。
- 复核未激活武器旁的攻击芯片不会影响当前激活武器。
- 用 Profiler / Player Build 复核多次背包重绘和邻接扫描没有明显热路径问题。
- 为 `ActivateDamageBoost()` 增加纯 C# 或可隔离回归测试，覆盖“哪一侧是激活武器”和“同武器多芯片累加”。

## 复盘

- 原来的理解：攻击芯片可以像弹匣一样直接读 `EffectValue` 加到武器上。
- 实践后的结论：芯片收益必须先进入邻接候选，再经过有效效果和真实激活武器过滤，最后写入独立乘区。
- 仍未理解：缺少当前环境亲自运行的 Play Mode 伤害样本、倍率封顶样本和自动化回归测试。

## 相关内容

- 前置：[武器稀有度与等级差异](weapon-rarity-and-level-scaling.md)
- 前置：[内容面铺开](content-expansion-fire-rate-boost.md)
- 前置：[构筑最小兑现](build-payoff-dual-wield.md)
- 前置：[旋转邻接方向修正](rotation-adjacency-direction-fix.md)
- 后续：[物品图标与背包可读性](item-icons-and-backpack-readability.md)
- C#：[C# 工程实践路线](../../csharp/engineering/index.md)
- 检查清单：[Unity 项目能力](../../checklists/unity-project.md)

> 标签：`Unity` `背包构筑` `AttackDamageChip` `DamageBoost` `邻接效果` `数值乘区` `Tooltip` `项目实践`
