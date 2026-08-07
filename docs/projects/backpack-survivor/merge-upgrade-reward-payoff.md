# 合并升级收益兑现

> 项目：[Backpack Survivor](index.md)
>
> 状态：项目中使用
>
> 验证状态：待验证。用户课程记录描述已实现合并升级后的价值 / 效果收益、FireRateBoost 升级收益、物品 Tooltip 和伤害数字显示修正；本环境完成静态审阅、项目文件只读复核与文档验证，未运行 Unity Editor / Play Mode。
>
> 日期：2026-08-03
>
> 阶段：V0.2 掉落与背包构筑 · 第 26 课

## 学习目标

- 把第 14 课的合并升级从“等级显示”推进成真实价值和战斗收益。
- 区分配置基础值与运行时当前值，避免升级收益污染静态掉落配置。
- 让 `ScoreValue / EffectValue` 由 `BaseValue * Level` 推导，消费侧继续读取同一属性。
- 让 `FireRateBoost` 自动吃到升级后的 `EffectValue`，并把攻速上限变成 Inspector 可调字段。
- 把格子内的详细价值 / 效果信息迁移到 Tooltip，让背包格子只保留快速识别信息。
- 修正伤害数字向上取整造成的反馈误导，并把最终数值显示方案留给后续平衡课统一决定。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `Item.baseScoreValue / baseEffectValue` | 保存 Lv.1 配置基础值，不随运行时等级改变 |
| `Item.ScoreValue / EffectValue` | 运行时当前收益，按基础值乘 `Level` 推导 |
| `InventoryGrid.TryMerge()` | 仍只负责合并规则：目标升级、来源移除 |
| `InventorySystem.DiscardToWorld()` | 丢弃时把基础值写回 `LootEntry`，避免运行时值污染配置 |
| `BackpackWeaponActivator.ActivateFireRateBoost()` | 读取邻接物品当前 `EffectValue`，让升级后的芯片影响攻速 |
| `maxBackpackFireRateMultiplier` | 背包攻速倍率上限，从硬编码改为序列化调参字段 |
| `ItemTooltipView` | 悬停显示当前等级、稀有度、尺寸、价值和效果 |
| `InventoryUIController` | 统一转发 Tooltip 显示 / 移动 / 隐藏，并在拖拽时隐藏 Tooltip |
| `ItemView` | 只保留物品名和等级，继续作为输入事件与轻量表现层 |
| `DamageNumberView` | 不再用 `CeilToInt` 向上夸大战斗伤害显示 |

第 25 课让背包价值进入 UI 和结算页，但当时 `ScoreValue / EffectValue` 仍可以被理解为“初始值”。第 26 课补上关键语义：物品等级会影响当前价值和效果，所以 Lv.2 / Lv.3 不只是标签，而是会被总价值、结算页、Tooltip 和战斗系统共同消费的运行时事实。

```text
LootEntry：Lv.1 基础配置
Item：基础值 + 等级 -> 当前值
InventoryGrid：合并只改变等级
UI / 结算 / 战斗：继续读取 Item 的当前属性
```

## 基础值与当前值

`Item` 新增基础值字段：

```csharp
private readonly int baseScoreValue;
private readonly float baseEffectValue;

public int ScoreValue => baseScoreValue * Level;
public float EffectValue => baseEffectValue * Level;
public int BaseScoreValue => baseScoreValue;
public float BaseEffectValue => baseEffectValue;
```

这里的核心不是公式多复杂，而是语义拆开：

| 概念 | 含义 |
|---|---|
| `BaseScoreValue / BaseEffectValue` | 掉落表给出的 Lv.1 基础值 |
| `Level` | 运行时合并升级状态 |
| `ScoreValue / EffectValue` | 运行时当前收益 |

这样后续即使从线性成长改成成长表，消费侧也不用改。UI、结算页、邻接效果都继续读取 `ScoreValue / EffectValue`，收益公式仍集中在 `Item` 里。

## 合并升级自然兑现

`InventoryGrid.TryMerge()` 没有扩张职责：

```csharp
public bool TryMerge(Item source, Item target)
{
    if (!CanMerge(source, target)) return false;
    target.IncreaseLevel();
    Remove(source);
    return true;
}
```

第 29 课补上了这里的事件语义债务：如果拖拽开始时 `source` 已经离开网格，`Remove(source)` 不会再触发 `OnChanged`，但 `target.Level` 已改变并会影响价值、Tooltip、芯片效果和武器倍率，因此合并成功后需要补发语义性刷新，详见[武器稀有度与等级差异](weapon-rarity-and-level-scaling.md)。

