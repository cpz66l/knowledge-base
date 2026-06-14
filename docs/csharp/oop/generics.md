# 泛型

> 用类型参数写出类型安全、可复用的代码 — 告别 `object` 和装箱拆箱

---

## 一句话理解

```csharp
// 没有泛型 — 用 object 凑合，类型不安全，有装箱开销
ArrayList list = new ArrayList();
list.Add(1);
list.Add("hello");       // 编译通过，运行时可能炸
int value = (int)list[0]; // 强制转型，烦人

// 有泛型 — 编译期就确定类型，安全、高效
List<int> list = new List<int>();
list.Add(1);
// list.Add("hello");    // ❌ 编译错误，直接拦住
int value = list[0];     // 无需转型
```

泛型的核心思想：**把类型当作参数传递**。写代码时用 `T` 占位，使用时指定具体类型。

---

## 泛型方法

### 基本语法

```csharp
// 方法名后加 <T>，T 可以在参数和返回值中使用
public T GetFirst<T>(List<T> list)
{
    if (list.Count == 0)
        return default(T);  // T 的默认值（int→0, 引用类型→null）
    return list[0];
}

// 调用
List<int> numbers = new List<int> { 1, 2, 3 };
int first = GetFirst<int>(numbers);   // 1 — 显式指定类型
int first2 = GetFirst(numbers);       // 1 — 编译器自动推断
```

### Unity 实用例子

```csharp
随机抽取数组中的一个元素
public T RandomElement<T>(T[] array)
{
    if (array == null || array.Length == 0)
        return default;
    int index = Random.Range(0, array.Length);
    return array[index];
}

// 使用 — 同一个方法，处理任意类型
string[] names = { "Alice", "Bob", "Charlie" };
string lucky = RandomElement(names);  // 随机一个名字

GameObject[] enemies = { ... };
GameObject target = RandomElement(enemies);  // 随机一个敌人
```

---

## 泛型类

### 基本语法

```csharp
// 类名后加 <T>，T 在整个类中可用
public class Pair<T>
{
    public T first;
    public T second;

    public Pair(T first, T second)
    {
        this.first = first;
        this.second = second;
    }

    public void Swap()
    {
        T temp = first;
        first = second;
        second = temp;
    }
}

// 使用
Pair<string> names = new Pair<string>("Alice", "Bob");
names.Swap();  // first="Bob", second="Alice"

Pair<int> scores = new Pair<int>(100, 200);
scores.Swap(); // first=200, second=100
```

---

## 泛型约束（`where T : ...`）

这是泛型最强大的部分——限制 `T` 能是什么类型，然后你就可以安全地调用该类型的方法。

| 约束 | 含义 | 示例用途 |
|------|------|----------|
| `where T : class` | T 必须是引用类型 | 限定为 class 以进行 null 检查 |
| `where T : struct` | T 必须是值类型 | 限定为 struct，Nullable<T> 的实现 |
| `where T : new()` | T 必须有公共无参构造函数 | 方法内部 `new T()` 创建实例 |
| `where T : BaseClass` | T 必须继承自某基类 | 限定为 Enemy 子类，调用 Enemy 的方法 |
| `where T : IInterface` | T 必须实现某接口 | 限定为 `IComparable`，在排序方法中比较 |
| `where T : unmanaged` | T 必须是非托管类型 | 配合 `fixed` / 指针使用 |

### 组合约束

```csharp
多个约束用逗号分隔
T 必须是 MonoBehaviour 子类 AND 有 new()
public class ObjectPool<T> where T : MonoBehaviour, new()
{
    // ...
}
```

---

## Unity 实战示例

### 1. 泛型单例基类

不用泛型时，每个 Manager 都要写一遍单例逻辑。用泛型一次写完：

