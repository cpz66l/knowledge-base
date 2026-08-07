# 敌人追击、近战与死亡流程

> 项目：[Backpack Survivor](index.md)
>
> 状态：项目中使用
>
> 验证状态：待验证。本页证据来自用户转述的外部检查；本环境未重新运行 Unity。
>
> 日期：2026-07-20
>
> 阶段：V0.1 战斗核心原型 · 第 2 课
>
> Unity 版本：项目记录为 Unity 6.3

## 学习目标

- 用少量条件分支表达敌人的待机、追击和攻击状态。
- 让敌人的近战伤害复用现有 `DamageInfo` 与 `Health` 管线。
- 用 `Health.OnDeath` 串起敌人死亡流程。
- 理解 `Awake`、`Start`、`Update` 与销毁阶段各自承担的职责。
- 把危险区的作用阵营从写死规则改成可配置数据。

## 当前实现

| 模块 | 当前职责 |
|---|---|
| `EnemyAI` | 缓存自身组件、查找玩家、按距离追击或攻击，并响应自身死亡事件 |
| `CharacterController` | 执行平面追击移动与基础重力处理 |
| `Health` | 同时作为玩家和敌人的生命值、阵营与死亡事件来源 |
| `HazardZone` | 通过 `targetFaction` 决定只伤害某阵营，或在中立配置下不过滤阵营 |

原始记录描述的运行结果是：敌人会在视野内追击玩家，进入攻击范围后周期性造成近战伤害；敌人生命值归零后执行死亡流程；中立危险区可以同时作用于玩家和敌人。用户补充说明 Kimi 已检查代码与 Unity 场景；本页将其记录为外部检查证据，本知识库环境没有完整工程，未自行复现运行结果。

## 最小状态分支

当前行为可以明确拆成三个状态，而不是“两态”：
```text
距离 > viewRange
  └─ 待机

attackRange < 距离 <= viewRange
  └─ 转向并追击

距离 <= attackRange
  └─ 停止追击并累计攻击计时
```

核心判断可以先保留在一个 `Update` 中：

```csharp
Vector3 toPlayer = playerTf.position - transform.position;
toPlayer.y = 0f;
float distance = toPlayer.magnitude;

if (distance > viewRange)
{
    return;
}

if (distance > attackRange)
{
    Quaternion targetRotation = Quaternion.LookRotation(toPlayer);
    transform.rotation = Quaternion.RotateTowards(
        transform.rotation,
        targetRotation,
        rotationSpeed * Time.deltaTime);

    characterController.SimpleMove(toPlayer.normalized * moveSpeed);
    return;
}

TickAttack();
```

状态少、切换条件单一时，显式分支比提前搭建完整 FSM 更容易调试。出现攻击前摇、硬直、击退、巡逻、技能阶段或多个状态共享进入/退出逻辑后，再提取状态对象或状态枚举更合适。

## 关键设计理解

### 1. 组件缓存与跨对象查找分开

当前实践在 `Awake` 中缓存同一对象上的 `CharacterController` 和 `Health`，在 `Start` 中查找玩家。这是一种清晰的项目约定，但不是 Unity 强制的“铁律”。真正需要保证的是：使用引用前已经完成初始化，并且不要在每帧热路径中反复执行场景查找。

`FindGameObjectWithTag` 在单玩家灰盒原型中可以接受，但应只查找一次并缓存。多人、重生、切场景或运行时替换玩家后，需要改成显式注入、生成器传参或玩家注册服务。

### 2. RequireComponent 只保证本对象的组件存在

```csharp
[RequireComponent(typeof(CharacterController))]
[RequireComponent(typeof(Health))]
public class EnemyAI : MonoBehaviour
{
}
```

它能降低敌人对象漏挂依赖组件的概率，但不能保证：

- 组件字段配置正确；
- Tag 为 `Player` 的对象一定存在；
- 玩家对象一定挂有 `Health`；
- 运行时移除组件后仍满足契约。

因此玩家查找与 `GetComponent<Health>()` 仍需要失败处理。

### 3. 近战攻击继续走统一伤害管线

敌人不直接修改玩家生命值，而是构造 `DamageInfo` 后调用 `TakeDamage`：

```csharp
DamageInfo info = new DamageInfo(
    contactDamage,
    gameObject,
    playerHealth.Position,
    false,
    knockbackForce);

playerHealth.TakeDamage(info);
```

这样危险区、近战、投射物可以共享受伤、死亡、日志与后续反馈入口。多伤害源同时存在时，`attacker` 也能帮助确认实际伤害来源。

### 4. 死亡事件完成一次性对象的闭环

第 2 课在 `Start` 订阅，在 `Die` 中退订并销毁对象：

