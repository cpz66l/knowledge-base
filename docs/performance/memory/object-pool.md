# 对象池

> 复用而非反复创建 — 用对象池降低创建成本和 GC 压力

---

## 一句话理解

```
没有对象池：          有对象池：
创建 → 使用 → 销毁    取出 → 使用 → 归还
创建 → 使用 → 销毁    取出 → 使用 → 归还
创建 → 使用 → 销毁    取出 → 使用 → 归还
  ↑ 创建/销毁成本         ↑ 稳态阶段减少重复分配
```

池子把暂时不用的对象保存起来，用完后归还，下次继续复用。本质是**用额外常驻内存换取更稳定的创建成本**。它可以降低分配和 GC 压力，但不保证整个业务流程“零分配”。

---

## 为什么需要对象池

### GC 尖峰是怎么产生的

```csharp
// ❌ 频繁创建和销毁 GameObject，会产生原生侧与托管侧成本
void Update()
{
    GameObject bullet = Instantiate(bulletPrefab, transform.position, Quaternion.identity);
    // Destroy 会销毁 Unity 对象；相关托管对象最终仍由 GC 处理
    Destroy(bullet, 3f);
}
```

一帧内大量调用 `Instantiate` / `Destroy` 会增加对象创建、初始化、销毁和托管分配成本，并可能形成帧时间尖峰。具体瓶颈必须通过 Profiler 采样确认，不能只根据代码形式判断。

```csharp
// ✅ 对象池方案：复用已经创建的对象，降低重复创建成本
private ObjectPool<GameObject> bulletPool;

void Start()
{
    // 构造池本身不会创建 20 颗子弹
    bulletPool = new ObjectPool<GameObject>(
        createFunc: () => Instantiate(bulletPrefab),
        actionOnGet: (obj) => obj.SetActive(true),
        actionOnRelease: (obj) => obj.SetActive(false),
        actionOnDestroy: (obj) => Destroy(obj),
        collectionCheck: true,
        defaultCapacity: 20,
        maxSize: 50
    );
}

void Update()
{
    if (Input.GetMouseButtonDown(0))
    {
        // 池为空时 Get 会调用 createFunc，仍然可能创建新对象
        GameObject bullet = bulletPool.Get();
        bullet.transform.position = transform.position;
        StartCoroutine(ReturnAfterDelay(bullet, 3f));
    }
}

IEnumerator ReturnAfterDelay(GameObject obj, float delay)
{
    yield return new WaitForSeconds(delay);
    bulletPool.Release(obj);
}
```

!!! note "对象池不等于整段逻辑零分配"
    `defaultCapacity` 只设置内部集合的初始容量，不会预创建对象。池为空时 `Get()` 会调用 `createFunc`；上例中的协程和 `new WaitForSeconds` 也可能产生额外分配。是否达到目标必须用 Profiler 验证。

### 哪些场景收益最大

| 场景 | 典型对象 | 创建频率 |
|------|---------|----------|
| 弹幕射击 | 子弹 | 每帧数颗~数十颗 |
| 粒子特效 | 爆炸、火花 | 每次命中 |
| 敌人生成 | Enemy GameObject | 波次生成 |
| UI 滚动列表 | 列表项 GameObject | 快速滚动时每帧数个 |
| 网络消息 | 消息包对象 | 每帧数十个 |
| 临时计算 | `List<T>` 中间结果 | 每帧多次 |

原则：**生命周期短 + 创建频率高 = 值得池化。**

---

## 核心概念

### 生命周期

```
         ┌─────────────────────────────┐
         │                             │
    Get  │   ┌──────┐          ┌──────┐│  Release
   (取出)│   │ 使用中 │ ──────→ │  空闲  ││  (归还)
         │   └──────┘          └──────┘│
         │        ↑                    │
         │        └── 需要时再 Get ────┘│
         └─────────────────────────────┘
                     池子
```

三个核心操作：

