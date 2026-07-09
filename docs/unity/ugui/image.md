# Image

> 图片显示 - 纯贴图、九宫格、填充条全靠它。

---

## 是什么

Image 用于在 UI 上显示一张 Sprite。既是最基础的图片控件，也是填充条（血条/进度条）和可点击区域的核心。

---

## 关键属性

| 属性 | 说明 |
|------|------|
| **Source Image** | 要显示的 Sprite（留空显示纯色矩形） |
| **Color** | 叠加颜色（白色 = 原色） |
| **Image Type** | 图片类型（见下表） |
| **Raycast Target** | 是否参与点击射线检测 |
| **Preserve Aspect** | 保持宽高比 |
| **Pixels Per Unit Multiplier** | 控制九宫格边缘粗细 |

---

## Image Type（图片类型）

| 类型 | 说明 | 典型用途 |
|------|------|----------|
| **Simple** | 原图直接拉伸显示 | 普通图片 |
| **Sliced** | 九宫格切片，边缘不变形 | 可伸缩的按钮/面板背景 |
| **Tiled** | 平铺重复 | 重复纹理（砖墙、格子） |
| **Filled** | 按比例部分填充 | 血条、冷却进度条 |

### Sliced（九宫格）

需要先在 Sprite 资源里设置 `Border`（四条边框宽度），切换为 Sliced 后图片四角不变形、中间拉伸。**做可缩放按钮背景必备**。

### Filled（填充条）

| 参数 | 说明 |
|------|------|
| **Fill Method** | Horizontal 水平 / Vertical 垂直 / Radial 扇形 360° 等 |
| **Fill Origin** | 填充起点 |
| **Fill Amount** | 0~1 的填充比例 |
| **Clockwise** | 扇形是否顺时针 |

把 `Fill Amount` 设为 0.7，就是 70% 的血条。

---

## 代码控制

```csharp
using UnityEngine;
using UnityEngine.UI;

public class ImageDemo : MonoBehaviour
{
    public Image hpBar;       // 血条 Image（Filled 类型）
    public Sprite newIcon;    // 要切换的图标

    public void SetHp(float ratio)
    {
        // 控制 Fill Amount（0~1），ratio = 当前血量 / 最大血量
        hpBar.fillAmount = ratio;
    }

    public void ChangeIcon()
    {
        // 切换显示的 Sprite
        hpBar.sprite = newIcon;
    }
}
```

---

## 常见坑

- **Sliced 没设 Border**：九宫格拉伸时四角也跟着变形。先在 Sprite 的 Inspector 设好 Border 再切 Sliced
- **Raycast Target 浪费性能**：纯装饰性图片（背景、图标）应取消勾选 `Raycast Target`，否则每帧参与射线检测
- **Filled 方向不对**：血条往回填，调整 `Fill Origin` 和 `Clockwise`

---

## 核心技巧

- 可缩放面板/按钮背景 -> Sprite 设 Border + Image Type = Sliced
- 血条/冷却 -> Image Type = Filled + 代码控制 fillAmount
- 装饰图关闭 Raycast Target 省性能

---

> 📎 标签：`UGUI` `Image` `九宫格` `填充条`
