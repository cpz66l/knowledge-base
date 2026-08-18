# 第 37 课：升级候选池模块

> 状态：项目中使用 / 用户复盘记录
> 对应版本：V0.3.1
> 证据归属：用户 `inbox/V0.3.1升级候选池复盘.md`；本环境整理为知识页，未运行 Unity Editor、Play Mode 或 Player Build
> 关联内容：[经验成长与三选一](level-progression-and-choice.md)、[Backpack Survivor 项目总览](index.md)

## 模块目标

V0.2 的升级系统已经跑通“三选一”，但选项仍偏固定。V0.3.1 的目标是把升级系统从“固定 3 个选项”推进到“可扩展候选池”：

- 候选项扩展到攻击、生存、机动、搜刮、构筑五类方向。
- 支持权重、等级门槛、同轮不重复和最大选择次数。
- 每个选项都要有真实消费侧，避免“能选但无效果”。
- `LevelUpChoiceView` 继续只负责展示，不参与生成规则。

## 核心结构

| 层级 | 职责 |
|---|---|
| `LevelUpOptionDefinition` | 配置事实源：ID、分类、标题、描述、数值、权重、等级门槛、最大选择次数 |
| `LevelUpOption` | 本次运行时展示对象，由 definition 生成 |
| `LevelUpOptionGenerator` | 根据等级、权重、选择次数和同轮去重生成候选项 |
| `GameSession` | 控制升级选择时机、暂停战斗、应用选择和恢复战斗 |
| `PlayerRunStats` | 统一承接本局升级属性 |

最终链路：

```text
LevelUpOptionDefinition
  ↓
LevelUpOptionGenerator.Generate(level, count)
  ↓
GameSession.RequestLevelUpChoice(level)
  ↓
LevelUpChoiceView
  ↓
GameSession.ChooseLevelUpOption(option)
  ↓
PlayerRunStats.Apply(option)
  ↓
Weapon / Player / Loot / Health / BackpackWeaponActivator
```

## 关键规则

- `Weight` 表示出现概率，不等于强度。
- `MinLevel = N` 表示玩家升到 N 级的这次选择就可以出现。
- `MaxPickCount` 记录玩家真正选择次数，不记录候选出现次数。
- 同轮不重复通过候选副本移除实现，不能依赖随机“刚好不重复”。
- 选择后才调用 `RecordPick()`，因为“出现在候选里”和“被玩家获得”是两件事。

## 消费侧接入

本模块新增或整理的属性统一从 `PlayerRunStats` 出口流向消费侧：

| 消费侧 | 承接内容 |
|---|---|
| `WeaponBase` | 伤害、暴击、暴伤、子弹速度 |
| `AutoWeapon` | 自动武器射程、射速 |
| `PlayerController` | 移动速度 |
| `PickUpMagnet` | 拾取范围 |
| `GameSession` | 经验倍率、金币倍率、最大生命选择入口 |
| `Health` | 最大生命、玩家减伤 |
| `BackpackWeaponActivator` | 激活武器上限 |

## 踩坑与沉淀

| 问题 | 根因 | 修复 / 规则 |
|---|---|---|
| `pickCounts.Clear()` 空引用 | 字段声明后没有初始化字典 | 运行期容器只要会被生命周期入口调用，字段声明阶段就要给有效对象 |
| 自动引入 `Mono.Cecil` | IDE 自动导入无关命名空间 | 运行时代码文件头部必须人工扫一眼 |
| 双持奖励占基础激活位 | 基础激活循环结束后才补双持奖励 | 基础武器激活后立即结算双持奖励，奖励武器不占基础名额 |
| 武器上限升级过强 | `MaxPickCount` 和开放等级符合配置但体验超模 | Demo 期改为最多一次，并推迟到 8 级开放 |
| 候选池变宽后成长不稳定 | 非战斗项稀释核心战斗成长出现率 | 上调部分战斗项收益，并后移经济 / 构筑项开放等级 |

## 面试表达

- 这次不是单纯“加了几个升级”，而是把升级项拆成配置 definition、运行时 option、生成器、运行期属性和消费侧。
- UI 不知道权重、等级门槛和上限，降低表现层耦合。
- 扩内容后概率结构会变化，数值必须重新评估；否则玩家会觉得升级变杂但不变强。

## 待验证

- 当前知识库未运行 Unity，只记录用户项目复盘和实机回归描述。
- 后续如果继续扩候选池，需要补概率样本、不同等级候选分布和战斗成长体感记录。