合并只处理“谁留下、谁消耗、等级是否提升”。它不直接写价值，也不直接写效果。等级变化后：

```text
target.Level + 1
  -> target.ScoreValue 变大
  -> target.EffectValue 变大
  -> 背包总价值、结算快照、Tooltip、FireRateBoost 消费侧自然读到新值
```

这避免了“升级时同步一堆字段”的脆弱结构。只要所有消费侧都读 `Item` 当前属性，就不会出现 UI 是 Lv.2、结算还是 Lv.1、战斗又是另一套数值的分裂。

## 丢弃路径写回基础值

第 25 课的丢弃路径把 `Item.ScoreValue` 写回 `LootEntry.scoreValue`。第 26 课语义改变后，这条路径必须修正：

```csharp
LootEntry entry = new LootEntry
{
    category = DropCategory.Equipment,
    id = item.Id,
    rarity = item.Rarity,
    width = item.Width,
    height = item.Height,
    amount = 1,
    itemTag = item.Tag,
    connectableSides = item.LocalConnectableSides,
    scoreValue = item.BaseScoreValue,
    effectValue = item.BaseEffectValue,
};
```

如果把 Lv.2 的 `ScoreValue / EffectValue` 写回静态掉落字段，玩家把物品丢出去再捡回来，会得到一个“Lv.1 外壳 + Lv.2 基础值”的污染物品。下一次再升级时，收益会越滚越离谱。

当前 Demo 的取舍是：

```text
丢弃升级物品会损失等级
但不会污染 Lv.1 基础配置
```

这不是最终物品保真方案。正式版本可以新增 `DropRuntimeData` 或让地面掉落承载 `level`、旋转、基础值等运行时信息，再解决完整往返保真。

## FireRateBoost 读取当前效果

第 22 课接入 `FireRateBoost` 时，弹夹的 `EffectValue` 是配置值。第 26 课之后，`EffectValue` 已经是当前值：

```csharp
float effectValue = effect.ItemB.EffectValue;
```

所以 Lv.2 弹夹会自然给出更高攻速加成，`BackpackWeaponActivator` 不需要知道“这是不是升级物品”。

攻速上限也从硬编码改为序列化字段：

```csharp
[SerializeField] private float maxBackpackFireRateMultiplier = 2.5f;

float fireRateMultiplier = 1f + effectValues;
fireRateMultiplier = Mathf.Min(fireRateMultiplier, maxBackpackFireRateMultiplier);
autoWeapon.SetBackpackFireRateMultiplier(fireRateMultiplier);
```

这是为第 27 课平衡做准备。升级后的弹夹可能很快撞上攻速上限，如果上限藏在代码里，调手感会变成反复改代码；暴露到 Inspector 后，Demo 阶段可以先快速找范围。第 27 课已经在这里继续收口：弹夹基础值调整为 10% / 15% / 20%，`EffectValue` 改用 Lv.1 1.0x、Lv.2 1.5x、Lv.3 2.0x 的等级倍率表，攻速上限回调到 2.0x。

## Tooltip 信息分层

第 25 课把价值文字放进 `ItemView`。第 26 课进一步调整 UI 信息密度：

```text
ItemView：物品名 + Lv，服务扫视和拖拽
Tooltip：稀有度 / 尺寸 / 当前价值 / 当前效果，服务查看详情
TotalValueText：背包整体反馈
ResultView：终局总结
```

`ItemTooltipView` 展示的是当前值：

```csharp
titleText.text = $"{item.Id} (Lv.{item.Level})";

if (item.EffectValue > 0)
{
    int percent = Mathf.RoundToInt(item.EffectValue * 100f);
    bodyText.text = $"稀有度: {item.Rarity}\n" +
                    $"大小: {item.Width}x{item.Height}\n" +
                    $"价值: ￥{item.ScoreValue}\n" +
                    $"效果: +{percent}%";
}
```

`ItemView` 只把鼠标事件交给控制器：

```csharp
public void OnPointerEnter(PointerEventData eventData)
{
    controller.ShowTooltip(item, eventData.position);
}
```

`InventoryUIController` 负责统一显示、移动和隐藏：

```csharp
public void ShowTooltip(Item item, Vector2 screenPosition)
{
    if (isDragging) return;
    tooltipView?.Show(item, screenPosition);
}
```

拖拽时关闭 Tooltip 是正确的交互边界。拖拽过程中鼠标下已经有 ghost 和红绿预览，再弹详情面板会干扰放置判断。

## 伤害数字不向上承诺

课程记录中发现一个反馈问题：

