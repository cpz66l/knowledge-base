# 背包纯数据网格

> 项目：[Backpack Survivor](index.md)
>
> 状态：项目中使用
>
> 验证状态：待验证。用户课程记录描述已完成 Debug.Log 剧本验证；本环境完成纯 C# 编译与最小运行测试、静态审阅和文档验证，未重新运行 Unity。
>
> 日期：2026-07-24
>
> 阶段：V0.2 掉落与背包构筑 · 第 9 课

## 学习目标

- 把背包玩法的核心规则从 MonoBehaviour 中拆出来，形成不依赖 UnityEngine 的纯 C# 数据内核。
- 用二维数组记录物品占格，回答“能不能放、放进去、拿出来、某格是谁、哪里有空位”。
- 通过 `BS.Inventory.asmdef` 和 No Engine References 练习程序集隔离。
- 区分“同一个物品实例”和“同一种物品”，为后续合并升级规则留出正确语义。
- 评估 `HashSet<Item>` O(1) 查询的收益与冗余状态同步成本。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `BS.Inventory.asmdef` | 自定义程序集，课程记录中勾选 No Engine References，让背包数据层无法直接引用 UnityEngine |
| `Item` | 纯数据物品类型，保存 `Id`、`Width`、`Height` |
| `InventoryGrid` | 背包数据内核，维护二维占格数组和放置、移除、查询、找空位操作 |
| `InventoryDeBugTest` | 临时 MonoBehaviour 测试驱动，用日志剧本验证核心路径 |

第 8 课的掉落拾取链路已经把物品送到 `DropItem.OnCollected(LootEntry)`。第 9 课建立的是这个事件未来的买家：

```text
怪物死亡 → 掉落 → 磁吸 → Collect → OnCollected(LootEntry)
      → 背包监听 → new Item(...) → TryFindFreeArea → Place
      → InventoryGrid.OnChanged → UI 重绘
```

本页记录数据层的规则和边界；第 10 课已经在[背包 UI 与拖拽](inventory-ui-and-drag.md)中把它接入 UGUI 显示和拖拽交互，第 14 课进一步在[合并升级与邻接联动](merge-upgrade-and-adjacency.md)中加入同名同级合并、标签、接口边和邻接扫描。

## 程序集隔离

课程记录中新增了 `BS.Inventory.asmdef`，并勾选 No Engine References。这个选择让 `BS.Inventory` 成为纯 C# 模块：

- 不能直接使用 `Vector2Int`、`MonoBehaviour`、`ScriptableObject` 等 UnityEngine 类型。
- 坐标用 `int x, int y` 表达，避免把数据层绑死在 Unity API 上。
- 背包规则可以脱离场景编译和测试，未来也更容易被服务器、工具或单元测试复用。

这里的代价也很清楚：任何需要 Unity 类型的数据，都要在边界层转换，不能偷懒把引擎对象传进内核。第 9 课只收到课程笔记，没有实际 `.asmdef`、`.meta` 或 Unity 工程文件，因此本环境只记录用户课程实践和纯 C# 编译结果，不声明已检查 Unity 中的程序集资产配置。

## 数据模型

`Item` 暂时只保留物品身份和占格尺寸：

```csharp
namespace BS.Inventory
{
    public class Item
    {
        public string Id { get; }
        public int Width { get; }
        public int Height { get; }

        public Item(string id, int width, int height)
        {
            Id = id;
            Width = width;
            Height = height;
        }
    }
}
```

原始踩坑里曾把字段封成 `private readonly`，导致 `InventoryGrid` 不能读取宽高。这里改成只读属性 `{ get; }`：外部能读，构造后不能改，既保留封装也满足数据层查询。

## 网格结构

`InventoryGrid` 用二维数组保存物品引用：

```csharp
private readonly Item[,] cells;
```

数组下标约定为 `cells[x, y]`，`x` 在前，`y` 在后。格子里存物品引用，而不是 `bool`，原因是：

- `bool` 只能回答“有没有东西”。
- `Item` 引用可以回答“这里是谁”，UI、合并、联动和移除都能直接拿到物品对象。
- 6 x 8 的背包只有 48 格，引用数组的空间成本很小。

