# 对象池

> 复用而非销毁 — 用对象池消除 GC 尖峰

---

## 一句话理解

```
没有对象池：          有对象池：
创建 → 使用 → 销毁    取出 → 使用 → 归还
创建 → 使用 → 销毁    取出 → 使用 → 归还
创建 → 使用 → 销毁    取出 → 使用 → 归还
  ↑ GC 尖峰              ↑ 零分配，零 GC
```

池子 = 预先创建一批对象存起来，用完放回去而不是销毁。本质是**用空间（预占内存）换时间（消除 GC 卡顿）**。

---

## 为什么需要对象池

### GC 尖峰是怎么产生的

```csharp
// ❌ 每一帧都在堆上分配 + 销毁 → GC 频繁触发
void Update()
{
    // Instantiate 在堆上分配内存
    GameObject bullet = Instantiate(bulletPrefab, transform.position, Quaternion.identity);
    // 子弹飞出屏幕后 Destroy → 产生待回收垃圾
    Destroy(bullet, 3f);
}
```

当一帧内有大量 Instantiate/Destroy 时，堆内存快速碎片化，GC 被迫运行，造成**帧时间尖峰**（从 2ms 飙到 50ms+），玩家感知为画面卡顿。

```csharp
// ✅ 对象池方案：只在初始化时分配，运行时零分配
private ObjectPool<GameObject> bulletPool;

void Start()
{
    // 初始化时一次性创建 20 颗子弹
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
        GameObject bullet = bulletPool.Get();       // 取出（零分配）
        bullet.transform.position = transform.position;
        StartCoroutine(ReturnAfterDelay(bullet, 3f));
    }
}

IEnumerator ReturnAfterDelay(GameObject obj, float delay)
{
    yield return new WaitForSeconds(delay);
    bulletPool.Release(obj);                        // 归还（零分配）
}
```

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
| `Clear()` | 清空池中所有对象，真正的 Destroy | 场景切换/不再需要池时 |

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

最通用的池，T 可以是任何类型：

```csharp
using UnityEngine.Pool;

// 创建池 — 传入四个关键委托
ObjectPool<Bullet> bulletPool = new ObjectPool<Bullet>(
    createFunc:       () => Instantiate(bulletPrefab).GetComponent<Bullet>(),  // 创建新对象
    actionOnGet:      (b) => b.gameObject.SetActive(true),                      // 取出时激活
    actionOnRelease:  (b) => b.gameObject.SetActive(false),                     // 归还时隐藏
    actionOnDestroy:  (b) => Destroy(b.gameObject),                             // 超出容量时真销毁
    collectionCheck:  true,   // 开启重复归还检测（开发期建议开）
    defaultCapacity:  10,     // 预分配容量
    maxSize:          50      // 最大容量上限
);

// 使用
Bullet b = bulletPool.Get();    // 取出
bulletPool.Release(b);          // 归还
bulletPool.Clear();             // 清空（场景切换时）
```

### IObjectPool<T> 接口

```csharp
// 接口注入 — 方便在类之间传递池而不暴露具体实现
public class Gun
{
    // 不依赖具体池类型，方便测试时替换
    public IObjectPool<Bullet> BulletPool { get; set; }

    public void Fire()
    {
        Bullet b = BulletPool.Get();
        // ...
    }
}
```

### PooledObject 模式（IDisposable）

用 `using` 自动归还，不怕忘记调用 Release：

```csharp
// Get() 返回 PooledObject<T>，用 using 包裹
public class BulletPoolWrapper
{
    private ObjectPool<Bullet> pool = ...;

    public PooledObject<Bullet> Get(out Bullet bullet)
    {
        return pool.Get(out bullet);  // 返回 IDisposable 包装
    }
}

// 使用 — using 结束时自动 Release
var wrapper = new BulletPoolWrapper();
using (wrapper.Get(out Bullet bullet))
{
    bullet.transform.position = firePoint.position;
    bullet.Fire();  // 子弹飞出...
} // ← using 结束，自动调用 bulletPool.Release(bullet)
```

### GenericPool<T> / UnsafeGenericPool<T>

如果 T 不需要特殊的创建/销毁逻辑，可以用更轻量的静态池：

