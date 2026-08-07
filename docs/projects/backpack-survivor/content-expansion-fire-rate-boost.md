# 内容面铺开

> 项目：[Backpack Survivor](index.md)
>
> 状态：项目中使用
>
> 验证状态：待验证。用户课程记录描述已实现 `LootEntry` 源头数据扩展、长期物品池、三类自动武器、`FireRateBoost` 战斗收益和 TMP 中文字体修复；本环境完成静态审阅、项目文件只读复核与文档验证，未运行 Unity Editor / Play Mode。
>
> 日期：2026-08-01
>
> 阶段：V0.2 掉落与背包构筑 · 第 22 课

## 学习目标

- 把 `LootEntry` 从“掉落概率条目”升级成背包物品的源头数据。
- 让拾取入包与丢弃回世界保留同一份物品身份、标签、价值和效果数值。
- 用普通、优秀、稀有、史诗、传说表撑起 Demo 的长期物品池。
- 在 `DualWield` 之外接入第一条可堆叠邻接收益：`FireRateBoost`。
- 把背包里的运行时 `Item` 实例映射到场景里的 `AutoWeapon`，让邻接效果作用到具体武器。
- 用项目内 TMP 字体资产链解决中文显示方块，而不是只在单个 Text 上临时换字体。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `LootEntry` | 新增 `itemTag`、`connectableSides`、`scoreValue`、`effectValue`，成为装备物品定义的入口 |
| `Item` | 保存 `ScoreValue` 与 `EffectValue`，让价值和战斗效果跟随运行时物品实例 |
| `InventorySystem` | `CreateItemFromLootEntry()` 入包、`DiscardToWorld()` 出包，两条链路都保留新增字段 |
| 掉落表资产 | 承载 Demo 长期物品池，覆盖多稀有度、多武器、多芯片和收集品 |
| `AdjacencyRuleBook` | 在 `DualWield` 之外新增步枪/霰弹枪向下连接弹匣的 `FireRateBoost` 规则 |
| `AdjacencyEffectResolver` | 继续让 `DualWield` 同效果互斥，同时让 `FireRateBoost` 可堆叠进入有效效果 |
| `BackpackWeaponActivator` | 维护 `Item -> AutoWeapon` 映射，基础激活、双持追加和攻速加成都读取同一批有效效果 |
| `AutoWeapon` | 消费背包攻速倍率，与本局升级倍率共同影响最终开火间隔 |
| TMP 字体资产 | 使用项目内 `SourceHanSansCN-Normal SDF` 作为默认字体和 fallback，修复中文方块 |

第 21 课让“手枪 + 手枪左右相邻”第一次兑现成真实战斗收益。第 22 课解决的是展示面和扩展面：玩家不只看到一个双持技巧，还能捡到不同稀有度、不同武器和不同芯片，并通过背包摆放直接看到射速收益。

```text
手枪 + 手枪左右相邻 = DualWield，突破默认武器上限
步枪/霰弹枪 + 弹匣上下相邻 = FireRateBoost，提高已激活武器射速
```

## LootEntry 源头数据

第 22 课把物品定义从运行时代码分支上移到掉落表配置。`LootEntry` 不再只回答“掉什么、权重多少、几格大小”，还回答“这是什么类型、能朝哪里连接、值多少钱、效果强度是多少”：

```csharp
[Serializable] public class LootEntry
{
    public DropCategory category = DropCategory.Equipment;
    public string id;
    public GameObject dropPrefab;
    public Rarity rarity;
    public int weight;
    public int amount = 1;
    public int width = 1;
    public int height = 1;

    public ItemTag itemTag = ItemTag.None;
    public ConnectableSides connectableSides = ConnectableSides.None;
    public int scoreValue;
    public float effectValue;
}
```

这一步的关键不是字段数量，而是事实源位置。以前如果按 `id` 在运行时写映射：

```text
id == "制式手枪" -> Pistol
id == "标准弹匣" -> Magazine
```

新增装备时就要同时修改掉落、背包、邻接、评分和战斗消费代码，漏一处就会出现“同一个物品在不同系统里身份不同”的问题。现在配置资产给出答案，运行时代码只负责搬运和消费。

## 入包与出包保真

