# 背包 UI 与拖拽

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现拾取自动入包、6 x 8 网格显示、拖拽整理、红绿预览和非法回弹；本环境完成静态审阅与文档验证，未重新运行 Unity
>
> 日期：2026-07-25
>
> 阶段：V0.2 掉落与背包构筑 · 第 10 课

## 学习目标

- 把第 9 课的 `InventoryGrid` 可视化为 6 x 8 背包 UI。
- 建立“UI 只是数据投影”的单一事实源习惯。
- 用 uGUI 分层解决 Grid Layout 与自由摆放物品之间的冲突。
- 实现拖拽三态：拿起、跟手预览、落位或回滚。
- 理解新 Input System 下 UI 拖拽应该使用 `PointerEventData.position`。
- 处理 `BS.Inventory` 与 Unity 层之间的程序集依赖方向。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| Canvas 三层结构 | `BagPanel` 承载外框，`CellLayer` 生成 48 个格子背景，`ItemLayer` 自由摆放物品视图 |
| `InventoryUIController` | 订阅 `InventoryGrid.OnChanged`，把数据全量重绘为 UI，并负责拖拽流程 |
| `ItemView` | 展示物品尺寸、文字、稀有度颜色，并把指针事件转发给控制器 |
| `InventorySystem` | 背包唯一主人，持有 `InventoryGrid`，订阅 `DropItem.OnCollected` 自动入包 |
| `Rarity` 搬迁 | 将稀有度枚举下沉到 `BS.Inventory`，避免纯数据层反向依赖玩法数据层 |
| `InventoryGrid` 补强 | 增加只读索引器和 `TryGetAnchor`，服务 UI 重绘与拖拽定位 |
| `PickupLogger` | 第 8 课临时收货口退役，由 `InventorySystem` 接管拾取事件 |

本课没有改变背包放置规则，而是把第 9 课的数据内核接进可交互 UI：

```text
DropItem.Collect()
  -> DropItem.OnCollected(LootEntry)
  -> InventorySystem.HandleCollected
  -> Grid.TryFindFreeArea + Grid.Place
  -> Grid.OnChanged
  -> InventoryUIController.Redraw
```

## UI 分层结构

原始记录里的关键问题是：`GridLayoutGroup` 会接管所有直属子物体。如果把可拖拽物品也放在同一个父节点下，它会被当成第 49 个格子自动排版。

因此 UI 拆成三层：

```text
Canvas
└─ BagPanel
   ├─ CellLayer    // 只放 48 个背景格，交给 Grid Layout Group
   └─ ItemLayer    // 只放物品视图，自由设置 anchoredPosition
```

`CellLayer` 负责稳定背景格，`ItemLayer` 负责动态物品。二者是兄弟节点，不互相抢布局控制权。拖拽中的物品用 `SetAsLastSibling()` 提到同层最上方，符合 uGUI “Hierarchy 越靠下越晚绘制”的规则。

## 投影渲染

`InventoryUIController` 不保存“背包里有什么”，只在 `InventoryGrid.OnChanged` 时重新读取数据：

```csharp
private void Start()
{
    grid = inventorySystem.Grid;
    grid.OnChanged += Redraw;
    Redraw();
}
```

全量重绘的规模是 6 x 8，当前只有 48 格，简单稳定比局部刷新更重要。重绘时只生成每个物品的左上角锚点视图：

```csharp
for (int y = 0; y < grid.Height; y++)
{
    for (int x = 0; x < grid.Width; x++)
    {
        Item item = grid[x, y];
        if (item == null) continue;

        if (x > 0 && grid[x - 1, y] == item) continue;
        if (y > 0 && grid[x, y - 1] == item) continue;

        ItemView itemView = Instantiate(itemViewPrefab, itemLayer);
        RectTransform rect = itemView.GetComponent<RectTransform>();
        rect.anchoredPosition = new Vector2(x * step, -y * step);
        itemView.Bind(item, step);
    }
}
```

这里的 `-y * step` 是 UI 坐标和背包格坐标之间的约定：背包数据的 `y` 向下增加，而 `RectTransform` 局部坐标里向上是正方向。项目里应尽量让 y 翻转只出现在这一类坐标转换边界，避免到处散落。