```csharp
public class SingletonMono<T> : MonoBehaviour where T : MonoBehaviour
{
    public static T Instance { get; private set; }

    protected virtual void Awake()
    {
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this as T;
        DontDestroyOnLoad(gameObject);
    }
}

// 使用 — 一行搞定
public class AudioManager : SingletonMono<AudioManager>
{
    public void PlaySound(string name) { /* ... */ }
}

public class UIManager : SingletonMono<UIManager>
{
    public void ShowPanel(string name) { /* ... */ }
}

// 调用
AudioManager.Instance.PlaySound("click");
UIManager.Instance.ShowPanel("settings");
```

### 2. 泛型对象池

```csharp
public class ObjectPool<T> where T : MonoBehaviour
{
    private T prefab;
    private Queue<T> pool = new Queue<T>();

    public ObjectPool(T prefab, int initialSize)
    {
        this.prefab = prefab;
        for (int i = 0; i < initialSize; i++)
        {
            T obj = Object.Instantiate(prefab);
            obj.gameObject.SetActive(false);
            pool.Enqueue(obj);
        }
    }

    public T Get()
    {
        T obj = pool.Count > 0 ? pool.Dequeue() : Object.Instantiate(prefab);
        obj.gameObject.SetActive(true);
        return obj;
    }

    public void Return(T obj)
    {
        obj.gameObject.SetActive(false);
        pool.Enqueue(obj);
    }
}

// 使用
ObjectPool<Bullet> bulletPool = new ObjectPool<Bullet>(bulletPrefab, 20);
Bullet b = bulletPool.Get();   // 拿出一个子弹，类型安全
bulletPool.Return(b);          // 归还
```

### 3. 泛型事件总线

```csharp
public static class EventBus
{
    private static Dictionary<Type, Delegate> events = new Dictionary<Type, Delegate>();

    public static void Subscribe<T>(Action<T> handler) where T : struct
    {
        Type key = typeof(T);
        if (events.ContainsKey(key))
            events[key] = Delegate.Combine(events[key], handler);
        else
            events[key] = handler;
    }

    public static void Unsubscribe<T>(Action<T> handler) where T : struct
    {
        Type key = typeof(T);
        if (events.ContainsKey(key))
            events[key] = Delegate.Remove(events[key], handler);
    }

    public static void Publish<T>(T args) where T : struct
    {
        Type key = typeof(T);
        if (events.TryGetValue(key, out Delegate del))
            (del as Action<T>)?.Invoke(args);
    }
}

// 定义事件数据类型
public struct EnemyDiedEvent
{
    public int enemyId;
    public Vector3 position;
}

// 使用
EventBus.Subscribe<EnemyDiedEvent>(OnEnemyDied);
EventBus.Publish(new EnemyDiedEvent { enemyId = 5, position = Vector3.zero });
```

### 4. 泛型 SaveData 包装器

```csharp
[System.Serializable]
public class SaveData<T>
{
    public T data;
    public long timestamp;
    public int version;

    public SaveData(T data, int version = 1)
    {
        this.data = data;
        this.timestamp = System.DateTimeOffset.UtcNow.ToUnixTimeSeconds();
        this.version = version;
    }

    public string ToJson()
    {
        return JsonUtility.ToJson(this);
    }

    public static SaveData<T> FromJson(string json)
    {
        return JsonUtility.FromJson<SaveData<T>>(json);
    }
}

// 使用 — 同一个类，存任意类型
SaveData<PlayerStats> playerSave = new SaveData<PlayerStats>(new PlayerStats { hp = 100 });
SaveData<GameSettings> settingsSave = new SaveData<GameSettings>(new GameSettings { volume = 0.8f });

string json = playerSave.ToJson();
SaveData<PlayerStats> loaded = SaveData<PlayerStats>.FromJson(json);
```

---

## 协变（`out`）与逆变（`in`）

只在接口和委托上使用，解决泛型类型的赋值兼容问题。

