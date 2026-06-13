# UGUI

> Unity 内置 UI 系统 — Canvas · RectTransform · 事件系统 · 自动布局

---

## 学习路线

```
阶段一 ──→ 阶段二 ──→ 阶段三 ──→ 阶段四
基础概念    核心控件    自动布局    高级与优化
```

---

## 阶段一：基础概念

> 理解 UI 的"画布"和"坐标系统"，这是 UGUI 一切操作的根基。

| 主题 | 要点 | 优先级 |
|------|------|--------|
| **Canvas** | 三种渲染模式(Overlay / Camera / World)、Canvas Scaler 缩放策略 | 🔴 必学 |
| **RectTransform** | anchor（锚点）、pivot（轴心）、anchoredPosition、sizeDelta | 🔴 必学 |
| **事件系统** | EventSystem 组件、InputModule、GraphicRaycaster 射线检测 | 🟡 了解 |

**练习**：创建一个 Canvas，切换三种渲染模式，感受同一 UI 在不同模式下的表现差异。

---

## 阶段二：核心控件

> 掌握每个常用控件的用途和参数，能独立搭建一个功能完整的 UI 界面。

| 控件 | 核心用途 | 关键属性 |
|------|----------|----------|
| **Text (TextMeshPro)** | 文字显示 | 字体、字号、富文本、SDF 渲染 |
| **Image** | 图片显示、填充条 | ImageType(Sliced/Tiled/Filled)、Pixels Per Unit |
| **Button** | 点击交互 | onClick 事件绑定、Transition(颜色/图片/动画) |
| **Toggle** | 开关/复选框 | isOn、OnValueChanged、Toggle Group 互斥 |
| **Slider** | 滑动条、进度条 | min/maxValue、OnValueChanged、方向设置 |
| **Dropdown** | 下拉选择 | Options 列表、OnValueChanged |
| **InputField** | 文本输入 | ContentType(标准/密码/数字)、OnValueChanged、OnEndEdit |
| **ScrollView** | 滚动列表 | ScrollRect、Viewport、Content、滚动条 |
| **Mask** | 裁剪遮罩 | 配合 Image 使用、性能注意事项 |

**练习**：搭建一个"设置菜单" — 音量 Slider + 画质 Dropdown + 全屏 Toggle + 确认 Button。

---

## 阶段三：自动布局

> 让 UI 自适应不同分辨率，告别手动拖坐标。

| 组件 | 作用 |
|------|------|
| **HorizontalLayoutGroup** | 子对象水平排列 |
| **VerticalLayoutGroup** | 子对象垂直排列 |
| **GridLayoutGroup** | 子对象网格排列（固定大小） |
| **ContentSizeFitter** | 根据子对象大小自动调整自身尺寸 |
| **AspectRatioFitter** | 强制宽高比 |
| **LayoutElement** | 控制布局中的最小/首选/弹性尺寸 |

**核心组合技**：

```
ScrollView
  └─ Content (GridLayoutGroup + ContentSizeFitter)
       ├─ Item 1
       ├─ Item 2
       └─ Item 3 ...
```

**练习**：做一个"背包格子" — 自动换行的 GridLayoutGroup + 动态增删物品。

---

## 阶段四：高级与优化

> 生产级 UI 的必备知识。

| 主题 | 要点 |
|------|------|
| **Canvas Group** | 统一控制子对象透明度、可交互性、射线阻挡 |
| **图集与 Drawcall** | 同一个图集的图片合批、减少 Drawcall、Sprite Atlas |
| **世界空间 UI** | World Space Canvas、UI 与 3D 对象混合、血条/名字板 |
| **事件系统深入** | 自定义输入处理、多种 InputModule、UI 与 3D 点击分层 |
| **Canvas 重建** | SetVerticesDirty、网格重建触发条件、避免频繁重建 |

**练习**：做一个 3D 角色头顶的"血条 + 名字"世界空间 UI，支持点击选中。

---

> 📎 标签：`UGUI` `Canvas` `RectTransform` `自动布局`
