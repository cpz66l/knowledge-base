# 容器搜刮与宝箱系统

> 项目：[Backpack Survivor](index.md)
>
> 状态：用户课程记录描述已实现宝箱交互、击杀触发生成、地图边界约束和掉落散落协程；本环境完成静态审阅与文档验证，未重新运行 Unity
>
> 日期：2026-07-27（课程记录：2026-07-26）
>
> 阶段：V0.2 掉落与背包构筑 · 第 12 课

## 学习目标

- 复用第 11 课的 `IInteractable` 管线，让宝箱不用改玩家侧探测器、提示 UI 和 E 键输入。
- 用“出池即配置”支持 Common / Uncommon / Rare 等级宝箱，而不是为每个等级维护一套 Prefab。
- 建立 `MapBounds` 作为地图边界单一事实源，供生成器和玩家位置钳制查询。
- 用拒绝采样实现“在地图内、离玩家足够远”的宝箱生成点选择。
- 用协程表现开箱后物品散落，并明确池化对象被中断时需要复位的副作用。
- 用幂等守卫和消费者清缓存处理池化引用过期、重复回收和重复入包风险。

## 交付范围

| 模块 | 当前职责 |
|---|---|
| `LootChest` | 宝箱交互对象，签 `IInteractable + IPoolable`，开箱后生成掉落、关闭触发器、变黑留残骸 |
| `ChestSpawner` | 订阅敌人死亡事件，按击杀数、场上上限、地图点位和权重等级生成宝箱 |
| `ChestTier` | 生成器内部等级配置：名称、颜色、掉落束表和权重 |
| `MapBounds` | 圆形竞技场边界：随机点、范围判断、位置钳制和 Gizmos 可视化 |
| `LootManager.TrySpawnDrop` | 从 `void` 演进为返回生成对象列表，旧敌人调用方可以忽略返回值 |
| `DropItem.PlayScatterFlight` | 掉落物自行执行抛物线散落协程，飞行期间关闭碰撞器，落地后恢复 |
| `InteractDetector` | 交互后主动清空目标，避免 0.1s 探测间隔内重复使用过期池化引用 |

第 12 课的主线是把第 11 课“装备可交互拾取”的接口能力扩展到环境物：宝箱成为另一个 `IInteractable` 实现类，玩家侧输入、提示和探测代码保持稳定。

## 宝箱交互链路

宝箱开箱不直接知道背包或 UI，只把自己当作掉落来源：

```text
玩家进入范围
  -> InteractDetector 发现 LootChest
  -> InteractPromptUI 显示“按 E 打开宝箱”
  -> LootChest.Interact()
  -> LootManager.TrySpawnDrop(dropPoint, lootBundle)
  -> DropItem 散落到地面
```

`LootChest` 的运行期状态需要围绕“未开箱可交互、已开箱不可重复交互、残骸稍后回收”来设计：

```csharp
public class LootChest : MonoBehaviour, IInteractable, IPoolable
{
    [SerializeField] private string chestName = "宝箱";
    [SerializeField] private LootTableData lootBundle;
    [SerializeField] private Renderer chestModel;
    [SerializeField] private Transform dropPoint;
    [SerializeField] private float survivalTime = 30f;

    public static int ActiveCount { get; private set; }

    private bool opened;
    private float survivalTimer;
    private Collider chestCollider;
    private LootManager lootManager;
    private Color originalColor;
    private ObjectPool pool;

    public string GetPrompt() => $"按 E 打开 {chestName}";

    public void Interact()
    {
        if (opened) return;

        opened = true;
        chestCollider.enabled = false;
        chestModel.material.color = Color.black;
        lootManager.TrySpawnDrop(dropPoint == null ? transform.position : dropPoint.position, lootBundle);
    }

    public void Initialize(string name, Color color, LootTableData bundle)
    {
        chestName = name;
        chestModel.material.color = color;
        lootBundle = bundle;
    }

    public void OnGetFromPool()
    {
        survivalTimer = 0f;
        opened = false;
        chestCollider.enabled = true;
        chestModel.material.color = originalColor;
        ActiveCount++;
    }

    public void OnReturnPool() => ActiveCount--;
}
```

这里的关键不是代码量，而是职责切分：`OnGetFromPool` 负责恢复中性出厂状态，`Initialize` 负责灌入本轮等级配置。两层都存在，宝箱才能既复用同一个池，又表现出不同等级。

## 生成器与拒绝采样

`ChestSpawner` 使用击杀事件作为触发源。以后如果改成波次、房间完成或 Boss 事件，只需要替换触发入口，生成策略仍可保留。

