# 构筑最小兑现

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现 `AdjacencyRuleBook`、`AdjacencyEffectResolver`、`DualWield` 有效效果解析、双持额外激活和 UI 真实有效效果投影；本环境完成静态审阅、项目文件只读复核与文档验证，未运行 Unity Editor / Play Mode
>
> 日期：2026-07-31
>
> 阶段：V0.2 掉落与背包构筑 · 第 21 课

## 学习目标

- 把第 14 课的 `DualWield` 从“邻接候选 + UI 高亮”推进成真实战斗收益。
- 把邻接规则从 UI 中上移到 `AdjacencyRuleBook`，让 UI、战斗和后续数值系统读取同一套事实源。
- 用 `AdjacencyEffectResolver` 区分候选效果和真实有效效果，承载互斥、堆叠和上限规则。
- 让 `DualWield` 只作为基础激活武器的邻接奖励，突破默认自动武器上限但不绕过背包位置优先级。
- 处理三把手枪横排时的“双持候选歧义”，避免中间手枪同时参与两组双持。
- 让 UI 金色接口显示 `validEffects`，不再显示尚未兑现的候选效果。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `AdjacencyRuleBook` | 纯 C# 邻接规则事实源，对外暴露 `IReadOnlyList<AdjacencyRule>` |
| `AdjacencyEffectResolver` | 将 `ScanAdjacency()` 的候选效果筛成真实有效效果 |
| `AddValidDualWieldEffects()` | 对 `DualWield` 单独应用 Item 互斥，防止三把手枪横排变成三持 |
| `BackpackWeaponActivator.TryActivateItem()` | 统一“激活场景武器对象 + 记录激活 Item 实例”的入口 |
| `BackpackWeaponActivator.ActivateDualWieldWeapons()` | 在基础激活上限之外，根据有效双持效果追加激活邻接武器 |
| `InventoryUIController.Redraw()` | 扫描候选效果后先解析 `validEffects`，再投影接口点金色高亮 |
| `InventoryGrid.ScanAdjacency()` | 继续只负责几何、标签和接口边命中，返回候选效果，不裁决玩法生效 |

本课前，背包 UI 已经能显示手枪左右相邻的接口命中，但战斗层还不消费这条效果。玩家看到“像是触发了”，实际收益没有兑现。

第 21 课补上的闭环是：

```text
规则表决定候选
  -> Resolver 决定真实有效
  -> 战斗层消费真实有效效果
  -> UI 层展示真实有效效果
```

这一步让“背包摆法”第一次真实改变战斗实体，是 Backpack Survivor 构筑玩法成立的关键节点。

## 规则事实源

第 14 课为了快速做出接口点表现，邻接规则曾靠近 `InventoryUIController`。第 21 课把规则上移到纯 C# 的 `AdjacencyRuleBook`：

```csharp
public static class AdjacencyRuleBook
{
    public static IReadOnlyList<AdjacencyRule> Rules => rules;

    private static readonly List<AdjacencyRule> rules = new List<AdjacencyRule>
    {
        new AdjacencyRule(
            ItemTag.Pistol,
            ConnectableSides.Right,
            ItemTag.Pistol,
            ConnectableSides.Left,
            AdjacencyEffectId.DualWield),

        new AdjacencyRule(
            ItemTag.Pistol,
            ConnectableSides.Left,
            ItemTag.Pistol,
            ConnectableSides.Right,
            AdjacencyEffectId.DualWield)
    };
}
```

这里的价值不是规则数量，而是职责位置：规则是事实层，UI 是投影层。只要规则藏在 UI 里，战斗层、数值层和后续配置系统都会被迫复制或反向依赖表现代码。

`Rules` 对外暴露为 `IReadOnlyList<AdjacencyRule>`，避免外部拿到 `List<T>` 后直接 `.Add()` 或 `.Clear()`。`readonly List<T>` 只能保证字段引用不被替换，不能保证集合内容不可变。

## 有效效果解析器

`InventoryGrid.ScanAdjacency()` 仍然只回答“规则是否命中”：

```text
两个格子相邻
  -> 不是同一个 Item 实例
  -> 双方接口边匹配
  -> 标签与规则匹配
  -> 生成 AdjacencyEffect 候选
```

真正决定“本轮能不能生效”的职责交给 `AdjacencyEffectResolver`：

