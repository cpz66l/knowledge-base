# 物品图标与背包可读性

> 学习状态：项目中使用
>
> 验证状态：待验证。用户记录称构建通过，本次未重复运行 Unity，且 alpha 差异仍待确认。
>
> 前置知识：[攻击芯片效果实装](attack-damage-chip-effect.md)、[背包 UI 与拖拽](inventory-ui-and-drag.md)、[旋转邻接方向修正](rotation-adjacency-direction-fix.md)
>
> 对应项目：[Backpack Survivor](index.md)
>
> 下一步：第 32 课新手目标提示与局内可读性
>
> 日期：2026-08-06
>
> 阶段：V0.2 掉落与背包构筑 · 第 31 课

## 学习目标

- 把背包格子从“文字 + 稀有度底色”升级成可扫读的图标化表达。
- 用 `ItemIconResolver` 在表现层完成 `ItemTag -> Sprite` 映射，保持 `BS.Inventory` 纯 C# 边界。
- 让透明 PNG 图标叠在稀有度底色上，同时保留文字兜底。
- 用等级星星替代格子内等级文字，减少阅读负担。
- 把邻接接口从点改成边，让“边连接”的规则更直观。
- 让图标、接边、星星和激活角标随物品矩形尺寸与旋转状态重新布局。

## 当前理解

第 31 课解决的是 Demo 可读性问题。第 21～30 课已经让背包构筑真实影响战斗，但如果背包格子主要靠文字和颜色，玩家仍需要逐个阅读才能判断物品类型、等级和连接方向。

当前信息层级改成：

```text
稀有度背景色
  -> 透明物品图标
  -> 邻接接边 / 激活武器角标 / 等级星星
  -> 悬停 Tooltip 详细信息
```

这条分层让格子只承担“一眼识别”，详细数值继续留给 Tooltip，避免小格子塞满文字。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `ItemIconResolver` | 在 `BS.Presentation` 中按 `ItemTag` 查询 `Sprite` |
| `InventoryUIController.itemIconResolver` | `Redraw()` 时查询图标并传入 `ItemView.Bind()` |
| `ItemView.iconImage` | 显示透明物品图标；无图标时关闭并回退文字 |
| `Image.preserveAspect` | 保持图标原始宽高比，避免 Sprite 被拉伸 |
| `Image.raycastTarget = false` | 防止装饰图标、星星和接边吃掉拖拽 / Tooltip 射线 |
| `LevelOne / LevelTwo / LevelThree` | 用右上角星星表达 Lv.1 / Lv.2 / Lv.3 |
| `top/right/bottom/leftConnector` | 从点状接口升级为边缘长条，灰色表示可连，金色表示生效 |
| `LayoutIcon()` | 按 `item.Width / item.Height` 计算矩形图标区域 |
| `HandleRotate()` | 旋转后通过 `UpdateOverlayLayout(step)` 统一重排表现层 |

## 最小示例

### ItemIconResolver

```csharp
public class ItemIconResolver : MonoBehaviour
{
    [System.Serializable]
    private class IconEntry
    {
        public ItemTag tag;
        public Sprite sprite;
    }

    [SerializeField] private List<IconEntry> icons;

    public Sprite GetIcon(Item item)
    {
        if (icons == null || item == null || icons.Count == 0)
            return null;

        foreach (var entry in icons)
        {
            if (entry.tag == item.Tag)
                return entry.sprite;
        }

        return null;
    }
}
```

`ItemIconResolver` 只做表现资源映射，不处理规则、掉落或战斗。它放在 `BS.Presentation`，可以避免把 Unity `Sprite` 引入第 9 课建立的纯 C# 背包数据层。

### Redraw 时传入图标

```csharp
Sprite sprite = itemIconResolver == null ? null : itemIconResolver.GetIcon(item);
itemView.Bind(item, step, this, sprite);
```

`InventoryUIController` 继续扮演投影器：数据层给 `Item`，表现层给 `Sprite`，最终由 `ItemView` 按当前格子状态显示。