| 操作 | 做了什么 | 何时发生 |
|------|---------|----------|
| `Get()` | 从池中取出一个可用对象，没有则创建新的 | 需要对象时 |
| `Release(obj)` | 把对象放回池中，标记为空闲 | 对象不再需要时 |
| `Clear()` | 清理池中的空闲对象，不影响仍在使用的对象 | 场景切换/不再需要池时 |

### 容量策略

| 策略 | 做法 | 适用场景 |
|------|------|----------|
| 预加热 (Pre-warm) | 初始化时提前创建 N 个 | 负载可预测（如最大 20 发子弹同时在场） |
| 动态扩容 | 池空时创建新对象，池满时归还 | 负载波动大 |
| 上限限制 | 超过 `maxSize` 后归还时直接 Destroy | 防止池无限膨胀 |

### 对象重置

归还前**必须**把对象恢复到干净状态，否则下一次 Get 会带着旧数据：

```
子弹归还前需要重置的项目：
✅ position = Vector3.zero
✅ rotation = Quaternion.identity
✅ trailRenderer.Clear()          ← 拖尾特效残留
✅ damage 伤害值归零
✅ 取消所有 pending 的 Coroutine
```

---

## UnityEngine.Pool（Unity 2021+）

Unity 2021 引入了 `UnityEngine.Pool` 命名空间，对象池成为一等公民。

### ObjectPool<T>

最通用的池，`T` 必须是引用类型：

```csharp
using UnityEngine.Pool;

// 创建池 — 传入四个关键委托
ObjectPool<Bullet> bulletPool = new ObjectPool<Bullet>(
    createFunc:       () => Instantiate(bulletPrefab).GetComponent<Bullet>(),  // 创建新对象
    actionOnGet:      (b) => b.gameObject.SetActive(true),                      // 取出时激活
    actionOnRelease:  (b) => b.gameObject.SetActive(false),                     // 归还时隐藏
    actionOnDestroy:  (b) => Destroy(b.gameObject),                             // 超出容量时真销毁
    collectionCheck:  true,   // 开启重复归还检测（开发期建议开）
    defaultCapacity:  10,     // 内部集合初始容量，不会创建 10 个 Bullet
    maxSize:          50      // 最多保留 50 个空闲对象
);

// 使用
Bullet b = bulletPool.Get();    // 取出
bulletPool.Release(b);          // 归还
bulletPool.Clear();             // 清空池中的空闲对象；不会处理仍在使用的对象
```

### IObjectPool<T> 接口

```csharp
// 接口注入 — 方便在类之间传递池而不暴露具体实现
public class Gun
{
    public IObjectPool<Bullet> BulletPool { get; set; }

    public Bullet RentBullet() => BulletPool.Get();

    public void ReturnBullet(Bullet bullet) => BulletPool.Release(bullet);
}
```

### PooledObject 模式（IDisposable）

`Get(out T)` 返回的 `PooledObject<T>` 适合生命周期完全包含在当前同步作用域中的临时对象：

```csharp
private readonly ObjectPool<List<Vector3>> pointsPool = new(
    createFunc: () => new List<Vector3>(),
    actionOnGet: points => points.Clear(),
    actionOnRelease: points => points.Clear()
);

using (pointsPool.Get(out List<Vector3> points))
{
    CollectVisiblePoints(points);
    DrawPoints(points);
} // using 结束时自动归还列表
```

飞行中的子弹、播放中的特效等对象会在当前方法返回后继续工作，不能用短作用域 `using`；它们应在生命周期真正结束时由统一出口调用 `Release()`。

### GenericPool<T> / UnsafeGenericPool<T>

如果 T 不需要特殊的创建/销毁逻辑，可以用更轻量的静态池：

```csharp
// ListPool 会在归还时清空列表
List<Vector3> points = ListPool<Vector3>.Get();
// ... 使用 ...
ListPool<Vector3>.Release(points);

// GenericPool<T> 适合无需特殊重置逻辑、且有默认构造函数的引用类型
// UnsafeGenericPool<T> 跳过重复归还检查，只在生命周期完全可控时使用
```

---

## 自定义对象池

UnityEngine.Pool 不是唯一选择。当需要特殊行为时，可以自己实现。

### 1. GameObject 池（最常用）

