# 远程敌人与波次混编

> 项目：《背包幸存者》Backpack Survivor  
> 模块周期：V0.3.8-V0.3.9  
> 学习状态：项目复盘已整理  
> 证据归属：用户 `inbox/V0.3.8-0.3.9远程敌人与波次混编复盘.md` 复盘记录；用户记录完整跑局无明显问题，且 `dotnet build BackpackSurvivor/BackpackSurvivor.sln --no-restore` 通过，本环境未重复运行 Unity / dotnet build  
> 关键词：RangedEnemyAI、ProjectilePoolProvider、EnemySpawner、WaveDirector、远程敌人、波次混编

## 学习目标

- 新增第一种远程敌人，让战斗压力不再只来自近战追击。
- 复用既有生命、掉落、投射物、对象池和波次系统，而不是为敌方子弹重写一套链路。
- 将远程敌人接入正式波次配置，控制生成比例和血量成长。

## 当前实现

远程敌人一期只做最小可用闭环：

- 根据距离靠近、停距、贴脸后退。
- 面向玩家并按冷却发射子弹。
- 子弹命中玩家造成伤害，命中或超距后回池。
- 远程敌人死亡后广播击杀、生成掉落并回池。
- `EnemySpawner / WaveDirector` 控制远程敌人生成概率和血量。

## 架构链路

```text
RangedEnemyAI
  查找玩家 / 判断距离
        ↓
EnemyMovement
  靠近 / 停距 / 后退
        ↓
firePoint + ProjectilePoolProvider
        ↓
Projectile.Initialize(..., Faction.Player, ...)
        ↓
命中玩家 / 超距回池
```

波次混编：

```text
WaveDirector.WaveStage
  rangedSpawnChance / rangedEnemyMaxHp
        ↓
EnemySpawner.ApplyWaveSettings()
        ↓
PickEnemyPool()
  远程池 / 精英池 / 普通池
```

## 关键取舍

### 为什么不急着抽 EnemyBase

近战和远程确实共享玩家查找、死亡、掉落和回池逻辑，但远程敌人一期还在验证行为边界。过早抽公共基类容易把尚未稳定的差异点固定下来。当前选择是先让远程怪独立跑通，等差异稳定后再评估 `EnemyBase`、`EnemyDeathHandler` 或 `EnemyLootDropper`。

### 为什么复用 Projectile

现有 `Projectile` 已经具备扫掠检测、攻击者自身过滤、目标阵营过滤、命中回池、超距回池和材质颜色处理。远程子弹只需要把 `targetFaction` 设成 `Faction.Player`，不需要为了“敌方子弹”复制一套系统。

### 为什么用 ProjectilePoolProvider

远程敌人是 prefab，不能稳定引用场景里的子弹池。`ProjectilePoolProvider` 让场景显式声明“我是子弹池提供者”，比按名字 `Find` 更可读，也减少对场景命名的隐式依赖。

### 为什么远程概率逐步提升

远程敌人的目标是改变中后期走位压力，而不是替代近战敌潮。前期低概率或不出现，中后期逐步提高，能让玩家在整理背包、追宝箱和躲弹之间产生权衡。

## 踩坑与修正

- 远程敌人转向初版不稳定，修正为 `Quaternion.RotateTowards(transform.rotation, toTarget, rotateSpeed * Time.deltaTime)`。
- 贴脸分支初版为空，修正为 `movement.Move(-toPlayer, moveSpeed)`。
- `contactDamage` 字段未使用，改成更明确的 `projectileDamage`。
- prefab 不能直接引用场景子弹池，新增 `ProjectilePoolProvider`。
- `EnemySpawner` 有 `rangedSpawnChance` 但初版没进入随机分支，导致远程怪不刷出。
- `WaveDirector` 初版没有下发远程概率和远程血量，后续补到 `WaveStage`。

## 验收记录

用户复盘记录覆盖：

- 远程敌人能生成、移动、停距、后退和射击。
- 子弹能命中玩家造成伤害，并在命中或超距后回池。
- 远程敌人死亡后能掉落，并计入击杀 / 宝箱击杀统计。
- `EnemySpawner` 能按 `rangedSpawnChance` 选择远程敌人池。
- `WaveDirector` 能下发远程敌人概率和血量。
- 远程、普通、精英敌人能在正式波次中混编。
- 中后期远程敌人能改变走位和背包整理压力，但不替代近战主节奏。
- 用户完整跑局反馈无明显问题。
- 用户记录 `dotnet build BackpackSurvivor/BackpackSurvivor.sln --no-restore` 通过，0 error。

本环境只整理复盘和知识页，没有重复运行 Unity、Profiler 或 dotnet build。

## 面试表达

```text
我在已有近战敌人和对象池基础上扩展了第一种远程敌人。远程敌人没有推倒原来的 EnemyAI，而是先用独立 RangedEnemyAI 验证保持距离、贴脸后退和冷却射击。子弹复用已有 Projectile，通过 targetFaction 参数切换为攻击玩家，避免重复实现命中和回池逻辑。因为 prefab 不能直接引用场景对象，我增加了 ProjectilePoolProvider，把场景子弹池显式暴露给远程敌人。最后再把远程敌人接入 EnemySpawner 和 WaveDirector，让波次能控制远程敌人概率和血量。
```

## 风险与下一步

- 近战和远程敌人已有部分死亡 / 掉落 / 玩家查找重复，敌人类型继续增加后再抽公共层。
- 远程子弹当前复用玩家 `Projectile`，如果后续需要预警、穿透、爆炸、减速，再拆专用敌方子弹。
- `ProjectilePoolProvider` 如果漏挂或漏拖池，远程敌人会停距但不发射。
- 远程概率过高会抢走敌潮压迫主节奏，需要继续用实机和数值调参控制比例。
- 下一模块进入[本地存档与最高纪录](local-save-and-records.md)。

> 标签：`Backpack Survivor` `远程敌人` `对象池` `Projectile` `波次系统`

