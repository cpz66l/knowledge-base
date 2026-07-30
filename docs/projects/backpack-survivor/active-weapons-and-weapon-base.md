# 主动武器与 WeaponBase 提炼

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户转述 Kimi 已检查代码与 Unity 场景；本环境未重新运行 Unity
>
> 日期：2026-07-22
>
> 阶段：V0.1 战斗核心原型 · 第 4 课

## 学习目标

- 让自动武器和主动武器共享同一条投射物与伤害管线。
- 用输入状态位表达“按住连发”，而不是只响应一次按键事件。
- 在出现第二个真实武器后提炼 `WeaponBase`，明确公共部分与差异部分。
- 处理鼠标地面瞄准中的 Y 轴拍平、零向量和首发冷却语义。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `WeaponBase` | 保存弹速、伤害、目标阵营、最大射程和枪口引用，并提供公共发射入口 |
| `AutoWeapon` | 查询注册表、转动枪口、检查角度门槛并自动开火 |
| `ActiveWeapon` | 读取 `AttackHeld`，朝鼠标地面点持续射击 |
| `InputReader` | 把 Input System 的 `performed` / `canceled` 转换为稳定状态位 |
| `Projectile` | 复用第 3 课的命中、阵营和伤害管线；第 5 课进一步接入对象池 |

原始记录描述的结果是：按住鼠标左键可以连续射击，松开即停；主动武器与自动武器同时工作，前者负责点杀、后者负责清杂。用户补充说明代码和 Unity 场景已由 Kimi 检查；这是本页的外部验证证据，本知识库环境没有完整源码、场景和输入资产，未自行复现该运行结果。

## 双战斗系统的数据流

```text
InputReader.AttackHeld ──┐
                         ├─ ActiveWeapon ─┐
TargetRegistry ──────────┘                │
                                          ├─ WeaponBase.Fire
                                          │       ↓
                                          └─ Projectile → IDamageable → Health
```

自动武器和主动武器的差异在“目标来源”和“触发方式”，不在弹道、伤害和阵营检查。共享 `Projectile` 后，手动与自动攻击不会各自维护一份命中逻辑。

## 为什么在第二把武器出现后提炼基类

第 2、3 课只有自动武器时，直接在具体类中保留字段和发射逻辑仍然清晰。第 4 课出现主动武器后，对比两个真实实现可以得到：

| 共同部分 | 差异部分 |
|---|---|
| projectile speed、damage、target faction、max distance、fire point | 目标来自注册表还是鼠标地面点 |
| 创建/取得投射物、传递初始化参数 | 按冷却自动发射还是读取按住状态 |
| 使用同一 `Projectile` 和 `DamageInfo` | 是否需要枪口转向和角度门槛 |

因此 `WeaponBase` 承载稳定的共同部分，子类只负责触发条件。这个抽象来自第二个真实案例，而不是先猜一个“未来可能有的武器体系”。

## WeaponBase 的职责

```csharp
public abstract class WeaponBase : MonoBehaviour
{
    [SerializeField] protected float projectileSpeed = 20f;
    [SerializeField] protected float damage = 5f;
    [SerializeField] protected Faction targetFaction = Faction.Enemy;
    [SerializeField] protected float maxDistance = 30f;
    [SerializeField] protected Transform firePoint;

    protected void Fire(Vector3 direction)
    {
        // 第 4 课灰盒版本：创建 GameObject + AddComponent。
        // 第 5 课正式版本：应从 Projectile 池 Get，并在取出时重置。
        GameObject bulletObject = new GameObject("Bullet");
        bulletObject.transform.position = firePoint.position;
        Projectile projectile = bulletObject.AddComponent<Projectile>();
        projectile.Initialize(
            projectileSpeed,
            damage,
            targetFaction,
            maxDistance,
            direction,
            0f,
            gameObject);
    }
}
```

`abstract` 禁止直接把没有完整触发逻辑的基类挂到场景对象上；`protected` 让子类读取配置，同时保留 Inspector 配置能力。进入第 5 课的池化版本后，`Fire` 的公共职责仍然保留，但“创建新 GameObject”应替换为投射物池的 `Get`，否则主动武器会绕过池化。后续第 17 课又让 `WeaponBase` 在发射前读取 `PlayerRunStats.DamageMultiplier`，让升级奖励通过同一条发射入口影响主动/自动武器，详见[经验成长与三选一](level-progression-and-choice.md)。

## 主动武器的输入状态

“按住连发”是持续状态，不是一次性事件。`InputReader` 把输入回调转换成外部只读、内部可写的属性：