```csharp
public class GameObjectPool
{
    private GameObject prefab;
    private Queue<GameObject> pool = new Queue<GameObject>();
    private Transform container;  // 池对象统一放在一个父节点下，保持 Hierarchy 整洁

    public GameObjectPool(GameObject prefab, int initialSize)
    {
        this.prefab = prefab;
        // 场景中创建一个容器节点收纳所有池对象
        container = new GameObject($"Pool_{prefab.name}").transform;
        Object.DontDestroyOnLoad(container.gameObject);

        // 预加热：提前创建 initialSize 个实例
        for (int i = 0; i < initialSize; i++)
        {
            GameObject obj = CreateNew();
            obj.SetActive(false);
            pool.Enqueue(obj);
        }
    }

    private GameObject CreateNew()
    {
        GameObject obj = Object.Instantiate(prefab, container);
        return obj;
    }

    public GameObject Get(Vector3 position, Quaternion rotation)
    {
        // 池空了就动态扩容
        GameObject obj = pool.Count > 0 ? pool.Dequeue() : CreateNew();
        obj.transform.SetPositionAndRotation(position, rotation);
        obj.SetActive(true);
        return obj;
    }

    public void Release(GameObject obj)
    {
        obj.SetActive(false);
        obj.transform.SetParent(container);
        pool.Enqueue(obj);
    }

    public void Clear()
    {
        while (pool.Count > 0)
            Object.Destroy(pool.Dequeue());
    }
}
```

### 2. 预加热策略

```csharp
// 场景加载时预加热常用池，避免运行时首次 Get 的创建开销
public class PoolManager : MonoBehaviour
{
    public Bullet bulletPrefab;
    public Explosion explosionPrefab;

    private void Awake()
    {
        // 先创建池；defaultCapacity 只设置内部集合容量
        Bullet.Pool = new ObjectPool<Bullet>(
            createFunc: () => Instantiate(bulletPrefab).GetComponent<Bullet>(),
            actionOnGet: (b) => b.gameObject.SetActive(true),
            actionOnRelease: (b) => b.gameObject.SetActive(false),
            actionOnDestroy: (b) => Destroy(b.gameObject),
            defaultCapacity: 30,
            maxSize: 80
        );

        // 显式 Get/Release 才会真正预创建 30 颗子弹
        List<Bullet> preWarm = new List<Bullet>(30);
        for (int i = 0; i < 30; i++)
            preWarm.Add(Bullet.Pool.Get());
        foreach (var b in preWarm)
            Bullet.Pool.Release(b);
    }
}
```

### 3. 固定容量 vs 动态扩容

| | 固定容量 | 动态扩容 |
|------|------|------|
| **内存** | 可预测，不会涨 | 峰谷时可能膨胀 |
| **CPU** | 超限时需等待或降级处理 | 扩容瞬间有一次分配开销 |
| **适用** | 确定最大并发数（如最多 4 名玩家） | 数量不可预测（如敌人波次） |
| **风险** | 池枯竭时逻辑要兜底 | 极端情况池膨胀 |

```csharp
// 固定容量的兜底策略 — 池空了怎么办？
public GameObject GetWithFallback()
{
    if (pool.Count > 0)
        return pool.Dequeue();

    // 方案 A：复用最老的正在用的对象（视觉上最远的子弹消失）
    RecycleOldestActive();

    // 方案 B：直接返回 null，调用方自己处理
    return null;
}
```

---

## 池化策略

### 何时取、何时还

```csharp
// ✅ 正确时机
Get() → 在需要对象的地方（开火、生成敌人、创建 UI 项）
Release() → 在对象生命周期结束时（飞出屏幕、死亡动画结束、滚动出视野）

// ❌ 错误时机
Get() → 在 Start() 里取一堆存着不用     ← 浪费
Release() → 归还后又继续使用             ← Bug
```

### 容量调优

```
1. 先给 `maxSize` 留出足够空间，用 Profiler 和 `CountActive` / `CountInactive` 观察真实峰值
2. 根据希望长期保留的空闲对象数量设置 `maxSize`，并为极端负载设计兜底
3. `defaultCapacity` 只影响内部集合首次扩容，可接近常见空闲数量，但不能替代预加热
4. 需要预加热时显式执行一组 `Get()` / `Release()`，并再次验证帧时间和常驻内存
```

