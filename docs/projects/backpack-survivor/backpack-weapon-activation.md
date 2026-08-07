# 背包武器激活

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现背包武器实体激活、左上优先级、激活物品 UI 标记、拖拽延迟重绘和覆盖层自适应；本环境完成静态审阅与文档验证，未重新运行 Unity
>
> 日期：2026-07-29
>
> 阶段：V0.2 掉落与背包构筑 · 第 15 课

## 学习目标

- 让背包中的武器物品真正驱动玩家身边的自动武器实体。
- 用 `InventoryGrid.OnChanged` 作为背包变化入口，集中刷新当前激活武器。
- 用背包位置作为可见、可操作的激活优先级规则。
- 区分 `ItemTag` 类别和 `Item` 实例：类别用于匹配武器类型，实例用于 UI 标记哪一件真正激活。
- 处理拖拽期间数据变化与 UI 全量重绘之间的冲突。
- 让接口点和激活角标根据格子尺寸、物品尺寸和旋转状态自适应布局。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `BackpackWeaponActivator` | 监听 `InventoryGrid.OnChanged`，按背包当前状态刷新玩家身边自动武器实体 |
| `WeaponSlot` | 把 `ItemTag` 与场景中的 `WeaponObject` 绑定成可配置关系 |
| `activeWeaponLimit` | 当前默认自动武器激活上限，课程目标为 `1` |
| `InventoryGrid.GetUniqueItems` | 按从上到下、从左到右返回背包内唯一物品实例列表 |
| `activeWeaponItems` | 用 `HashSet<Item>` 记录当前真正激活的物品实例 |
| `InventoryUIController.Redraw` | 生成 `ItemView` 时查询具体物品是否激活，并投影为激活角标 |
| `needsRedrawAfterDrag` | 拖拽期间延迟一次被拦截的重绘，结束后按需要补画 |
| `ItemView.UpdateOverlayLayout` | 根据 `step` 计算接口点和激活角标尺寸、锚点与内边距 |

第 15 课把第 14 课的“构筑候选”推进到更直观的一步：背包里有哪把武器，会影响场景里哪把自动武器可用。本课先完成 Demo 能看懂的激活闭环，DualWield 在后续[构筑最小兑现](build-payoff-dual-wield.md)中进入真实战斗结算；真实冷却遮罩仍后移。第 16 课随后在[单局框架与基础 HUD](run-session-and-basic-hud.md)中补上本局时间、胜负、暂停和基础 HUD。

第 29 课进一步沿用这个激活入口：`TryActivateItem()` 不只负责开启具体 `AutoWeapon`，还会按背包中的具体 `Item.Rarity / Item.Level` 注入武器伤害倍率，详见[武器稀有度与等级差异](weapon-rarity-and-level-scaling.md)。

## Demo 收口闸

课程开头继续执行运行时代码卫生门闸：

```text
UnityEditor.*
ShadowCascadeGUI
Mono.Cecil
多余 Rendering using
临时测试注释
```

这类清理不是知识正文的重点，但它是项目交付习惯的一部分：不能把“能跑但不干净”的临时状态滚进下一课。第 15 课还特别校准了场景规则：默认自动武器激活上限为 `1`，后续第 21 课由 DualWield 负责突破默认上限。

## 背包武器激活器

`BackpackWeaponActivator` 监听背包变化，每次变化后刷新武器实体：

```csharp
[System.Serializable]
private class WeaponSlot
{
    public ItemTag Tag;
    public GameObject WeaponObject;
}

[SerializeField] private int activeWeaponLimit = 1;
[SerializeField] private List<WeaponSlot> weaponSlots;
```

`WeaponSlot` 的价值是把“什么物品对应什么武器实体”变成配置表。后续新增步枪、霰弹枪、狙击枪时，优先在 Inspector 配置，不优先改一串逻辑分支。

刷新策略采用“先全关，再按当前背包重算”：

```csharp
private void RefreshActiveWeapons()
{
    foreach (var weapon in weaponSlots)
    {
        if (weapon == null) continue;
        if (weapon.WeaponObject == null) continue;

        weapon.WeaponObject.SetActive(false);
    }

    activeWeaponItems.Clear();

    List<Item> items = inventorySystem.Grid.GetUniqueItems();
    int activatedCount = 0;

    foreach (var item in items)
    {
        foreach (var weapon in weaponSlots)
        {
            if (weapon == null) continue;
            if (activatedCount >= activeWeaponLimit) break;
            if (item.Tag != weapon.Tag) continue;
            if (weapon.WeaponObject == null) continue;

            weapon.WeaponObject.SetActive(true);
            activeWeaponItems.Add(item);
            activatedCount++;
            break;
        }
    }
}
```

背包变化频率低，武器数量也少。当前阶段用全量重算换取确定性和可审阅性，比维护一套复杂差量状态更稳。等武器状态、冷却和多效果都稳定后，再考虑差量更新。

