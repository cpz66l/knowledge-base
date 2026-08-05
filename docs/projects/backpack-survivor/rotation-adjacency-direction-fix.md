# 旋转邻接方向修正

> 学习状态：已应用，待复测
>
> 前置知识：[背包交互补丁](inventory-interaction-patches.md)、[合并升级与邻接联动](merge-upgrade-and-adjacency.md)、[构筑最小兑现](build-payoff-dual-wield.md)
>
> 对应项目：[Backpack Survivor](index.md)
>
> 下一步：[第 29 课武器稀有度与等级差异](weapon-rarity-and-level-scaling.md)
>
> 日期：2026-08-04
>
> 阶段：V0.2 掉落与背包构筑 · 第 28 课

## 学习目标

- 把物品旋转从“只影响宽高”推进到“同时影响接口方向和邻接规则”。
- 区分物品配置里的本地方向与背包摆放后的世界方向。
- 用四状态 `RotationState` 表达 `0° / 90° / 180° / 270°`，替代只能表示双态的 `bool Rotated`。
- 让 UI 灰色接口点、金色生效边、`ScanAdjacency()` 候选效果和真实战斗收益使用同一方向事实源。
- 修正正反向邻接匹配，保证 `TagA + SideA` 与 `TagB + SideB` 不被拆散。

## 当前理解

第 13 课的旋转主要解决“物品能不能换宽高放进背包”；第 14 课的邻接接口先以原始朝向建立规则。第 28 课补上二者之间真正缺失的规则语义：

```text
规则表写的是物品自己的本地方向
背包扫描看到的是当前摆放后的世界方向
中间必须用 Item.RotationState 做转换
```

如果只让 UI 接口点跟着旋转，而扫描器仍然用本地方向直接和世界接触边比较，就会出现“看起来接上了，规则不触发”或“规则触发了，金边显示错”的分裂。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `Item.RotationState` | 保存四状态旋转，表达当前摆放姿态 |
| `Item.Width / Height` | 根据 `RotationState` 判断是否互换基础宽高 |
| `Item.BaseWidth / BaseHeight` | 保留原始尺寸，供丢弃还原静态掉落配置 |
| `Item.GetWorldSides()` | 将本地方向集合按当前旋转换算为世界方向集合 |
| `Item.GetWorldConnectableSides()` | 返回当前摆放后的真实可连接边 |
| `InventoryGrid.TryFindFreeArea()` | 临时旋转找空位；失败时恢复调用前状态 |
| `InventoryGrid.TryMatchNeighbor()` | 用世界接口做接触检查，并用正反向匹配处理规则顺序 |
| `AdjacencyEffect` | 记录扫描现场的实际世界边，供 UI 和战斗消费 |
| `InventoryUIController.HandleRotate()` | 拖拽中按 R 后即时刷新 ghost 尺寸、灰色接口点和覆盖层 |
| `InventorySystem.DiscardToWorld()` | 丢弃时写回原始尺寸和原始本地接口，不保存运行时旋转态 |

## 最小示例

### 四状态旋转

```csharp
public Rotation RotationState { get; private set; }

public enum Rotation
{
    None,
    Clockwise90,
    Clockwise180,
    Clockwise270
}

public void Rotate()
{
    if (RotationState == Rotation.Clockwise270)
        RotationState = Rotation.None;
    else
        RotationState++;
}
```

`bool Rotated` 能表达“宽高是否互换”，但不能表达 90° 和 270° 的不同接口方向。只要旋转进入规则系统，就需要四状态。

### 宽高与原始尺寸

```csharp
public int BaseWidth => baseWidth;
public int BaseHeight => baseHeight;

public int Width
{
    get
    {
        if (RotationState == Rotation.None || RotationState == Rotation.Clockwise180)
            return baseWidth;
        return baseHeight;
    }
}

public int Height
{
    get
    {
        if (RotationState == Rotation.None || RotationState == Rotation.Clockwise180)
            return baseHeight;
        return baseWidth;
    }
}
```

180° 旋转不会改变矩形占格尺寸，但会改变接口方向。因此宽高和方向必须分别按旋转状态推导，不能把“宽高没变”误当成“方向没变”。

### 本地方向转世界方向

```csharp
public ConnectableSides GetWorldConnectableSides()
{
    return GetWorldSides(LocalConnectableSides);
}

public ConnectableSides GetWorldSides(ConnectableSides localSides)
{
    ConnectableSides worldSides = ConnectableSides.None;

    if (RotationState == Rotation.None)
        worldSides = localSides;
    else if (RotationState == Rotation.Clockwise90)
    {
        if ((localSides & ConnectableSides.Up) != 0)
            worldSides |= ConnectableSides.Right;
        if ((localSides & ConnectableSides.Right) != 0)
            worldSides |= ConnectableSides.Down;
        if ((localSides & ConnectableSides.Down) != 0)
            worldSides |= ConnectableSides.Left;
        if ((localSides & ConnectableSides.Left) != 0)
            worldSides |= ConnectableSides.Up;
    }

    return worldSides;
}
```