### Trim 与自动缩容

```csharp
// ObjectPool 没有内置 Trim，可以手动检查
public void TrimExcess(int desiredCount)
{
    while (pool.Count > desiredCount)
    {
        var obj = pool.Dequeue();
        Object.Destroy(obj.gameObject);  // 真销毁多余对象
    }
}

// 场景结束后缩容，释放多余内存
void OnBossDefeated()
{
    // 清掉 80% 的空闲子弹，只留一些应付下一波
    int keep = pool.Count / 5;
    TrimExcess(keep);
}
```

---

## 🎯 Unity 实战练习

### 练习 1：基础子弹池

在 `Gun.cs` 中用 `ObjectPool<Bullet>` 实现子弹发射逻辑。

要素：
- 初始化池（容量 20）
- 鼠标点击时取子弹
- 子弹飞出屏幕后自动归还

**填空练习：**
```csharp
public class Gun : MonoBehaviour
{
    [SerializeField] private Bullet bulletPrefab;
    private ObjectPool<Bullet> bulletPool;

    void Start()
    {
        bulletPool = new ObjectPool<Bullet>(
            createFunc:       ______________,   // TODO: 创建子弹
            actionOnGet:      ______________,   // TODO: 激活子弹
            actionOnRelease:  ______________,   // TODO: 隐藏子弹
            defaultCapacity:  20,
            maxSize:          50
        );
    }

    void Update()
    {
        if (Input.GetMouseButtonDown(0))
        {
            Bullet b = ______________;  // TODO: 从池中取子弹
            b.transform.position = transform.position;
            b.Fire();
        }
    }
}
```

---

### 练习 2：敌人生成池

将以下频繁 Instantiate/Destroy 的敌人生成改为对象池：

```csharp
// 原始代码 — 找出性能问题并改写
public class EnemySpawner : MonoBehaviour
{
    public GameObject enemyPrefab;

    void SpawnWave(int count)
    {
        for (int i = 0; i < count; i++)
        {
            GameObject enemy = Instantiate(enemyPrefab, Random.insideUnitCircle * 10, Quaternion.identity);
            // 敌人死亡时 Destroy(enemy)
        }
    }
}
```

**改写要求：**
1. 用 `ObjectPool<GameObject>` 替换 Instantiate
2. 敌人在死亡动画结束后自动归还
3. 场景切换时 Clear 池

---

### 练习 3：滚动列表项池

实现一个可复用的 `ListViewPool`，管理 UI 列表项的创建和回收。

**思考：**
- 用什么数据结构存储空闲项？
- 列表项显示/隐藏时分别调用什么方法？
- 如果内容高度不同，池的大小怎么估算？

> 🚧 更多练习待补充 — 欢迎贡献你的实战场景

---

## ⚠️ 常见坑

### 1. 归还后忘记重置状态

```csharp
// ❌ 归还前没有重置
bulletPool.Release(bullet);
// 下次 Get 出来，子弹可能还带着上次的速度、目标、拖尾特效

// ✅ 在 actionOnRelease 中完整重置
actionOnRelease: (b) =>
{
    b.gameObject.SetActive(false);
    b.trailRenderer.Clear();      // 清拖尾
    b.damage = 0;                 // 归零伤害
    b.owner = null;               // 清空拥有者引用
    b.velocity = Vector3.zero;    // 归零速度
}
```

### 2. 池对象被外部持有引用

```csharp
// ❌ 归还后外部还持有引用
Bullet b = bulletPool.Get();
activeBullets.Add(b);           // 外部列表持有
bulletPool.Release(b);          // 归还
// activeBullets 里还保留着 b → 下次取出来可能被重复操作

// ✅ 归还前解除所有外部引用
activeBullets.Remove(b);
bulletPool.Release(b);
```

### 3. 只取不还或过早归还