```csharp
// 协变 out — 泛型类型只能出现在返回值位置
// 效果：IEnumerable<Cat> 可以赋值给 IEnumerable<Animal>
public interface IReadOnlyList<out T>
{
    T Get(int index);
}

IReadOnlyList<string> strings = ...;
IReadOnlyList<object> objects = strings;  // ✅ 协变允许

// 逆变 in — 泛型类型只能出现在参数位置
// 效果：IComparer<Animal> 可以赋值给 IComparer<Cat>
public interface IComparer<in T>
{
    int Compare(T a, T b);
}

IComparer<object> objectComparer = ...;
IComparer<string> stringComparer = objectComparer;  // ✅ 逆变允许
```

> Unity 日常开发中很少需要自定义协变/逆变接口，理解内置的 `IEnumerable<T>`、`Action<T>`、`Func<T>` 的行为即可。

---

## 泛型 vs object 性能

```csharp
// ❌ object 方案 — 每次访问都要装箱/拆箱
ArrayList list = new ArrayList();
list.Add(42);              // 装箱：int → object（堆分配）
int value = (int)list[0];  // 拆箱：object → int

// ✅ 泛型方案 — 零装箱，类型安全
List<int> list = new List<int>();
list.Add(42);              // 直接存 int，无装箱
int value = list[0];       // 直接取 int，无拆箱
```

---

## ⚠️ 常见坑

### 1. `default(T)` 的行为因类型而异

```csharp
public T GetDefault<T>()
{
    return default(T);  // 值类型→0/false, 引用类型→null
}

int i = GetDefault<int>();          // 0
bool b = GetDefault<bool>();        // false
string s = GetDefault<string>();    // null — 注意判空！
```

### 2. 泛型 + Unity 序列化的限制

```csharp
// ❌ Unity 无法序列化泛型字段
public class MyBehaviour : MonoBehaviour
{
    public List<SomeGenericClass<int>> data;  // 嵌套泛型也可能有问题
}

// ✅ 用具体类型包装
[System.Serializable]
public class IntList : List<int> { }  // 继承泛型并固化类型参数

public class MyBehaviour : MonoBehaviour
{
    public IntList data;  // 可以在 Inspector 显示了
}
```

### 3. 泛型方法不能是 `extern`

```csharp
// ❌ 编译错误
[DllImport("native.dll")]
public static extern T Foo<T>();

// ✅ 为每种类型写具体的 extern 方法
```

---

## 常用内置泛型

| 类型 | 非泛型替代 | 用途 |
|------|-----------|------|
| `List<T>` | `ArrayList` | 动态数组 |
| `Dictionary<K,V>` | `Hashtable` | 键值对 |
| `Queue<T>` | `Queue` | 先进先出 |
| `Stack<T>` | `Stack` | 后进先出 |
| `HashSet<T>` | — | 不重复集合 |
| `Action<T>` | 自定义 delegate | 无返回值委托 |
| `Func<T,R>` | 自定义 delegate | 有返回值委托 |
| `Nullable<T>` | — | 值类型可空（语法糖 `T?`） |

---

## 何时用 / 何时不用

| ✅ 适合用泛型 | ❌ 不适合用泛型 |
|-------------|---------------|
| 工具类/工具方法（对象池、单例、随机） | 逻辑因类型差异巨大（用重载或接口） |
| 容器/集合（List、Dictionary） | 需要 Unity 序列化到 Inspector |
| 算法不依赖具体类型（排序、搜索） | 类型参数超过 3 个（可读性差） |
| 减少重复代码（多个 Manager 的单例模式） | 性能极端敏感的热路径（极少见） |

---

## 核心技巧

- 泛型 = 类型参数，编译时确定类型，零装箱
- `where T : ...` 约束让泛型从"万能"变"可控" — 能调方法、能 `new`、能判 null
- 泛型单例基类是减少重复代码的经典用法
- `out`（协变）和 `in`（逆变）只用于接口/委托，日常开发了解即可
- Unity 中泛型类不能直接序列化到 Inspector — 用具体子类包装

---

> 📎 标签：`泛型` `generics` `类型参数` `约束` `Unity`
