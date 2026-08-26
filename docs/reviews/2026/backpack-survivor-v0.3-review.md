# Backpack Survivor V0.3 版本复盘：内容深度、反馈与留存

> 周期：2026-08-11 至 2026-08-20  
> 阶段目标：在 V0.2 可试玩 Demo 基础上，补充内容深度、反馈包装、敌人变化、设置能力和本地留存记录  
> 证据归属：用户 `inbox/V0.3版本复盘.md` 阶段复盘；其中提交数、脚本数、行数、Profiler 和 Build 结论来自用户记录，本环境未重新统计外部 Unity 项目或运行 Build  
> 对应项目：[Backpack Survivor](../../projects/backpack-survivor/index.md)

## 交付结论

V0.3 阶段目标达成：项目从“完整可试玩”推进到“具备内容扩展、反馈包装和局外记录”的版本。

V0.2 解决的是能否从主菜单进入 15 分钟 Demo，并完整跑通战斗、掉落、背包和结算；V0.3 进一步回答：这个 Demo 是否有更多构筑选择、更强反馈、更稳定敌群、更完整设置和可累计的长期目标。

核心成果：

```text
构筑深度：升级候选池 + 邻接汇总 + 背包被动物品 + 武器品质/等级倍率
战斗变化：近战敌群 Steering + 远程敌人 + 波次混编
反馈包装：分武器音效 + BGM + UI/胜负/拾取音效 + 设置菜单
留存目标：本地 JSON 存档 + 历史纪录 + 胜利累计局外收益
发布闸门：Profiler 快扫 + Windows Build 实测
```

## 阶段产出

| V0.3 核心目标 | 状态 | 代表模块 / 能力 |
|---|---|---|
| 升级候选池扩容 | 完成 | `LevelUpOptionGenerator` / `PlayerRunStats` |
| 邻接效果架构升级 | 完成 | `BackpackEffectCollector` / `BackpackItemModifier` |
| 背包构筑效果扩展 | 完成 | `CritBoost` / `MechanicalArm` / `Armor` / `MagnetCore` |
| 内容池与价值平衡 | 完成 | `Item.Id` 图标解析 / `scoreValue` / 宝箱投放 |
| 基础音频与 BGM | 完成 | `SfxId` / `WeaponSfxId` / `AudioCue` / `MusicVolumeApplier` |
| 设置菜单 | 完成 | `GameSettings` / `SettingsService` / `SettingsPanelView` |
| 敌群移动优化 | 完成 | `EnemyMovement` / 分离力 / 障碍避让 / 错峰采样 |
| 远程敌人与波次混编 | 完成 | `RangedEnemyAI` / `ProjectilePoolProvider` / `WaveDirector` |
| 本地存档与纪录 | 完成 | `SaveData` / `SaveService` / `MainMenuRecordView` |
| 发布前验收 | 完成 | Profiler 快扫 / Windows Build 实测记录 |

用户阶段复盘记录：约 10 天完成 V0.3 主体扩展，2026-08-20 完成 V0.3 Build 验收；截至复盘编写，外部项目记录为 63 次 Git 提交、86 个 C# 脚本、6972 行 C# 代码。这些数字本次未由知识库环境重新统计。

## 系统扩展复盘

### 升级候选池

V0.3 将升级拆成定义、生成和消费三层：

```text
LevelUpOptionDefinition：稳定 ID、分类、标题、描述、数值、权重、等级门槛、最大选择次数
LevelUpOptionGenerator：按等级和次数筛选，再按权重抽取，同轮去重
PlayerRunStats：统一承接升级结果，并提供各系统消费出口
```

这让升级项不只是 UI 弹窗，而能真实影响伤害、射速、暴击、生命、减伤、移动、拾取、经验、金币和武器上限等运行期属性。

### 邻接与背包构筑

V0.3 没有继续把每种邻接效果塞进 `BackpackWeaponActivator`，而是新增汇总层：

```text
InventoryGrid.ScanAdjacency
  -> AdjacencyEffectResolver 筛出有效效果
  -> BackpackEffectCollector 汇总数值 modifier
  -> Activator / 武器 / 被动系统消费
```

`DualWield` 作为激活类效果保留特殊处理，攻速、伤害、暴击等数值类效果进入 modifier 汇总，机械臂、护甲和磁吸核心作为背包被动生效。

### 内容、音频与设置

内容池把新增规则回填到真实掉落表：机械臂、磁吸核心、护甲、瞄准镜、高价值收集品和传说物进入宝箱与掉落体系。图标解析从 `ItemTag` 粗粒度绑定升级为 `Item.Id` 优先、`ItemTag` 兜底。

音频从零散字段升级为 cue 表驱动：