```csharp
// ❌ 异常路径下忘记归还
Bullet b = bulletPool.Get();
if (target == null)
{
    b.Explode();  // 炸了就完了，忘记归还
    return;
}

// ✅ 异步生命周期对象在真正结束时从统一出口归还
Bullet b = bulletPool.Get();
if (target == null)
{
    b.Explode();
    bulletPool.Release(b);
    return;
}

b.Fire(target, onFinished: () => bulletPool.Release(b));
```

`onFinished`、碰撞、取消和场景切换必须汇入同一个回收出口，防止漏还或重复归还。`using` 只适合不会逃出当前同步作用域的临时对象。

### 4. 容量设置不当

```csharp
// maxSize 太小 → 归还时直接被 Destroy，池白建了
maxSize: 10;
// 实际 15 颗子弹同时在场 → 多出的 5 颗被销毁而不是回收

// maxSize 太大 → 峰值过后可能长期保留过多空闲对象
maxSize: 1000;
// 设置 maxSize 本身不会预创建对象，但已经创建并归还的对象最多可保留 1000 个
```

### 5. 只停用对象，没有恢复可复用生命周期

把死亡流程从 `Destroy(gameObject)` 改成 `SetActive(false)` 只是让对象进入休眠，并不等于已经完成对象池。再次取出前还必须恢复运行时状态和外部关系。

[Backpack Survivor 第 3 课](../../projects/backpack-survivor/target-registry-and-auto-weapon.md)暴露了一个典型问题：敌人在 `Start` 中订阅死亡事件，在 `Die` 中退订并停用；但 `Start` 每个实例只执行一次，重新启用后不会再次订阅。第 5 课已经在[刷怪器与对象池](../../projects/backpack-survivor/spawner-and-object-pooling.md)中把订阅迁移到 `OnEnable` / `OnDisable`，并使用池化钩子重置生命值与攻击计时。第 8 课要求掉落物磁吸状态机和速度在取出时归零；第 11 课又通过 `XpOrb` 复用问题验证了同一条规则：新增运行期字段后，同一分钟检查 `OnGetFromPool`，否则复用对象会带着旧状态复活。

```text
归还时
  ├─ 注销注册表和事件
  ├─ 停止协程、动画和特效
  └─ 解除外部引用

再次取出时
  ├─ 重置 Health、计时器和目标
  ├─ 恢复激活期订阅
  └─ 设置位置、朝向和新一轮配置
```

池化对象应有明确的 `Initialize` / `ResetForReuse` / `Release` 协议，并通过“死亡 → 归还 → 再次取出 → 再次死亡”的回归测试证明状态闭环。

---

## 何时用 / 何时不用

| ✅ 适合用对象池 | ❌ 不适合用对象池 |
|-------------|---------------|
| 频繁创建/销毁（每帧数次） | 创建一次、长期持有（如玩家对象） |
| 生命周期短（几秒内） | 生命周期长、跨场景（如 Manager） |
| 同类对象数量大（弹幕/粒子） | 类型差异大、各自逻辑复杂 |
| GC 尖峰在 Profiler 中肉眼可见 | Profiler 显示 GC 不是瓶颈 |
| 移动端 / 低端机优先 | Editor 上跑得顺不代表真顺 |

---

## 核心技巧

- 对象池 = 空间换时间 — 用常驻对象降低重复创建和回收压力
- Unity 2021+ 优先用 `UnityEngine.Pool.ObjectPool<T>`，别重复造轮子
- `actionOnGet` 激活，`actionOnRelease` 重置 — 这是池的"开关"
- 开启 `collectionCheck: true` 开发防 Bug，发布后视情况关掉
- `defaultCapacity` 不会预创建对象；预加热需要显式 `Get()` / `Release()`
- `Clear()` 只清理池中的空闲对象，仍在使用的对象必须单独追踪和回收
- 对象池只优化对象生命周期的一部分，协程、集合扩容和业务代码仍可能分配
- 归还前完整重置状态 — 这是最容易出 BUG 的地方

---

> 📎 标签：`对象池` `ObjectPool` `GC优化` `Unity` `UnityEngine.Pool`