```csharp
private void AddKillsCount()
{
    killsCount++;

    if (killsCount >= killsToSpawn)
    {
        if (TrySpawnChest())
        {
            killsCount = 0;
        }
    }
}

private bool TrySpawnChest()
{
    if (LootChest.ActiveCount >= maxFieldCount) return false;
    if (!TryFindSpawnPoint(out Vector3 pos)) return false;
    if (tiers == null || tiers.Length == 0) return false;

    ChestTier tier = PickByWeight(tiers);
    if (tier == null) return false;

    chestPool.Get(pos)
        .GetComponent<LootChest>()
        .Initialize(tier.chestName, tier.color, tier.bundle);

    return true;
}
```

守卫顺序按成本排列：先做场上数量这种整数比较，再做随机点采样，最后才掷等级和动池子。击杀计数只在生成成功后清零，因此当场上宝箱已满时，生成配额会被“背压”保留。

点位选择采用拒绝采样：

```text
生成候选点
  -> 验证离玩家距离
  -> 不合格重摇
  -> 最多尝试 N 次
  -> 失败则本轮不刷
```

这套骨架可迁移到刷怪点、装饰物、事件点和后续 Roguelike 房间布局。必须保留重试预算，否则条件过严时可能卡死在循环里。

## MapBounds 单一事实源

第 12 课把地图边界抽成独立组件：

```csharp
public class MapBounds : MonoBehaviour
{
    [SerializeField] private float radius = 40f;

    public Vector3 Center => transform.position;

    public Vector3 GetRandomPoint()
    {
        Vector2 offset = Random.insideUnitCircle * radius;
        return transform.position + new Vector3(offset.x, 0f, offset.y);
    }

    public Vector3 ClampToInside(Vector3 pos)
    {
        Vector3 offset = pos - Center;
        offset.y = 0f;

        if (offset.sqrMagnitude <= radius * radius) return pos;

        Vector3 clamped = Center + offset.normalized * radius;
        clamped.y = pos.y;
        return clamped;
    }
}
```

切分标准是：换地图时要改的知识进入 `MapBounds`，换玩法时要改的策略留在调用方。`ChestSpawner` 负责“离玩家多远、尝试几次、上限多少”，`MapBounds` 只负责“地图内点位和边界钳制”。

玩家边界钳制也应信任这个 API：

```csharp
transform.position = mapBounds.ClampToInside(transform.position);
```

原始记录中的“角色飞天”来自调用方提前把偏移和绝对位置混在一起，并把 y 清零后交给 `CharacterController` 解穿透。这里沉淀出的规则是：调用 API 前先确认契约，不要替被调用方做一半内部工作。

## 散落协程

宝箱需要“开箱后掉落物飞散”，因此 `LootManager.TrySpawnDrop` 从无返回值改为返回生成对象列表。敌人死亡处仍可忽略返回值，宝箱则可以拿到对象后命令它们散落。

```csharp
public void PlayScatterFlight(Vector3 from, Vector3 to)
{
    transform.position = from;
    StartCoroutine(FlyRoutine(from, to));
}

private IEnumerator FlyRoutine(Vector3 from, Vector3 to)
{
    itemCollider.enabled = false;

    float t = 0f;
    while (t < 1f)
    {
        t += Time.deltaTime / flightDuration;
        t = Mathf.Min(t, 1f);

        Vector3 horizontal = Vector3.Lerp(from, to, t);
        float height = arcHeight * 4f * t * (1f - t);
        transform.position = horizontal + Vector3.up * height;

        yield return null;
    }

    transform.position = to;
    itemCollider.enabled = true;
}
```

协程适合这种有明确起点、终点和时长的一次性动作。池化场景下额外要问：如果对象飞到一半被回收，哪些副作用会残留？本课答案是碰撞器可能一直关闭，所以 `OnGetFromPool` 必须恢复 `itemCollider.enabled = true`。

## 幂等与过期引用

本课记录了一个双重回收问题：交互探测器在下一次扫描前仍缓存旧目标，玩家连按 E 可能对已回池对象再次 `Collect()`，造成重复归还和重复入包。

修复采用双端设防：

```csharp
public void Collect()
{
    if (isCollected) return;

    isCollected = true;
    OnCollected?.Invoke(lootEntry);
    Recycle();
}
```

```csharp
private void Interact()
{
    if (CurrentTarget == null) return;

    CurrentTarget.Interact();
    previousTarget = null;
    CurrentTarget = null;
    OnTargetChanged?.Invoke(null);
}
```