入包时，`InventorySystem.CreateItemFromLootEntry()` 从 `LootEntry` 创建完整 `Item`：

```csharp
private Item CreateItemFromLootEntry(LootEntry entry)
{
    if (entry == null) return null;

    return new Item(
        entry.id,
        entry.rarity,
        entry.width,
        entry.height,
        entry.itemTag,
        entry.connectableSides,
        entry.scoreValue,
        entry.effectValue);
}
```

出包时，`DiscardToWorld()` 再把 `Item` 还原成 `LootEntry`：

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
    scoreValue = item.ScoreValue,
    effectValue = item.EffectValue,
};
```

这条往返链路是本课最值得保留的工程习惯：字段升级不是只补“创建入口”，还要检查反向链路。否则玩家把物品捡进背包时有标签和数值，拖出背包再捡回来就可能丢掉 `Tag`、接口方向、价值或芯片强度。

## 长期物品池

第 22 课同步整理了 Demo 期长期物品池：

| 稀有度 | 主要职责 | 示例方向 |
|---|---|---|
| 普通 | 让玩家频繁看到基础装备和可摆放素材 | 收集品、标准弹匣、制式手枪、急救绷带 |
| 优秀 / 稀有 | 拉开早期体验差异 | 改装手枪、突击步枪、霰弹枪、扩容弹匣、高速供弹模块 |
| 史诗 / 传说 | 支撑宝箱期待和结算价值 | 高价值收集品、强力模块、稀有武器 |

本环境只读抽样看到 `CommonEquipDrops`、`UncommonEquipDrops`、`RareEquipDrops`、`EpicEquipDrops`、`LegendaryBonusDrops` 中已经出现 `itemTag`、`connectableSides`、`scoreValue` 与部分 `effectValue` 字段。这个结论属于静态资产复核，不能替代 Unity 中的真实掉落、拾取和宝箱节奏验证。

普通怪掉落目前仍可能带有测试倾向。第 23 课已经把这个方向落到普通/精英掉落职责拆分、宝箱品质曲线和终局压力强化中：普通怪回到经验为主，精英和宝箱承担高价值装备入口。第 25 课继续把这里的 `scoreValue` 投影到 ItemView、背包总价值和结算快照。

## FireRateBoost 规则

`FireRateBoost` 继续沿用第 14 课的“正确物品 + 正确方向 + 规则匹配”思路，没有写成所有武器都吃所有芯片：

```csharp
new AdjacencyRule(
    ItemTag.Rifle,
    ConnectableSides.Down,
    ItemTag.Magazine,
    ConnectableSides.Up,
    AdjacencyEffectId.FireRateBoost),

new AdjacencyRule(
    ItemTag.Shotgun,
    ConnectableSides.Down,
    ItemTag.Magazine,
    ConnectableSides.Up,
    AdjacencyEffectId.FireRateBoost)
```

`DualWield` 改变的是武器数量上限，需要同效果互斥，防止三把手枪横排变成三持。`FireRateBoost` 改变的是某把武器的数值，可以允许多个弹匣叠到同一把武器上，真正需要处理的是聚合、封顶和反馈清晰。

因此 resolver 分成两类策略：

```csharp
public static List<AdjacencyEffect> ResolveValidEffects(List<AdjacencyEffect> candidateEffects)
{
    List<AdjacencyEffect> validEffects = new List<AdjacencyEffect>();

    if (candidateEffects == null) return validEffects;

    AddValidDualWieldEffects(candidateEffects, validEffects);
    AddValidFireRateBoostEffects(candidateEffects, validEffects);

    return validEffects;
}
```

这也是第 21 课留出的正确扩展点：不要把“一个 `Item` 参与过任何效果就不能再参与”写成全局规则。不同效果类型应该有自己的互斥、堆叠、层数和上限策略。

## 武器映射与倍率消费

第 15 课只需要知道哪些背包物品已经激活，`HashSet<Item>` 足够。第 22 课要把芯片效果应用到具体自动武器对象，所以多了一张映射表：

```csharp
private readonly Dictionary<Item, AutoWeapon> activeWeaponsByItem =
    new Dictionary<Item, AutoWeapon>();
