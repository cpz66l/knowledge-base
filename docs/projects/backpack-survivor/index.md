# Backpack Survivor（背包幸存者）

> 状态：V0.2 掉落分层与交互拾取已记录，继续推进容器搜刮
>
> 首次记录：2026-07-20
>
> Unity 版本：Unity6.3

## 项目目标

通过一个可持续扩展的幸存者类项目，把 C#、Unity 组件设计、战斗系统、UI、数据配置和工程验证串成完整实践，而不是只保留互相孤立的知识文章。

## 已完成里程碑

V0.1 已建立战斗核心原型：

- 统一可受伤对象契约。
- 建立通用生命值组件。
- 用危险区、敌人近战和投射物复用同一条伤害管线。
- 完成敌人追击、自动索敌、枪口转向、主动/自动双武器和投射物命中闭环。
- 用刷怪器形成持续战斗，并让敌人和投射物进入对象池复用周期。
- 通过第 5 课修复 `Start` 订阅在对象复用后丢失、生命值未重置等生命周期问题。

V0.2 已开始扩展掉落与背包构筑：

- 用 `LootTableData` 建立掉落表配置。
- 用 `LootRoller` 记录权重随机和保底计数。
- 用 `LootManager` 将敌人死亡、对象池取出和掉落物表现串成一条链路。
- 用 `PickUpMagnet` 和 `DropItem.OnCollected` 将掉落物推进到拾取与临时收货口。
- 用 `BS.Inventory` 纯 C# 程序集和 `InventoryGrid` 建立背包占格数据内核。
- 用 `InventorySystem` 与 UGUI 将拾取自动入包、网格显示、拖拽预览和非法回滚串成闭环。
- 用两级掉落表、`ICollectable`、`IInteractable` 和局部物理查询区分货币自动拾取与装备手动拾取。

## 实践记录

| 课次 | 内容 | 状态 |
|---|---|---|
| 第 1 课 | [伤害管线与危险区](damage-pipeline-and-hazard-zone.md) | 已实现，待补充 Unity 版本与更完整边界测试 |
| 第 2 课 | [敌人追击、近战与死亡流程](enemy-ai-and-melee.md) | 已应用；Kimi 外部检查代码与 Unity 场景 |
| 第 3 课 | [目标注册表、自动武器与投射物](target-registry-and-auto-weapon.md) | 已应用；池化边界在第 5 课继续修复 |
| 第 4 课 | [主动武器与 WeaponBase 提炼](active-weapons-and-weapon-base.md) | 已应用；主动/自动武器共用投射物管线 |
| 第 5 课 | [刷怪器与对象池](spawner-and-object-pooling.md) | 已应用；敌人与投射物完成池化复用 |
| 第 7 课 | [掉落系统与保底机制](loot-drop-and-pity.md) | 已记录；静态检查发现零权重表空引用边界待修正 |
| 第 8 课 | [拾取与磁吸](pickup-and-magnet.md) | 已记录；静态事件退订、Unity 假 null 和批量拾取副作用待验证 |
| 第 9 课 | [背包纯数据网格](inventory-data-grid.md) | 已记录；纯 C# 数据层已完成本环境编译与最小运行测试，asmdef 资产配置待 Unity 工程复核 |
| 第 10 课 | [背包 UI 与拖拽](inventory-ui-and-drag.md) | 已记录；课程记录描述已实现自动入包、拖拽预览和非法回弹，本环境完成静态审阅 |
| 第 11 课 | [掉落分层与交互拾取](loot-layering-and-interaction.md) | 已记录；课程记录描述已实现两级掉落、经验球自动拾取和装备交互拾取，本环境完成静态审阅 |

阶段总结：[V0.1 阶段复盘](../../reviews/2026/backpack-survivor-v0.1-review.md)。

## 当前验证证据

- 原始学习记录描述了实际运行结果：玩家进入危险区持续掉血，离开后停止，死亡后不再受伤。
- 本知识库环境使用 .NET SDK 和最小 Unity API 桩完成了脚本编译，并通过 `Health` 扣血/死亡守卫、危险区进入/tick/退出的逻辑冒烟测试；但没有真实 Unity 物理场景、Prefab 或运行截图，因此不能代替 Unity 场景复测。
- 第 2～5 课课程记录描述了敌人追击、双武器、自动索敌、扫掠命中、刷怪和对象池的场景运行结果。
- 用户补充说明 Kimi 已检查代码与 Unity 场景；知识库将其记录为外部检查证据。本环境仍没有完整 Unity 工程与 Profiler 数据，因此不声称亲自复现了运行或性能结果。
- 第 7 课课程记录描述了掉落系统、权重随机、保底计数和掉落物超时回收。本环境完成静态审阅，未运行 Unity 场景；其中零权重表、掉落 Prefab 是否接入对象池、`FindAnyObjectByType` 成本和材质实例化仍待项目验证。
- 第 8 课课程记录描述了拾取磁吸、`DropItem.OnCollected` 静态事件和临时 `PickupLogger`。本环境完成静态审阅，未运行 Unity 场景；静态事件生命周期、Unity 假 null、批量拾取副作用和 Profiler 数据仍待验证。
- 第 9 课课程记录描述了 `BS.Inventory` 纯数据程序集、`Item`、`InventoryGrid` 和 Debug.Log 验证剧本。本环境用 .NET SDK 对整理后的纯 C# 数据层完成编译与最小运行测试；未检查实际 `.asmdef`、`.meta` 或 Unity 工程资产。
- 第 10 课课程记录描述了背包 UI、拖拽、红绿预览、非法回弹和拾取自动入包。本环境完成静态审阅和文档构建，未运行 Unity Editor、Play Mode 或检查 Prefab / Canvas 层级。
- 第 11 课课程记录描述了掉落分层、保底修正、经验球自动拾取、装备 E 键交互和提示 UI。本环境完成静态审阅和文档构建，未运行 Unity Editor、Play Mode 或检查 Prefab / Input Actions / Layer 配置。

## 下一步

- 第 6 课工程 hygiene 资料尚未入库，后续收到后再补。
- 第 12～13 课推进容器搜刮、合并升级和邻接联动。
- 为 `TargetRegistry` 增加场景/Play Mode 清理、按阵营计数和失效目标处理。
- 补做低帧率、多 Collider、命中缓冲区满载、刷怪点合法性、跨池归还、批量拾取、拖拽中断和交互拾取失败测试。
- 使用 Profiler 验证预热量、扩容次数、索敌、物理查询、UI 重绘、经验球吸附和 GC Alloc。