生产者保证同一生命周期只收一次；消费者在使用完目标后立即清缓存，不等待下一轮探测。第 13 课把 `Interact()` 演进为返回 `bool` 后，会进一步把“成功才清目标”写进接口契约。

## 常见错误

| 问题 | 根因 | 处理方式 |
|---|---|---|
| Renderer 空引用 | MeshRenderer 在子物体，脚本只 `GetComponent<Renderer>()` 查自己 | Inspector 拖槽或使用 `GetComponentInChildren`，并在 Prefab 复核引用 |
| 生成点总在错误位置 | 把圆心和偏移相乘，混淆平移与缩放 | 圆心加随机偏移：`center + offset` |
| 复制代码后玩家引用为空 | 生成器不是玩家，`GetComponent<Health>()` 挂载对象错了 | 复制模式时先确认脚本挂在哪个对象上 |
| `private new Collider collider` 警告 | 字段遮盖 `MonoBehaviour.collider` 旧成员名 | 改成 `chestCollider` 这类具体命名 |
| 宝箱复用后颜色错误 | `OnGetFromPool` 没恢复原色 | 缓存 `originalColor`，每次取出恢复 |
| 飞行后不可交互 | 协程中关闭碰撞器，回池或异常中断未复位 | `OnGetFromPool` 统一恢复碰撞器 |
| 重复开箱或重复入包 | 缓存目标指向已回池对象，连按触发重复 `Collect()` | 生产者幂等守卫 + 消费者交互后清目标 |
| UnityEditor using 混入运行时代码 | 自动补 using 时未检查命名空间 | 提交前扫描改动文件头部 using |

## 如何验证

### 宝箱交互

- 玩家进入宝箱范围时显示正确提示，离开或开箱后提示立即隐藏。
- 同一个宝箱连续按 E 只生成一次掉落。
- 开箱后触发器关闭，模型变黑，30s 后残骸回池。
- Common / Uncommon / Rare 宝箱分别使用配置的名称、颜色和掉落束表。

### 生成与边界

- 每满指定击杀数才尝试生成宝箱，场上数量达到上限时不继续取池对象。
- 玩家附近排除圈生效，`maxAttempts` 耗尽时本轮安全失败。
- `MapBounds` Gizmos 与实际随机点、玩家钳制范围一致。
- 玩家在边界处不会被压入地面或被 CharacterController 弹飞。

### 池化与散落

- 宝箱回池再取出后 `opened`、计时器、颜色和碰撞器都恢复。
- 掉落物飞行期间不可拾取，落地后重新可交互。
- 飞行中被回收再取出时，碰撞器不会保持关闭。
- 对象池重复归还检测不再报警。
- Profiler 记录生成、协程、对象池扩容和 GC Alloc；没有数据前不写性能收益结论。

## 当前证据分层

| 结论 | 证据等级 | 说明 |
|---|---|---|
| 第 12 课实现了宝箱交互、击杀触发生成、等级配置、地图边界和掉落散落 | B | 来自用户放入 Inbox 的课程记录 |
| `IInteractable` 让宝箱接入时玩家侧探测器、提示 UI 和 E 键输入无需新增专用分支 | B | 原始记录明确描述了复用结果 |
| 拒绝采样适合当前“地图内且离玩家足够远”的点位选择 | C | 本环境基于代码结构和生成策略静态审阅 |
| 协程中关闭碰撞器的副作用必须进入池化复位清单 | C | 基于池化对象生命周期和协程中断语义推断 |
| 第 12 课已由当前环境在 Unity Editor / Play Mode 中运行通过 | D | 本次未收到完整 Unity 工程、场景、Prefab、Input Actions、Layer 或 `.meta`，未运行 Unity |
| 宝箱生成与散落已验证无 GC 分配或性能收益显著 | D | 缺少 Profiler 数据，暂不写成性能结论 |

## 相关内容

- 前置：[掉落分层与交互拾取](loot-layering-and-interaction.md)
- 前置：[刷怪器与对象池](spawner-and-object-pooling.md)
- 后续：[背包交互补丁](inventory-interaction-patches.md)
- 后续：[战斗反馈快包](combat-feedback-pack.md)
- Unity：[Unity 生命周期](../../unity/lifecycle.md)
- 性能：[对象池](../../performance/memory/object-pool.md)
- C#：[委托与事件](../../csharp/oop/delegates-and-events.md)

> 📎 标签：`Unity` `宝箱系统` `IInteractable` `对象池` `协程` `拒绝采样` `MapBounds` `项目实践`