```

激活物品时，`TryActivateItem()` 找到匹配标签且未激活的 `WeaponSlot`，再记录背包 `Item` 到场景 `AutoWeapon` 的关系。后续 `FireRateBoost` 只对已经激活的武器生效：

```csharp
float fireRateMultiplier = 1f + effectValues;
fireRateMultiplier = Mathf.Min(fireRateMultiplier, 1.75f);
autoWeapon.SetBackpackFireRateMultiplier(fireRateMultiplier);
```

`AutoWeapon` 最终把本局升级倍率和背包邻接倍率合并到攻击间隔：

```csharp
float finalAttackInterval =
    attackInterval / (stats.FireRateMultiplier * backpackFireRateMultiplier);
```

这保持了两个来源的边界：

```text
PlayerRunStats.FireRateMultiplier = 升级系统给的本局成长
backpackFireRateMultiplier = 背包邻接给的构筑收益
```

封顶 `1.75x` 是 Demo 体验护栏。允许玩家明显变强，但不让一两个高值芯片把射速推到视觉不可读或平衡失控。第 27 课根据合并升级后的实测风险继续回调：弹夹基础值收为 10% / 15% / 20%，等级倍率改为 1.0x / 1.5x / 2.0x，最终背包攻速上限调整到 2.0x。

第 29 课继续把“类型”和“强度”拆开：芯片仍通过 `EffectValue` 表达可堆叠效果，武器稀有度 / 等级则通过 `WeaponItemStatResolver` 翻译成独立伤害倍率，避免把武器品质也塞进芯片字段，详见[武器稀有度与等级差异](weapon-rarity-and-level-scaling.md)。

## 三类自动武器

场景 `BackpackWeaponActivator.weaponSlots` 在静态 YAML 中可见当前顺序为：

```text
Pistol / Rifle / Shotgun / Pistol
```

第一个 `Pistol` 服务基础体验，第二个 `Pistol` 继续给 `DualWield` 留出额外激活槽；`Rifle` 和 `Shotgun` 则用于展示 `FireRateBoost` 的三类基础武器体验。

这里不建议让 prefab 自己用 `GameObject.Find()` 找场景武器。预制体资产不应稳定依赖场景对象名字；场景对象关系由场景级管理器显式接线，依赖方向更清楚，复制场景或改名时也更容易排查。

## TMP 中文字体链

中文显示方块通常不是 Text 内容错，而是 TMP 字体资产缺字、材质引用残留或 fallback 没接好。第 22 课采用的是“修事实源”的路径：

```text
旧字体资产缺字 / 旧材质引用残留
  -> 替换为 SourceHanSansCN-Normal SDF
  -> 场景与 prefab 字体引用统一切换
  -> TMP Settings 默认字体 + fallback 更新
  -> Dynamic + Multi Atlas 允许运行时补字
```

本环境只读复核到：

- `SourceHanSansCN-Normal.ttf` 与 `SourceHanSansCN-Normal SDF.asset` 及 `.meta` 存在。
- `SourceHanSansCN-Normal SDF.asset` 引用源字体 GUID，`m_AtlasPopulationMode: 1`，`m_ClearDynamicDataOnBuild: 0`。
- `TMP Settings.asset` 默认字体与 fallback 指向同一个新 SDF GUID，并关闭 Build 时清空动态数据。
- `DamageNumber.prefab`、`ItemView.prefab` 和 `01-Run.unity` 中可见 TMP 字体/材质引用指向新 SDF GUID。

这些都属于静态资产链证据。是否所有中文都已覆盖、Build 后是否仍不丢字，还需要在 Unity Editor / Player Build 中实际观察。

## 周期链路

### 掉落入包

```text
LootTableData.LootEntry
  -> LootRoller 掷骰选中条目
  -> LootManager.SpawnEntry()
  -> DropItem.Initialize(entry)
  -> 玩家按 E 拾取
  -> DropItem.OnCollected(entry)
  -> InventorySystem.CreateItemFromLootEntry(entry)
  -> InventoryGrid.Place()
  -> Grid.OnChanged
  -> InventoryUIController.Redraw()
  -> BackpackWeaponActivator.RefreshActiveWeapons()