### 透明图标与文字兜底

```csharp
if (iconImage != null && iconSprite != null)
{
    iconImage.sprite = iconSprite;
    iconImage.preserveAspect = true;
    iconImage.raycastTarget = false;
    iconImage.enabled = true;
}
else if (iconImage != null)
{
    iconImage.enabled = false;
    label.text = $"{item.Id}";
}
```

图标配置遗漏时不让格子空白，仍用物品名兜底。装饰性 `Image` 必须关闭射线，否则透明区域仍可能按矩形挡住拖拽和 Tooltip。

### 星星和接边布局

```csharp
float starSize = Mathf.Clamp(step * 0.20f, 12f, 18f);
float edgeThickness = Mathf.Clamp(step * 0.08f, 4f, 7f);

Vector2 upAndDown = new Vector2(itemPixelWidth - inset * 2, edgeThickness);
Vector2 leftAndRight = new Vector2(edgeThickness, itemPixelHeight - inset * 2);

LayoutEdge(topConnector, new Vector2(0.5f, 1), new Vector2(0, -edgeInset), upAndDown);
LayoutImage(LevelOne, new Vector2(1, 1), new Vector2(-inset, -inset - 3f), starSize);
```

星星从右上角向左展开，接边按物品真实宽高拉成长条。邻接规则的本质是边与边相连，用接边比小点更贴近玩家直觉。

### 矩形图标适配

```csharp
float availableW = itemPixelWidth - inset * 2f;
float availableH = itemPixelHeight - inset * 2f;

float iconWidth = availableW * 0.85f;
float iconHeight = availableH * 0.85f;
Vector2 size = new Vector2(iconWidth, iconHeight);
```

长条武器、防具和芯片不再被统一塞进正方形图标框。图标容器跟随物品占格比例，Sprite 本体再用 `preserveAspect` 保持等比。

## 项目中的应用

### 数据层不碰 Sprite

背包数据层继续只知道 `ItemTag / Rarity / Level / Size`。图标是表现层资源，由场景中的 `ItemIconResolver` 配置映射。这样以后要替换图标、换图集或加图标偏移，不会影响 `BS.Inventory` 的纯 C# 测试边界。

### 稀有度、类型、等级、规则分层显示

当前格子里每层信息各司其职：

```text
背景色：稀有度
透明图标：物品类型
星星：合成等级
灰边：可连接方向
金边：真实有效效果
激活角标：当前驱动战斗的武器
Tooltip：详细价值和效果
```

这比把名称、等级、价值和效果全部写进格子更可读，也更接近正式 Demo 观感。

### 旋转后自动重排

`HandleRotate()` 已经更新 ghost 的尺寸并调用 `UpdateOverlayLayout(step)`。因为图标区域、接边、星星和激活角标都从 `item.Width / item.Height` 推导，旋转后不需要额外写一套图标补丁。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 图标挡住拖拽或 Tooltip | 透明 `Image` 仍按 RectTransform 吃射线 | 装饰性图标、星星、接边关闭 `Raycast Target` |
| 图标被拉伸变形 | 容器矩形直接拉 Sprite | 设置 `preserveAspect = true` |
| 长条武器看起来像头像 | 所有图标都塞进正方形框 | 图标区域按物品 `Width / Height` 做矩形适配 |
| 格子信息过载 | 同时显示名称、等级、价值、效果和图标 | 格子只保留扫读信息，详细信息交给 Tooltip |
| 规则显示不像规则 | 邻接方向用小点表达 | 改成边缘长条，贴近“边连接”的规则本质 |
| 图标系统污染数据层 | `Item` 直接持有 `Sprite` | 用 `ItemIconResolver` 在 Presentation 层映射 |
| 颜色 alpha 超出设计范围 | Unity `Color` alpha 应按 0～1 理解 | 保持透明度参数在 0～1，并在代码审阅中检查 |

