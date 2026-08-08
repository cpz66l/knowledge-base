# UGUI

> Unity 内置 UI 系统 — Canvas · RectTransform · 事件系统 · 自动布局

---

## 学习路线

```
阶段一 ──→ 阶段二 ──→ 阶段三 ──→ 阶段四 ──→ 阶段五
基础概念    核心控件    自动布局    综合实战    高级与优化
```

---

## 阶段一：基础概念

> 理解 UI 的"画布"和"坐标系统"，这是 UGUI 一切操作的根基。

| 主题 | 要点 | 优先级 |
|------|------|--------|
| **[Canvas](canvas.md)** | 三种渲染模式(Overlay / Camera / World)、Canvas Scaler 缩放策略 | 🔴 必学 |
| **RectTransform** | [anchor（锚点）](anchor.md)、pivot（轴心）、anchoredPosition、sizeDelta | 🔴 必学 |
| **事件系统** | EventSystem 组件、InputModule、GraphicRaycaster 射线检测 | 🟡 了解 |

**练习**：创建一个 Canvas，切换三种渲染模式，感受同一 UI 在不同模式下的表现差异。

---

## 阶段二：核心控件

> 掌握每个常用控件的用途和参数，能独立搭建一个功能完整的 UI 界面。

| 控件 | 核心用途 | 关键属性 |
|------|----------|----------|
| **[Text (TextMeshPro)](controls/text-tmp.md)** | 文字显示 | 字体、字号、富文本、SDF 渲染 |
| **[Image](controls/image.md)** | 图片显示、填充条 | ImageType(Sliced/Tiled/Filled)、Pixels Per Unit |
| **[Button](controls/button.md)** | 点击交互 | onClick 事件绑定、Transition(颜色/图片/动画) |
| **[Toggle](controls/toggle.md)** | 开关/复选框 | isOn、OnValueChanged、Toggle Group 互斥 |
| **[Slider](controls/slider.md)** | 滑动条、进度条 | min/maxValue、OnValueChanged、方向设置 |
| **[Scrollbar](controls/scrollbar.md)** | 滚动条定位 | Value、Size、NumberOfSteps |
| **[Dropdown](controls/dropdown.md)** | 下拉选择 | Options 列表、OnValueChanged |
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

## 阶段四：综合实战

> 将多个组件组合起来，解决实际界面开发中的完整问题。

| 实战 | 使用组件 | 学习目标 |
|------|----------|----------|
| **[可滚动任务列表](scrollable-task-list.md)** | ScrollRect、RectMask2D、VerticalLayoutGroup、GridLayoutGroup、ContentSizeFitter | 掌握滚动、裁剪、自动排列和动态生成列表项 |
| **[Backpack Survivor：背包 UI 与拖拽](../../projects/backpack-survivor/inventory-ui-and-drag.md)** | Canvas、RectTransform、GridLayoutGroup、EventSystem、PointerEventData | 掌握数据驱动 UI、拖拽坐标换算、合法性预览和回滚 |
| **[Backpack Survivor：背包交互补丁](../../projects/backpack-survivor/inventory-interaction-patches.md)** | CanvasGroup、GraphicRaycaster、RectTransformUtility、PointerEventData | 掌握纯展示 UI 不挡射线、面板外丢弃判定和交互失败反馈 |
| **[Backpack Survivor：合并升级与邻接联动](../../projects/backpack-survivor/merge-upgrade-and-adjacency.md)** | ItemView、Image 接口点、全量重绘投影 | 掌握把规则扫描结果投影成接口点显隐与激活状态 |
| **[Backpack Survivor：背包武器激活](../../projects/backpack-survivor/backpack-weapon-activation.md)** | ItemView 覆盖层、激活角标、延迟重绘 | 掌握拖拽期间保护 ghost、结束后补偿重绘和覆盖层自适应 |
| **[Backpack Survivor：单局框架与基础 HUD](../../projects/backpack-survivor/run-session-and-basic-hud.md)** | TextMeshProUGUI、状态文本、事件刷新 | 掌握 HUD 订阅事件、拉取初始快照和显示局内状态 |
| **[Backpack Survivor：经验成长与三选一](../../projects/backpack-survivor/level-progression-and-choice.md)** | Button、TextMeshProUGUI、面板显隐、事件回传 | 掌握升级选择 UI 只展示选项并把玩家选择交回规则层 |
| **[Backpack Survivor：波次导演与 15 分钟节奏](../../projects/backpack-survivor/wave-director-and-run-pacing.md)** | TextMeshProUGUI、事件刷新、颜色反馈 | 掌握 HUD 只显示导演广播的阶段名和颜色，不自己判断波次规则 |
| **[Backpack Survivor：战斗反馈快包](../../projects/backpack-survivor/combat-feedback-pack.md)** | World Space Canvas、TextMeshProUGUI、CanvasGroup、Billboard | 掌握世界空间伤害数字、上浮渐隐和对象池复用下的状态重置 |
| **[Backpack Survivor：胜负结算与重开闭环](../../projects/backpack-survivor/run-result-and-restart-loop.md)** | ResultPanel、Button、TextMeshProUGUI、Image.fillAmount、Slider Navigation | 掌握结算面板事件投影、环形进度显示和 HUD 控件显示化 |
| **[Backpack Survivor：构筑最小兑现](../../projects/backpack-survivor/build-payoff-dual-wield.md)** | ItemView 接口点、激活角标、validEffects 投影 | 掌握 UI 显示真实有效效果，避免候选效果和战斗收益错位 |
| **[Backpack Survivor：内容面铺开](../../projects/backpack-survivor/content-expansion-fire-rate-boost.md)** | TextMeshProUGUI、TMP Font Asset、fallback、prefab/scene 字体引用 | 掌握中文字体资产链修复，避免只在单个 Text 上临时换字体 |
| **[Backpack Survivor：物品图标与背包可读性](../../projects/backpack-survivor/item-icons-and-backpack-readability.md)** | Image 图标、透明 PNG、等级星星、邻接接边、Raycast Target | 掌握图标化背包格子的层级、射线边界和矩形适配 |
| **[Backpack Survivor：主菜单与场景流](../../projects/backpack-survivor/main-menu-and-scene-flow.md)** | Button、CanvasScaler、ScrollRect、Scrollbar | 掌握主菜单入口、声明面板、分辨率适配和场景按钮行为 |
| **[Backpack Survivor：场景氛围与演示包装](../../projects/backpack-survivor/scene-atmosphere-and-demo-polish.md)** | CanvasGroup、Input System、Tooltip 显隐 | 掌握背包面板显隐时同步透明度、交互和射线阻挡 |

---

## 阶段五：高级与优化

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

> 📎 标签：`UGUI` `Canvas` `RectTransform` `自动布局` `综合实战`
