# 合并升级与邻接联动

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现同名同级合并、物品构筑标签、方向受限邻接扫描和接口点 UI；本环境完成静态审阅与文档验证，未重新运行 Unity
>
> 日期：2026-07-28
>
> 阶段：V0.2 掉落与背包构筑 · 第 14 课

## 学习目标

- 把背包物品从“只占格”推进到“可合并升级、可参与构筑规则”的数据模型。
- 区分查询和命令：`CanMerge` 只判断，`TryMerge` 才真正修改背包。
- 用 `ItemTag` 和 `[Flags] ConnectableSides` 描述物品类型与可连接方向。
- 用规则表表达邻接组合，避免把玩法组合写死进扫描器的 `if-else`。
- 让 `InventoryGrid.ScanAdjacency` 只返回候选效果，不替玩法层裁决最终生效规则。
- 用接口点 UI 表现可连接边和已触发边，同时为未来多邻接效果保留表现能力。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `Item.Level / MaxLevel` | 表达物品合并升级状态，`ItemView.Bind` 显示 `Lv.x` |
| `InventoryGrid.CanMerge` | 判断同 `Id`、同等级、不同实例、目标未满级是否可以合并 |
| `InventoryGrid.TryMerge` | 执行目标升级和来源移除，触发背包变化 |
| `ItemTag` | 表达物品构筑类别，例如 `Pistol`、`Magazine`、`Scope`、`FireCore` |
| `ConnectableSides` | 用 bitmask 表达 `Up / Right / Down / Left` 接口边 |
| `AdjacencyRule` | 表达 A 标签 + A 接触边 + B 标签 + B 接触边 → 效果 ID |
| `AdjacencyEffect` | 表达一次扫描命中的候选效果和双方触发边 |
| `InventoryGrid.ScanAdjacency` | 扫描背包中右邻和下邻，生成去重后的候选邻接效果 |
| `ItemView.SetConnectors` | 将无接口、未触发接口和已触发接口分别表现为隐藏、灰色、金色 |
| `InventoryUIController.Redraw` | 重绘前扫描邻接效果，并把可连接边与激活边投影到视图 |

本课让背包从“容器 UI”开始变成“构筑棋盘”。合并升级解决物品成长，邻接扫描则为后续双持、芯片、模块化装备和构筑效果打底。

## 合并升级

合并规则暂定为：

```text
同 Id
同 Level
不同实例
目标未达到 MaxLevel
```

判断和执行分离：

```csharp
public bool CanMerge(Item source, Item target)
{
    if (source == null || target == null) return false;
    if (source == target) return false;
    if (source.Id != target.Id) return false;
    if (source.Level != target.Level) return false;
    if (target.Level >= target.MaxLevel) return false;

    return true;
}

public bool TryMerge(Item source, Item target)
{
    if (!CanMerge(source, target)) return false;

    target.IncreaseLevel();
    Remove(source);
    return true;
}
```

这里的核心是语义诚实：`CanMerge` 是查询，不产生副作用；`TryMerge` 是命令，会改变世界。拖拽预览、松手执行、未来自动整理都能共享同一套判断，不需要复制规则。

拖拽链路变成：

```text
BeginDrag
  -> grid.Remove(source)
  -> Dragging：目标格无法放置时，检查能否与目标物品合并
  -> EndDrag：优先 TryMerge(source, target)
  -> target.Level + 1，source 被移除
  -> OnChanged -> Redraw -> ItemView 显示新 Lv
```

合并是“来源消耗 + 目标成长”，不是单纯改目标数字。否则来源物品会继续留在背包中，数据和 UI 都会出现假增长。

## 标签与接口边

第 14 课开始给物品加构筑标签：

```csharp
public enum ItemTag
{
    None,
    Pistol,
    Rifle,
    Shotgun,
    SniperRifle,
    Magazine,
    Scope,
    FireCore,
    Armor,
    Medical,
}
```

方向接口使用 bitmask：

```csharp
[Flags]
public enum ConnectableSides
{
    None = 0,
    Up = 1 << 0,
    Right = 1 << 1,
    Down = 1 << 2,
    Left = 1 << 3,
}
```

`Item` 保留本地接口定义，并预留世界方向查询：

```csharp
public ItemTag Tag { get; }
public ConnectableSides LocalConnectableSides { get; }

public ConnectableSides GetWorldConnectableSides()
{
    return LocalConnectableSides;
}
```

当前 `GetWorldConnectableSides()` 直接返回本地接口，说明接口方向暂未随物品旋转变化。这个命名仍然有价值：以后若决定接口跟着 `Rotated` 旋转，只需要在这里做方向变换，扫描器继续问“世界方向上有没有接口”。

## 邻接规则表

邻接规则不写成长串 `if-else`，而是数据化为一张规则表：

