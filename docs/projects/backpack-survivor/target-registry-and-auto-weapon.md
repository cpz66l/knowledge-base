# 目标注册表、自动武器与投射物

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户转述 Kimi 已检查代码与 Unity 场景；本环境未重新运行 Unity
>
> 日期：2026-07-21
>
> 阶段：V0.1 战斗核心原型 · 第 3 课
>
> Unity 版本：项目记录为 Unity 6.3

## 学习目标

- 用目标注册表缩小自动索敌的查询范围。
- 用 `OnEnable` / `OnDisable` 对齐目标的登记与注销。
- 让枪械在角色完成本帧转向后独立瞄准。
- 用扫掠检测降低高速投射物穿透目标的风险。
- 识别 NonAlloc、静态服务和对象池准备工作各自仍需验证的边界。

## 当前实现

| 模块 | 当前职责 |
|---|---|
| `TargetRegistry` | 保存已登记的 `IDamageable`，按阵营、射程和距离查询最近目标 |
| `AutoWeapon` | 每帧索敌，在 `LateUpdate` 中转动枪口，满足冷却与角度条件后开火 |
| `Projectile` | 沿本帧位移做 `SphereCastNonAlloc`，过滤发射者与 Trigger，再把命中交给伤害管线 |
| `EnemyAI` | 启用时登记/订阅、禁用时注销/退订，死亡后由第 5 课对象池回收 |
| `PlayerController` | 只旋转身体表现节点，让身体与枪械可以分别控制朝向 |

原始记录描述的运行结果是：玩家静止时武器会瞄准最近敌人并自动开火，子弹命中后扣血，敌人死亡后武器切换到下一个目标；同时修复了 Trigger 挡子弹、枪口尚未对准就发射和敌人阵营漏配等问题。

用户补充说明 Kimi 已检查代码与 Unity 场景，因此本页把运行结果记录为外部检查证据。当前知识库没有完整工程与 Profiler 记录，可以复核设计和代码片段，但不能自行证明 Unity 物理行为或“零分配”。

## 系统流程

```text
Enemy OnEnable
  ↓ Register(Health)
TargetRegistry
  ↓ 最近目标查询
AutoWeapon.LateUpdate
  ↓ 转向 + 冷却 + 角度门槛
Projectile
  ↓ 本帧路径 SphereCast
IDamageable.TakeDamage
  ↓
Health.OnDeath
  ↓ ObjectPool.Return
Enemy OnDisable
  ↓ Unregister(Health) + 取消死亡订阅
```

## 关键设计理解

### 1. 注册表缩小搜索集合

武器不再每次从全场景对象中查找敌人，而是遍历主动登记的目标：

```csharp
for (int i = allTargets.Count - 1; i >= 0; i--)
{
    IDamageable target = allTargets[i];
    if (target == null || target.IsDead || target.Faction != targetFaction)
    {
        continue;
    }

    float sqrDistance = (target.Position - fromPos).sqrMagnitude;
    // 记录射程内距离最小的目标
}
```

查询复杂度仍是 O(T)，其中 T 是已登记目标数；`List.Contains`、`Remove` 也仍是 O(T)。收益来自“只遍历候选目标”和避免场景查找，不是把最近目标查询变成常数时间。当前敌人数较少时，列表方案足够清晰；只有实际测量证明查询成为瓶颈后，才需要空间分区、分帧查询或更复杂的数据结构。

### 2. 登记与激活状态对齐

```csharp
private void OnEnable()
{
    TargetRegistry.Register(health);
}

private void OnDisable()
{
    TargetRegistry.Unregister(health);
}
```

目标能否被索敌，本质上与对象当前是否启用一致。相较只在 `Awake` 登记、`OnDestroy` 注销，`OnEnable` / `OnDisable` 能覆盖重复启用和停用，是对象池友好的方向。

这里依赖 `health` 已在 `Awake` 缓存。对于正常激活的组件，`Awake` 会先于该实例的第一次 `OnEnable`。更完整的生命周期边界见[Unity 生命周期](../../unity/lifecycle.md)。

