# static 静态

> 属于类型本身，不属于任何一个实例

---

## 一句话理解

| | 实例成员 (Instance) | 静态成员 (Static) |
|------|------|------|
| **属于谁** | 具体的对象 | 类型本身 |
| **内存** | 每个对象各有一份 | 全局只有一份 |
| **访问方式** | `obj.Method()` | `ClassName.Method()` |
| **有 `this` 吗** | ✅ 有 | ❌ 没有 |
| **何时初始化** | `new` 时 | 第一次访问类型时 |

---

## static 能修饰什么

| 修饰目标 | 含义 |
|---------|------|
| `static class` | 不能实例化，只能包含静态成员 |
| `static field` | 所有实例共享同一份数据 |
| `static method` | 不依赖实例，通过类型名调用 |
| `static constructor` | 类型第一次被访问时自动执行，且只执行一次 |
| `static property` | 同静态字段，但带 get/set 逻辑 |

---

## 静态字段：全局共享

```csharp
public class Player
{
    public string name;              // 每个玩家有自己的名字
    public static int playerCount;   // 所有玩家共享同一个计数器
}

// 使用
Player p1 = new Player();
Player.playerCount++;  // 通过类名访问，不通过实例

Player p2 = new Player();
Player.playerCount++;  // p1 和 p2 看到的是同一个值 → 2
```

---

## 静态方法：不依赖实例

```csharp
public class MathHelper
{
    // 静态方法：不需要 new 就能用
    public static float Remap(float value, float fromMin, float fromMax, float toMin, float toMax)
    {
        return (value - fromMin) / (fromMax - fromMin) * (toMax - toMin) + toMin;
    }

    // ❌ 静态方法里不能直接用实例成员
    // public static void Foo() { name = "hello"; }  // 编译错误：没有 this
}

// 调用
float result = MathHelper.Reman(0.5f, 0f, 1f, 0f, 100f);  // → 50
```

---

## 静态构造函数：只跑一次

```csharp
public class ConfigManager
{
    public static Dictionary<string, string> settings;

    // 静态构造函数 — 无参数、无访问修饰符、自动调用
    static ConfigManager()
    {
        settings = new Dictionary<string, string>();
        LoadFromFile();
        Debug.Log("ConfigManager 初始化完成（只跑一次）");
    }

    private static void LoadFromFile()
    {
        // 从配置文件读取...
    }
}

// 第一次访问 ConfigManager.settings 时自动触发静态构造函数
// 之后无论访问多少次都不会再跑
```

---

## 静态类：禁止实例化

```csharp
public static class GameConstants
{
    public const float Gravity = -9.81f;
    public const int MaxPlayers = 4;

    // 全是工具方法
    public static int ToLayerMask(int layer)
    {
        return 1 << layer;
    }
}

// ❌ GameConstants g = new GameConstants();  // 编译错误：不能实例化静态类
// ✅ 直接用
int mask = GameConstants.ToLayerMask(8);
```

---

## Unity 中的常见用法

### 1. 全局配置 / 常量

```csharp
public static class GameConfig
{
    // 玩家设置
    public static float MouseSensitivity = 1f;
    public static float MusicVolume = 0.8f;

    // 游戏参数
    public const int TargetFrameRate = 60;
    public const float DefaultGravity = -9.81f;
}
```

### 2. 单例模式（最常用）

```csharp
public class AudioManager : MonoBehaviour
{
    // 静态引用 → 全局唯一的访问点
    public static AudioManager Instance { get; private set; }

    private void Awake()
    {
        // 单例检查：保证场景中只有一个
        if (Instance != null && Instance != this)
        {
            Destroy(gameObject);
            return;
        }
        Instance = this;
        DontDestroyOnLoad(gameObject);  // 切场景不销毁
    }

    public void PlaySound(string soundName)
    {
        // 播放音效...
    }
}

// 任何脚本里调用
AudioManager.Instance.PlaySound("footstep");
```

### 3. 静态工厂方法

```csharp
public class Enemy
{
    public float health;
    public float speed;

    private Enemy() { }  // 私有构造器，禁止外部 new

    // 静态工厂方法：语义化创建
    public static Enemy CreateMelee()
    {
        return new Enemy { health = 100f, speed = 3f };
    }

    public static Enemy CreateRanged()
    {
        return new Enemy { health = 60f, speed = 1.5f };
    }
}

// 使用
Enemy melee = Enemy.CreateMelee();
Enemy ranged = Enemy.CreateRanged();
```

### 4. 跨场景数据传递

```csharp
public static class GameState
{
    // 切场景时 GameObject 会销毁，但静态数据保留
    public static int currentLevel = 1;
    public static int score = 0;
    public static bool hasKey = false;
}

// 场景 A — 赢了 Boss
GameState.hasKey = true;

// 场景 B — 检查钥匙
if (GameState.hasKey)
{
    // 开门...
}
```

---

## ⚠️ 常见坑

### 1. 静态字段不会自动清理

```csharp
// 离开 Play Mode 再进入，静态字段可能还保留旧值
// 解决方案：用 RuntimeInitializeOnLoadMethod 重置
[RuntimeInitializeOnLoadMethod(RuntimeInitializeLoadType.SubsystemRegistration)]
static void Reset()
{
    GameState.score = 0;
    GameState.hasKey = false;
}
```

### 2. 静态事件 / 回调 → 内存泄漏

```csharp
public class Enemy : MonoBehaviour
{
    // ❌ 静态事件：所有敌人实例监听同一个事件
    public static event Action OnAllEnemiesDied;

    void OnDestroy()
    {
        OnAllEnemiesDied?.Invoke();
        // 如果忘记取消订阅，静态事件会一直持有引用 → GC 无法回收
    }
}
```

**正确做法**：确保 `OnDestroy` 中取消订阅，或避免静态事件。

### 3. 多线程访问静态字段

```csharp
public static int counter;

// 多个线程同时修改 counter → 数据竞争
// 解决方案：lock 或用 Interlocked
Interlocked.Increment(ref counter);
```

---

## 何时用 / 何时不用

| ✅ 适合用 static | ❌ 不适合用 static |
|------|------|
| 工具方法、数学计算 | 需要多态 / 继承的成员 |
| 全局配置、常量 | 需要序列化到 Inspector 的字段 |
| 跨场景的全局状态 | 需要在 Inspector 中拖拽赋值的引用 |
| 单例访问点 | 频繁创建/销毁的对象 |
| 工厂方法 | 需要单元测试 mock 的依赖 |

---

## 核心技巧

- 静态成员属于**类**，实例成员属于**对象** — 这是唯一需要记住的区别
- Unity 中 `MonoBehaviour` 不能用 `new`，所以静态字段+单例是最常见的组合
- 静态数据在 Play Mode 停止后可能残留 → 加 `RuntimeInitializeOnLoadMethod` 重置
- 能用 `const` 就用 `const`（编译期常量），其次 `static readonly`（运行期常量）

---

> 📎 标签：`static` `单例` `内存模型` `Unity`