```csharp
public class AdjacencyRule
{
    public ItemTag TagA { get; }
    public ConnectableSides SideA { get; }
    public ItemTag TagB { get; }
    public ConnectableSides SideB { get; }
    public AdjacencyEffectId EffectId { get; }
}
```

第一条效果是 `DualWield` 候选：

```text
Pistol.Right 接 Pistol.Left  -> DualWield
Pistol.Left  接 Pistol.Right -> DualWield
```

这比“只要两个手枪相邻就触发”更有构筑感。方向受限后，玩家需要考虑摆放和旋转，而不是只把物品塞进背包空地。

## 邻接扫描

`ScanAdjacency` 只检查右边和下边：

```csharp
for (int y = 0; y < Height; y++)
{
    for (int x = 0; x < Width; x++)
    {
        Item item = cells[x, y];
        if (item == null) continue;

        TryMatchNeighbor(x, y, x + 1, y,
            ConnectableSides.Right, ConnectableSides.Left,
            rules, effects, triggeredKeys);

        TryMatchNeighbor(x, y, x, y + 1,
            ConnectableSides.Down, ConnectableSides.Up,
            rules, effects, triggeredKeys);
    }
}
```

全格扫描时，如果四个方向都查，A 的右边是 B，B 的左边又会再次命中 A，天然重复。只查右和下可以覆盖所有水平/垂直邻接对，同时避免双向重复。

`TryMatchNeighbor` 的守卫顺序：

```text
邻居坐标越界或为空
  -> 自身多格邻接：itemA == itemB
  -> 双方接口边不存在
  -> 规则表未命中
  -> 去重 key 已存在
  -> 生成 AdjacencyEffect 候选
```

同一个 2 x 2 物品会写入多个格子，扫描相邻格时可能碰到同一实例。这里用引用相等 `itemA == itemB` 跳过，是因为要排除“同一物品不同占格之间的邻接”，而不是排除同 Id 的两件物品。

## 候选效果不是最终生效

`ScanAdjacency` 返回的是候选效果：

```csharp
public class AdjacencyEffect
{
    public AdjacencyEffectId EffectId { get; }
    public Item ItemA { get; }
    public Item ItemB { get; }
    public ConnectableSides SideA { get; }
    public ConnectableSides SideB { get; }
}
```

这条边界很重要。三把手枪横排时，扫描层可能发现两条候选 `DualWield`：

```text
A-B 命中 DualWield
B-C 也命中 DualWield
```

扫描器只能证明“几何、标签和方向规则命中了”；不能决定玩法是否允许中间手枪同时参与两组双持。真正的裁决应留给后续 `AdjacencyEffectResolver`：

```text
候选效果
  -> 唯一性 / 可叠加 / 互斥 / 上限规则
  -> 真正生效效果
  -> UI 与战斗系统消费
```

这能让底层网格保持纯净。双持可以每把武器最多参与一组，芯片可以可叠加，元素效果可以互斥；这些策略不应该混进扫描器。

## 接口点 UI

`ItemView` 增加四个接口点，按状态显示：

```csharp
private void SetConnector(
    Image connector,
    ConnectableSides side,
    ConnectableSides visibleSides,
    ConnectableSides activeSides)
{
    if ((visibleSides & side) == 0)
    {
        connector.gameObject.SetActive(false);
        return;
    }

    connector.gameObject.SetActive(true);
    connector.color = (activeSides & side) != 0
        ? new Color(1f, 0.78f, 0.15f, 1f)
        : new Color(0.55f, 0.55f, 0.55f, 0.9f);
}
```

`activeSides` 必须累加，不能覆盖：

```csharp
private ConnectableSides GetActiveSides(Item item, List<AdjacencyEffect> effects)
{
    ConnectableSides activeSides = ConnectableSides.None;

    foreach (var effect in effects)
    {
        if (effect.ItemA == item)
            activeSides |= effect.SideA;

        if (effect.ItemB == item)
            activeSides |= effect.SideB;
    }

    return activeSides;
}
```

表现层应该有能力显示多个激活边。至于哪些效果可以同时生效，是结算层的职责；UI 不应该用“覆盖某一边”来假装完成玩法限制。

## 临时硬编码与退出路线

当前手枪标签和左右接口临时写在收货口或物品创建入口，邻接规则也临时放在 UI 控制器附近。这在教学阶段可以接受，因为目标是先跑通构筑闭环；但长期方案必须迁移到数据定义：

| 临时位置 | 风险 | 退出路线 |
|---|---|---|
| `CreateItemFromLootEntry` 特判手枪标签和接口 | 物品定义分散，新增装备要改代码 | 做 `ItemDefinition`，由掉落条目引用定义 |
| `InventoryUIController` 内部维护规则表 | 表现层拥有玩法规则 | 做 `RuleDefinition` 或静态规则配置，由规则层提供 |
| `GetWorldConnectableSides()` 暂不处理旋转 | 接口方向与玩家视觉旋转可能不一致 | 明确接口是否随旋转变化，并在该方法统一转换 |
| `ScanAdjacency` 结果直接用于 UI 激活边 | 候选效果和真实生效效果暂时混用 | 第 16 课加入结算器后，UI 改用 resolved effects |