```csharp
public static List<AdjacencyEffect> ResolveValidEffects(List<AdjacencyEffect> candidateEffects)
{
    List<AdjacencyEffect> validEffects = new List<AdjacencyEffect>();

    if (candidateEffects == null) return validEffects;

    AddValidDualWieldEffects(candidateEffects, validEffects);

    return validEffects;
}
```

这条分层很重要：

```text
candidateEffects：扫描层发现的候选命中
validEffects：玩法层认可的真实生效效果
```

候选效果可以很多，真实效果要遵守互斥、堆叠、层数、优先级和上限。把这些规则放进 resolver，可以让网格扫描继续保持纯粹。

## DualWield 防三持

三把手枪横排时，候选效果可能是：

```text
A - B - C

A-B 命中 DualWield
B-C 命中 DualWield
```

如果两条都生效，中间的 B 就同时参与两组双持，设计语义会从“双持”变成“三持”或连锁武器网络。

当前 resolver 对 `DualWield` 单独使用 `HashSet<Item>`：

```csharp
private static void AddValidDualWieldEffects(
    List<AdjacencyEffect> candidateEffects,
    List<AdjacencyEffect> validEffects)
{
    HashSet<Item> usedItems = new HashSet<Item>();

    foreach (AdjacencyEffect effect in candidateEffects)
    {
        if (effect == null) continue;
        if (effect.EffectId != AdjacencyEffectId.DualWield) continue;

        if (usedItems.Contains(effect.ItemA)) continue;
        if (usedItems.Contains(effect.ItemB)) continue;

        validEffects.Add(effect);
        usedItems.Add(effect.ItemA);
        usedItems.Add(effect.ItemB);
    }
}
```

注意这里不是“一个物品参与过任何效果就不能再参与效果”，而是只对 `DualWield` 应用互斥。这样未来同一把手枪可以一边双持，一边吃攻速芯片、火焰芯片或暴击芯片；不同效果类型应有不同结算策略。

## 武器激活入口

第 15 课已经让背包物品按左上优先级激活场景武器。第 21 课把激活动作收束到 `TryActivateItem()`：

```csharp
private bool TryActivateItem(Item item)
{
    if (item == null) return false;
    if (activeWeaponItems.Contains(item)) return false;

    foreach (WeaponSlot weapon in weaponSlots)
    {
        if (weapon == null) continue;
        if (weapon.WeaponObject == null) continue;
        if (weapon.WeaponObject.activeSelf) continue;
        if (weapon.Tag != item.Tag) continue;

        weapon.WeaponObject.SetActive(true);
        activeWeaponItems.Add(item);
        return true;
    }

    return false;
}
```

这个入口同时完成两件事：

- 激活场景里的 `WeaponObject`。
- 把背包中的具体 `Item` 实例加入 `activeWeaponItems`。

两件事必须绑定在同一个入口里。否则很容易出现“UI 认为某个 Item 激活了，但场景里复用了同一个武器对象”或“场景武器开了，但 UI 角标没跟上”的分裂状态。

`weapon.WeaponObject.activeSelf` 守卫也很关键。场景里如果配置了两个 `Pistol` 槽，第二把手枪必须找到另一个未激活的手枪对象；不能让两个 Item 都记录为激活，却指向同一个场景武器实体。

## 基础激活与双持追加

刷新顺序是本课的核心：

```csharp
private void RefreshActiveWeapons()
{
    List<AdjacencyEffect> effects = inventorySystem.Grid.ScanAdjacency(AdjacencyRuleBook.Rules);
    List<AdjacencyEffect> validDualWieldEffects = AdjacencyEffectResolver.ResolveValidEffects(effects);

    DeactivateAllWeapons();

    List<Item> items = inventorySystem.Grid.GetUniqueItems();
    int activatedCount = 0;

    foreach (Item item in items)
    {
        if (activatedCount >= activeWeaponLimit) break;

        if (TryActivateItem(item))
            activatedCount++;
    }

    ActivateDualWieldWeapons(validDualWieldEffects);
}
```

这代表当前设计语义：

```text
默认上限先决定基础激活武器
  -> DualWield 只奖励已激活武器的邻接伙伴
```

所以 `DualWield` 不是把 `activeWeaponLimit` 永久改成 2，也不是让任意一组相邻手枪免费激活。它是基础激活武器的构筑奖励。

额外激活逻辑只处理“一方已激活，另一方未激活”的情况：

