# 背包交互补丁

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已修复提示框射线阻挡、补齐丢弃闭环、R 键旋转和拾取请求-确认；本环境完成静态审阅与文档验证，未重新运行 Unity
>
> 日期：2026-07-27
>
> 阶段：V0.2 掉落与背包构筑 · 第 13 课

## 学习目标

- 识别透明 UI 也会参与 `GraphicRaycaster`，并用 `CanvasGroup.blocksRaycasts` 管理展示层射线阻挡。
- 把 `LootManager` 的生成能力提炼成 `SpawnEntry`，让敌人掉落、宝箱散落和背包丢弃共用入口。
- 为背包拖拽增加第三结局：面板外松手时把物品丢回世界。
- 用 `Rotated` 标志位建模物品旋转，保持 `Width` / `Height` 对外只读。
- 将 `IInteractable.Interact()` 从 `void` 演进为 `bool`，让交互入口能表达成功或失败。
- 用请求-确认和兜底吐回两层保护，避免背包满时吞掉玩家物品。
- 用“镜像原则”检查订阅/退订、点亮/熄灭、启用/禁用是否成对。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `InteractPromptUI` | 提示框纯展示层不阻挡射线；交互失败时短暂显示“背包已满” |
| `LootManager.SpawnEntry` | 根据单个 `LootEntry` 生成世界掉落物，供掉落、宝箱和丢弃复用 |
| `InventorySystem.DiscardToWorld` | 将背包 `Item` 还原为 `LootEntry` 并散落到玩家附近 |
| `InventoryUIController.EndDrag` | 区分面板内落位、非法回滚和面板外丢弃 |
| `Item.Rotated` | 原始尺寸不变，`Width` / `Height` 按旋转标志计算 |
| `InputReader.OnRotate` | 把 R 键作为拖拽中的旋转事件发布给 UI 控制器 |
| `InventorySystem.CanAccept` | 预审背包是否能容纳掉落，不直接修改正式背包 |
| `DropItem.Interact` | 先问背包能否接收，成功才 `Collect()`，失败留在地上 |
| `InteractDetector` | 交互成功才清目标，失败广播 `OnInteractFailed` |
| `InventoryGrid.TryFindFreeArea` | 内置双朝向查找，成功时保留匹配朝向，失败时恢复原样 |

第 13 课不是新系统，而是一次合并升级前的交互债务清理：第 10 课暴露的拖拽中断、第 11 课暴露的吞物品、第 12 课带来的散落能力，都在本课被接成闭环。

## 提示框射线阻挡

原始问题是：提示面板全屏拉伸，透明 `Image` 的 `Raycast Target` 仍默认开启。提示框一显示，背包拖拽的射线就被全屏吃掉。

系统性修法不是逐个关闭 `Image.raycastTarget`，而是给纯展示层加 `CanvasGroup`：

```text
PromptPanel
  -> CanvasGroup.blocksRaycasts = false
```

沉淀规则：

```text
不响应点击的 UI
  -> 不应该挡射线
  -> 优先用 CanvasGroup 批量声明
  -> 不靠逐个控件默认值碰巧正确
```

这条规则归入 UGUI 事件系统边界：可见、透明、能否点击、是否挡射线是四个不同问题。

## 丢弃闭环

第 12 课让 `DropItem` 具备 `PlayScatterFlight`，第 13 课把它复用于背包丢弃。

```text
拖起物品
  -> 从 Grid.Remove
  -> 面板外松手
  -> InventorySystem.DiscardToWorld(item)
  -> LootManager.SpawnEntry(entry, playerPosition)
  -> DropItem.PlayScatterFlight
  -> 世界掉落物重新可交互
```

核心是把“从条目生成世界掉落物”提成单入口：

```csharp
public GameObject SpawnEntry(LootEntry entry, Vector3 position)
{
    if (entry == null) return null;

    if (entry.category == DropCategory.Equipment)
    {
        GameObject go = dropPool.Get(position);
        go.GetComponent<DropItem>().Initialize(entry);
        return go;
    }

    if (entry.category == DropCategory.Xp)
    {
        GameObject go = currencyPool.Get(position);
        go.GetComponent<XpOrb>().Initialize(entry);
        return go;
    }

    return null;
}
```

`EndDrag` 现在有三种结局：

```csharp
public void EndDrag(Vector2 pointerPos)
{
    if (!isDragging) return;
    isDragging = false;

    if (!RectTransformUtility.RectangleContainsScreenPoint(bagPanel, pointerPos, null))
    {
        inventorySystem.DiscardToWorld(dragItem);
        Destroy(ghost.gameObject);
        ClearDragState();
        return;
    }

    if (grid.CanPlaceAt(targetX, targetY, dragItem))
    {
        grid.Place(targetX, targetY, dragItem);
    }
    else
    {
        grid.Place(oldX, oldY, dragItem);
    }

    ClearDragState();
}
```