```csharp
health.OnDeath += Die;

private void Die()
{
    health.OnDeath -= Die;
    Destroy(gameObject);
}
```

对于“创建一次、死亡后销毁”的敌人，这条路径能够表达订阅和清理。第 3 课改成停用并准备复用后，这组生命周期一度不再完整；第 5 课已把订阅迁移到 `OnEnable` / `OnDisable`，并在取出时重置 `Health`，详见[刷怪器与对象池](spawner-and-object-pooling.md)。

### 5. 危险区差异先配置化

敌我危险区目前只在目标阵营上有差异，使用 `SerializeField` 配置比为每种区域建立子类更直接。中立值的语义是“跳过阵营过滤”，并不代表它本身是一个会被攻击的阵营。

公开枚举成员应使用 PascalCase，例如 `Faction.Neutral`。此外，原有危险区的多 Collider、子物体 Collider 和接口销毁判空边界仍然存在，见[伤害管线与危险区](damage-pipeline-and-hazard-zone.md)。

## 静态检查发现的边界

### 玩家依赖没有完整守卫

原片段只检查了玩家对象是否存在，没有检查 `playerHealth`：

```csharp
playerHealth = player.GetComponent<Health>();
```

如果 Player Tag 配置正确但 `Health` 缺失，下一帧读取 `playerHealth.IsDead` 会抛出空引用异常。应在初始化阶段一起校验并给出明确日志。

### 配置值需要约束

至少要保证：

- `moveSpeed >= 0`；
- `attackInterval > 0`；
- `0 <= attackRange <= viewRange`；
- `contactDamage >= 0`。

可在 `OnValidate`、自定义 Inspector 或运行时初始化中阻止无效配置。

### 攻击计时语义还没有定义完整

计时器只在攻击范围内累积，目标离开后会保留进度。重新进入时可能很快受到下一击。`attackTimer -= attackInterval` 能保留一次跨帧余量，但遇到一帧跨越多个攻击间隔时，仍需要决定是补发、限制为一击，还是直接丢弃积压。

这些都不是单纯的代码对错，而是需要先确定：首次贴身是否立即攻击、离开范围是否重置前摇、卡顿后是否允许连续补击。

### 直接追击不等于完整寻路

`CharacterController.SimpleMove` 适合灰盒平地追击，但当前逻辑没有路径规划、视线遮挡、坡度与卡墙恢复策略。遇到障碍物时，敌人可能持续朝玩家方向挤压，而不会绕路。

`CharacterController` 已提供角色碰撞形状；额外的 `CapsuleCollider` 不应被一概视为禁止，但如果两个形状重叠并同时参与物理，必须明确各自是实体碰撞、Trigger 还是命中盒，并通过 Layer Collision Matrix 避免重复响应。

### 第 5 课已补齐对象池生命周期

当死亡从 `Destroy` 改成 `SetActive(false)` 后，`Start` 不会在再次激活时重跑。第 3 课因此暴露了死亡事件不会重新订阅、生命值和 `IsDead` 未重置的问题。第 5 课已将订阅/退订迁移到 `OnEnable` / `OnDisable`，并通过池化钩子调用 `ResetToFull()`、清零攻击计时器，形成“死亡 → 归还 → 重置 → 再次启用”的闭环。跨池归还、场景清理和更多运行时状态仍需继续测试。

## 如何验证

在 Unity 工程中应保留以下可重复测试：

- 玩家位于视野外、追击区和攻击区时，敌人分别进入正确分支。
- 玩家对象缺失或缺少 `Health` 时，敌人安全停用并输出可定位日志。
- 敌人只在攻击范围内造成伤害，首次攻击和离开后重入的计时符合设计。
- 人为降低帧率后，移动速度、旋转速度与攻击频率符合预期。
- 敌人死亡只执行一次清理；再次激活时事件、生命值和注册状态能够恢复。
- 障碍物、斜坡、多个 Collider 与中立危险区同时存在时没有重复伤害或异常推挤。

用户转述 Kimi 已检查代码与 Unity 场景；本知识库仍只完成文档静态复核与构建验证，没有在当前环境重新执行这些场景测试。

## 相关内容

- [伤害管线与危险区](damage-pipeline-and-hazard-zone.md)
- [目标注册表、自动武器与投射物](target-registry-and-auto-weapon.md)
- [刷怪器与对象池](spawner-and-object-pooling.md)
- [Unity 生命周期](../../unity/lifecycle.md)
- [委托与事件](../../csharp/oop/delegates-and-events.md)

> 📎 标签：`Unity` `敌人 AI` `状态机` `CharacterController` `事件` `项目实践`