```csharp
// GenericPool — 需要 T 有默认构造函数
List<Vector3> points = GenericPool<List<Vector3>>.Get();
// ... 使用 ...
GenericPool<List<Vector3>>.Release(points);

// UnsafeGenericPool — 更快，但跳过 CollectionCheck
// 只在 Release 完全由你控制时使用
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

### 2. 纯 C# 对象池（不涉及 GameObject）

```csharp
// 适合 List、StringBuilder、网络消息包等非 MonoBehaviour 对象
public class ListPool<T>
{
    private static Stack<List<T>> pool = new Stack<List<T>>();

    public static List<T> Get()
    {
        if (pool.Count > 0)
        {
            List<T> list = pool.Pop();
            list.Clear();  // ⚠️ 归还前清空旧数据
            return list;
        }
        return new List<T>();
    }

    public static void Release(List<T> list)
    {
        list.Clear();
        pool.Push(list);
    }
}

// 使用
List<Vector3> temp = ListPool<Vector3>.Get();
// ... 临时计算 ...
ListPool<Vector3>.Release(temp);  // 放回去，下回再用
```

### 3. 预加热策略

```csharp
// 场景加载时预加热常用池，避免运行时首次 Get 的创建开销
public class PoolManager : MonoBehaviour
{
    public Bullet bulletPrefab;
    public Explosion explosionPrefab;

    private void Awake()
    {
        // 在场景开始时预创建，确保战斗中零分配
        Bullet.Pool = new ObjectPool<Bullet>(
            createFunc: () => Instantiate(bulletPrefab).GetComponent<Bullet>(),
            actionOnGet: (b) => b.gameObject.SetActive(true),
            actionOnRelease: (b) => b.gameObject.SetActive(false),
            actionOnDestroy: (b) => Destroy(b.gameObject),
            defaultCapacity: 30,     // 预创建 30 颗子弹
            maxSize: 80
        );

        // 强制立即预创建 — 多出来的开销在加载画面消化掉
        List<Bullet> preWarm = new List<Bullet>();
        for (int i = 0; i < 30; i++)
            preWarm.Add(Bullet.Pool.Get());
        foreach (var b in preWarm)
            Bullet.Pool.Release(b);
    }
}
```

### 4. 固定容量 vs 动态扩容

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
1. 先不加 maxSize，跑几场战斗，用 Profiler 看峰值
2. maxSize 设为峰值的 1.2~1.5 倍
3. defaultCapacity 设为常见场景的并发数
4. 后续用 Profiler 验证池内对象数是否稳定
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

### 3. 只取不还（泄漏）

```csharp
// ❌ 异常路径下忘记归还
Bullet b = bulletPool.Get();
if (target == null)
{
    b.Explode();  // 炸了就完了，忘记归还
    return;
}

// ✅ using 模式：自动归还
using (bulletPool.Get(out Bullet b))
{
    if (target == null)
    {
        b.Explode();
        return;                     // early return 也会自动 Release
    }
    b.Fire(target);
}  // ← 出了 using 块，自动归还
```

### 4. 容量设置不当

```csharp
// maxSize 太小 → 归还时直接被 Destroy，池白建了
maxSize: 10;
// 实际 15 颗子弹同时在场 → 多出的 5 颗被销毁而不是回收

// maxSize 太大 → 内存占用过高
maxSize: 1000;
// 实际只要 20 颗 → 顶峰时 1000 颗子弹预留在内存里
```

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

- 对象池 = 空间换时间 — 用预分配内存换取零 GC 运行时
- Unity 2021+ 优先用 `UnityEngine.Pool.ObjectPool<T>`，别重复造轮子
- `actionOnGet` 激活，`actionOnRelease` 重置 — 这是池的"开关"
- 开启 `collectionCheck: true` 开发防 Bug，发布后视情况关掉
- 预加热在场景加载时做，战斗中零分配
- 场景切换时 `Clear()`，避免池对象跨场景残留
- 归还前完整重置状态 — 这是最容易出 BUG 的地方

---

> 📎 标签：`对象池` `ObjectPool` `GC优化` `Unity` `UnityEngine.Pool`
