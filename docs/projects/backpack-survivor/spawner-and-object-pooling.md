# 刷怪器与对象池

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户转述 Kimi 已检查代码与 Unity 场景；本环境未重新运行 Unity
>
> 日期：2026-07-22
>
> 阶段：V0.1 战斗核心原型 · 第 5 课

## 学习目标

- 用环带随机位置持续生成敌人，并限制场上活跃数量。
- 用预热、弹性扩容和回收替代战斗中的频繁 `Instantiate` / `Destroy`。
- 用 `IPoolable` 把池子的生命周期指令与敌人、投射物的重置逻辑解耦。
- 让池化对象的状态、事件订阅和目标注册在每次复用时保持闭环。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `IPoolable` | 定义 `SetPool`、`OnGetFromPool`、`OnReturnPool` 三个池化钩子 |
| `ObjectPool` | 维护空闲队列、预热、弹性扩容、防重复归还和自归还入口 |
| `EnemySpawner` | 在玩家周围环带取点，按场上目标数控制刷怪 |
| `EnemyAI` | 在 `OnEnable` / `OnDisable` 中登记/注销和订阅/退订，死亡时归还池子 |
| `Projectile` | 命中、撞墙、超程三条结束路径统一归还 |
| `Health` | 提供 `ResetToFull()`，并把受击位置改为瞄准点或碰撞体中心 |

原始记录称敌人从玩家周围环带持续刷出，场上数量受上限约束，敌人与子弹均已池化；在一次完整运行中，Hierarchy 数量稳定且战斗期间没有发生额外 `Instantiate`。用户补充说明代码和 Unity 场景已经由 Kimi 检查。本页将其记录为外部检查证据；“战斗中零 Instantiate”是特定预热与负载下的观察结果，不是池化实现的无条件保证。

## 对象池完整周期

```text
预热 Instantiate
    ↓
Get：出队 → 定位 → 激活 → 绑定池 → 重置
    ↓
服役：移动、受击、攻击
    ↓
Die / 命中 / 撞墙 / 超程
    ↓
Return：判空 → 防重复 → OnReturn → 休眠 → 入队
    ↓
再次 Get：恢复同一个实例
```

对象池用常驻内存换取运行时更稳定的创建成本。它不能自动消除所有 GC，也不能替代状态重置、事件清理、特效清理和外部引用管理。

## IPoolable 契约

```csharp
public interface IPoolable
{
    void SetPool(ObjectPool pool);
    void OnGetFromPool();
    void OnReturnPool();
}
```

池子只发三条指令，不需要知道对象是敌人还是子弹：

- `SetPool`：记录本次拥有者或归还通道；
- `OnGetFromPool`：恢复生命值、计时器、速度、目标、拖尾和其他可变状态；
- `OnReturnPool`：停止协程、清理表现、解除外部引用，并准备停用。

这和 `IDamageable` 的思路相同：系统之间依赖行为契约，而不是依赖具体类。项目当前形成了“伤害契约 + 池化契约”两条接口主线。

## ObjectPool 的最小实现

```csharp
private readonly Queue<GameObject> idle = new();
private readonly HashSet<GameObject> idleSet = new();

public GameObject Get(Vector3 position)
{
    GameObject obj = idle.Count == 0
        ? Instantiate(prefab)
        : DequeueAndUntrack();

    obj.transform.position = position;
    IPoolable poolable = obj.GetComponent<IPoolable>();
    poolable?.SetPool(this);
    poolable?.OnGetFromPool();
    obj.SetActive(true);
    return obj;
}

public void Return(GameObject obj)
{
    if (obj == null || idleSet.Contains(obj))
    {
        return;
    }

    obj.GetComponent<IPoolable>()?.OnReturnPool();
    obj.SetActive(false);
    idle.Enqueue(obj);
    idleSet.Add(obj);
}
```

上面的顺序把绑定与重置放在激活前，减少 `OnEnable` 到池状态准备完成之间的窗口。原始课程片段是在 `SetActive(true)` 后再调用 `SetPool` / `OnGetFromPool`；在当前项目中如果 `OnEnable` 只做注册和订阅，功能可以成立，但更稳妥的通用协议应明确“先准备，再激活”。无论采用哪种顺序，都要保证池对象不会在重置完成前被 `Update` 或外部系统使用。

## 敌人的池化适配

```csharp
private void OnEnable()
{
    TargetRegistry.Register(health);
    health.OnDeath += Die;
}

private void OnDisable()
{
    TargetRegistry.Unregister(health);
    health.OnDeath -= Die;
}

private void Die()
{
    if (pool != null)
    {
        pool.Return(gameObject);
    }
    else
    {
        gameObject.SetActive(false);
    }
}

public void OnGetFromPool()
{
    health.ResetToFull();
    attackTimer = 0f;
}
```

这解决了第 3 课暴露的“`Start` 订阅丢失”问题：每次激活重新订阅，每次停用注销；每次取出时恢复生命值和攻击计时。`OnDisable` 中的注销与退订必须保持幂等，避免死亡、手动回收和场景清理走不同路径时重复操作。

## 环带刷怪与场上上限

```csharp
spawnTimer += Time.deltaTime;
if (spawnTimer < spawnInterval)
{
    return;
}

if (TargetRegistry.Count >= maxAlive)
{
    return;
}

float radius = Random.Range(spawnInsideRadius, spawnOutsideRadius);
float angle = Random.Range(0f, 360f) * Mathf.Deg2Rad;
Vector3 spawnPosition = playerTf.position + new Vector3(
    Mathf.Cos(angle) * radius,
    0f,
    Mathf.Sin(angle) * radius);

enemyPool.Get(spawnPosition);
spawnTimer -= spawnInterval;
```