```csharp
if (itemAActive && !itemBActive)
    TryActivateItem(effect.ItemB);
else if (itemBActive && !itemAActive)
    TryActivateItem(effect.ItemA);
```

如果两把都没激活，就不处理。这样可以保护第 15 课建立的背包位置优先级：放在右下角的两把相邻手枪，不能绕过左上优先规则凭空获得战斗收益。

## UI 显示真实有效效果

第 14 课中 UI 显示的是候选效果。第 21 课改成：

```csharp
List<AdjacencyEffect> candidateEffects = grid.ScanAdjacency(AdjacencyRuleBook.Rules);
List<AdjacencyEffect> validEffects = AdjacencyEffectResolver.ResolveValidEffects(candidateEffects);

ConnectableSides visibleSides = item.GetWorldConnectableSides();
ConnectableSides activeSides = GetActiveSides(item, validEffects);
itemView.SetConnectors(visibleSides, activeSides);
```

灰色接口表示“这件物品这个方向可以连接”。金色接口现在表示“这次真的触发了有效效果”。

这能避免一个很坏的体验：三把手枪横排时 UI 两边都亮金色，但战斗层只兑现一组。玩家看到的承诺和系统实际给的收益必须一致，否则构筑系统会失去可信度。

## 周期链路

```text
背包内容变化
  -> InventoryGrid.OnChanged
  -> BackpackWeaponActivator.RefreshActiveWeapons()
  -> ScanAdjacency(AdjacencyRuleBook.Rules)
  -> AdjacencyEffectResolver.ResolveValidEffects()
  -> 先按 GetUniqueItems() 位置优先级激活基础武器
  -> 再用 DualWield 追加激活邻接武器
  -> activeWeaponItems 记录真实激活的 Item 实例
  -> InventoryUIController.Redraw()
  -> UI 显示激活角标 + validEffects 金色接口
```

这条链路同时解决两类错位：

| 错位 | 修复方式 |
|---|---|
| UI 显示触发，但战斗没有收益 | UI 和战斗都读取 `validEffects` |
| 战斗实际生效，但玩家看不出原因 | UI 金色接口显示真实有效效果 |

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 规则藏在 UI 里 | 为了快速显示，把规则表放在表现层 | 规则上移到 `AdjacencyRuleBook`，UI 和战斗都读同一份 |
| 三把手枪横排变成三持 | 候选 `A-B` 和 `B-C` 都直接生效 | `DualWield` resolver 用 `usedItems` 做同效果互斥 |
| 未来芯片被双持互斥误伤 | 把“Item 参与过效果”做成全局互斥 | 按 `EffectId` 分支处理互斥、堆叠和层数 |
| 双持绕过左上优先级 | 两把都未基础激活也能被额外激活 | 只处理“一方已激活，另一方未激活”的邻接奖励 |
| 两个 Item 复用同一个武器对象 | 激活时不检查 `WeaponObject.activeSelf` | `TryActivateItem()` 跳过已激活的武器对象 |
| UI 金色接口多亮 | UI 直接显示 `candidateEffects` | UI 改为显示 resolver 输出的 `validEffects` |
| `readonly List<T>` 被误当不可变 | 只锁住字段引用，没锁住集合内容 | 对外暴露 `IReadOnlyList<T>` |
| 基础激活和双持激活逻辑分叉 | 双持额外激活另写一套 SetActive / HashSet 逻辑 | 两条路径都走 `TryActivateItem()` |

## 如何验证

### 规则与解析

- 两把手枪左右正确相邻时，`ScanAdjacency()` 产生 `DualWield` 候选。
- 镜像方向也能产生 `DualWield` 候选。
- `AdjacencyEffectResolver.ResolveValidEffects()` 返回真实有效效果。
- 三把手枪横排时，只允许一组 `DualWield` 进入 `validEffects`。
- 非 `DualWield` 效果后续接入时，有自己的互斥或堆叠策略，不复用双持的全局 Item 互斥。

### 战斗兑现

- 默认 `activeWeaponLimit = 1` 时，背包只放一把手枪只激活一把自动手枪。
- 两把手枪左右正确相邻，且其中一把吃到基础激活位时，第二把手枪额外激活。
- 两把相邻手枪都没有吃到基础激活位时，不应凭空激活。
- 三把手枪横排时，最多激活一组双持，不出现三把同时因同一组双持网络激活。
- 场景中需要有足够的 `Pistol` 武器槽；只有一个手枪槽时，第二把无法激活不应报错。

