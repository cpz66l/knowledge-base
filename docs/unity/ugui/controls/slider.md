# Slider

> 滑动条 - 拖拽手柄选择范围内的数值（音量、进度）。

---

## 是什么

Slider 让用户在一个数值区间内拖拽选择，自带 `Fill`（已填充部分）和 `Handle`（可拖拽手柄）两个子对象。典型用途：音量条、角色创建的数值滑条、进度条。

---

## 结构

```
Slider
  ├─ Background          背景轨道
  ├─ Fill Area
  │    └─ Fill             已填充部分（随 Value 变长）
  └─ Handle Slide Area
       └─ Handle           可拖拽手柄
```

---

## 关键属性

| 属性 | 说明 |
|------|------|
| **Min Value / Max Value** | 数值区间（默认 0~1） |
| **Whole Numbers** | 只取整数（关闭可取小数） |
| **Value** | 当前值 |
| **Direction** | Left To Right / Right To Left / Bottom To Top / Top To Bottom |
| **Interactable** | 是否可拖拽 |
| **On Value Changed (Single)** | 值变化事件，参数是新的 float 值 |

---

## 代码控制

```csharp
using UnityEngine;
using UnityEngine.UI;

public class SliderDemo : MonoBehaviour
{
    public Slider volumeSlider;

    void Start()
    {
        // 监听拖拽，参数 float = 新值
        volumeSlider.onValueChanged.AddListener(value =>
        {
            Debug.Log("音量：" + value);
        });

        // 代码设置当前值
        volumeSlider.value = 0.5f;
    }
}
```

---

## 常见坑

- **拖不动手柄**：Handle 的 `Raycast Target` 被关了，或场景缺 EventSystem
- **值带小数**：要整数勾 `Whole Numbers`
- **方向反了**：调 `Direction`
- **初始值超出范围**：Value 会被自动 clamp 到 [Min, Max]

---

## 核心技巧

- 音量/进度 -> Slider + OnValueChanged
- 要离散值勾 Whole Numbers
- Fill 和 Handle 子对象可换 Sprite 自定义外观

---

> 📎 标签：`UGUI` `Slider` `滑动条` `OnValueChanged`