临时代码最大的问题不是“不够漂亮”，而是忘记它只是临时的。本页把退出路线写清楚，避免硬编码悄悄变成永久架构。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 合并后还剩两件物品 | 只升级目标，没有移除来源实例 | `TryMerge` 中先 `target.IncreaseLevel()`，再 `Remove(source)` |
| 预览和执行规则分叉 | UI 复制了一份合并判断 | `CanMerge` 统一服务预览，`TryMerge` 统一服务执行 |
| 多格物品和自己触发邻接 | 同一实例占多个格子，扫描相邻格碰到自己 | `itemA == itemB` 直接跳过 |
| 邻接效果重复 | 四方向扫描或多格边界重复命中 | 只查右/下，并用双方实例 hash + 效果 ID 去重 |
| 接口激活边被覆盖 | `activeSides = effect.SideA` 抹掉前一次命中 | 使用 `activeSides |= effect.SideA` 累加 |
| 三把手枪横排产生歧义 | 扫描层发现多条候选双持 | 留给后续结算器裁决唯一性 |
| 玩法规则落在 UI 控制器 | 为了快速显示把规则表放进表现层 | 后续迁到物品/规则定义表 |
| Local / World 命名不兑现 | `GetWorldConnectableSides()` 暂未处理旋转 | 明确当前是占位演进点，并在后续统一转换 |

## 如何验证

### 合并升级

- 两件同 `Id`、同 `Level`、不同实例的物品拖到一起时，目标升级，来源消失。
- 不同 `Id`、不同等级、同一实例或目标满级时不能合并。
- 合并后 `ItemView` 显示的新等级正确。
- 合并路径触发 `OnChanged` 并驱动 UI 重绘。
- 拖拽预览和松手执行使用同一套 `CanMerge` 规则。

### 邻接扫描

- 两把手枪按右接左放置时产生 `DualWield` 候选效果。
- 镜像方向放置时也能产生候选效果。
- 不相邻、标签不匹配或接口边不匹配时不产生效果。
- 2 x 2 物品不会和自己的相邻格触发效果。
- 只查右/下仍能覆盖所有邻接对，不出现重复候选。
- 三把手枪横排时可观察到候选歧义，并明确标记为后续结算器问题。

### UI 表现

- 无接口边的物品不显示接口点。
- 有接口但未触发的边显示灰色。
- 已触发候选效果的边显示金色。
- 一个物品多个边同时命中时，多个接口点都能显示为激活。
- 背包重绘后接口点状态与当前网格关系一致，没有残留上一次状态。

### 工程边界

- `BS.Inventory` 仍不引用 UnityEngine；标签、方向、规则和候选效果可留在纯 C# 数据层。
- 表现层只消费扫描结果，不长期拥有玩法规则。
- 本环境没有完整 Unity 工程，因此仍需在 Unity Editor 中复核脚本、Prefab、ItemView 接口点引用、字体资源、`.meta` / GUID、场景配置和 Play Mode 结果。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 14 课实现了同名同级合并、等级显示、标签、接口边、邻接规则和接口点 UI | B | 来自用户放入 Inbox 的课程记录 |
| `CanMerge` / `TryMerge` 分离用于统一预览与执行规则 | B | 原始记录明确描述了实现与设计理由 |
| `ScanAdjacency` 只返回候选效果，不裁决最终玩法生效 | B | 原始记录明确将结算器挂到账后续课程 |
| bitmask 适合当前上下左右接口集合 | C | 本环境基于固定小集合、频繁判断和代码片段静态审阅 |
| 第 14 课已由当前环境在 Unity Editor / Play Mode 中运行通过 | D | 本次未收到完整 Unity 工程、场景、Prefab、ItemView 引用、字体资源或 `.meta`，未运行 Unity |
| DualWield 已完成战斗系统生效 | D | 原始记录明确把真实结算和战斗兑现留到第 16 课 |

## 相关内容

- 前置：[背包纯数据网格](inventory-data-grid.md)
- 前置：[背包 UI 与拖拽](inventory-ui-and-drag.md)
- 前置：[背包交互补丁](inventory-interaction-patches.md)
- C#：[值类型 vs 引用类型](../../csharp/oop/value-vs-reference.md)
- C#：[委托与事件](../../csharp/oop/delegates-and-events.md)
- UGUI：[UGUI 总览](../../unity/ugui/index.md)

> 📎 标签：`Unity` `背包系统` `合并升级` `邻接规则` `bitmask` `数据驱动` `UGUI` `项目实践`