丢弃分支没有调用 `Place`，不会触发 `Grid.OnChanged`，因此需要手动销毁拖拽中的 ghost 视图。这里的规则是：依赖事件重绘之前，要确认自己是否真的走过会触发事件的写路径。

## R 键旋转

旋转没有直接交换宽高字段，而是保留原始尺寸，用 `Rotated` 表达姿态：

```csharp
public class Item
{
    public string Id { get; }
    public Rarity Rarity { get; }
    public bool Rotated { get; private set; }

    private readonly int baseWidth;
    private readonly int baseHeight;

    public int Width => Rotated ? baseHeight : baseWidth;
    public int Height => Rotated ? baseWidth : baseHeight;

    public void Rotate() => Rotated = !Rotated;
}
```

这个方案的价值在于保住第 9、10 课建立的只读契约：网格判定、UI 尺寸和红绿预览继续读取 `Width` / `Height`，不需要知道旋转的存储细节。

拖拽中的旋转链路：

```text
按 R
  -> InputReader.OnRotate
  -> InventoryUIController.HandleRotate
  -> dragItem.Rotate()
  -> ghost 尺寸重算
  -> CanPlaceAt 重新判定红绿状态
```

原始记录中 R 键失效来自 `OnEnable` 早于 `Start`：订阅事件时 `inputReader` 还没缓存好，空引用让订阅失败。修复后形成项目生命周期约定：

```text
Awake：缓存自身和场景引用
OnEnable：订阅事件
Start：依赖其他对象完成初始化后的连接
```

## 请求-确认拾取

第 11 课保留了“背包满时拾取会吞物品”的设计债。第 13 课将 `IInteractable` 从无返回值改成有结果：

```csharp
public interface IInteractable
{
    string GetPrompt();
    bool Interact();
}
```

`DropItem` 不再无条件 `Collect()`：

```csharp
public bool Interact()
{
    if (inventorySystem.CanAccept(lootEntry))
    {
        Collect();
        return true;
    }

    return false;
}
```

`InteractDetector` 只有成功才清目标：

```csharp
private void Interact()
{
    if (CurrentTarget == null) return;

    if (!CurrentTarget.Interact())
    {
        OnInteractFailed?.Invoke();
        return;
    }

    previousTarget = null;
    CurrentTarget = null;
    OnTargetChanged?.Invoke(null);
}
```

这样失败拾取会留下地面物品，并触发 UI 反馈，而不是把物品回收到池里。

## CanAccept 与双朝向查找

预审不应该修改正式背包，所以 `CanAccept` 使用探针物品：

```csharp
public bool CanAccept(LootEntry entry)
{
    if (entry == null) return false;

    Item probe = new Item(entry.id, entry.rarity, entry.width, entry.height);
    return Grid.TryFindFreeArea(probe, out _, out _);
}
```

第 13 课进一步把“双朝向查找”下沉到 `TryFindFreeArea`：

```csharp
public bool TryFindFreeArea(Item item, out int x, out int y)
{
    if (TryFindFreeAreaCurrentRotation(item, out x, out y))
    {
        return true;
    }

    item.Rotate();
    if (TryFindFreeAreaCurrentRotation(item, out x, out y))
    {
        return true;
    }

    item.Rotate();
    x = -1;
    y = -1;
    return false;
}
```

契约要写清楚：成功时，`item` 可能保留为了落位而旋转后的朝向；失败时，`item` 必须恢复调用前状态。这样预审和真正入包走同一条能力路径，避免“预审说能收，兑现却放不下”。

## 兜底吐回

请求-确认是前门保护，`HandleCollected` 的兜底吐回是后门保护：

```csharp
private void HandleCollected(LootEntry entry)
{
    if (entry == null) return;

    Item item = new Item(entry.id, entry.rarity, entry.width, entry.height);
    if (Grid.TryFindFreeArea(item, out int x, out int y))
    {
        Grid.Place(x, y, item);
    }
    else
    {
        DiscardToWorld(item);
    }
}
```

对玩家资源这类关键数据，最好有两层防线：入口尽量不让错误发生，出口仍能在异常路径下保住资源不丢。

## 镜像原则

本课多个问题都可以归因于成对操作不镜像：

| 成对操作 | 错误表现 | 修正习惯 |
|---|---|---|
| `+=` / `-=` | `OnDisable` 误写成继续 `+=`，重复订阅 | 写完逐字符对比 |
| 点亮 / 熄灭 | 显示“背包已满”后关闭了错误对象 | 点亮谁，熄灭谁 |
| 父显隐 / 子显隐 | 父对象重新显示时，残留 active 子物体跟着复活 | 显示父级前复位子级状态 |
| `OnEnable` / `Start` | 订阅时引用还没准备好 | 引用缓存放 `Awake` |
| 预审 / 兑现 | `CanAccept` 和 `Place` 的朝向能力不一致 | 两者复用同一查找能力 |

