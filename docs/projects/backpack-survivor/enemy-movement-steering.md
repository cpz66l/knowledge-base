# 敌人寻路与群体移动优化

> 项目：《背包幸存者》Backpack Survivor  
> 模块周期：V0.3.7  
> 学习状态：项目复盘已整理  
> 证据归属：用户 `inbox/V0.3.7敌人寻路与群体移动优化复盘.md` 复盘记录；用户记录实机跑局后明显更稳，且 `dotnet build BackpackSurvivor/BackpackSurvivor.sln --no-restore` 通过，本环境未重复运行 Unity / dotnet build  
> 关键词：EnemyAI、EnemyMovement、局部 steering、分离力、障碍避让、低频采样、方向平滑

## 学习目标

- 在开放竞技场 Demo 中解决敌人挤压、重叠、贴障碍和障碍边缘摇摆问题。
- 将高层 AI 决策与移动执行拆开，降低 `EnemyAI` 职责。
- 用局部 steering 替代过早引入 NavMesh，并记录后续升级边界。

## 当前实现

V0.3.7 没有做完整全局寻路系统，而是针对当前开放地图做轻量移动优化：

- `EnemyAI` 负责查找玩家、判断视野、追击 / 攻击、死亡和回池。
- `EnemyMovement` 负责移动方向计算、转向和 `CharacterController.SimpleMove()`。
- 敌人之间加入分离力，减少完全重叠。
- 前方障碍用局部检测和侧向绕行处理。
- 邻居和障碍检测低频错峰采样，避免所有敌人同帧重算。
- 实际移动方向每帧平滑，绕行方向保留短期记忆，降低抖动。

## 架构链路

```text
EnemyAI
  判断玩家距离 / 追击或攻击
        ↓
EnemyMovement.Move(toPlayer, moveSpeed)
        ↓
低频计算 desiredMoveDirection
  追玩家方向 + 分离力 + 障碍避让
        ↓
每帧 Slerp 到 cachedMoveDirection
        ↓
RotateTowards + SimpleMove
```

进入攻击范围后，`EnemyAI` 调用 `movement.Stop()`，同时清理目标方向和缓存方向，避免停下后残留旧移动趋势。

## 关键取舍

### 为什么当前不上 NavMesh

当前地图是开放竞技场，不是迷宫或多房间长路径地图。敌人目标主要是追玩家并形成压力，而不是精确走复杂路线。此时“追玩家方向 + 分离力 + 局部避障”更轻，也更容易兼容现有 `CharacterController`、对象池和刷怪系统。

### 为什么决策低频、移动每帧

如果每帧都做 `OverlapSphereNonAlloc()` 和 `SphereCastNonAlloc()`，敌人数量上来后会增加物理查询压力。若低频计算后直接切方向，又会带来移动跳变。因此最终做法是：昂贵决策低频错峰，移动执行每帧连续平滑。

### 为什么抖动不是靠继续降频解决

本模块中真正有效的修正是分离力钳制、方向平滑和绕行方向记忆。只靠降低更新频率，反而可能让方向跳变更明显。

## 踩坑与修正

- 普通 / 精英敌人刷出距离约 10-15 米，但 `viewRange` 太低时不主动追击；后续在 Inspector 中调到能覆盖刷怪半径。
- 分离力过强导致敌群中心抽动，改为返回前 `Vector3.ClampMagnitude(separation, 1f)`。
- 低频采样后移动摇摆，拆成 `desiredMoveDirection` 和 `cachedMoveDirection`，每帧用 `Vector3.Slerp()` 平滑。
- 障碍边缘左右切换，新增 `avoidSide` 记住上一次可行绕行方向。
- `Stop()` 不清理方向缓存会保留旧趋势，修正为同时清理目标方向和缓存方向。

## 验收记录

用户复盘记录覆盖：

- `EnemyAI` 不再直接执行旋转和 `SimpleMove()`。
- `EnemyMovement` 独立负责移动方向计算、转向和移动执行。
- 普通 / 精英敌人视野覆盖当前刷怪半径。
- 敌人之间有轻微分离，不再明显堆成一个点。
- 遇到障碍能尝试侧向绕行，障碍边缘摇摆减少。
- 敌群中后期移动明显更稳。
- 用户实机跑一局后反馈没有大问题。
- 用户记录 `dotnet build BackpackSurvivor/BackpackSurvivor.sln --no-restore` 通过，0 error。
- 危险 `using` 扫描通过。

本环境只整理复盘和知识页，没有重复运行 Unity、Profiler 或 dotnet build。

## 面试表达

```text
我没有直接给所有敌人上 NavMeshAgent，而是根据开放竞技场场景做了轻量局部 steering。EnemyAI 只负责追击/攻击决策，EnemyMovement 负责移动执行；最终方向由追玩家方向、敌群分离和障碍避让叠加得到。为了控制性能，我把邻居和障碍检测改成低频错峰采样，再用每帧方向平滑保证手感连续。后续如果地图变复杂，再评估 NavMesh 或 Flow Field。
```

## 风险与下一步

- 当前仍是局部规则，不保证处理复杂迷宫、长墙和封闭障碍。
- `enemyLayer`、`obstacleLayer` 依赖 prefab / 场景配置，新敌人或新障碍加入时要检查 Layer。
- 分离力、避障力和方向平滑速度都是手感参数，不同敌人类型需要单独调参。
- 同屏敌人数量继续上升时，需要用 Profiler 观察 Physics 查询占比。
- 下一模块进入[远程敌人与波次混编](ranged-enemies-and-wave-mix.md)。

> 标签：`Backpack Survivor` `EnemyMovement` `寻路` `Steering` `性能取舍`