```text
SfxId / WeaponSfxId
  -> AudioCue / WeaponAudioCue
  -> SfxPlayer.PlaySfx / PlayWeaponShoot
```

设置系统形成数据、服务和 UI 三层：

```text
GameSettings：音量、分辨率、窗口模式
SettingsService：Load / Save / Apply
SettingsPanelView：Slider / Dropdown 映射
```

### 敌人移动和远程敌人

V0.3 将移动从 `EnemyAI` 中拆出为 `EnemyMovement`，加入追玩家方向、分离力、障碍避让、低频错峰采样、方向平滑和绕行方向记忆。当前地图是开放竞技场，轻量 steering 比全员 NavMeshAgent 更符合成本收益。

远程敌人复用已有 `Health`、掉落、投射物和对象池链路，通过保持距离、冷却射击和敌方子弹给中后期战斗增加走位压力，并通过 `WaveDirector` 纳入正式波次混编。

### 本地存档与纪录

V0.3 的存档没有做断点续玩，而是做战绩留存：

```text
totalRuns
totalWins
bestBackpackValue
totalGold
legendaryFoundCount
legendaryCollectedValue
lastPlayedVersion
```

开局即记录总局数，胜利才累计胜场、局外金币和传说带出数据。这样失败和胜利的统计口径清晰，也避免把本地存档做成复杂局内状态快照。

## 关键问题与修正

| 类型 | 问题 | 根因 | 处理 |
|---|---|---|---|
| 升级生成 | 首次升级能抽到 2 级选项 | 玩家第一次升级后等级为 2 | 明确 `MinLevel` 语义，保留该行为 |
| 武器激活 | 双持奖励可能占基础激活位 | 基础激活和奖励激活顺序混在一起 | 基础武器激活后再结算双持奖励 |
| 音频按钮 | 开始游戏偶发无反应 | 等待点击音协程延迟加载场景 | 立即加载，点击音用跨场景临时音源播放 |
| 设置 UI | 分辨率 / 窗口索引理解成本高 | Dropdown 索引和候选列表映射不直观 | 候选列表集中生成，再按索引读取 |
| 敌人移动 | 敌群抖动和避障摇摆 | 避让方向频繁左右切换 | 增加方向平滑和绕行方向记忆 |
| 存档服务 | MainMenu UI 被带进 Run 场景 | `SaveService` 挂在 Canvas 上并 `DontDestroyOnLoad` | 改为独立根对象承载跨场景服务 |
| 弹窗点击 | 设置 / 纪录面板外仍能点到后方按钮 | UI 没有遮挡点击穿透 | 增加全屏遮罩或阻挡层 |

## 性能与发布验证

用户阶段复盘记录 V0.3 发布前做了 Editor Profiler 快扫和 Build 实测。快扫中部分尖刺主要落在资源预加载、纹理上传、GPU 等待或 Editor / Profiler 观察环境。用户记录普通帧中 `PlayerLoop` 很低，正式 Build 完整试玩无明显卡顿，战斗节奏和数值压力没有明显缺陷。

因此 V0.3 没有在发布前做大规模性能重构，而是记录证据、保留观察项，延续“先判断瓶颈属于哪里，再决定是否改代码”的原则。

## 不足与风险

- 内容仍是 Demo 量级，距离完整商业内容仍有差距。
- 配置数据化还不彻底，部分内容仍在代码表或场景字段中维护。
- 存档缺少正式迁移策略，字段结构变化时需要补迁移逻辑。
- 音频没有完整混音管线，AudioMixer、低血量提示和命中音色层次仍可补。
- 敌人移动仍是开放地图方案，复杂关卡、长墙和封闭区域要重新评估导航体系。
- 资源授权仍需谨慎，公开展示和商业化前要逐项确认授权。

## 下一阶段方向

V0.3 之后不建议立刻追 Boss 或大而全系统，优先围绕“内容深度和作品表达”继续推进：

```text
P0：补更多高性价比升级项、芯片和背包被动物品
P1：做构筑收益展示，让玩家知道当前总收益
P1：给局外金币增加消费出口，形成更明确的长期目标
P2：补第二种远程敌人或特殊敌人，增强中后期压力变化
P2：完善音频混音、命中反馈和低血量提示
P3：再评估 Boss、复杂关卡、完整数据化和更重的导航方案
```

## 阶段总结

V0.3 的核心价值可以概括为：在不推倒 V0.2 主干的前提下，把《背包幸存者》扩展成一个更有构筑深度、更有战斗变化、更像正式 Demo 的版本。

对求职展示来说，V0.3 体现的能力不只是 Unity API 使用，而是从玩法、架构、内容、性能验证到发布包装的完整工程推进能力。

> 标签：`Backpack Survivor` `项目复盘` `Unity` `版本复盘` `作品集`

