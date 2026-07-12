# 使用 ScrollRect 与自动布局实现可滚动任务列表

> 组合 ScrollRect、RectMask2D、VerticalLayoutGroup、GridLayoutGroup 与 ContentSizeFitter，实现能够动态增删内容的滚动列表。

---

## 实现目标

- 任务项超过可见区域后可以上下滑动
- 超出 Viewport 的内容不会显示
- 新增或删除任务时，Content 自动调整高度
- 支持纵向任务列表与网格任务列表两种排列方式

验证环境：Unity 6，UGUI。

---

## 核心思路

滚动列表不是由单个组件完成的，而是几个组件分工协作：

| 组件 | 职责 |
|------|------|
| **ScrollRect** | 接收拖拽和滚轮输入，改变 Content 的位置 |
| **Viewport** | 定义列表的可见区域 |
| **RectMask2D / Mask** | 裁剪超出 Viewport 的内容 |
| **VerticalLayoutGroup** | 将任务项从上到下自动排列 |
| **GridLayoutGroup** | 将任务项按固定网格排列 |
| **ContentSizeFitter** | 根据布局结果调整 Content 的高度 |
| **Scrollbar** | 显示并控制当前滚动位置，可选 |

核心关系可以概括为：

```text
ScrollRect 负责移动 Content
Mask 负责隐藏超出 Viewport 的部分
LayoutGroup 负责排列 Content 的子对象
ContentSizeFitter 负责让 Content 包住所有子对象
```

---

## Hierarchy 层级

```text
TaskPanel
└─ Scroll View                         # ScrollRect
   ├─ Viewport                         # Image + RectMask2D
   │  └─ Content                       # VerticalLayoutGroup + ContentSizeFitter
   │     ├─ TaskItem
   │     ├─ TaskItem
   │     └─ TaskItem
   └─ Scrollbar Vertical               # 可选
```

!!! tip "可以直接创建 Scroll View"
    在 Hierarchy 中选择 `UI -> Scroll View`，Unity 会自动生成 ScrollRect、Viewport、Content 和 Scrollbar 的基础结构。删除不需要的水平滚动条后，再调整各组件参数即可。

---

## 第一步：配置 ScrollRect

ScrollRect 一般挂在 `Scroll View` 根对象上。

| 属性 | 推荐设置 | 说明 |
|------|----------|------|
| **Content** | 拖入 Content | ScrollRect 实际移动的对象 |
| **Viewport** | 拖入 Viewport | 列表的可视范围 |
| **Horizontal** | 关闭 | 任务列表通常不需要水平滚动 |
| **Vertical** | 开启 | 允许上下滚动 |
| **Movement Type** | Clamped 或 Elastic | Clamped 不越界，Elastic 有回弹效果 |
| **Inertia** | 开启 | 松手后保留惯性 |
| **Scroll Sensitivity** | 按手感调整 | 控制鼠标滚轮的滚动速度 |

如果使用垂直 Scrollbar，将它拖入 `Vertical Scrollbar`，并根据界面需要设置 Visibility。

!!! warning "内容必须比 Viewport 大"
    当 Content 的高度不大于 Viewport 时，没有可滚动距离。此时拖不动通常不是 ScrollRect 失效，而是 Content 尺寸没有正确更新。

---

## 第二步：配置裁剪区域

`Viewport` 决定用户能够看到多大的区域。矩形列表推荐使用 `RectMask2D`。

### RectMask2D 与 Mask 的区别

| 组件 | 特点 | 适合场景 |
|------|------|----------|
| **RectMask2D** | 只支持矩形裁剪，不依赖模板缓冲，开销通常更低 | 普通列表、背包、任务面板 |
| **Mask** | 根据 Image 图形使用模板缓冲进行裁剪 | 圆形或其他非矩形遮罩 |

使用 `Mask` 时，Viewport 需要有一个 `Image` 组件。若不想显示这个 Image，可以关闭 Mask 的 `Show Mask Graphic`，不要直接删除 Image。

---

## 第三步：配置 Content

纵向列表的 Content 应该从顶部开始增长。推荐的 RectTransform 设置为：

```text
Anchor Min: (0, 1)
Anchor Max: (1, 1)
Pivot:      (0.5, 1)
Left:       0
Right:      0
Pos Y:      0
```

其中：

- 水平方向 Stretch，使 Content 宽度跟随 Viewport
- Anchor 与 Pivot 位于顶部，使新增任务从上向下排列
- Content 高度由 ContentSizeFitter 自动计算

---

## 方案一：纵向任务列表

在 Content 上添加：

- `VerticalLayoutGroup`
- `ContentSizeFitter`

### VerticalLayoutGroup

| 属性 | 推荐设置 |
|------|----------|
| **Padding** | 根据界面设置列表内边距 |
| **Spacing** | 设置任务项间距 |
| **Child Alignment** | Upper Left 或 Upper Center |
| **Control Child Size / Width** | 开启，让任务项适应 Content 宽度 |
| **Child Force Expand / Height** | 关闭，避免任务项被强制拉高 |

任务项高度有两种常见控制方式：

1. **固定高度**：关闭 `Control Child Size / Height`，直接设置 TaskItem 的 RectTransform 高度。
2. **由布局决定**：开启 `Control Child Size / Height`，在 TaskItem 上使用 `LayoutElement` 设置 `Preferred Height`。