## 位置优先级

`InventoryGrid.GetUniqueItems()` 返回唯一物品列表：

```csharp
public List<Item> GetUniqueItems()
{
    List<Item> placedItems = new List<Item>();
    HashSet<Item> itemSet = new HashSet<Item>();

    for (int y = 0; y < Height; y++)
    {
        for (int x = 0; x < Width; x++)
        {
            Item item = cells[x, y];
            if (item == null) continue;
            if (itemSet.Contains(item)) continue;

            itemSet.Add(item);
            placedItems.Add(item);
        }
    }

    return placedItems;
}
```

`HashSet<Item>` 用于去重：一个 2 x 2 物品会占四个格子，但它仍然只能作为一个物品参与激活。

遍历顺序本身成为玩法契约：

```text
y 从小到大
  x 从小到大
    -> 从上到下、从左到右
    -> 越靠左上，激活优先级越高
```

这条规则比隐藏的 `Priority` 字段更适合 Demo：玩家能看见、能操作、能通过移动物品立刻理解“背包整理 = 战斗选择”。

## 实例级激活标记

UI 标记不能只看 `ItemTag`：

```csharp
itemView.SetActiveWeapon(backpackWeaponActivator.IsWeaponItemActive(item));
```

如果记录的是 `ItemTag.Pistol`，背包里所有手枪都会亮；但默认上限为 1 时，真正激活的只是一把具体手枪。因此 `BackpackWeaponActivator` 用 `HashSet<Item>` 保存激活实例。

这条边界和第 14 课一致：

```text
ItemTag：类别，用于匹配“这是什么武器”
Item：实例，用于回答“当前生效的是哪一件”
```

当系统里出现“同类多个对象但只有部分生效”时，应优先检查自己需要的是类别还是实例。

## 拖拽延迟重绘

第 15 课遇到一个典型事件驱动 UI 问题：

```text
BeginDrag
  -> grid.Remove(item)
  -> OnChanged
  -> Redraw()
  -> 但 isDragging == true，不能全量重绘，否则 ghost 会被销毁
```

修复是设置延迟重绘标记：

```csharp
private void Redraw()
{
    if (isDragging)
    {
        needsRedrawAfterDrag = true;
        return;
    }

    needsRedrawAfterDrag = false;
    // 执行全量重绘
}
```

拖拽结束后，在清理 `dragItem` 和 `ghost` 之后补画：

```csharp
dragItem = null;
ghost = null;

if (needsRedrawAfterDrag)
{
    Redraw();
}
```

补画主要服务不会自然触发 `Place()` 的结局，例如面板外丢弃、合并、满包兜底丢弃。正常放置仍交给 `InventoryGrid.Place()` 的 `OnChanged` 驱动，避免一件事被画两遍。

## 覆盖层自适应

第 14 课的接口点和第 15 课的激活角标都属于 `ItemView` 覆盖层。它们不能假设所有物品都是 1 x 1，也不能只依赖 Prefab 初始摆放。

```csharp
public void UpdateOverlayLayout(float step)
{
    float connectorSize = Mathf.Clamp(step * 0.16f, 10f, 14f);
    float activeMarkerSize = Mathf.Clamp(step * 0.28f, 18f, 24f);
    float inset = Mathf.Clamp(step * 0.1f, 6f, 8f);

    LayoutImage(topConnector, new Vector2(0.5f, 1), new Vector2(0, -inset), connectorSize);
    LayoutImage(rightConnector, new Vector2(1, 0.5f), new Vector2(-inset, 0), connectorSize);
    LayoutImage(bottomConnector, new Vector2(0.5f, 0), new Vector2(0, inset), connectorSize);
    LayoutImage(leftConnector, new Vector2(0, 0.5f), new Vector2(inset, 0), connectorSize);
    LayoutImage(activeWeaponUI, new Vector2(0, 1), new Vector2(inset, -inset), activeMarkerSize);
}
```

`Bind()` 和拖拽旋转后都要刷新覆盖层布局：

```text
Item 尺寸变化
  -> ItemView sizeDelta 更新
  -> UpdateOverlayLayout(step)
  -> 接口点和激活角标重新贴边
```

背包游戏里，物品尺寸就是玩法信息。覆盖层贴边、贴角、跟随旋转，不只是美术细节，也会影响玩家是否相信系统规则。

## 为什么暂不做冷却遮罩

激活角标是离散状态：这件物品是否正在驱动自动武器。冷却遮罩是连续状态：需要武器实体持续向背包 UI 回传进度。

冷却遮罩至少牵涉：

```text
Item 实例
  -> 对应 WeaponObject
  -> 武器冷却进度
  -> UI 订阅或轮询
  -> 拖拽、合并、丢弃时映射更新
```

