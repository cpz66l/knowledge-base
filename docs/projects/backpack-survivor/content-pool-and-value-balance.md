# 内容池扩展与价值平衡

> 项目：《背包幸存者》Backpack Survivor  
> 模块周期：V0.3.4  
> 学习状态：项目复盘已整理  
> 证据归属：用户 `inbox/V0.3.4内容池扩展与价值平衡复盘.md` 复盘记录；用户记录实机回归全绿，本环境未运行 Unity Editor / Play Mode / Player Build  
> 关键词：内容池扩展、掉落配置、背包价值、物品图标、武器激活上限、数值投放

## 学习目标

- 把 V0.3.1-V0.3.3 已搭好的升级、邻接和背包被动规则落到真实内容池。
- 区分 `scoreValue` 与 `effectValue`，让结算价值和战斗收益可以产生取舍。
- 建立物品图标、Tooltip、宝箱投放和武器槽位上限的一致验证清单。

## 当前实现

V0.3.4 的核心不是继续扩底层规则，而是把已有规则变成玩家实际能摸到、看懂、取舍的内容。

本次扩展覆盖：

- 普通、不凡、稀有、史诗、传说五档掉落池。
- 机械臂、磁吸核心、护甲、瞄准镜、高价值传说收集品等构筑物品。
- `scoreValue` 价值曲线和 `effectValue` 战斗收益的语义区分。
- 宝箱多频道束表的高品质掉落期待。
- `Item.Id` 优先、`ItemTag` 兜底的图标解析。
- 手枪、步枪、霰弹枪各自的同类武器实体槽位上限。

## 架构链路

### 掉落到背包价值

```text
LootTableData.LootEntry
  id / rarity / itemTag / scoreValue / effectValue / level
        ↓
InventorySystem.CreateItemFromLootEntry
        ↓
Item
        ↓
InventoryGrid.GetTotalScoreValue
        ↓
HUD / ResultView 背包价值
```

`scoreValue` 决定背包结算价值，`effectValue` 决定战斗或被动收益，`level` 同时影响显示和部分收益。这样战斗物品不必天然拥有最高分数，收集品也能承担更高价值密度。

### 宝箱投放

```text
ChestSpawner 根据波次权重选宝箱等级
        ↓
LootManager.RollBundle
        ↓
每个 DropChannel 独立按 probability 判定
        ↓
Roll 子掉落表
        ↓
生成装备 / 金币 / 其他掉落
```

高级宝箱使用“稳定奖励 + 附加期待”的方式提高内容密度，而不是只改一个颜色或只掉一件物品。

### 图标解析

```text
ItemView.SetItem
        ↓
ItemIconResolver.GetIcon(item)
        ↓
按 Item.Id 查专属图标
        ↓
按 ItemTag 查兜底图标
        ↓
无图标时显示文字
```

`ItemTag` 表达玩法类型，`Item.Id` 表达具体物品身份。传说收集品如果继续共用 `Collection` 图标，会削弱内容辨识度。

### 武器激活

```text
InventoryGrid.GetUniqueItems 位置优先
        ↓
基础激活位 + 升级加成 + 机械臂加成
        ↓
TryActivateItem 按 ItemTag 找空闲 WeaponSlot
        ↓
同类槽位数量决定该类武器最多同时出现几个实体
        ↓
DualWield 作为邻接奖励额外拉起相邻手枪
```

当前用 `weaponSlots` 中同 `ItemTag` 的槽位数量表达同类武器上限，适合 Demo 阶段，成本低、可视化强。后续如果需要动态调整某类武器上限，再抽 `WeaponTypeLimit` 或 `WeaponActivationPolicy`。

## 关键取舍

### 为什么先扩内容池

V0.3.1-V0.3.3 已经证明规则能扩展，但如果玩家实际游玩摸不到新物品，架构深度不会转化成体验深度。V0.3.4 的价值在于把规则变成可见内容：新图标、高价值物品、机械臂、磁吸核心、瞄准镜和宝箱投放节奏。

### 为什么分离分数价值和战斗价值

如果强战斗物品也总是最高分，玩家会无脑拿强装备。背包玩法更需要玩家在战斗力、结算价值、大格子核心和小格子收集品之间做取舍。

### 为什么机械臂语义要修正

旧配置用 `effectValue = 0.5`、`level = 3` 间接凑出 +1，能跑但难读。本次改成 `effectValue = 1`、`level = 1`，让 Tooltip、配置表和真实效果语义一致。

## 验证记录

用户复盘记录本模块实机回归全绿，覆盖：

- 新增掉落物正常生成、拾取、入包。
- 专属图标优先于 Tag 兜底图标。
- Tooltip 显示新增物品价值与收益。
- 背包价值显示与物品等级、`scoreValue` 一致。
- 机械臂显示 +1 激活武器上限，且真实生效。
- 磁吸核心、护甲、瞄准镜、芯片仍能正常生效。
- 普通 / 不凡 / 稀有 / 史诗 / 传说价值阶梯更清晰。
- 稀有、史诗、传说宝箱提供更高价值期待。
- 同类武器槽位限制生效，双持仍作为邻接奖励。
- 危险 `using` 扫描干净。

本环境只整理复盘和知识页，没有运行 Unity、Profiler 或 Player Build。

## 面试表达

可以这样讲：

```text
V0.3.4 我没有继续盲目加规则，而是先把升级、邻接和背包被动落到真实内容池。这里我把 scoreValue 和 effectValue 分开，让结算价值和战斗收益形成取舍；图标解析从 ItemTag 升级到 Item.Id 优先，让传说物和高价值物品有独立身份；武器上限先用场景 WeaponSlot 数量表达，等未来需要动态限制时再抽策略表。
```

## 风险与下一步

- `WeaponSlot` 数量限制不是完整武器类型上限系统，后续动态上限需要重新抽象。
- `PickUpMagnet` 继续保留背包被动重复汇总风险，见[性能优化记录](performance-optimization-log.md)。
- 内容池扩大后，需要继续用样本统计验证宝箱期望、构筑强度和终局掉落密度。
- 下一模块进入[基础音频系统与 BGM](audio-system-and-bgm.md)。

> 标签：`Backpack Survivor` `掉落系统` `数值平衡` `物品图标` `项目复盘`