不要同时让多个组件争夺同一个尺寸的控制权。

### ContentSizeFitter

```text
Horizontal Fit: Unconstrained
Vertical Fit:   Preferred Size
```

VerticalLayoutGroup 计算所有任务项所需的首选高度，ContentSizeFitter 再将 Content 高度设置成这个值。

---

## 方案二：网格任务列表

如果任务要显示成卡片、图标或者多列布局，可以将 `VerticalLayoutGroup` 替换为 `GridLayoutGroup`。

| 属性 | 推荐设置 | 说明 |
|------|----------|------|
| **Cell Size** | 设置卡片宽高 | 所有项目使用相同尺寸 |
| **Spacing** | 设置行列间距 | X 为列间距，Y 为行间距 |
| **Start Axis** | Horizontal | 先从左到右，再换行 |
| **Constraint** | Fixed Column Count | 固定列数，方便计算 Content 高度 |
| **Constraint Count** | 2、3 等 | 根据面板宽度决定 |

ContentSizeFitter 仍然设置为：

```text
Horizontal Fit: Unconstrained
Vertical Fit:   Preferred Size
```

!!! note "VerticalLayoutGroup 与 GridLayoutGroup 二选一"
    两个 LayoutGroup 不应同时挂在同一个 Content 上。纵向任务条使用 VerticalLayoutGroup，多列卡片使用 GridLayoutGroup。

---

## 动态添加任务项

将 TaskItem 制作成 Prefab，然后实例化到 Content 下：

```csharp
using UnityEngine;
using UnityEngine.UI;

public class TaskListView : MonoBehaviour
{
    [SerializeField] private RectTransform content;
    [SerializeField] private TaskItemView itemPrefab;

    public void AddTask(TaskData taskData)
    {
        TaskItemView item = Instantiate(itemPrefab, content);
        item.SetData(taskData);
    }

    public void RemoveTask(TaskItemView item)
    {
        Destroy(item.gameObject);
    }

    public void RefreshLayoutImmediately()
    {
        Canvas.ForceUpdateCanvases();
        LayoutRebuilder.ForceRebuildLayoutImmediate(content);
    }
}
```

UGUI 通常会在当前帧结束前自动刷新布局。只有在创建项目后需要**立刻读取 Content 高度或滚动位置**时，才需要手动调用 `RefreshLayoutImmediately`。

例如刷新后跳到列表顶部：

```csharp
[SerializeField] private ScrollRect scrollRect;

public void ScrollToTop()
{
    RefreshLayoutImmediately();
    scrollRect.verticalNormalizedPosition = 1f;
}
```

垂直滚动位置中，`1` 表示顶部，`0` 表示底部。

---

## 常见问题

### 列表无法滚动

- 检查 ScrollRect 是否正确引用 Content 和 Viewport
- 检查是否开启 Vertical
- 检查 Content 高度是否真的大于 Viewport
- 检查 ContentSizeFitter 的 Vertical Fit 是否为 Preferred Size

### 内容能拖动，但松手后立即回去

通常说明 Content 没有被布局系统撑高。ScrollRect 判断内容没有超出 Viewport，因此将它恢复到边界内。

### 第一个任务出现在中间

检查 Content 的 Anchor 和 Pivot 是否位于顶部，并将 VerticalLayoutGroup 的 Child Alignment 设置为 Upper 开头的选项。

### 任务项高度异常

检查 VerticalLayoutGroup 的 `Control Child Size / Height`、`Child Force Expand / Height`，以及任务项上的 LayoutElement 是否互相冲突。

### 新增任务后尺寸没有立刻变化

布局默认在帧末更新。如果当前代码必须立即使用新尺寸，可以调用 `Canvas.ForceUpdateCanvases` 和 `LayoutRebuilder.ForceRebuildLayoutImmediate`。

### Mask 没有裁剪内容

- 确认需要裁剪的对象是 Viewport 的子孙对象
- 使用普通 Mask 时确认同一对象上存在 Image
- 普通矩形列表优先检查并使用 RectMask2D

---

## 性能注意事项

- 少量任务可以直接使用 LayoutGroup 和 ContentSizeFitter
- 避免嵌套过多 LayoutGroup，这会增加布局重建成本
- 批量创建任务时，尽量一次完成数据更新，再统一刷新布局
- 不要每帧调用 `ForceRebuildLayoutImmediate`
- 数百或数千个任务项不应全部实例化，应使用对象池和列表虚拟化，只保留可见区域附近的项目

---

## 核心技巧

- ScrollRect 负责滚动，Scrollbar 只是可选的定位和显示部件
- 普通矩形列表优先使用 RectMask2D，而不是 Mask
- Content 的顶部 Anchor 与 Pivot 决定列表增长方向
- VerticalLayoutGroup 适合单列任务，GridLayoutGroup 适合多列卡片
- ContentSizeFitter 的任务是让 Content 尺寸跟随布局结果
- 强制刷新布局只用于必须立即读取布局结果的场景

---

> 📎 标签：`UGUI` `ScrollRect` `RectMask2D` `VerticalLayoutGroup` `GridLayoutGroup` `ContentSizeFitter` `滚动列表`
