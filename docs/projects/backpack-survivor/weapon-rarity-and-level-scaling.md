# 武器稀有度与等级差异

> 学习状态：已应用，待复测
>
> 前置知识：[旋转邻接方向修正](rotation-adjacency-direction-fix.md)、[背包武器激活](backpack-weapon-activation.md)、[合并升级收益兑现](merge-upgrade-reward-payoff.md)
>
> 对应项目：[Backpack Survivor](index.md)
>
> 下一步：[第 30 课攻击芯片效果实装](attack-damage-chip-effect.md)
>
> 日期：2026-08-05
>
> 阶段：V0.2 掉落与背包构筑 · 第 29 课

## 学习目标

- 让同类型武器根据 `Item.Rarity` 和 `Item.Level` 产生可感知的战斗差异。
- 用 `WeaponItemStatResolver` 把背包物品解释为武器实例倍率，避免把数值公式塞进 `BackpackWeaponActivator`。
- 在 `WeaponBase.Fire()` 中建立武器 prefab 基础伤害、玩家升级倍率和背包武器倍率三个乘区。
- 让基础激活和 DualWield 额外激活都走同一个 `TryActivateItem()`，保证每把激活武器吃自己的实例倍率。
- 修正合并升级后 `OnChanged` 漏发的问题，让 UI、Tooltip、背包价值和武器倍率能即时刷新。
- 让 Tooltip 复用同一个 Resolver 解释武器伤害提升，避免 UI 和真实战斗公式分叉。

## 当前理解

第 29 课解决的是掉落期待问题：同类型武器如果只共享一个 prefab，没有稀有度和等级差异，玩家捡到蓝枪、紫枪或合成 Lv.2 武器时只会看到标签变化，战斗体感不够明确。

当前方案不复制多套 prefab，而是在激活武器时把背包中的具体 `Item` 实例解析成倍率：

```text
背包 Item 实例
  -> WeaponItemStatResolver 解析 Rarity / Level
  -> BackpackWeaponActivator 激活 AutoWeapon 时注入倍率
  -> WeaponBase.Fire() 统一计算最终伤害
  -> 子弹真实伤害与伤害数字使用同一结果
```

这里的关键不是“把伤害写大”，而是建立清楚的乘区和事实源：武器类型由 prefab 表达，武器品质由运行时 `Item` 表达，玩家成长由 `PlayerRunStats` 表达。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `WeaponItemStatResolver` | 根据运行时 `Item.Rarity / Item.Level` 输出武器伤害倍率 |
| `WeaponStat` 序列化表 | 在场景中配置不同稀有度对应的基础伤害倍率 |
| `levelDamageMultiplier` | 表示每升一级额外获得的武器等级倍率 |
| `WeaponBase.backpackWeaponMultiplier` | 保存背包武器实例倍率，默认 `1f` |
| `WeaponBase.SetBackpackWeaponMultiplier()` | 提供外部写入倍率的安全入口，当前最小值钳到 `1f` |
| `WeaponBase.Fire()` | 按基础伤害 × 玩家升级倍率 × 背包武器倍率计算最终伤害 |
| `BackpackWeaponActivator.weaponItemStatResolver` | 激活具体背包武器时查询并注入倍率 |
| `DeactivateAllWeapons()` | 每次全量刷新前重置旧攻速倍率和旧武器伤害倍率 |
| `InventoryGrid.TryMerge()` | 合并升级成功时补发语义性 `OnChanged` |
| `ItemTooltipView.weaponItemStatResolver` | Tooltip 显示武器伤害提升，和战斗共用 Resolver |

## 最小示例

### WeaponItemStatResolver

```csharp
public class WeaponItemStatResolver : MonoBehaviour
{
    [System.Serializable]
    private class WeaponStat
    {
        public Rarity rarity;
        public float damageMultiplier = 1f;
    }

    [SerializeField] private List<WeaponStat> weaponStats;
    [SerializeField] private float levelDamageMultiplier = 0.25f;

    public float GetDamageMultiplier(Item item)
    {
        if (item == null || weaponStats == null)
            return 1f;

        foreach (var stat in weaponStats)
        {
            if (stat.rarity == item.Rarity)
                return stat.damageMultiplier *
                    (1 + (item.Level - 1) * levelDamageMultiplier);
        }

        return 1f;
    }
}
```

Resolver 是“背包物品如何被战斗系统理解”的翻译层。`Item` 仍保持数据身份，`BackpackWeaponActivator` 不承担稀有度公式，Tooltip 也不重新写一套倍率表。

### WeaponBase 乘区

```csharp
protected float backpackWeaponMultiplier = 1f;

protected void Fire(Vector3 direction)
{
    sfx?.PlayShoot();

    float rawDamage = damage * stats.DamageMultiplier * backpackWeaponMultiplier;
    float finalDamage = Mathf.RoundToInt(rawDamage);

    Projectile bullet = bulletPool.Get(firePoint.position).GetComponent<Projectile>();
    bullet.Initialize(projectileSpeed, finalDamage, targetFaction, maxDistance, direction, 0f, gameObject);
}

public void SetBackpackWeaponMultiplier(float multiplier)
{
    backpackWeaponMultiplier = Mathf.Max(1f, multiplier);
}
```

