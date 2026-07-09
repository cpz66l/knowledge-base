# Anchor 锚点

> 自适应 UI 的核心 - 锚点决定元素相对父级的位置与缩放方式。

---

## 是什么

Anchor（锚点）定义一个 UI 元素如何相对其父容器定位、以及父容器尺寸变化时它如何跟着缩放。**写好锚点，UI 才能在不同分辨率下不跑偏。** 配合 [Canvas Scaler](canvas.md) 才是真正的自适应 UI。

每个 UI 元素的锚点由两个归一化坐标描述（范围 0~1，相对于父级矩形）：

- `anchorMin`：锚点框**左下角**
- `anchorMax`：锚点框**右上角**

---

## 锚点框的三种形态

| anchorMin 与 anchorMax 的关系 | 形态 | 行为 |
|------|------|------|
| 相等（同一点） | **点锚** | 元素保持固定位置，不随父级拉伸 |
| 水平拉开 | **水平拉伸** | 父级宽度变化时元素左右跟随拉伸 |
| 水平+垂直都拉开 | **全拉伸** | 元素铺满父级，边距随父级变化 |

---

## Anchor Presets（锚点预设）

Inspector 里 RectTransform 左上角的锚点方块，点开是 **16 种预设**：

- 9 个点位置（左上、上中、右下…）：固定在父级某个相对位置
- 3 个水平拉伸、3 个垂直拉伸、1 个全拉伸

**快捷键（点预设方块时）：**

| 按键 | 作用 |
|------|------|
| `Shift` + 点击 | 同时设置 pivot（轴心）到对应位置 |
| `Alt` + 点击 | 同时设置元素当前位置到对应锚点 |
| `Shift + Alt` + 点击 | 锚点 + 轴心 + 位置全部对齐（一键居中等） |

---

## 相关概念：pivot / anchoredPosition / sizeDelta

| 概念 | 说明 |
|------|------|
| **pivot（轴心）** | 元素自身的旋转/缩放中心，归一化 (0~1, 0~1)，(0.5,0.5)=正中 |
| **anchoredPosition** | 相对锚点的偏移位置 |
| **sizeDelta** | 相对锚点框的尺寸偏移（拉伸时是边距，点锚时是宽高） |

---

## 代码控制

```csharp
using UnityEngine;

public class AnchorDemo : MonoBehaviour
{
    public RectTransform rect;

    void Start()
    {
        // 设为全拉伸锚点（铺满父级，留 20 边距）
        rect.anchorMin = Vector2.zero;          // 左下角 (0,0)
        rect.anchorMax = Vector2.one;           // 右上角 (1,1)
        rect.offsetMin = new Vector2(20, 20);   // 左下边距
        rect.offsetMax = new Vector2(-20, -20); // 右上边距

        // 设为顶部居中点锚
        // rect.anchorMin = new Vector2(0.5f, 1f);
        // rect.anchorMax = new Vector2(0.5f, 1f);
    }
}
```

!!! tip "offsetMin / offsetMax 与 sizeDelta"
    `offsetMin` = 左下边距，`offsetMax` = 右上边距（负值表示向内缩）。比直接设 `sizeDelta` 更直观地控制拉伸元素的边距。

---

## 常见坑

- **不设锚点 -> UI 跑偏**：默认锚点在中心，分辨率一变元素就飘了。每个 UI 元素都要按设计意图设锚点
- **按钮贴边但锚点居中**：按钮在边缘，分辨率变宽后离边缘越来越远 -> 把锚点设到对应边
- **全屏背景图**：用全拉伸锚点（anchorMin=0,0；anchorMax=1,1）而不是固定尺寸

---

## 核心技巧

- 16 个预设 + Shift/Alt 快捷键能覆盖 90% 场景
- 拉伸 UI 用拉伸锚点 + offsetMin/offsetMax 控边距
- 边角元素锚点贴对应角，居中元素锚点居中

---

> 📎 标签：`UGUI` `Anchor` `RectTransform` `自适应`