## 拾取自动入包

`InventorySystem` 成为背包唯一主人：

```csharp
public InventoryGrid Grid { get; private set; }

private void Awake()
{
    Grid = new InventoryGrid(6, 8);
}

private void OnEnable()  => DropItem.OnCollected += HandleCollected;
private void OnDisable() => DropItem.OnCollected -= HandleCollected;
```

收到掉落事件后，将配置数据转成背包运行时物品：

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
        Debug.Log("背包已满");
    }
}
```

这里把“唯一的 `new InventoryGrid`”集中在 `InventorySystem.Awake()`，能避免 UI、拾取、调试脚本各自创建一份背包数据。UI 只向 `InventorySystem.Grid` 要引用，不自己 `new`。

## 拖拽三态

拖拽流程围绕一个核心约束：无论玩家怎么松手，物品不能丢。

### BeginDrag：拿起并记住旧锚点

```csharp
public void BeginDrag(Item item, ItemView view)
{
    if (!grid.TryGetAnchor(item, out oldX, out oldY)) return;

    targetX = oldX;
    targetY = oldY;
    dragItem = item;
    ghost = view;
    isDragging = true;

    grid.Remove(item);
    ghost.transform.SetAsLastSibling();
}
```

先记旧锚点，再从数据层 `Remove`。这一步有三个好处：

- 原位置被腾空，非法落位时回滚必然能放回去。
- 预览时不会发生“物品自己挡住自己”。
- 拖拽期间如果 `Remove` 触发 `OnChanged`，`isDragging` 会让 `Redraw` 暂停，不会把正在拖的视图销毁。

### Dragging：跟手与红绿预览

```csharp
public void Dragging(Vector2 pointerPos)
{
    if (!isDragging || ghost == null) return;

    ghost.transform.position = pointerPos;

    RectTransformUtility.ScreenPointToLocalPointInRectangle(
        itemLayer, pointerPos, null, out Vector2 localPos);

    targetX = Mathf.FloorToInt(localPos.x / step);
    targetY = Mathf.FloorToInt(-localPos.y / step);

    ghost.SetValidColor(grid.CanPlaceAt(targetX, targetY, dragItem));
}
```

`ScreenPointToLocalPointInRectangle` 的局部原点由目标 `RectTransform.pivot` 决定。原始记录中拖哪都回弹，原因之一就是 `ItemLayer` pivot 在中心，换算出来的格坐标整体偏移。把 `ItemLayer` pivot 设为左上角后，`localPos.x / step` 和 `-localPos.y / step` 才能对应网格坐标。

### EndDrag：合法落位或回滚

```csharp
public void EndDrag()
{
    if (!isDragging) return;
    isDragging = false;

    if (grid.CanPlaceAt(targetX, targetY, dragItem))
    {
        grid.Place(targetX, targetY, dragItem);
    }
    else
    {
        grid.Place(oldX, oldY, dragItem);
    }

    dragItem = null;
    ghost = null;
}
```

回滚路径必须“数学上必成功”：因为 BeginDrag 已经把原格腾空，旧锚点没有被自己占住。后续如果支持拖拽期间其他系统修改同一格，就需要额外的锁定或冲突处理策略。

## 输入系统边界

项目启用了新 Input System，并禁用了旧输入 API。原始记录里 `Input.mousePosition` 会抛异常，导致该行之后的坐标更新完全不执行，表现为 `targetX / targetY` 永远不变。

UI 指针事件已经把光标位置放在 `PointerEventData.position`：

```csharp
public void OnPointerDown(PointerEventData e) => controller.BeginDrag(item, this);
public void OnDrag(PointerEventData e)       => controller.Dragging(e.position);
public void OnPointerUp(PointerEventData e)  => controller.EndDrag();
```

在 UI 事件流里，优先使用事件对象自带的数据，不要绕去查另一个输入系统。

## 程序集依赖方向

第 10 课让 `Item` 增加了 `Rarity`。如果 `Rarity` 留在 `BS.Data`，纯数据程序集 `BS.Inventory` 就需要反向引用玩法数据层，破坏依赖方向。

本课选择把 `Rarity` 下沉到 `BS.Inventory`：

```csharp
namespace BS.Inventory
{
    public enum Rarity
    {
        Common,
        Uncommon,
        Rare,
        Epic,
        Legendary
    }
}
```

规则是：共享概念放到底层，依赖箭头朝下。Unity 层、玩法数据层可以引用 `BS.Inventory` 的类型，但 `BS.Inventory` 不应该认识 Unity 表现层或更高层配置结构。

## 数据层补强

第 10 课为了服务 UI，给 `InventoryGrid` 增加了两个读取入口：

```csharp
public Item this[int x, int y] => GetItemAt(x, y);
```

索引器只是只读窗口，外部可以写 `grid[x, y]` 读取，但不能绕过 `Place` / `Remove` 直接写入数组。

```csharp
public bool TryGetAnchor(Item item, out int x, out int y)
{
    for (int j = 0; j < Height; j++)
    {
        for (int i = 0; i < Width; i++)
        {
            if (cells[i, j] == item)
            {
                x = i;
                y = j;
                return true;
            }
        }
    }

    x = -1;
    y = -1;
    return false;
}
```

因为第 9 课已经约定同一个多格物品会写入每个占用格，从左上到右下扫描时第一次遇到该引用的位置就是左上角锚点。

## 当前静态审阅发现

> 后续演进：第 13 课已补入提示框射线阻挡修复、面板外丢弃、R 键旋转和请求-确认拾取，详见[背包交互补丁](inventory-interaction-patches.md)；第 14 课进一步加入合并预览、等级显示和接口点表现，详见[合并升级与邻接联动](merge-upgrade-and-adjacency.md)；第 15 课补入激活角标、覆盖层自适应和拖拽延迟重绘，详见[背包武器激活](backpack-weapon-activation.md)；第 21 课让接口点高亮改为投影真实有效效果，详见[构筑最小兑现](build-payoff-dual-wield.md)；第 25 课在 ItemView 上加入纯展示价值文本，并把背包总价值接到 UI 与结算快照，详见[背包价值与物品价值显示](backpack-value-and-item-value-display.md)；第 26 课又把详细价值 / 效果信息迁移到 Tooltip，详见[合并升级收益兑现](merge-upgrade-reward-payoff.md)；第 31 课把背包格子升级为图标、星星和接边分层显示，详见[物品图标与背包可读性](item-icons-and-backpack-readability.md)。本页仍保留第 10 课当时的历史边界。

- `InventoryUIController.Start()` 订阅了 `grid.OnChanged`，原始片段未展示退订。如果 UI 控制器可能被销毁而 `InventorySystem.Grid` 仍存活，应在 `OnDestroy` 或 `OnDisable` 中退订。
- 拖拽被打断时需要兜底取消流程。原始思考题已经指出，面板关闭、暂停或失焦可能导致 `EndDrag` 不触发，此时物品已从数据层移除，需要统一 `CancelDrag()` 回滚。
- `ItemView.Start()` 中 `FindAnyObjectByType<InventoryUIController>()` 适合当前小项目快速接线；如果后续大量生成物品视图或出现多个背包面板，应改成 `Bind` 时注入控制器或由父级创建后赋值。
- `DestroyAllChilden` 是原始片段中的方法名拼写，调用和定义一致时能工作，但正式代码建议重命名为 `DestroyAllChildren`，降低维护误读。
- 全量重绘当前只有 48 格，可以接受；如果背包、仓库、商店同时打开或格子规模扩大，再考虑脏标记、视图复用和局部刷新。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| `ItemLayer` 被当成第 49 个格子 | `GridLayoutGroup` 接管所有直属子物体 | 背景格和自由物品层拆成兄弟节点 |
| 拖哪都回弹 | `ItemLayer` pivot 在中心，局部坐标原点偏移 | 拖拽换算前先确认 pivot，本课改为左上角 |
| `targetX / targetY` 不更新 | 新 Input System 下调用旧 `Input.mousePosition` 抛异常 | UI 拖拽用 `PointerEventData.position` |
| 红色预览不出现 | `SetValidColor` 外又包了一层 `if (canPlace)` | 红绿分支都要实际可达 |
| 预制体字段引用不到控制器 | Prefab 资产不能引用场景对象 | 运行时查找、事件注册或创建时注入 |
| 拖拽中物品消失 | 已 `Remove` 但关闭面板导致 `EndDrag` 不触发 | 所有中断出口汇聚到 `CancelDrag()` 回滚 |
| 背包数据出现多份 | UI 或调试脚本自己 `new InventoryGrid` | `InventorySystem` 持有唯一 Grid，其他对象只取引用 |

## 如何验证

### 功能验证

- 拾取掉落物后，`InventorySystem` 收到 `LootEntry` 并生成 `Item`。
- 空背包中物品自动放到首个可用位置。
- 背包满时不会吞物品，至少有日志或吐回地上的后续策略。
- 物品显示尺寸等于 `Width x Height` 乘以 `step`。
- 稀有度颜色与 GDD 色表一致。
- 拖拽合法位置时变绿并落位。
- 拖拽非法位置、越界或重叠位置时变红并回到旧锚点。
- 未移动直接松手时，物品能放回原位置。
- 面板关闭、暂停、失焦、对象禁用时，拖拽物品不会从数据层丢失。

### UI 与生命周期验证

- `BagPanel`、`CellLayer`、`ItemLayer` 层级正确，`GridLayoutGroup` 只控制背景格。
- `ItemLayer` pivot 为左上角，坐标换算与格子位置一致。
- 场景存在 EventSystem、GraphicRaycaster 和匹配项目设置的 Input Module。
- 关闭 UI 后不会继续响应旧的 `InventoryGrid.OnChanged`。
- 重复打开背包不会重复订阅或重复生成视图。
- Profiler 观察全量重绘、实例化/销毁和 Canvas rebuild；没有数据前不写性能已优化结论。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 10 课实现了拾取自动入包、背包网格显示、拖拽、红绿预览和非法回弹 | B | 来自用户放入 Inbox 的课程记录 |
| 项目已将 `DropItem.OnCollected` 接入 `InventorySystem` 并由 `InventoryGrid.OnChanged` 驱动 UI 重绘 | B | 来自原始课程记录中的代码与链路说明 |
| UI 分层、pivot、PointerEventData 和回滚流程是本课关键设计 | B | 原始记录提供踩坑、修复过程和课程实现说明 |
| `OnChanged` 退订、拖拽取消和多面板查找仍需继续验证 | C | 根据代码片段静态审阅发现，未收到完整工程或运行日志 |
| 第 10 课已由当前环境在 Unity Editor / Play Mode 中运行通过 | D | 本次未收到完整 Unity 工程、场景、Prefab 或 `.meta`，未运行 Unity |

## 相关内容

- 前置：[背包纯数据网格](inventory-data-grid.md)
- 前置：[拾取与磁吸](pickup-and-magnet.md)
- 后续：[掉落分层与交互拾取](loot-layering-and-interaction.md)
- 后续：[背包交互补丁](inventory-interaction-patches.md)
- 后续：[合并升级与邻接联动](merge-upgrade-and-adjacency.md)
- 后续：[背包武器激活](backpack-weapon-activation.md)
- 后续：[构筑最小兑现](build-payoff-dual-wield.md)
- 后续：[背包价值与物品价值显示](backpack-value-and-item-value-display.md)
- 后续：[合并升级收益兑现](merge-upgrade-reward-payoff.md)
- 后续：[物品图标与背包可读性](item-icons-and-backpack-readability.md)
- UGUI：[UGUI 总览](../../unity/ugui/index.md)
- C#：[委托与事件](../../csharp/oop/delegates-and-events.md)
- 性能：[优化小 Tips](../../performance/perf-tips.md)

> 📎 标签：`Unity` `UGUI` `背包系统` `拖拽` `PointerEventData` `RectTransform` `事件驱动 UI` `项目实践`