实际项目代码还包含 180° 与 270°。关键是方向转换只保留一处：UI、邻接扫描和规则匹配都问 `Item`，而不是各自写一套旋转逻辑。

### 正向与反向匹配

```csharp
bool forwardMatched =
    rule.TagA == itemA.Tag &&
    rule.TagB == itemB.Tag &&
    itemA.GetWorldSides(rule.SideA) == sideA &&
    itemB.GetWorldSides(rule.SideB) == sideB;

bool reverseMatched =
    rule.TagA == itemB.Tag &&
    rule.TagB == itemA.Tag &&
    itemB.GetWorldSides(rule.SideA) == sideB &&
    itemA.GetWorldSides(rule.SideB) == sideA;

if (!forwardMatched && !reverseMatched)
    continue;
```

这段代码最重要的是字段归属：`rule.TagA` 对到哪个物品，`rule.SideA` 就必须由同一个物品转换成世界方向。不能把标签和边拆开做“分别存在”的模糊匹配。

## 项目中的应用

### 方向事实源集中在 `Item`

`LocalConnectableSides` 仍然来自静态掉落配置，表达物品原始朝向下有哪些接口。`RotationState` 是运行时姿态，表达当前背包里被转到了哪个角度。`GetWorldSides()` 把二者合并成当前世界方向。

```text
LocalConnectableSides
  -> RotationState
  -> GetWorldSides(localSides)
  -> UI 显示 / 邻接扫描 / 规则匹配共用
```

这比让 UI、扫描器和战斗系统各自推方向更安全。方向一旦分散，最容易出现灰点、金点和真实效果不一致。

### `ScanAdjacency()` 仍只扫描右边和下边

扫描右边和下边是为了避免重复：

```text
A 的右边是 B
B 的左边是 A
```

如果四个方向都扫，同一对物品会被扫到两次。第 28 课没有改变扫描覆盖策略，而是把“规则表顺序不一定等于扫描顺序”交给 `forwardMatched / reverseMatched` 处理。

```text
扫描层：找当前世界中的接触边
匹配层：把规则本地方向转成世界方向后判断
去重层：同一对物品 + 同一效果只产出一次
结算层：继续决定候选效果是否真正生效
```

### `AdjacencyEffect` 存世界边

即使是反向规则匹配成功，运行时效果仍然记录扫描现场：

```csharp
new AdjacencyEffect(rule.EffectId, itemA, sideA, itemB, sideB);
```

这是正确的，因为 UI 金边关心的是“当前背包里哪条边正在生效”，不是规则表里的本地方向。让 `AdjacencyEffect` 保存世界边，可以让 `ItemView.SetConnectors()` 直接投影结果，不再理解规则表和旋转细节。

### 拖拽中旋转即时刷新

拖拽期间 `Redraw()` 会被门闸拦住，所以按 R 后不能等全量重绘。`HandleRotate()` 需要主动刷新 ghost：

```text
Item.Rotate()
  -> ghost RectTransform.sizeDelta
  -> CanPlaceAt / CanMerge 红绿判定
  -> SetConnectors(visibleSides, None)
  -> UpdateOverlayLayout(step)
```

拖拽中的 `activeSides` 给 `None` 是刻意的。手持物品已经离开背包数据层，不参与真实邻接扫描，只能显示灰色可连接边，不能显示假金边。

### 丢弃恢复原始朝向

当前 `LootEntry` 是静态掉落结构，没有保存运行时旋转态。丢弃时如果写当前 `Width / Height`，但 `connectableSides` 仍写原始本地方向，就会产生“尺寸像旋转过、接口像没旋转”的混合数据。

所以第 28 课选择：

```text
width / height 写 BaseWidth / BaseHeight
connectableSides 写 LocalConnectableSides
丢出再捡回恢复原始朝向
```