实际项目里池化子弹和无池兜底子弹都使用同一个 `rawDamage`。共同事实先算出来，再分支生成投射物，可以避免两条路径伤害不一致。

### 激活具体 Item 时注入倍率

```csharp
if (autoWeapon != null)
{
    activeWeaponsByItem[item] = autoWeapon;

    if (weaponItemStatResolver == null)
        autoWeapon.SetBackpackWeaponMultiplier(1f);
    else
    {
        float weaponDamageMultiplier = weaponItemStatResolver.GetDamageMultiplier(item);
        autoWeapon.SetBackpackWeaponMultiplier(weaponDamageMultiplier);
    }
}
```

倍率按具体 `Item` 实例解析，而不是按 `ItemTag` 解析。这样同样是 `Pistol`，Common Lv.1、Rare Lv.1 和 Rare Lv.2 都能打出不同伤害。

### 合并升级后补发 OnChanged

```csharp
public bool TryMerge(Item source, Item target)
{
    if (!CanMerge(source, target)) return false;
    target.IncreaseLevel();

    bool sourceInGrid = Contains(source);
    Remove(source);

    if (!sourceInGrid)
        OnChanged?.Invoke();

    return true;
}
```

第 29 课把 `OnChanged` 的语义从“格子数组变了”扩展成“背包数据语义变了”。合并升级改变 `target.Level`，会影响价值、Tooltip、武器倍率和芯片效果，即使格子引用没有发生新增删除，也应该广播。

## 项目中的应用

### 武器品质乘区

当前最终伤害链路是：

```text
Weapon prefab 基础 damage
  × PlayerRunStats.DamageMultiplier
  × backpackWeaponMultiplier
  -> Mathf.RoundToInt
  -> Projectile.Initialize(finalDamage)
```

这把“角色成长”和“装备质量”拆成两个来源不同的乘区。玩家升级提高角色火力，高稀有度 / 高等级武器提高装备质量；两者相乘后，高品质武器会更值得围绕它继续构筑。

### 不复制多套 prefab

当前 prefab 继续表达武器类型手感：手枪、步枪、霰弹枪的基础伤害、射速、射程、枪口和投射物仍来自武器实体。运行时 `Item` 和 Resolver 表达掉落到背包里的这把武器品质。

```text
Prefab：这是什么武器类型
Item.Rarity / Item.Level：这件武器实例有多强
Resolver：把实例品质翻译成战斗倍率
```

这比为每个稀有度和等级复制 prefab 更轻，也更适合 Demo 阶段调参。

### DualWield 也吃实例倍率

基础激活和 DualWield 额外激活都调用同一个 `TryActivateItem(item)`。倍率注入写在这个方法里，所以第二把双持武器也会按自己的稀有度和等级计算伤害。

这条统一入口很重要：如果双持额外激活绕过 `TryActivateItem()`，就会出现基础武器有品质倍率，双持奖励武器没有倍率的分裂。

### Tooltip 复用 Resolver

Tooltip 按 `ItemTag` 分流：

```text
Magazine / AttackDamageChip：显示 EffectValue
Pistol / Rifle / Shotgun：显示 Resolver 计算出的伤害提升
其他收集品：显示稀有度、尺寸和价值
```

武器 Tooltip 不重新写稀有度表，而是复用 `WeaponItemStatResolver.GetDamageMultiplier(item)`。UI 的职责是解释真实规则，不是复制规则。

### 当前场景配置

本环境只读复核 `01-Run.unity`，可见 `WeaponItemStatResolver` 已挂入场景，并被 `BackpackWeaponActivator` 和 `ItemTooltipView` 引用。当前静态 YAML 中可见倍率表：

| Rarity 枚举值 | 静态可见倍率 |
|---:|---:|
| `0` | `1.0x` |
| `1` | `1.2x` |
| `2` | `1.4x` |
| `3` | `1.6x` |