镜像原则适合纳入日常 code review：订阅、注册、加锁、点亮、禁用、临时状态修改，凡是成对出现的操作都需要看退出路径是否一一对应。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 提示框显示后拖不动背包 | 透明全屏 UI 仍挡射线 | 纯展示层 `CanvasGroup.blocksRaycasts = false` |
| 丢弃后 ghost 残留 | 丢弃不触发 `Grid.OnChanged`，没人重绘 | 丢弃分支手动销毁 ghost 并清状态 |
| R 键无效 | `OnEnable` 订阅时引用在 `Start` 才赋值 | 引用缓存放到 `Awake` |
| 背包满时吞物品 | 旧 `Interact()` 无条件 `Collect()` 和回池 | `CanAccept` 预审，失败留地上 |
| 预审与入包能力不一致 | 预审试旋转，兑现只按默认朝向 | 双朝向能力下沉到 `TryFindFreeArea` |
| 查询方法留下隐藏副作用 | 查找失败后物品仍保持旋转态 | 失败路径必须恢复原样 |
| 闪字反复异常 | 显隐和订阅不镜像 | 点亮/熄灭、订阅/退订逐项成对 |
| 丢弃后旋转态丢失 | `LootEntry` 没有记录 `Rotated` | 作为低优先级挂账，后续需要扩展条目字段 |

## 如何验证

### UI 与拖拽

- 提示框显示时，背包物品仍能正常拖拽。
- 只展示的 UI 不阻挡背包、按钮或场景点击。
- 面板内合法位置落位，非法位置回滚。
- 面板外松手生成世界掉落物，原背包格子清空，ghost 不残留。
- 背包窗口移动或缩放后，`RectangleContainsScreenPoint` 仍按实时面板判定内外。

### 旋转与放置

- 拖拽中按 R 会交换显示尺寸并立即刷新红绿预览。
- 旋转后的物品放下后占格正确，再次拿起仍保持旋转态。
- `TryFindFreeArea` 原朝向找不到但旋转后能放时，最终保留可放朝向。
- 双朝向都失败时，物品恢复调用前朝向。
- 丢弃再捡回目前会丢失旋转态；若后续要保真，需要让 `LootEntry` 记录旋转信息。

### 请求-确认

- 背包能容纳时，按 E 拾取后物品入包并回池，提示隐藏。
- 背包满或形状放不下时，按 E 后物品留在地上，提示仍指向该目标，并闪“背包已满”。
- `HandleCollected` 兜底路径能把无法入包的物品重新吐回世界。
- 连按 E 不会重复入包或重复归还对象池。

### 工程检查

- `IInteractable.Interact()` 改签名后，所有实现类和调用点都已编译更新。
- `OnEnable` / `OnDisable` 的事件订阅逐项镜像。
- 改动文件头部没有误引入 `UnityEditor` 命名空间。
- 本环境没有完整 Unity 工程，因此仍需在 Unity Editor 中复核 Prefab、CanvasGroup、Input Actions、Layer、场景引用和 Play Mode 结果。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 13 课修复了提示框射线阻挡，并补齐丢弃、旋转和请求-确认拾取 | B | 来自用户放入 Inbox 的课程记录 |
| `CanvasGroup.blocksRaycasts = false` 是当前提示框不挡拖拽射线的修法 | B | 原始记录明确描述了 BUG-006 根因与修复 |
| `Item.Rotated` 保留只读宽高契约，让下游网格和 UI 继续读取 `Width` / `Height` | B | 原始记录提供实现方式和取舍说明 |
| 交互返回 `bool` 后，探测器应成功才清目标，失败保留目标并反馈 | B | 原始记录描述了请求-确认链路 |
| 镜像原则适合用于事件订阅、显隐和临时状态的 review | C | 本环境基于本课多个问题进行静态归纳 |
| 第 13 课已由当前环境在 Unity Editor / Play Mode 中运行通过 | D | 本次未收到完整 Unity 工程、场景、Prefab、Canvas、Input Actions、Layer 或 `.meta`，未运行 Unity |

## 相关内容

- 前置：[背包 UI 与拖拽](inventory-ui-and-drag.md)
- 前置：[掉落分层与交互拾取](loot-layering-and-interaction.md)
- 前置：[容器搜刮与宝箱系统](container-looting-and-chests.md)
- 后续：[合并升级与邻接联动](merge-upgrade-and-adjacency.md)
- Unity：[UGUI 总览](../../unity/ugui/index.md)
- Unity：[Unity 生命周期](../../unity/lifecycle.md)
- C#：[委托与事件](../../csharp/oop/delegates-and-events.md)
- 性能：[对象池](../../performance/memory/object-pool.md)

> 📎 标签：`Unity` `UGUI` `背包系统` `拖拽` `旋转` `IInteractable` `请求确认` `项目实践`