同一个多格物品会被写入它覆盖的每一个格子。这样 `GetItemAt(x, y)` 可以 O(1) 返回该格所属物品，不需要再查一张“锚点表”。

## 放置校验链

`Place` 是动作接口，但它不能相信调用方已经先问过 `CanPlaceAt`，所以内部仍要防御性校验：

```text
Place(x, y, item)
  ├─ Contains(item)？同一实例已经在背包中，拒绝
  ├─ CanPlaceAt(x, y, item)
  │   ├─ item == null，拒绝
  │   ├─ 锚点矩形越界，拒绝
  │   └─ 任一目标格已有物品，拒绝
  ├─ 逐格写入 item 引用
  └─ OnChanged?.Invoke()
```

核心实现：

```csharp
public bool CanPlaceAt(int x, int y, Item item)
{
    if (item == null)
    {
        return false;
    }

    if (x < 0 || y < 0 || x + item.Width > width || y + item.Height > height)
    {
        return false;
    }

    for (int i = 0; i < item.Width; i++)
    {
        for (int j = 0; j < item.Height; j++)
        {
            if (cells[x + i, y + j] != null)
            {
                return false;
            }
        }
    }

    return true;
}

public bool Place(int x, int y, Item item)
{
    if (Contains(item))
    {
        return false;
    }

    if (!CanPlaceAt(x, y, item))
    {
        return false;
    }

    for (int i = 0; i < item.Width; i++)
    {
        for (int j = 0; j < item.Height; j++)
        {
            cells[x + i, y + j] = item;
        }
    }

    OnChanged?.Invoke();
    return true;
}
```

这里的 `Contains(item)` 是“物理不可能原则”：同一个物品实例不能同时占两块地。但两个 `new Item("gun", 1, 2)` 是两个实例，可以共存；这给第 14 课“同 Id、同等级、非同一实例”的合并规则留下空间。

## 移除与查询

移除时按引用全扫，把同一个实例占据的所有格子清空：

```csharp
public void Remove(Item item)
{
    if (item == null)
    {
        return;
    }

    bool removed = false;

    for (int i = 0; i < width; i++)
    {
        for (int j = 0; j < height; j++)
        {
            if (cells[i, j] == item)
            {
                cells[i, j] = null;
                removed = true;
            }
        }
    }

    if (removed)
    {
        OnChanged?.Invoke();
    }
}
```

`removed` 标记避免“没有实际变化也广播”。数据层事件应该表达真实状态变化，否则 UI 可能因为空操作重复重绘。

查询接口保持简单：

```csharp
public Item GetItemAt(int x, int y)
{
    if (x < 0 || y < 0 || x >= width || y >= height)
    {
        return null;
    }

    return cells[x, y];
}
```

先判界再碰数组，是所有网格代码的基本习惯。

## 找空位

`TryFindFreeArea` 从上到下、从左到右扫描锚点，找到第一个能放的位置：