```text
显示伤害：25
敌人血量：50
实际需要：3 枪
```

根因是显示层用了向上取整，而真实扣血仍是浮点伤害。第 26 课先把伤害数字改为不向上夸大：

```csharp
damageText.text = Mathf.FloorToInt(damage).ToString();
```

这不是最终格式方案。`FloorToInt(24.9)` 会显示 24，也可能低估玩家实际伤害。真正要在第 27 课统一决定的是：

```text
方案 A：伤害源头整数化，显示和扣血都用整数
方案 B：继续浮点伤害，UI 显示一位小数或按统一规则格式化
```

本课先保留最低要求：战斗 UI 不要向上承诺规则没有真正给出的伤害。第 27 课最终选择方案 A：在 `WeaponBase` 源头把伤害取整，子弹、扣血和伤害数字共用同一份整数伤害语义。

## 周期链路

### 合并升级收益

```text
拖拽物品 source 到同名同级 target 上
  -> InventoryUIController.EndDrag()
  -> grid.TryMerge(source, target)
  -> target.IncreaseLevel()
  -> Item.Level 提升
  -> ScoreValue = BaseScoreValue * Level
  -> EffectValue = BaseEffectValue * Level
```

### 背包价值与结算

```text
Item.Level
  -> Item.ScoreValue
  -> InventoryGrid.GetTotalScoreValue()
  -> InventoryUIController.RefreshTotalValue()
  -> GameSession.EndRun()
  -> RunResult.BackpackValue
  -> ResultView 显示终局背包价值
```

### 攻速芯片收益

```text
Magazine 合并升级
  -> Magazine.Level 提升
  -> Magazine.EffectValue 提升
  -> AdjacencyEffectResolver 产出 validEffects
  -> BackpackWeaponActivator.ActivateFireRateBoost()
  -> 激活武器读取邻接芯片当前 EffectValue
  -> AutoWeapon.SetBackpackFireRateMultiplier()
```

### Tooltip 展示

```text
鼠标进入 ItemView
  -> OnPointerEnter(eventData)
  -> InventoryUIController.ShowTooltip(item, position)
  -> ItemTooltipView.Show(item, position)
  -> 显示当前 Lv / 稀有度 / 尺寸 / 价值 / 效果
```

### 丢弃还原

```text
Lv.2 Item
  -> InventorySystem.DiscardToWorld(item)
  -> LootEntry.scoreValue = item.BaseScoreValue
  -> LootEntry.effectValue = item.BaseEffectValue
  -> DropItem 落地
  -> 再拾取 new Item(...)
  -> 回到 Lv.1 基础值
```

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| Lv.2 只改显示，不改收益 | 等级没有进入收益公式 | `ScoreValue / EffectValue` 由基础值和等级推导 |
| `TryMerge()` 到处同步数值 | 合并命令承担收益公式 | `TryMerge()` 只提升等级，收益集中在 `Item` |
| Lv.2 丢出再捡回变成伪 Lv.1 强物品 | 当前值写回 `LootEntry` 基础字段 | 丢弃写 `BaseScoreValue / BaseEffectValue` |
| 弹夹升级后战斗没变化 | 攻速消费侧读了基础值或旧缓存 | `ActivateFireRateBoost()` 读取当前 `EffectValue` |
| 升级收益被上限吃掉看不出来 | 攻速上限硬编码且过低 | 暴露 `maxBackpackFireRateMultiplier`，后续平衡课调参 |
| 背包格子文字太挤 | 格子内同时显示名称、等级、价值、效果 | 格子只保留扫视信息，详情进 Tooltip |
| Tooltip 干扰拖拽 | 拖拽时仍显示悬停面板 | `ShowTooltip()` 遇到 `isDragging` 直接返回，拖拽开始时隐藏 |
| 伤害数字 overpromise | UI 向上取整，真实扣血是浮点 | 暂时不向上夸大；第 27 课统一数值格式 |

## 如何验证

### 合并收益

- 两个同名同级物品合并后，目标等级 +1，来源被移除。
- Lv.2 物品的 `ScoreValue` 是 Lv.1 基础价值的 2 倍，Lv.3 是 3 倍。
- Lv.2 / Lv.3 弹夹的 `EffectValue` 随等级增长。
- 背包总价值、结算页 `BackpackValue` 和 Tooltip 都显示升级后的当前价值。

### 丢弃与回捡

