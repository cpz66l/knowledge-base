# 背包价值与物品价值显示

> 项目：[Backpack Survivor](index.md)
>
> 状态：项目中使用
>
> 验证状态：待验证。用户课程记录描述已实现单件物品价值显示、背包总价值、唯一物品去重和结算页背包价值快照；本环境完成静态审阅、项目文件只读复核与文档验证，未运行 Unity Editor / Play Mode。
>
> 日期：2026-08-03
>
> 阶段：V0.2 掉落与背包构筑 · 第 25 课

## 学习目标

- 让 `LootEntry.scoreValue` 从配置字段进入运行时 `Item`，成为 UI 和结算可读的物品事实。
- 在 `ItemView` 中显示单件价值，但不让 UI 反查掉落表或按 `id` 写规则。
- 用 `InventoryGrid.GetUniqueItems()` 计算背包总价值，避免大物品按占格重复计分。
- 让 `InventoryUIController` 只投影总价值，不保存第二份背包经济状态。
- 把终局背包价值写入 `RunResult` 快照，保证结算页显示的是结束瞬间的数据。
- 保持金币与背包价值的语义分离，为后续最终评分模型留下清晰字段。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `LootEntry.scoreValue` | 静态配置源，定义装备初始搜刮 / 结算价值 |
| `Item.ScoreValue` | 运行时物品价值，跟随拾取、拖拽、丢弃和结算 |
| `InventorySystem.CreateItemFromLootEntry()` | 创建运行时物品时传入 `scoreValue` |
| `InventorySystem.DiscardToWorld()` | `Item -> LootEntry` 还原时保留 `scoreValue` 和 `effectValue` |
| `ItemView.valueText` | 显示单件价值，作为纯展示文本关闭射线 |
| `InventoryGrid.GetTotalScoreValue()` | 通过唯一物品列表累加背包总价值 |
| `InventoryUIController.totalValueText` | 背包面板显示当前总价值 |
| `RunResult.BackpackValue` | 终局时冻结背包价值，供 `ResultView` 显示 |

第 24 课让金币成为局内可见资源。第 25 课处理另一条经济线：背包里的装备和收集品也有价值，玩家能在局内看到单件价值和背包总价值，结算页也能冻结这局结束时的背包收益。

```text
LootEntry：初始配置
Item：运行时物品事实
InventoryGrid：背包数据查询
InventoryUIController / ResultView：表现层投影
RunResult：终局快照
```

## 价值链路

第 22 课已经把 `scoreValue` 写入 `LootEntry` 和 `Item`。第 25 课把它推进到玩家可见层：

```csharp
public int ScoreValue { get; }

public Item(
    string id,
    Rarity rarity,
    int width,
    int height,
    ItemTag itemTag,
    ConnectableSides connectableSides,
    int scoreValue,
    float effectValue)
{
    Id = id;
    ScoreValue = scoreValue;
    EffectValue = effectValue;
}
```

价值从配置进入运行时对象后，UI 和结算都不需要再反查掉落表：

```text
LootTableData.LootEntry.scoreValue
  -> InventorySystem.CreateItemFromLootEntry(entry)
  -> new Item(..., entry.scoreValue, entry.effectValue)
  -> Item.ScoreValue
  -> ItemView / InventoryGrid / RunResult
```

这为后续第 26 课“合并升级后价值成长”留下空间：一旦运行时物品价值会随等级变化，配置表只代表初始值，UI 和结算必须读 `Item` 的当前值。

## 往返保真

新增字段不能只看拾取入口，还要看丢弃出口。

```csharp
LootEntry entry = new LootEntry
{
    category = DropCategory.Equipment,
    id = item.Id,
    rarity = item.Rarity,
    width = item.Width,
    height = item.Height,
    amount = 1,
    itemTag = item.Tag,
    connectableSides = item.LocalConnectableSides,
    scoreValue = item.ScoreValue,
    effectValue = item.EffectValue,
};
```

如果 `DiscardToWorld()` 漏写 `scoreValue`，玩家把物品丢出去再捡回来，价值就会掉成默认值。第 25 课延续的工程习惯是：

```text
字段新增
  -> 查配置到运行时
  -> 查运行时回世界
  -> 查 UI 显示
  -> 查结算快照
```

## 单件价值显示

`ItemView` 只读绑定进来的 `Item`：

```csharp
if (valueText != null)
{
    if (item.ScoreValue <= 0)
        valueText.text = "￥ 0";
    else
        valueText.text = $"￥{item.ScoreValue}";
}
```

这里有两条边界：

- `ItemView` 不根据 `item.Id` 写 if-else。
- `ItemView` 不反查 `LootTableData`。

价值文本是表现层，它展示 `Item.ScoreValue` 这个运行时事实。静态 Prefab 检查可见 `ItemView.valueText` 已接到 `ValueText`，且 `ValueText` 的 `m_RaycastTarget: 0`，避免纯展示文本吃掉拖拽射线。

