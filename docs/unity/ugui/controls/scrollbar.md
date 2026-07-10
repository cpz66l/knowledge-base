# Scrollbar

> 滚动条 - 拖拽手柄在长内容里定位（与 ScrollView 配合）。

---

## 是什么

Scrollbar 是用于**滚动定位**的条，手柄大小反映"可见区域占总内容的比例"。通常作为 ScrollView 的子部件，也可单独使用。

!!! tip "Scrollbar vs Slider"
    - **Slider**：选数值，手柄固定大小
    - **Scrollbar**：滚动定位（0~1 位置），手柄大小随内容多少变化（Size）

    别拿 Scrollbar 当 Slider 用。

---

## 关键属性

| 属性 | 说明 |
|------|------|
| **Value** | 手柄位置（0~1，0=最左/顶，1=最右/底） |
| **Size** | 手柄占整条的比例（0~1，反映可见区占比） |
| **NumberOfSteps** | 离散步数（0=连续，>0 离散滚动） |
| **Direction** | 水平 / 垂直方向 |
| **On Value Changed (Single)** | 值变化事件 |

---

## 代码控制

```csharp
using UnityEngine;
using UnityEngine.UI;

public class ScrollbarDemo : MonoBehaviour
{
    public Scrollbar scrollbar;

    void Start()
    {
        // 监听滚动位置
        scrollbar.onValueChanged.AddListener(pos =>
        {
            Debug.Log("滚动位置：" + pos);
        });

        // 跳到顶部
        scrollbar.value = 0f;
    }
}
```

---

## 常见坑

- **手柄占满整条**：`Size` 默认 1.0 时手柄铺满，看不到滚动效果。配合 ScrollView 时 Size 由内容自动算
- **拿 Scrollbar 当 Slider**：见上文区别，两者用途不同
- **NumberOfSteps = 0**：连续滚动；设 >0 可做"翻页"式离散滚动

---

## 核心技巧

- 滚动定位用 Scrollbar，数值选择用 Slider
- 单独用时手动设 Size 控制手柄大小
- 通常让 ScrollView 自动管理其内部 Scrollbar

---

> 📎 标签：`UGUI` `Scrollbar` `滚动条`