- Lv.2 物品丢弃到世界时，生成的 `LootEntry.scoreValue / effectValue` 使用基础值。
- 当前 Demo 中，升级物品丢出再捡回应回到 Lv.1，不生成伪高基础值物品。
- 旋转后丢弃的尺寸、接口方向和再次拾取表现仍需在 Unity 中复核；当前静态代码可见丢弃写的是 `item.Width / item.Height` 与 `LocalConnectableSides`，这可能影响正式保真策略。

### FireRateBoost

- 弹夹升级后，与激活武器形成有效 `FireRateBoost` 时，攻速倍率读取升级后的 `EffectValue`。
- 多个弹夹叠加时，倍率不超过 `maxBackpackFireRateMultiplier`。
- 修改 Inspector 上限后，Play Mode 中攻速手感随上限变化。

### Tooltip 与 UI

- 鼠标悬停物品时显示 Tooltip，移出后隐藏。
- Tooltip 展示当前等级、稀有度、尺寸、价值和效果。
- 拖拽期间不显示 Tooltip，也不遮挡红绿预览和放置判断。
- `ItemView` 仍能正常拖拽、旋转、合并和显示接口 / 激活角标。

### 伤害显示

- 伤害数字不再向上显示超过真实浮点伤害的整数。
- 如果真实伤害不是整数，第 27 课需要决定源头整数化还是 UI 小数显示。
- 不把本课的 `FloorToInt` 当成最终伤害格式方案。

### 工程边界

- `InventoryGrid.TryMerge()` 不直接管理价值、效果或 UI 文案。
- `ItemTooltipView` 只显示传入 `Item` 的当前事实，不反查掉落表。
- `BackpackWeaponActivator` 不按等级写分支，只读取邻接物品当前 `EffectValue`。
- 本环境未运行 Unity Editor / Play Mode / Profiler / Player Build；真实 Tooltip 位置、射线、中文字体、攻速体感、伤害显示和性能仍需项目内验证。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 26 课实现了合并升级后的价值 / 效果收益、Tooltip 和伤害数字显示修正 | B | 来自用户放入 Inbox 的课程记录 |
| `Item` 已保存 `baseScoreValue / baseEffectValue`，`ScoreValue / EffectValue` 由基础值乘等级推导 | C | 本环境只读查看外部 Unity 工程 `Item.cs` |
| `InventoryGrid.TryMerge()` 仍只调用 `target.IncreaseLevel()` 并移除来源 | C | 本环境只读查看 `InventoryGrid.cs` |
| `InventorySystem.DiscardToWorld()` 已把 `BaseScoreValue / BaseEffectValue` 写回 `LootEntry` | C | 本环境只读查看 `InventorySystem.cs` |
| `BackpackWeaponActivator` 已使用序列化 `maxBackpackFireRateMultiplier`，并在 `ActivateFireRateBoost()` 中读取当前 `EffectValue` | C | 本环境只读查看脚本和 `01-Run.unity` YAML |
| `ItemTooltipView`、`InventoryUIController.tooltipView` 和 `ItemView` 鼠标事件桥接代码存在，场景中可见 Tooltip 引用 | C | 本环境只读查看表现层脚本、`.meta` 和场景 YAML |
| `DamageNumberView` 已改为 `Mathf.FloorToInt(damage)` 显示 | C | 本环境只读查看 `DamageNumberView.cs` |
| 合并升级收益、Tooltip、FireRateBoost 升级收益和伤害数字已在 Unity Play Mode 中确认 | D | 本环境未启动 Unity 或观察画面 |
| Tooltip 中文、射线、位置、Player Build 与 Profiler 数据已确认 | D | 未运行 Player Build 或 Profiler |

## 相关内容

- 前置：[合并升级与邻接联动](merge-upgrade-and-adjacency.md)
- 前置：[构筑最小兑现](build-payoff-dual-wield.md)
- 前置：[内容面铺开](content-expansion-fire-rate-boost.md)
- 前置：[背包价值与物品价值显示](backpack-value-and-item-value-display.md)
- 前置：[背包 UI 与拖拽](inventory-ui-and-drag.md)
- 系统：[战斗反馈快包](combat-feedback-pack.md)
- 后续：[数值调参台与首轮平衡](balance-tuning-and-first-playtest.md)
- 后续：[武器稀有度与等级差异](weapon-rarity-and-level-scaling.md)
- C#：[C# 工程实践路线](../../csharp/engineering/index.md)
- UGUI：[Text (TextMeshPro)](../../unity/ugui/controls/text-tmp.md)
- 检查清单：[Unity 项目能力](../../checklists/unity-project.md)

> 📎 标签：`Unity` `背包构筑` `合并升级` `FireRateBoost` `Tooltip` `伤害数字` `数值平衡` `项目实践`