## 背包总价值

背包是二维占格结构，但价值属于物品，不属于格子。第 25 课把总价值放在数据层：

```csharp
public int GetTotalScoreValue()
{
    int total = 0;
    foreach (Item item in GetUniqueItems())
    {
        if (item == null) continue;
        total += item.ScoreValue;
    }
    return total;
}
```

关键是 `GetUniqueItems()`。一个 2x2 物品会占 4 个格子，如果直接遍历 `cells[x, y]` 累加，价值会被算 4 次。

```text
空间问题：按格子判断能不能放
价值问题：按唯一物品累加
```

这也是把总价值放在 `InventoryGrid` 的原因。结算页、调试面板、任务系统或背包 UI 都可以读同一条数据查询，不用各算一遍。

## 背包 UI 投影

`InventoryUIController` 在 `Redraw()` 后刷新总价值：

```csharp
private void RefreshTotalValue()
{
    if (totalValueText == null) return;
    if (grid == null) return;

    totalValueText.text = $"背包价值：￥{grid.GetTotalScoreValue()}";
}
```

UI 的职责是投影当前数据，不保存总价值。拖拽期间原本已有重绘门闸，第 25 课不绕过它，只在结束重绘时统一刷新价值，避免拖拽中间态制造第二套显示规则。

静态场景检查可见 `InventoryUIController.totalValueText` 已接到 `TotalValueText`，并且该 TMP 文本 `m_RaycastTarget: 0`。

## RunResult 冻结背包价值

结算页展示的是“本局结束瞬间”的成绩，不应该实时追问背包。

```csharp
public int BackpackValue { get; }

public RunResult(
    GameState finalState,
    float elapsed,
    int level,
    int totalXp,
    int killCount,
    int backpackValue)
{
    BackpackValue = backpackValue;
}
```

`GameSession.EndRun()` 在终局时取一次背包总价值：

```csharp
int backpackValue = 0;
if (inventorySystem != null && inventorySystem.Grid != null)
    backpackValue = inventorySystem.Grid.GetTotalScoreValue();

RunResult runResult = new RunResult(
    finalState,
    Elapsed,
    Level,
    TotalXp,
    killCount,
    backpackValue);
```

然后 `ResultView` 只显示快照：

```csharp
statsText.text =
    $"存活时间：{FormatTime(runResult.Elapsed)}\r\n" +
    $"等级：{runResult.Level}\r\n" +
    $"总经验：{runResult.TotalXp}\r\n" +
    $"击杀数：{runResult.KillCount}\r\n" +
    $"背包价值：￥{runResult.BackpackValue}";
```

这延续第 20 课的规则：`RunResult` 是终局数据包，`ResultView` 是展示器。不要让结果页直接查 `InventorySystem`，否则重开、清理对象或后续状态变化都可能影响结算显示。

## 金币与背包价值分离

第 24 课有 `TotalGold`，第 25 课有 `BackpackValue`。它们都属于经济反馈，但含义不同：

| 字段 | 含义 |
|---|---|
| `TotalGold` | 本局拾取到的货币收入 |
| `BackpackValue` | 终局时背包中物品的搜刮价值 |

当前不急着混成一个最终分数。玩家需要知道收益来自哪里：

```text
金币收入
背包携带价值
击杀 / 等级战斗表现
最终评分
```

后续可以在 `RunResult` 中继续增加 `GoldEarned`、`CombatScore`、`FinalScore`，但不要提前把所有经济含义塞进一个字段。

## 周期链路

### 单件价值

```text
LootEntry.scoreValue
  -> CreateItemFromLootEntry(entry)
  -> Item.ScoreValue
  -> ItemView.Bind(item)
  -> ValueText 显示 ￥X
```

### 背包总价值

```text
InventoryGrid.cells[x,y]
  -> GetUniqueItems()
  -> HashSet<Item> 去重
  -> GetTotalScoreValue()
  -> InventoryUIController.RefreshTotalValue()
  -> TotalValueText 显示 背包价值
```

### 结算快照

```text
玩家死亡 / 时间到
  -> GameSession.EndRun(finalState)
  -> inventorySystem.Grid.GetTotalScoreValue()
  -> new RunResult(..., backpackValue)
  -> OnRunEnded(runResult)
  -> ResultView 显示背包价值
```

### 丢弃回捡