`levelDamageMultiplier` 为 `0.25`。这说明 Lv.2 会在稀有度基础倍率上再乘 `1.25x`，Lv.3 再乘 `1.5x`。当前静态表只看到 Common / Uncommon / Rare / Epic 四档，Legendary 是否需要配置仍待后续平衡确认。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 同类武器稀有度没体感 | 只按 `ItemTag` 激活同一个 prefab，没有实例倍率 | 用 `WeaponItemStatResolver` 按 `Item.Rarity / Level` 输出倍率 |
| Activator 变成数值公式桶 | 激活器同时负责找武器、解释稀有度、算等级 | 把公式放进 Resolver，Activator 只消费结果 |
| 芯片和武器共用 `EffectValue` | 字段语义混乱 | 芯片继续用 `EffectValue`，武器品质走 Resolver |
| 双持第二把不吃品质倍率 | DualWield 额外激活绕过统一入口 | 基础激活和奖励激活都走 `TryActivateItem()` |
| 高稀有倍率残留到普通武器 | 刷新前只关闭 GameObject，不重置倍率 | `DeactivateAllWeapons()` 同时重置攻速和武器伤害倍率 |
| 合并升级后伤害不立刻变 | `target.Level` 变化没有触发 `OnChanged` | `TryMerge()` 成功后补发语义事件 |
| 池化与无池伤害不一致 | 两个分支各自计算伤害 | 在分支前统一计算 `rawDamage` 和 `finalDamage` |
| Tooltip 显示和真实倍率不一致 | UI 自己写一套倍率表 | Tooltip 复用 Resolver |
| 代码看着正确但倍率无效 | 场景没有挂 Resolver 或引用为空 | 同时查脚本链路和 `01-Run.unity` 接线 |

## 如何验证

### 当前已记录证据

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 29 课实现武器稀有度 / 等级伤害差异、Tooltip 可读性和合并后即时刷新 | B | 来自用户放入 Inbox 的课程记录 |
| 用户记录已实测不同类型、不同稀有度、不同等级武器伤害有差异，玩家升级倍率会与武器倍率相乘 | B | 用户课程记录描述了测试结果 |
| 外部 Unity 工程存在 `WeaponItemStatResolver.cs` 与 `.meta`，GUID 为 `fb09011c2f9c4004e8b02df8d100c019` | C | 本环境只读查看外部 Unity 工程文件 |
| `WeaponBase.cs` 可见 `backpackWeaponMultiplier`、`SetBackpackWeaponMultiplier()` 和统一 `rawDamage` 计算 | C | 本环境只读查看外部 Unity 工程脚本 |
| `BackpackWeaponActivator.cs` 可见 Resolver 引用、激活时注入倍率、刷新时重置倍率 | C | 本环境只读查看外部 Unity 工程脚本 |
| `InventoryGrid.TryMerge()` 可见合并升级后按 `sourceInGrid` 补发 `OnChanged` | C | 本环境只读查看外部 Unity 工程脚本 |
| `ItemTooltipView.cs` 可见 Tooltip 复用 Resolver 显示武器伤害提升，并区分芯片 / 武器 / 收集品 | C | 本环境只读查看外部 Unity 工程脚本 |
| `01-Run.unity` 中可见 `BackpackWeaponActivator` 与 `ItemTooltipView` 引用同一个 Resolver，倍率表和 `levelDamageMultiplier` 已序列化 | C | 本环境只读查看场景 YAML |
| 当前环境未运行 Unity Editor / Play Mode、Profiler 或 Player Build | D | 未启动 Unity，未亲自复测真实画面、交互、性能或 Build |

### 待补验证

- 用 Play Mode 记录 Common / Uncommon / Rare / Epic 的实际伤害数字，确认与 Resolver 表一致。
- 合并 Lv.2 / Lv.3 武器后立即开火，确认 `OnChanged` 能让倍率即时刷新。
- 测试 DualWield 第二把武器是否按自己的稀有度和等级打出伤害。
- 测试玩家升级伤害倍率与背包武器倍率是否按乘区叠加，而不是覆盖或重复加成。
- 确认 Legendary 武器是否需要进入 `weaponStats` 表；当前静态场景只看到四档配置。
- 增加纯 C# 回归测试覆盖 `TryMerge()` 语义事件、Resolver 默认值和等级倍率公式。
- 用 Profiler / Player Build 复核 Resolver 查表、Tooltip 显示和伤害计算没有明显热路径问题。

## 复盘

- 原来的理解：不同稀有度武器可以等后面多做 prefab 再体现。
- 实践后的结论：Demo 阶段优先用运行时倍率注入建立掉落期待，既能立刻看到伤害差异，又不会复制大量资产。
- 仍未理解：还缺当前环境亲自运行的 Play Mode 伤害样本、Legendary 配置策略和纯 C# 回归测试。

## 相关内容

- 前置：[旋转邻接方向修正](rotation-adjacency-direction-fix.md)
- 前置：[背包武器激活](backpack-weapon-activation.md)
- 前置：[内容面铺开](content-expansion-fire-rate-boost.md)
- 前置：[合并升级收益兑现](merge-upgrade-reward-payoff.md)
- 前置：[数值调参台与首轮平衡](balance-tuning-and-first-playtest.md)
- 后续：[攻击芯片效果实装](attack-damage-chip-effect.md)
- C#：[C# 工程实践路线](../../csharp/engineering/index.md)
- 检查清单：[Unity 项目能力](../../checklists/unity-project.md)

> 标签：`Unity` `背包构筑` `武器倍率` `稀有度` `合并升级` `Tooltip` `数值乘区` `项目实践`
