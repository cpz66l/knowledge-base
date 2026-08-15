# Backpack Survivor 面试复盘第 01 阶段

> 日期：2026-08-12  
> 范围：前 5 轮模拟问答  
> 主题：项目总览、背包分层、拾取入包链路、拖拽蒸发 Bug、`EndDrag` 兜底设计  
> 证据归属：用户放入 `inbox/BackpackSurvivor-面试复盘-第01阶段-2026-08-12.md` 的模拟面试复盘；本次整理未打开 Unity 工程或复跑项目

---

## 阶段结论

这轮复盘能证明用户确实做过 Backpack Survivor，尤其能回忆背包拖拽、旧格被抢占、物品蒸发和版本差异。但当前表达还偏“项目介绍”和“现象回忆”，需要继续训练成面试官容易判断的工程表达：类名准确、调用链准确、版本边界准确、验证方式准确。

最重要的训练方向：少说抽象词，多说事实源、投影层、适配器和事件流。比如背包系统不要只说“MVC”，而要说清楚 `InventoryGrid` 是事实源，`InventoryUIController` 是 UI 投影，`InventorySystem` 是外部适配器，战斗接入由 `BackpackWeaponActivator / Resolver` 完成。

## 5 轮表现摘要

| 轮次 | 主题 | 当前表现 | 主要改进点 |
|---|---|---|---|
| 1 | 1 分钟项目介绍 | 能说明项目类型和范围 | 补类名、链路、Demo 边界和验证方式 |
| 2 | 背包系统分层 | 抓住纯 C# 数据层和 UI 投影 | 避免硬套 MVC，改说 Model + UI 投影 + Gameplay Adapter |
| 3 | 地上装备入包链路 | 主线方向正确 | 顺序要从 `InteractDetector / IInteractable` 开始，先 `CanAccept` 后 `Collect` |
| 4 | BUG-001 物品蒸发 | 能说到核心根因 | 按“现象 -> 复现 -> 排查 -> 根因 -> 修复 -> 验证”展开 |
| 5 | `EndDrag` 兜底设计 | 能意识到版本差异 | 验证方式要从“试玩”升级为分支覆盖 |

## 必背表达卡

### 背包分层一句话

> 我这个背包不是严格教科书 MVC，更准确是纯数据 Model + UI 投影 + Gameplay Adapter。`InventoryGrid` 是事实源，UI 不复制规则；`InventorySystem` 负责外部掉落进出背包；战斗侧由 `BackpackWeaponActivator` 和 Resolver 读取背包结果影响武器。

### 拾取链路一句话

> 装备拾取采用请求-确认：`DropItem.Interact()` 先问 `InventorySystem.CanAccept(lootEntry)`，能放才 `Collect()` 回池并广播；不能放就返回 `false`，物品留在地上，避免吞物品。

准确链路应这样讲：

```text
玩家按 E
  -> InputReader.OnInteract
  -> InteractDetector 调用当前目标 IInteractable.Interact()
  -> DropItem.Interact()
  -> InventorySystem.CanAccept(lootEntry) 侦察式试放
  -> 能放：DropItem.Collect()
  -> DropItem.OnCollected 广播
  -> InventorySystem 根据 LootEntry 创建运行时 Item
  -> InventoryGrid.TryFindFreeArea()
  -> InventoryGrid.Place()
  -> InventoryGrid.OnChanged
  -> InventoryUIController.Redraw()
  -> 生成 ItemView
```

### BUG-001 一句话

> 这个 Bug 的根因不是 UI ghost，而是拖拽回滚依赖“旧格子仍为空”的脆弱假设；自动入包会破坏这个不变量，所以 `EndDrag` 必须设计多级归宿，保证物品要么在背包，要么在世界，要么继续手持，不能蒸发。

### 验证一句话

> 我会按每个分支构造场景验证，而不是只靠正常试玩；验证标准是物品在数据层、世界层和 UI 层的状态不能分叉。

## `EndDrag` 当前版本归宿优先级

当前 v0.2 可以这样表达：

```text
1. 面板外松手：直接 DiscardToWorld
2. 面板内目标格可放：Place(target)
3. 目标格不可放但可合并：TryMerge
4. 新位置失败：回滚 oldX / oldY
5. 旧位置也失败：TryFindFreeArea 任意空位
6. 背包完全无位置：DiscardToWorld
```

这条链路的面试价值在于：先尊重玩家目标放置意图，再尊重旧位置回滚体验，然后尽量保留在背包中，最后才退到世界掉落，保证物品不消失。

## 真实面试风险

| 风险 | 表现 | 修正方式 |
|---|---|---|
| 抽象词偏多 | “MVC 分层思想”“作战体系”后面没有类名 | 抽象词后立刻接类名、职责和数据流 |
| 版本边界混乱 | 早期手持兜底和 v0.2 世界丢弃混在一起 | 主动说“当时版本”和“当前 v0.2” |
| 验证表达偏弱 | “我再玩一遍观察”偏玩家测试 | 改成构造场景、分支覆盖、检查事实源 |
| 事件语义不准 | 把 `OnChanged` 说成直接传 item 给 UI | 改成“通知数据变了，UI 重新读取 Grid 并重绘” |

## 下一轮训练重点

后续模拟面试优先从对象池开始，因为它能串起多个真实 Bug，也是 Unity 客户端实习高频追问点：

1. `ObjectPool / IPoolable` 生命周期与池化状态复位。
2. `TargetRegistry` 自动索敌为什么不用每帧 `Find`。
3. `AdjacencyRuleBook / AdjacencyEffectResolver` 为什么拆成规则发现和有效效果裁决。
4. `WaveDirector` 为什么是导演，`EnemySpawner` 为什么只是执行器。
5. Profiler 快扫中如何区分 `EditorLoop`、资源上传和真实 `PlayerLoop` 热点。

## 证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 用户完成了 Backpack Survivor 前 5 轮模拟面试复盘 | B | 来自用户放入 Inbox 的复盘文档 |
| 用户能回忆背包拖拽、请求-确认、BUG-001 和 `EndDrag` 版本差异 | B | 复盘文档记录了原回答、问题和推荐表达 |
| 本页整理的“必背表达卡”可用于下一轮面试训练 | C | 当前模型基于用户复盘提炼，未重新模拟面试 |
| 当前模型已在 Unity 中验证 `EndDrag` 所有分支 | D | 本次未打开 Unity、未运行 Play Mode、未构造分支测试 |

## 相关内容

- 项目：[Backpack Survivor 项目总览](../../projects/backpack-survivor/index.md)
- 背包：[背包 UI 与拖拽](../../projects/backpack-survivor/inventory-ui-and-drag.md)
- 补丁：[背包交互补丁](../../projects/backpack-survivor/inventory-interaction-patches.md)
- Bug：[Bug 记录簿](../../projects/backpack-survivor/bug-log.md)
- 面试：[面试与表达检查清单](../../checklists/interview.md)

> 标签：`Backpack Survivor` `面试复盘` `项目表达` `背包系统` `Bug 复盘`