## 如何验证

### 当前已记录证据

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 31 课已通过用户验收：主要物品有图标，透明图标能叠稀有度底色，星星与接边提升可读性，拖拽、旋转、Tooltip、武器激活标记未被破坏 | B | 来自用户放入 Inbox 的课程记录 |
| 用户记录称 `dotnet build` 通过，危险 using 扫描干净 | B | 来自用户课程记录；本次未重复运行外部工程构建 |
| 外部工程静态可见 `ItemIconResolver.cs` 与 `.meta`，GUID 为 `fa1071621d7284d4c8adbcb5323dc0db` | C | 本环境只读查看外部 Unity 工程文件 |
| `InventoryUIController.cs` 静态可见 `itemIconResolver` 查询并把 `Sprite` 传入 `ItemView.Bind()` | C | 本环境只读查看外部 Unity 工程脚本 |
| `ItemView.cs` 静态可见 `iconImage`、`LevelOne/Two/Three`、接边布局、矩形图标适配、`preserveAspect` 与 `raycastTarget = false` | C | 本环境只读查看外部 Unity 工程脚本 |
| `ItemView.prefab` 静态可见 `iconImage` 与三颗星星引用 | C | 本环境只读查看 Prefab YAML |
| `01-Run.unity` 静态可见 `ItemIconResolver` 挂入场景、7 个 `ItemTag -> Sprite` 映射、`InventoryUIController.itemIconResolver` 引用 | C | 本环境只读查看场景 YAML |
| 图标 PNG 与 `.meta` 静态可见，主要纹理 `alphaIsTransparency: 1` | C | 本环境只读查看 `Art/BackpackItemTextures` |
| 当前环境未运行 Unity Editor / Play Mode、Profiler 或 Player Build | D | 未启动 Unity，未亲自复测真实画面、交互、性能或 Build |
| 笔记称接边 alpha 已控制在 0～1，但外部 `ItemView.cs` 仍静态可见金色接边 `new Color(..., 8f)` | D | 证据冲突，需在后续代码或 Unity 中确认是否已修正 |

### 待补验证

- 在 Unity Play Mode 中逐项确认 Pistol / Rifle / Shotgun / Magazine / AttackDamageChip / Armor / Medical / Collection 的图标显示。
- 复核透明图标不会挡住拖拽、悬停、Tooltip 和背包放置。
- 复核 1x1、2x1、3x2、2x3 物品的图标矩形适配和旋转后的重排。
- 复核灰色可连接边与金色有效边在不同稀有度底色上都可读。
- 复核 `ItemView.cs` 中金色接边 alpha 是否已改回 0～1 范围。
- 用 Player Build 复核图标 Sprite、透明通道、星星和中文 Tooltip 在构建后仍正常显示。

## 复盘

- 原来的理解：背包格子有文字和稀有度颜色就足够开发期使用。
- 实践后的结论：构筑系统越复杂，越需要图标、星星和接边把规则翻译成一眼能读懂的 UI。
- 仍未理解：缺少当前环境亲自运行的 Play Mode 画面证据、Player Build 证据，以及 `alpha = 8f` 与笔记描述之间的差异确认。

## 相关内容

- 前置：[攻击芯片效果实装](attack-damage-chip-effect.md)
- 前置：[背包 UI 与拖拽](inventory-ui-and-drag.md)
- 前置：[旋转邻接方向修正](rotation-adjacency-direction-fix.md)
- 前置：[构筑最小兑现](build-payoff-dual-wield.md)
- UGUI：[Image](../../unity/ugui/controls/image.md)
- UGUI：[UGUI 总览](../../unity/ugui/index.md)
- C#：[C# 工程实践路线](../../csharp/engineering/index.md)
- 检查清单：[Unity 项目能力](../../checklists/unity-project.md)

> 标签：`Unity` `UGUI` `背包 UI` `ItemIconResolver` `透明贴图` `Raycast Target` `邻接接边` `项目实践`