这里复用了 `TargetRegistry.Count`，没有为刷怪器再维护一份“活着的敌人数量”。但这个计数只有在注册表明确只登记敌人时才等价于敌人数；如果未来玩家、可破坏物或其他阵营也登记到同一表，应改成按阵营计数或提供专门的敌人计数接口。

角度必须转换为弧度，`Mathf.Sin` / `Mathf.Cos` 不接受角度值。半径直接在内外半径之间均匀抽样，会让靠近内圈的位置更密；如果目标是“环带面积均匀”，应对半径平方做均匀抽样后再开平方。当前项目只需要环带感时，简单方案可以接受，但不要把它误写成面积均匀分布。

> 后续演进：第 18 课没有把“第几分钟该多难”塞进 `EnemySpawner`，而是新增 `WaveDirector` 读取 `GameSession.Elapsed`，只在阶段变化时调用 `EnemySpawner.ApplyWaveSettings()`。这样刷怪器继续做执行器，15 分钟压力曲线由导演调度，详见[波次导演与 15 分钟节奏](wave-director-and-run-pacing.md)。

## 关键设计理解

### 预热与弹性扩容

预热把一部分 `Instantiate` 成本移动到加载或初始化阶段；池为空时仍可弹性扩容。战斗期间出现扩容次数，正好可以作为预热量不足的指标。预热数量应根据同屏峰值、目标平台内存预算和加载时长共同决定，而不是固定套用某个数字。

### 防重复归还

`HashSet<GameObject>` 记录空闲对象，可以拦截命中、超程、手动取消或场景清理同时归还同一实例的情况。真正的池还应验证对象确实属于自己；仅检查“是否已经在 idleSet”无法阻止外部对象被错误塞进池中。需要时维护 `allObjects` 集合或在 `IPoolable` 中记录拥有者。

### 状态重置是池化的核心

敌人至少要重置生命值、死亡标记、攻击计时、当前目标和池引用；子弹还要重置方向、速度、伤害、攻击者、命中列表、拖尾和协程。任何只在第一次 `Awake` / `Start` 初始化的可变状态，都必须重新评估是否属于 `OnGetFromPool`。

### Unity 生命周期在池化下的语义

`Awake` / `Start` 适合实例级一次性初始化，`OnEnable` / `OnDisable` 适合每次激活和休眠的注册、订阅与注销。`SetActive(false)` 不是销毁，`OnDestroy` 也不会在每次归还时触发。详见[Unity 生命周期](../../unity/lifecycle.md)。

## 需要保留的边界

- `ObjectPool.Start` 预热与 `EnemySpawner.Start` 的初始化顺序不能靠默认顺序假设；正式项目应显式初始化或在 `Awake` / 启动服务中建立依赖。
- `TargetRegistry.Count` 需要明确统计范围，不能永远假定注册表只包含敌人。
- `EnemySpawner` 需要处理玩家引用缺失、半径参数非法、刷怪点落入障碍物或距离地形不合适等配置问题。
- 直接 `spawnPosition.y = 1f` 只适合当前平面灰盒；复杂地形需要采样地面、NavMesh 或碰撞验证。
- 预热不足时仍会扩容；“战斗中零 Instantiate”必须结合实际峰值和 Profiler 记录。
- `Return` 需要防止跨池归还、重复归还和对象已被销毁的情况。
- Unity 对象判空应优先使用 `UnityEngine.Object` 的 `== null` / 布尔语义；接口引用和 `?.` 可能绕过引擎的“假 null”行为，不能把 C# 普通引用的判空规则直接套进 Unity。
- 池化并不自动消除所有 GC；队列扩容、协程、特效、日志和业务集合仍需 Profiler 验证。

## 如何验证

### 功能与生命周期

- 预热数量、池空扩容和归还后再次取出均可观察。
- 敌人死亡、子弹命中、撞墙、超程和手动取消都只归还一次。
- 归还后注册表数量下降，再次取出后重新登记和订阅。
- 敌人再次生成时满血、计时器清零、目标为空，子弹没有上一次飞行状态。
- 场上上限只统计目标阵营，切换场景或停止游戏后没有静态残留。

### 性能与资源

- 记录预热峰值、战斗期间扩容次数、活跃/空闲数量和内存占用。
- 用 Profiler 对比池化前后的 Instantiate、Destroy、GC Alloc 和主线程帧时间。
- 验证池化对象的 Prefab、`.meta`、材质、碰撞层和子物体引用在反复取出/归还后保持正确。

用户记录称代码和 Unity 场景已由 Kimi 检查；本次入库将此作为外部检查记录，但没有在当前环境重新打开 Unity 工程或运行上述测试。

## 相关内容

- [主动武器与 WeaponBase 提炼](active-weapons-and-weapon-base.md)
- [目标注册表、自动武器与投射物](target-registry-and-auto-weapon.md)
- [波次导演与 15 分钟节奏](wave-director-and-run-pacing.md)
- [战斗反馈快包](combat-feedback-pack.md)
- [Unity 生命周期](../../unity/lifecycle.md)
- [对象池专题](../../performance/memory/object-pool.md)
- [优化小 Tips](../../performance/perf-tips.md)

> 📎 标签：`Unity` `刷怪器` `对象池` `IPoolable` `预热` `弹性扩容` `项目实践`