这是 Demo 阶段的自洽取舍。正式版若要保留地面物品旋转状态，应新增运行时掉落数据，而不是污染静态 `LootEntry`。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 90° 和 270° 方向无法区分 | `bool Rotated` 只能表达双态 | 改为四状态 `RotationState` |
| 180° 宽高没变就忽略旋转 | 把几何占格和接口方向混为一谈 | 宽高与接口方向分别由 `RotationState` 推导 |
| 规则方向直接对比扫描边 | `rule.SideA` 是本地方向，`sideA` 是世界方向 | 用具体物品的 `GetWorldSides(rule.SideX)` 转换后再比 |
| 正反向匹配误触发 | 把 Tag 和 Side 拆散，只判断“分别存在” | 保持 `TagA + SideA` 与 `TagB + SideB` 成对绑定 |
| 自动找空位失败后偷偷改变物品 | 临时旋转后只回滚一次 | 四状态下失败后再转 3 次回到调用前状态 |
| 拖拽中接口点不更新 | `Redraw()` 被拖拽门闸拦住 | `HandleRotate()` 主动刷新 ghost 尺寸和接口点 |
| 拖拽中显示假金边 | 手持物品未在网格中，却复用旧 active 边 | 拖拽 ghost 的 `activeSides` 给 `None` |
| 丢弃后生成混合朝向物品 | 当前尺寸和原始接口被同时写入 `LootEntry` | 丢弃写回 `BaseWidth / BaseHeight / LocalConnectableSides` |

## 如何验证

### 当前已记录证据

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 28 课完成四状态旋转、接口方向转换、正反向邻接匹配、拖拽 ghost 刷新和丢弃还原 | B | 来自用户放入 Inbox 的课程记录 |
| 用户记录已通过 Unity 内测，灰点、金点和真实效果一致 | B | 用户课程记录描述了 Unity 内测验收结果 |
| `Item.cs` 中可见 `RotationState`、`BaseWidth / BaseHeight`、`GetWorldSides()` 和四状态方向转换 | C | 本环境只读查看外部 Unity 工程脚本 |
| `InventoryGrid.cs` 中可见 `TryFindFreeArea()` 失败回滚 3 次、`TryMatchNeighbor()` 使用世界接口和正反向匹配 | C | 本环境只读查看外部 Unity 工程脚本 |
| `InventoryUIController.cs` 中可见拖拽旋转后刷新尺寸、红绿判定、接口点和覆盖层 | C | 本环境只读查看外部 Unity 工程脚本 |
| `InventorySystem.cs` 中可见丢弃写回 `BaseWidth / BaseHeight / LocalConnectableSides` | C | 本环境只读查看外部 Unity 工程脚本 |
| 相关脚本 `.meta` 文件存在，静态脚本扫描未发现旧 `Rotated` 残留或 `UnityEditor` 误引入 | C | 本环境只读扫描外部 Unity 工程脚本和 `.meta` |
| 当前环境未运行 Unity Editor / Play Mode、Profiler 或 Player Build | D | 未启动 Unity，未亲自复测真实画面、交互、性能或 Build |

### 待补验证

- 在 Unity Play Mode 中复核单接口物品按 R 后是否按 `Up -> Right -> Down -> Left -> Up` 循环。
- 复核原本能触发的邻接规则在未旋转布局中仍能触发。
- 复核原本不能触发的布局在旋转后能触发，且 UI 灰点、金点和真实战斗效果一致。
- 复核规则表写 `Rifle + Magazine` 时，实际摆成 `Magazine + Rifle` 也能通过反向匹配触发。
- 复核拖拽中旋转不会显示假金边，放下后由 `Redraw()` 重新计算真实生效边。
- 复核丢弃再拾取恢复原始朝向是当前期望行为，并记录未来是否需要 `DropRuntimeData` 保留旋转态。
- 用纯 C# 最小测试覆盖 `GetWorldSides()` 四方向映射和 `TryFindFreeArea()` 失败回滚，降低后续改规则时的回归风险。

## 复盘

- 原来的理解：旋转只要让宽高互换，背包放置就算完成。
- 实践后的结论：只要旋转影响邻接接口，就必须显式区分本地方向和世界方向，并把转换集中到同一个事实源。
- 仍未理解：缺少当前环境亲自运行的 Play Mode 证据，也还没有纯 C# 回归测试覆盖方向映射和规则匹配。

## 相关内容

- 前置：[背包交互补丁](inventory-interaction-patches.md)
- 前置：[合并升级与邻接联动](merge-upgrade-and-adjacency.md)
- 前置：[构筑最小兑现](build-payoff-dual-wield.md)
- 前置：[内容面铺开](content-expansion-fire-rate-boost.md)
- 前置：[合并升级收益兑现](merge-upgrade-reward-payoff.md)
- 后续：[武器稀有度与等级差异](weapon-rarity-and-level-scaling.md)
- C#：[C# 工程实践路线](../../csharp/engineering/index.md)
- 检查清单：[Unity 项目能力](../../checklists/unity-project.md)

> 标签：`Unity` `背包系统` `旋转` `邻接规则` `bitmask` `本地方向` `世界方向` `项目实践`