### 3. LateUpdate 分离身体和枪口的写入顺序

角色身体在 `Update` 中转向，枪械在 `LateUpdate` 中根据最终身体姿态设置瞄准节点的世界旋转，可以避免同一帧内两个系统争夺朝向结果。

`LateUpdate` 解决的是回调阶段顺序，不等于所有瞄准依赖都自动正确。若还有相机、动画 Rig 或其他 `LateUpdate` 脚本修改相同节点，仍需要明确组件职责或配置 Script Execution Order。

### 4. 开火前检查视觉朝向

枪口逐步旋转时，使用角度容差阻止过早开火：

```csharp
if (Quaternion.Angle(aimPivot.rotation, targetRotation) > fireAngleTolerance)
{
    return;
}

Fire((currentTarget.Position - firePoint.position).normalized);
```

这让视觉朝向与真实弹道使用同一个目标方向。容差大小属于手感参数，应在不同旋转速度、敌人移动速度和帧率下验证。

### 5. 扫掠检测覆盖本帧路径

高速子弹只检查新位置时，可能在相邻两帧之间跨过较薄的 Collider。当前做法从旧位置沿本帧位移执行 `SphereCastNonAlloc`，再选择返回结果中距离最近的有效碰撞。

`QueryTriggerInteraction.Ignore` 解决了危险区 Trigger 阻挡弹道的问题，但也意味着项目必须保证真正可命中的敌人至少有一个非 Trigger 命中 Collider，或为不同碰撞用途建立更明确的 Layer 和查询规则。

### 6. NonAlloc 只减少查询结果数组的分配

复用 `RaycastHit[]` 缓冲区可以避免每次物理查询都返回新数组，但“整条子弹逻辑零分配”还需要 Profiler 证据。创建 `GameObject`、`AddComponent`、日志、特效和其他业务逻辑仍可能产生托管或原生侧成本。

### 7. 灰盒期代码生成子弹

```csharp
GameObject bulletObject = new GameObject("Bullet");
Projectile projectile = bulletObject.AddComponent<Projectile>();
projectile.Initialize(...);
```

这条路线不依赖 Prefab，适合快速验证弹道。需要注意：`AddComponent<Projectile>()` 会先触发该组件的 `Awake`，之后才执行 `Initialize`，因此 `Awake` 不能依赖初始化参数已经就绪。

这是第 3 课的灰盒路径，当时仍然每发创建新对象。第 5 课已经把投射物改成 Prefab + 对象池；自动武器和第 4 课主动武器都应通过同一发射入口取得池化投射物，详见[主动武器与 WeaponBase 提炼](active-weapons-and-weapon-base.md)和[刷怪器与对象池](spawner-and-object-pooling.md)。

## 后续演进与仍需验证的边界

### 1. 第 5 课已补齐敌人复用闭环

第 2 课在 `Start` 中订阅死亡事件，并在 `Die` 中取消订阅；第 3 课把死亡改成 `SetActive(false)`：

```csharp
private void Die()
{
    health.OnDeath -= Die;
    gameObject.SetActive(false);
}
```

这段第 3 课代码会在再次激活时丢失死亡订阅。第 5 课已经完成以下修复：

- 在 `OnEnable` / `OnDisable` 中成对订阅和退订；
- 通过 `IPoolable.OnGetFromPool` 重置生命值和攻击计时；
- 死亡后调用池的 `Return`；
- 使用空闲集合防止重复归还。

项目仍需验证目标引用、协程、动画、特效、跨池归还和场景清理是否全部复位。

### 2. 接口引用与静态列表可能残留失效目标

`IDamageable` 接口引用可能绕过 Unity 对已销毁对象的特殊 null 比较。查询中只写 `target == null` 不一定能识别原生对象已经销毁的情况。当前 `GetNearestTarget` 也只是跳过死亡目标，没有从列表中清理它们，`Count` 可能包含不可用项。

静态列表还需要定义切场景、退出 Play Mode，以及关闭 Domain Reload 时的清理时机。单场景原型可以暂用 static，但应补充显式 `Clear`、场景级所有者或运行时初始化重置，并保留一个可可靠判断销毁状态的 `UnityEngine.Object` 引用。