```csharp
public bool AttackHeld { get; private set; }

public void Attack(InputAction.CallbackContext context)
{
    if (context.performed)
    {
        AttackHeld = true;
    }
    else if (context.canceled)
    {
        AttackHeld = false;
    }
}
```

具体回调阶段还取决于 Input Action 的类型与 Interaction 配置；本项目的 Button 动作采用 `performed` 表示进入按下状态，`canceled` 表示释放。武器在 `Update` 中读取状态并按时间间隔发射，避免把“按住期间的每一发”都塞进输入回调。

## 主动瞄准与计时

```csharp
private void Awake()
{
    inputReader = GetComponentInParent<InputReader>();
    if (firePoint == null)
    {
        firePoint = transform;
    }

    fireTimer = fireInterval;
}

private void Update()
{
    fireTimer += Time.deltaTime;
    if (inputReader == null || !inputReader.AttackHeld)
    {
        return;
    }

    if (fireTimer < fireInterval)
    {
        return;
    }

    Vector3 direction = inputReader.worldPoint - firePoint.position;
    direction.y = 0f;
    if (direction.sqrMagnitude < 0.0001f)
    {
        return;
    }

    Fire(direction.normalized);
    fireTimer -= fireInterval;
}
```

这里有三个容易被忽略的顺序：

1. 鼠标地面点与枪口高度不同，先把方向拍平到 XZ 平面。
2. 拍平后再判断零向量，否则 Y 分量可能掩盖“实际没有水平方向”。
3. 使用减法保留跨帧余量，避免把计时器直接归零造成长期漂移。

`fireTimer = fireInterval` 表示第一次满足输入时可以立即发射；究竟使用 `>=` 还是 `>`、方向无效时是否消耗冷却、松开后是否保留余量，都应写入手感测试，而不是只凭注释判断。

## 重构边界与常见错误

### 重构只改变结构，不改变行为

安全顺序是：先提交可回滚版本，对比 AutoWeapon 与 ActiveWeapon 的字段和发射流程，再小步把共同部分搬到基类，最后验证索敌、手动瞄准、阵营、伤害和冷却行为没有变化。若重构后攻击手感改变，应先区分是搬运错误还是有意调整。

### 零向量会制造无效投射物

鼠标指向角色脚下时，拍平后的方向可能为零。若不提前返回，投射物可能无法移动，也无法触发超程自毁，形成悬挂对象。这个守卫必须放在拍平之后。

### `InputReader`、`firePoint` 和 `worldPoint` 都是外部依赖

`GetComponentInParent<InputReader>()` 失败、`firePoint` 未配置或输入世界点尚未初始化时，应在初始化阶段给出明确日志或停用武器。不能把所有错误推迟到 `Update` 的空引用异常。

### 灰盒发射路径不是最终池化路径

第 4 课的 `new GameObject + AddComponent` 适合去掉 Prefab 依赖、快速验证功能；第 5 课已经建立投射物池后，两个武器都应通过同一个池取得子弹。否则“敌人池化、子弹池化”的阶段结论会被主动武器的旧代码绕开。

## 如何验证

- 按住、松开和快速点击时，`AttackHeld` 状态和发射次数符合预期。
- 鼠标指向脚下、角色正下方和远处时，不会生成零方向投射物。
- 自动武器和主动武器同时开火时，阵营、命中、伤害和投射物归还逻辑一致。
- 首发是否即时、冷却跨帧余量、低帧率补发策略与设计文档一致。
- 缺少 `InputReader`、`firePoint` 或输入世界点无效时能够安全失败。
- 使用第 5 课投射物池时，主动武器没有重新 `Instantiate`，并且投射物复用前状态已重置。

当前证据分层如下：

- 用户课程记录：主动/自动双武器功能已经完成。
- 用户补充的外部证据：Kimi 检查过代码与 Unity 场景。
- 本知识库验证：文章结构、链接和 MkDocs 构建；没有完整工程运行验证。

## 相关内容

- [目标注册表、自动武器与投射物](target-registry-and-auto-weapon.md)
- [刷怪器与对象池](spawner-and-object-pooling.md)
- [背包武器激活](backpack-weapon-activation.md)
- [战斗反馈快包](combat-feedback-pack.md)
- [Unity 生命周期](../../unity/lifecycle.md)
- [委托与事件](../../csharp/oop/delegates-and-events.md)
- [对象池专题](../../performance/memory/object-pool.md)

> 📎 标签：`Unity` `主动武器` `WeaponBase` `Input System` `继承` `对象池` `项目实践`