### UI 表现

- 灰色接口显示物品可连接方向。
- 金色接口只显示 `validEffects` 中真正生效的边。
- 三把手枪横排时，UI 金色接口数量与真实生效的双持组一致。
- 激活角标仍然标记具体 `Item` 实例，不把同类手枪全部点亮。
- 拖拽、合并、丢弃和旋转后，接口点与激活角标都能刷新到当前状态。

### 工程边界

- `BS.Inventory.asmdef` 保持 `noEngineReferences: true`，邻接规则和 resolver 不依赖 UnityEngine。
- `InventoryGrid.ScanAdjacency()` 不承担互斥、堆叠和战斗激活策略。
- `BackpackWeaponActivator` 对 `InventoryGrid.OnChanged` 的订阅和退订保持成对。
- `InventoryUIController` 与 `BackpackWeaponActivator` 都读取 `AdjacencyRuleBook.Rules` 和 `AdjacencyEffectResolver`，不维护第二套邻接规则。
- 本环境只做项目文件只读复核，没有运行 Unity Editor / Play Mode；仍需在 Unity 中复核 Inspector 槽位、Prefab、ItemView 接口点、真实自动武器数量、拖拽刷新和战斗表现。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 21 课实现了邻接规则事实源、有效效果解析器、DualWield 防三持、双持额外激活和 UI 真实效果投影 | B | 来自用户放入 Inbox 的课程记录 |
| 项目工作区存在 `AdjacencyRuleBook.cs`、`AdjacencyEffectResolver.cs` 及对应 `.meta` | C | 本环境对 `E:\YouXiKaiFa\Backpack Survivor` 做只读文件扫描 |
| `AdjacencyRuleBook.Rules` 对外暴露 `IReadOnlyList<AdjacencyRule>`，当前包含两条 Pistol 左右双持规则 | C | 本环境只读查看脚本 |
| `AdjacencyEffectResolver` 使用 `HashSet<Item>` 让每个 Item 最多参与一组 `DualWield` | C | 本环境只读查看脚本，未运行测试 |
| `BackpackWeaponActivator` 可见先解析 `validDualWieldEffects`、基础激活后再 `ActivateDualWieldWeapons()`，并通过 `TryActivateItem()` 统一激活入口 | C | 本环境只读查看脚本 |
| `InventoryUIController` 可见扫描候选后解析 `validEffects`，并用 `validEffects` 计算金色接口 | C | 本环境只读查看脚本 |
| `BS.Inventory.asmdef` 设置 `noEngineReferences: true`，且当前 Inventory 脚本扫描未发现 `UnityEngine` 引用 | C | 本环境只读检查 asmdef 与脚本文本 |
| `01-Run.unity` 中 `BackpackWeaponActivator.activeWeaponLimit` 为 `1`，并可见两个 `Tag: 1` 的 Pistol 武器槽 | C | 本环境只读检查场景 YAML |
| 当前环境已在 Unity Editor / Play Mode 中验证双持、三持防护、UI 高亮和战斗收益 | D | 未启动 Unity，未运行 Play Mode |
| 所有新增装备掉落、槽位、Prefab 和数据资产已经完整接线 | D | 外部 Unity 工作区存在装备掉落表等未提交修改，本次只按第 21 课主题做只读静态复核，未逐项验证数据资产 |

## 相关内容

- 前置：[合并升级与邻接联动](merge-upgrade-and-adjacency.md)
- 前置：[背包武器激活](backpack-weapon-activation.md)
- 前置：[背包 UI 与拖拽](inventory-ui-and-drag.md)
- 前置：[目标注册表、自动武器与投射物](target-registry-and-auto-weapon.md)
- 前置：[胜负结算与重开闭环](run-result-and-restart-loop.md)
- 后续：[内容面铺开](content-expansion-fire-rate-boost.md)
- C#：[值类型 vs 引用类型](../../csharp/oop/value-vs-reference.md)
- C#：[委托与事件](../../csharp/oop/delegates-and-events.md)
- C#：[C# 工程实践路线](../../csharp/engineering/index.md)
- UGUI：[UGUI 总览](../../unity/ugui/index.md)

> 📎 标签：`Unity` `背包构筑` `DualWield` `邻接规则` `有效效果解析` `自动武器` `UGUI` `项目实践`