```

### 丢弃回世界

```text
玩家拖出背包
  -> InventoryUIController.EndDrag()
  -> InventorySystem.DiscardToWorld(item)
  -> Item 还原 LootEntry
  -> LootManager.SpawnEntry(entry)
  -> DropItem.PlayScatterFlight()
  -> 地面装备可再次 E 键拾取
```

### FireRateBoost 战斗收益

```text
背包布局变化
  -> InventoryGrid.ScanAdjacency(AdjacencyRuleBook.Rules)
  -> AdjacencyEffectResolver.ResolveValidEffects()
  -> 筛出 FireRateBoost
  -> BackpackWeaponActivator 找到已激活 Item 对应的 AutoWeapon
  -> 读取相邻芯片 Item.EffectValue
  -> 同一武器效果值累加并封顶
  -> AutoWeapon.SetBackpackFireRateMultiplier()
  -> finalAttackInterval 变短，射速提高
```

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| 新字段只补入包，不补丢弃 | 数据往返只检查一个方向 | 字段升级时同时检查 `LootEntry -> Item` 与 `Item -> LootEntry` |
| 用 `ItemTag` 表达强度 | Tag 只能分类，不能表达数值差异 | `ItemTag.Magazine` 表示类型，`EffectValue` 表示强度 |
| 所有效果共享同一套互斥 | 把 `DualWield` 的互斥规则扩散成全局规则 | 按 `EffectId` 分支处理互斥、堆叠和封顶 |
| 未激活武器也吃芯片收益 | 只看邻接候选，不看战斗实体是否激活 | 只通过 `activeWeaponsByItem` 给已激活 `AutoWeapon` 应用倍率 |
| 可堆叠数值没有上限 | 只做加法，不考虑 Demo 可读性 | 聚合后封顶，例如当前 `1.75x` |
| 中文方块只改单个 Text | 没修 TMP 默认字体、fallback 和材质引用 | 统一项目字体资产、SDF、TMP Settings 和 prefab/scene 引用 |
| 把测试掉落当正式经济 | 为了调试提高普通怪高品质掉落 | 在报告中标明测试配置，后续把高价值入口交给精英和宝箱 |

## 如何验证

### 数据保真

- 拾取不同 `LootEntry` 后，`Item.Id`、`Rarity`、`Tag`、`LocalConnectableSides`、`ScoreValue`、`EffectValue` 与原条目一致。
- 拖出背包生成世界掉落物后，再拾取回来，标签、方向、价值和效果数值不丢失。
- 旋转、拖拽、背包满自动丢出和手动丢弃都走同一份出包链路。

### 物品池

- 普通、优秀、稀有、史诗、传说掉落表都能在 Inspector 中看到新增字段。
- 宝箱束表引用的子表存在，且不会把高价值装备只塞进普通怪测试掉落。
- 不同稀有度装备在 UI 中能展示尺寸、名称、稀有度与价值差异。

### FireRateBoost

- 步枪向下连接弹匣时，`ScanAdjacency()` 产生 `FireRateBoost` 候选。
- 霰弹枪向下连接弹匣时，同样产生 `FireRateBoost` 候选。
- `ResolveValidEffects()` 保留可堆叠 `FireRateBoost`，但仍对 `DualWield` 做同效果互斥。
- 同一把已激活武器连接多个弹匣时，效果值累加并封顶到 `1.75x`。
- 未激活武器连接弹匣时，不应产生玩家看不见的实际射速收益。
- 刷新背包布局后，旧的背包攻速倍率会重置为 `1f`，不会残留到下一套摆法。

### 字体链

- 场景 HUD、伤害数字和背包 ItemView 中文不显示方块。
- `TMP Settings.asset` 默认字体和 fallback 指向项目内中文 SDF。
- 新 SDF 的动态补字和 Build 清空动态数据设置符合预期。
- Player Build 中重复检查中文显示，不能只依赖 Editor 视图。

### 工程边界

- `BS.Inventory.asmdef` 仍保持纯 C# 数据层边界，邻接规则和 resolver 不依赖 UnityEngine。
- 不在运行时代码里按物品 `id` 继续堆标签、价值和效果强度映射。
- `BackpackWeaponActivator.weaponSlots` 中至少有 `Pistol / Rifle / Shotgun / Pistol` 对应的场景对象。
- 当前仍需在 Unity 中复核 Inspector 槽位、Prefab、字体覆盖、Play Mode 射速变化、真实掉落和 Build Settings 场景路径。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 22 课实现了内容面扩展、物品源头字段、三类自动武器、`FireRateBoost` 和 TMP 字体修复 | B | 来自用户放入 Inbox 的课程记录 |
| `LootEntry` 已新增 `itemTag`、`connectableSides`、`scoreValue`、`effectValue` | C | 本环境只读查看外部 Unity 工程 `LootTableData.cs` |
| `Item` 已保存 `ScoreValue` 与 `EffectValue`，`InventorySystem` 入包与丢弃回世界都传递这些字段 | C | 本环境只读查看 `Item.cs` 与 `InventorySystem.cs` |
| `AdjacencyRuleBook` 包含 Pistol 双持规则以及 Rifle/Shotgun 向下连接 Magazine 的 `FireRateBoost` 规则 | C | 本环境只读查看 `AdjacencyRuleBook.cs` |
| `AdjacencyEffectResolver` 对 `DualWield` 做同效果互斥，并让 `FireRateBoost` 直接进入有效效果列表 | C | 本环境只读查看 `AdjacencyEffectResolver.cs` |
| `BackpackWeaponActivator` 维护 `Dictionary<Item, AutoWeapon>`，刷新时重置倍率、基础激活后再处理双持和攻速加成 | C | 本环境只读查看 `BackpackWeaponActivator.cs` |
| `AutoWeapon` 使用 `stats.FireRateMultiplier * backpackFireRateMultiplier` 计算最终攻击间隔 | C | 本环境只读查看 `AutoWeapon.cs` |
| `01-Run.unity` 中 `activeWeaponLimit` 为 `1`，`weaponSlots` 可见 `Pistol / Rifle / Shotgun / Pistol` | C | 本环境只读检查场景 YAML |
| 掉落表资产已出现多稀有度装备、`scoreValue` 与部分 `effectValue` 配置 | C | 本环境只读抽样检查 EquipDrops 与 ChestDropLoot 资产 |
| `SourceHanSansCN-Normal` 字体、SDF、TMP Settings、DamageNumber、ItemView 和场景引用静态可见 | C | 本环境只读检查字体 `.meta`、SDF、TMP Settings、Prefab 与场景 YAML |
| 本环境已经在 Unity Editor / Play Mode 中验证掉落、FireRateBoost 射速变化、TMP 中文和 Player Build | D | 未启动 Unity，未运行 Play Mode、Profiler 或 Player Build |
| `EditorBuildSettings.asset` 的场景路径已经修正为当前检查的 `01-Run.unity` | D | 静态检查仍看到 Build Settings 指向 `Assets/BackpackSurvivor/Scenes/Run/Run1.unity` |

## 相关内容

- 前置：[构筑最小兑现](build-payoff-dual-wield.md)
- 前置：[合并升级与邻接联动](merge-upgrade-and-adjacency.md)
- 前置：[背包武器激活](backpack-weapon-activation.md)
- 前置：[掉落分层与交互拾取](loot-layering-and-interaction.md)
- 前置：[胜负结算与重开闭环](run-result-and-restart-loop.md)
- 后续：[精英宝箱与终局压力强化](elite-chests-endgame-pressure.md)
- 后续：[背包价值与物品价值显示](backpack-value-and-item-value-display.md)
- 后续：[合并升级收益兑现](merge-upgrade-reward-payoff.md)
- 后续：[数值调参台与首轮平衡](balance-tuning-and-first-playtest.md)
- 后续：[武器稀有度与等级差异](weapon-rarity-and-level-scaling.md)
- 后续：[攻击芯片效果实装](attack-damage-chip-effect.md)
- C#：[值类型 vs 引用类型](../../csharp/oop/value-vs-reference.md)
- UGUI：[Text (TextMeshPro)](../../unity/ugui/controls/text-tmp.md)
- 检查清单：[Unity 项目能力](../../checklists/unity-project.md)

> 📎 标签：`Unity` `背包构筑` `LootEntry` `FireRateBoost` `自动武器` `TextMeshPro` `项目实践`