```text
Item.ScoreValue
  -> InventorySystem.DiscardToWorld(item)
  -> LootEntry.scoreValue = item.ScoreValue
  -> LootManager.SpawnEntry(entry, position)
  -> DropItem.Initialize(entry)
  -> 再次拾取
  -> Item.ScoreValue 不丢失
```

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 2x2 物品价值算 4 次 | 按格子遍历累加 | 先 `GetUniqueItems()`，再按唯一物品累加 |
| UI 价值和配置不一致 | `ItemView` 反查表或按 `id` 写分支 | UI 只读 `Item.ScoreValue` |
| 丢弃后价值变 0 | `Item -> LootEntry` 反向路径漏字段 | `DiscardToWorld()` 保留 `scoreValue` 和 `effectValue` |
| 结算价值变化不稳定 | `ResultView` 实时查背包 | `GameSession.EndRun()` 写入 `RunResult.BackpackValue` |
| 展示文本挡住拖拽 | TMP / Image 仍开 Raycast Target | 纯展示控件关闭 `RaycastTarget` |
| 把金币和背包价值混成一个数 | 经济字段语义过早合并 | 分别记录 `TotalGold` 和 `BackpackValue`，最终评分另建模型 |
| Lv.2/Lv.3 价值不变 | 第 25 课阶段 `ScoreValue` 仍可理解为初始值 | 后续第 26 课已通过基础值 / 当前值拆分兑现升级收益 |

## 如何验证

### 单件价值

- 不同稀有度装备的 `ItemView` 显示对应 `ScoreValue`。
- `scoreValue <= 0` 时显示为 0，不出现空文本或旧值。
- `ValueText` 不吃拖拽射线，不影响拿起、拖动、放下。
- UI 不按物品名反查配置。

### 背包总价值

- 1x1、1x2、2x2 物品都只按单个 `Item.ScoreValue` 计一次。
- 拾取、拖拽、旋转、合并、丢弃后总价值刷新。
- 背包满自动丢出和手动丢弃后，总价值减少。
- 丢弃再捡回后，单件价值和总价值不丢失。

### 结算价值

- 玩家死亡或时间胜利时，`RunResult.BackpackValue` 等于终局瞬间背包总价值。
- 打开结算面板后，即使场景对象继续清理，显示值也不变化。
- 重开后新局背包价值从空背包重新计算。
- 如果未来金币进入结算，应新增字段，不复用 `BackpackValue`。

### 工程边界

- `InventoryGrid.GetTotalScoreValue()` 不依赖 UnityEngine，可随纯 C# 数据层测试。
- `InventoryUIController` 不保存总价值字段，只刷新文本。
- `ResultView` 不直接查 `InventorySystem`。
- `GameSession.EndRun()` 对 `inventorySystem` 和 `Grid` 做空引用保护。
- 本环境未运行 Unity Editor / Play Mode / Player Build；真实拖拽、射线、结算画面和字体显示仍需项目内验证。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 25 课实现了单件价值、背包总价值和结算页背包价值快照 | B | 来自用户放入 Inbox 的课程记录 |
| `Item` 已包含只读 `ScoreValue`，`LootEntry.scoreValue` 创建 `Item` 时被传入 | C | 本环境只读查看 `Item.cs`、`LootTableData.cs` 与 `InventorySystem.cs` |
| `DiscardToWorld()` 已把 `Item.ScoreValue` 写回 `LootEntry.scoreValue` | C | 本环境只读查看 `InventorySystem.cs` |
| `InventoryGrid.GetTotalScoreValue()` 已通过 `GetUniqueItems()` 累加唯一物品价值 | C | 本环境只读查看 `InventoryGrid.cs` |
| `ItemView.valueText`、`InventoryUIController.totalValueText` 和 `ResultView` 背包价值显示代码存在 | C | 本环境只读查看表现层脚本 |
| `RunResult` 已包含 `BackpackValue`，`GameSession.EndRun()` 已把终局背包价值写入快照 | C | 本环境只读查看 `RunResult.cs` 与 `GameSession.cs` |
| `ItemView.prefab` 中 `ValueText` 已接入且 `m_RaycastTarget: 0`；`01-Run.unity` 中 `TotalValueText` 已接入且 `m_RaycastTarget: 0` | C | 本环境只读检查 Prefab / 场景 YAML |
| 背包价值 UI、拖拽射线和结算页已在 Unity Play Mode 中确认 | D | 本环境未运行 Unity 或观察画面 |
| 合并升级后 `ScoreValue` / `EffectValue` 已随等级成长 | B / C | 第 26 课课程记录描述已实现；本环境另页完成脚本静态复核 |


## 相关内容

- 前置：[金币掉落与局内经济 HUD](gold-drops-and-economy-hud.md)
- 前置：[内容面铺开](content-expansion-fire-rate-boost.md)
- 前置：[背包 UI 与拖拽](inventory-ui-and-drag.md)
- 前置：[胜负结算与重开闭环](run-result-and-restart-loop.md)
- 前置：[合并升级与邻接联动](merge-upgrade-and-adjacency.md)
- 后续：[合并升级收益兑现](merge-upgrade-reward-payoff.md)
- C#：[C# 工程实践路线](../../csharp/engineering/index.md)
- UGUI：[Text (TextMeshPro)](../../unity/ugui/controls/text-tmp.md)
- 检查清单：[Unity 项目能力](../../checklists/unity-project.md)

> 📎 标签：`Unity` `背包价值` `ItemView` `RunResult` `结算快照` `UI 投影` `项目实践`