```csharp
public bool TryFindFreeArea(Item item, out int x, out int y)
{
    for (int j = 0; j < height; j++)
    {
        for (int i = 0; i < width; i++)
        {
            if (CanPlaceAt(i, j, item))
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

返回值回答“找没找到”，`out x, out y` 带出“在哪”。没找到时输出 `-1` 作为哨兵值，调用方不应该在 `false` 情况下继续使用坐标。

## 为什么暂时不用 HashSet

原始记录里专门讨论了 `Contains` 能否优化成 O(1)。方案是维护一个 `HashSet<Item>`：

```text
Place 成功 → set.Add(item)
Remove 成功 → set.Remove(item)
Contains → set.Contains(item)
```

这个方案语义上可行，因为 `Item` 是 class，默认 `==` 和默认哈希比较都按引用身份判断。但它会引入冗余状态：同一件物品是否在背包里，同时存在于 `cells` 和 `HashSet` 两处。

第 9 课选择不用 `HashSet`，理由是：

- 当前网格只有 6 x 8，最多 48 格，全扫描成本很低。
- 一旦引入冗余状态，未来移动、替换、合并、拆分等所有写入路径都必须同时维护两份结构。
- 如果以后 `Item` 重写 `Equals` / `GetHashCode` 改成按 `Id` 比较，`HashSet<Item>` 的语义会从“同一实例”悄悄变成“同一种物品”。

这不是拒绝优化，而是先把同步契约的维护成本算清楚。小规模数据结构里，简单和单一事实源通常比理论上的 O(1) 更值钱。

## 数据层事件

`InventoryGrid` 通过 C# 事件通知外部“数据变了”：

```csharp
public event Action OnChanged;
```

这不依赖 Unity，是纯 C# 能力。背包 UI 后续应该订阅 `OnChanged`，在数据变化后重绘；UI 不保存玩法状态，只把 `InventoryGrid` 的当前状态投影出来。

第 9 课确立了一个重要方向：

```text
玩家操作或拾取事件 → 改 InventoryGrid
InventoryGrid.OnChanged → UI 重绘
```

也就是说，状态单一事实源在数据层。UI 崩了可以重画，数据不应该散落在 UI 格子对象里。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| `item.Width` 不可访问 | 把 `Item` 字段封成 `private readonly` | 用只读属性 `{ get; }`，外部可读、构造后不可改 |
| 属性和参数命名混乱 | 没分清公开成员与局部变量命名 | 公开成员用 PascalCase，参数和局部变量用 camelCase |
| 测试假阳性 | 想测 `item2` 却误写成 `item1` | 测试通过后仍要确认“绿的原因对不对” |
| 命名空间写错 | `BS.Tests` 手滑写成 `BS.Text` | 命名空间和目录职责保持一致，重命名用 IDE 重构 |
| 同一实例占两块地 | `Place` 没先检查 `Contains` | 动作入口内部做完整防御校验 |
| `HashSet` 优化过早 | 为 O(1) 引入冗余状态 | 小网格先保持 `cells` 一个事实源，确有瓶颈再优化 |

## 如何验证

### 数据规则验证

- 空物品不能放入。
- 越界矩形不能放入，包括负坐标和右下边界越界。
- 与已有物品重叠时不能放入。
- 同一个实例不能被放入两次。
- 两个同 `Id` 但不同实例的物品可以共存。
- `GetItemAt` 能从任一占用格返回正确物品。
- `Remove` 能清掉同一实例占用的所有格子，未删除任何内容时不触发 `OnChanged`。
- `TryFindFreeArea` 找到首个可放锚点，找不到时返回 `false` 并输出 `-1, -1`。

### 工程边界验证

- `BS.Inventory` 不引用 UnityEngine 类型。
- UI、拾取、掉落等 Unity 层只通过边界接口把数据转入 `InventoryGrid`。
- `OnChanged` 只在真实数据变化时触发。
- 后续引入合并、移动、旋转时，先确认它们是否会增加新的写入路径和同步债务。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 9 课实现了 `Item`、`InventoryGrid`、占格放置、移除、查询、找空位和 `OnChanged` | B | 来自用户放入 Inbox 的课程记录 |
| 用户课程记录中的六条 Debug.Log 剧本已通过 | B | 原始资料描述，未提供完整 Unity 工程或日志文件 |
| 本页整理后的纯 C# 数据层可以脱离 Unity 编译并通过最小运行测试 | A | 本环境使用 .NET SDK 临时项目验证核心规则 |
| `HashSet<Item>` 暂时不值得引入 | C | 基于 6 x 8 网格规模、冗余状态同步成本和引用相等语义的静态分析 |
| `BS.Inventory.asmdef` 在 Unity 项目中已正确配置 No Engine References | D | 原始资料描述了做法，但本次未收到 `.asmdef`、`.meta` 或 Unity 工程文件，无法检查资产配置 |

## 相关内容

- 前置：[拾取与磁吸](pickup-and-magnet.md)
- 后续：[背包 UI 与拖拽](inventory-ui-and-drag.md)
- 后续：[合并升级与邻接联动](merge-upgrade-and-adjacency.md)
- C#：[委托与事件](../../csharp/oop/delegates-and-events.md)
- C#：[值类型 vs 引用类型](../../csharp/oop/value-vs-reference.md)
- 工程：[C# 工程实践路线](../../csharp/engineering/index.md)

> 📎 标签：`Unity` `背包系统` `纯 C#` `asmdef` `二维数组` `事件` `引用相等` `项目实践`
