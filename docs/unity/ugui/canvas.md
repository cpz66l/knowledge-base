# Canvas

> UI 的"画布" - 所有 UGUI 元素的根容器，决定 UI 如何渲染到屏幕。

---

## 是什么

Canvas 是所有 UI 元素的**根容器**。每个 UGUI 控件（Text、Image、Button…）都必须是某个 Canvas 的子对象，否则不会渲染。一个场景可以有多个 Canvas。

---

## 三种渲染模式

Canvas 组件的 `Render Mode` 决定 UI 怎么画到屏幕上：

| 模式 | 说明 | 典型场景 |
|------|------|----------|
| **Screen Space - Overlay** | UI 画在屏幕最上层，覆盖一切 3D 内容（默认） | 主菜单、HUD、弹窗 |
| **Screen Space - Camera** | UI 画在摄像机前某个距离的平面上，受摄像机效果影响 | 需要 UI 受后处理/景深影响 |
| **World Space** | UI 作为 3D 物体存在于场景中，可被遮挡、可旋转 | 游戏内告示牌、角色头顶血条 |

!!! tip "Overlay 与 Camera 的区别"
    Overlay 模式 UI 永远在最上层，不受摄像机 FOV/旋转影响；Camera 模式 UI 像贴在摄像机前的一块板，会被摄像机的属性影响。新手默认用 Overlay 即可。

---

## Canvas Scaler（缩放策略）

Overlay / Camera 模式下，Canvas 上挂载的 `Canvas Scaler` 决定 UI 如何适应不同分辨率：

| 模式 | 行为 | 适用 |
|------|------|------|
| **Constant Pixel Size** | 固定像素大小，不随分辨率缩放 | 像素精确的复古游戏 |
| **Scale With Screen Size** ⭐ | 以设计分辨率为基准等比缩放（推荐） | 绝大多数项目 |
| **Constant Physical Size** | 按物理尺寸（DPI）缩放 | 需要真实物理尺寸的 UI |

**Scale With Screen Size 关键参数：**

- `Reference Resolution`：设计分辨率（如 1920×1080）
- `Screen Match Mode`：
  - `Match Width Or Height` - 按 width/height 权重缩放（最常用）
  - `Expand` - 扩展不裁切
  - `Shrink` - 收缩不超出

!!! warning "Match 值怎么选"
    `Match` 滑条 0=只跟宽度、1=只跟高度。横屏游戏偏 0，竖屏游戏偏 1，常见取 0.5 兼顾。配合 [Anchor 锚点](anchor.md) 才能让 UI 真正自适应。

---

## 创建与层级

1. Hierarchy 右键 -> `UI` -> `Canvas`（会自动带上 EventSystem）
2. 控件作为 Canvas 的子对象
3. 多个 Canvas 用 `Sorting Layer` / `Order in Layer` 控制叠加顺序

---

## 常见坑

- **忘加 EventSystem**：Button/Toggle 点击无反应，先检查场景里有没有 EventSystem 对象
- **Overlay 模式 UI 不受光照**：想要 UI 受光照影响得用 Camera / World Space
- **嵌套 Canvas**：子 Canvas 可独立设 Render Mode，常用于局部 UI 性能优化（减少主 Canvas 重建范围）

---

## 核心技巧

- 默认 Screen Space - Overlay + Scale With Screen Size
- 多 Canvas 用 Sorting Order 控制层叠
- World Space 做游戏内 UI（血条、名牌）

---

> 📎 标签：`UGUI` `Canvas` `渲染模式` `Canvas Scaler`