第 15 课先完成“背包物品影响战斗实体”的核心表达；真实冷却遮罩后移，避免 Demo 冲刺期过早扩大战斗 UI 状态同步复杂度。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 丢掉激活武器后 UI 不立刻更新 | 拖拽期间 `Redraw` 被拦截，丢弃结局没有后续 `Place` 触发重绘 | 用 `needsRedrawAfterDrag` 延迟并补偿一次重绘 |
| 同类武器全亮 | 用 `ItemTag` 记录激活状态 | 用 `HashSet<Item>` 记录激活实例 |
| 多格武器重复挤占上限 | `GetUniqueItems` 没有按实例去重 | 用 `HashSet<Item>` 过滤同一实例的多个占格 |
| 测试值改掉玩法目标 | Inspector 中 `activeWeaponLimit` 临时调成 3 | 提交前回到课程目标 `1` |
| 武器映射变成 if-else | 逻辑里硬编码 Tag 与 GameObject | 用 `WeaponSlot` 配置表承载映射 |
| 覆盖层旋转后不贴边 | 接口点和角标只靠 Prefab 初始位置 | `Bind` 和旋转后按 `step` 重新布局 |
| 全量刷新误伤拖拽 ghost | `OnChanged` 立即销毁并重建 UI 子物体 | 拖拽期间挡住重绘，结束后补偿 |

## 如何验证

### 武器激活

- 背包为空时，所有场景武器实体关闭。
- 背包放入一把带 `ItemTag.Pistol` 的物品时，对应手枪自动武器实体开启。
- 移除、丢弃或合并导致武器物品离开背包时，对应实体关闭。
- 多把同类武器存在时，默认只激活左上优先的一把。
- 调整背包位置后，激活标记和场景武器实体随优先级变化。
- `activeWeaponLimit = 1` 与课程目标一致；后续第 21 课由 DualWield 突破默认上限。

### UI 与拖拽

- 当前激活的具体物品显示角标，同类未激活物品不显示角标。
- 面板外丢弃激活物品后，新顶上的武器若被激活，UI 角标立即更新。
- 合并、满包丢弃和正常放置后，UI 不漏重绘也不重复绘制。
- 物品旋转后，接口点和激活角标仍贴边、贴角。
- 1 x 1、2 x 1、1 x 2 等尺寸下覆盖层位置都合理。

### 工程边界

- `BackpackWeaponActivator` 订阅和退订 `InventoryGrid.OnChanged` 成对。
- `WeaponSlot` 缺少 `WeaponObject` 时安全跳过，并能给出足够上下文的调试信息。
- 场景中的 `WeaponObject` 初始激活状态不会和刷新逻辑冲突。
- 本环境没有完整 Unity 工程，因此仍需在 Unity Editor 中复核脚本、Prefab、`01-Run.unity`、`ItemView` 引用、字体资源、`.meta` / GUID 和 Play Mode 结果。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 15 课实现了背包武器激活、位置优先级、激活角标、拖拽延迟重绘和覆盖层自适应 | B | 来自用户放入 Inbox 的课程记录 |
| `GetUniqueItems` 的遍历顺序被定义为“左上优先”的玩法规则 | B | 原始记录明确描述了规则和设计理由 |
| 激活状态应记录具体 `Item` 实例而不是 `ItemTag` | B | 原始记录明确描述多把手枪时的标记差异 |
| 全关再开适合当前低频、小规模背包武器刷新 | C | 本环境基于当前系统规模和职责边界静态审阅 |
| 第 15 课已由当前环境在 Unity Editor / Play Mode 中运行通过 | D | 本次未收到完整 Unity 工程、场景、Prefab、字体资源或 `.meta`，未运行 Unity |
| 真实冷却遮罩已完成 | D | 原始记录明确将冷却遮罩后移，不纳入本课 Demo 主线 |

## 相关内容

- 前置：[合并升级与邻接联动](merge-upgrade-and-adjacency.md)
- 前置：[背包交互补丁](inventory-interaction-patches.md)
- 前置：[主动武器与 WeaponBase 提炼](active-weapons-and-weapon-base.md)
- 前置：[目标注册表、自动武器与投射物](target-registry-and-auto-weapon.md)
- 后续：[单局框架与基础 HUD](run-session-and-basic-hud.md)
- 后续：[构筑最小兑现](build-payoff-dual-wield.md)
- 后续：[武器稀有度与等级差异](weapon-rarity-and-level-scaling.md)
- 后续：[攻击芯片效果实装](attack-damage-chip-effect.md)
- C#：[值类型 vs 引用类型](../../csharp/oop/value-vs-reference.md)
- C#：[委托与事件](../../csharp/oop/delegates-and-events.md)
- UGUI：[UGUI 总览](../../unity/ugui/index.md)

> 📎 标签：`Unity` `背包系统` `自动武器` `UGUI` `事件驱动 UI` `实例身份` `项目实践`