### 3. 固定命中缓冲区可能截断结果

`RaycastHit[8]` 只保存有限数量的结果。当返回数量等于缓冲区长度时，应把它视为“可能已满”，不能证明缓冲区之外没有更近的有效碰撞。可按项目密度选择：

- 使用 LayerMask 先减少无关候选；
- 记录缓冲区满载次数并调整容量；
- 对极端密集场景使用可扩容的备用路径；
- 明确子弹出生时已经与 Collider 重叠的处理方式。

### 4. 无目标时的冷却注释与行为不一致

```csharp
if (currentTarget == null)
{
    attackTimer = 0f;
    return;
}
```

这会让新目标出现后重新等待完整攻击间隔，并不是“保持就绪”。如果设计是立刻开火，可以把计时器保持在已就绪状态；如果设计是锁定后蓄力，则清零是合理的，但注释和测试用例应与之统一。

当冷却已经完成但枪口尚未对准时，计时器还会继续累积。对准后只减去一个间隔，可能形成短时间连续补发。应决定是允许积压、把计时器封顶到一个间隔，还是在瞄准阶段暂停冷却。

### 5. 最近目标不一定是最稳定或可命中的目标

距离相近的两个敌人可能让目标每帧切换，遮挡物后的最近敌人也可能阻止武器选择稍远但可见的目标。当前原型先验证“最近目标”是合理的；后续再根据实际问题增加目标锁定迟滞、视线检测、优先级或查询降频。

### 6. 输入和配置仍需防御

- `maxRange`、`attackInterval`、`rotationSpeed`、投射物速度与最大距离需要非负约束。
- `firePoint`、`aimPivot` 和阵营配置缺失时应在初始化阶段失败，而不是等到 `LateUpdate` 抛异常。
- `TargetRegistry` 应进入与目录一致的命名空间，并移除无关 `using`。
- `~0` 会查询所有 Layer；正式碰撞规则应改用明确的 LayerMask。

## 如何验证

### 功能测试

- 一个、多个和零个敌人时，索敌结果符合射程与阵营规则。
- 两个等距敌人、目标死亡、目标禁用和目标离开射程时，切换行为稳定。
- 枪口未对准时不发射，对准后冷却语义符合设计。
- Trigger 不挡子弹，实体墙能挡子弹，敌人的有效命中 Collider 不会被忽略。
- 高速子弹、低帧率、薄 Collider 和出生点重叠情况下没有非预期穿透。
- 命中缓冲区满载时能够记录并采用预定降级策略。

### 生命周期测试

- 敌人反复 `SetActive(true/false)` 后，注册表数量不会重复增长或遗漏。
- 敌人死亡、回收、重置并再次启用后，仍能再次触发死亡流程。
- 切换场景和关闭 Domain Reload 的 Play Mode 配置下，静态列表不会保留上一轮目标。

### 性能测试

- 在目标数和子弹数逐步增加时记录主线程物理耗时。
- 使用 Profiler 的 GC Alloc 列确认查询热路径是否真的没有每帧分配。
- 对比逐帧索敌、5–10 Hz 降频索敌与锁定当前目标的成本和手感。

用户转述 Kimi 已检查代码与 Unity 场景；本知识库没有在当前环境重复运行，也没有 Profiler 数据，因此性能和极端边界测试仍待保留证据。

## 相关内容

- [敌人追击、近战与死亡流程](enemy-ai-and-melee.md)
- [伤害管线与危险区](damage-pipeline-and-hazard-zone.md)
- [主动武器与 WeaponBase 提炼](active-weapons-and-weapon-base.md)
- [刷怪器与对象池](spawner-and-object-pooling.md)
- [Unity 生命周期](../../unity/lifecycle.md)
- [对象池](../../performance/memory/object-pool.md)
- [优化小 Tips](../../performance/perf-tips.md)

> 📎 标签：`Unity` `自动索敌` `目标注册表` `投射物` `SphereCastNonAlloc` `LateUpdate` `项目实践`
