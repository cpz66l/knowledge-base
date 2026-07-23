# 委托与事件

> 让方法像变量一样传递 — 用委托解耦调用，用事件安全广播

---

## 一句话理解

| | 委托 (Delegate) | 事件 (Event) |
|------|------|------|
| **本质** | 类型安全的函数指针 — 把方法当作参数传递 | 对委托的封装 — 只允许外部"订阅/取消"，禁止外部"触发" |
| **谁定义** | 任意代码 | 定义在发布者（Publisher）内部 |
| **谁调用** | 持有委托引用的代码都可以 `Invoke()` | **只有发布者自己**可以触发 |
| **谁订阅** | 任意代码 `+=` | 订阅者 `+=`，订阅者 `-=` |
| **类比** | 电话号码（谁拿到都能打） | 广播频道（只有电台能广播，听众只能调频） |

```csharp
// 委托 — 类型安全的函数指针
public delegate void MyDelegate(string msg);
MyDelegate d = Console.WriteLine;
d("hello");  // 调用 Console.WriteLine("hello")

// 事件 — 封装的委托，外部只能 += / -=
public event Action<string> OnMessage;
OnMessage += Console.WriteLine;
// OnMessage("hello");  // ❌ 外部类不能触发事件
```

---

## 委托基础

### 自定义委托

```csharp
// 声明委托类型 — 定义签名（返回值 + 参数列表）
public delegate int Operation(int a, int b);

// 实例化 — 指向签名匹配的任何方法
Operation op = Add;
op += Subtract;  // 多播委托：一个委托链多个方法

int result = op(10, 5);  // 先调 Add（返回 15），再调 Subtract（返回 5）
                          // 只返回最后一个结果 → 5

int Add(int a, int b) => a + b;
int Subtract(int a, int b) => a - b;
```

> ⚠️ 多播委托有返回值时，只保留最后一个方法的返回值。需要逐个获取返回值时用 `GetInvocationList()`。

### 内置委托：Action / Func / Predicate

日常开发中几乎不需要自定义委托，内置的已覆盖绝大多数场景：

| 委托 | 签名 | 用途 |
|------|------|------|
| `Action` | `void()` | 无参无返回值 |
| `Action<T>` | `void(T)` | 有参无返回值 |
| `Action<T1,T2,...>` | `void(T1,T2,...)` | 最多 16 个参数 |
| `Func<TResult>` | `TResult()` | 无参有返回值 |
| `Func<T, TResult>` | `TResult(T)` | 有参有返回值 |
| `Func<T1,T2,...,TResult>` | `TResult(T1,T2,...)` | 最多 16 个参数 + 返回值 |
| `Predicate<T>` | `bool(T)` | 判断条件，等价 `Func<T, bool>` |

```csharp
// 选择适合的就行了，无需自定义 delegate
Action<string> log = msg => Debug.Log(msg);
Func<int, int, int> add = (a, b) => a + b;
Predicate<int> isPositive = n => n > 0;

log("hello");           // → Debug.Log("hello")
int sum = add(3, 5);    // → 8
bool ok = isPositive(3); // → true
```

### Lambda 表达式

Lambda 是给委托赋值的快捷方式：

```csharp
// 完整写法
Action<int> f1 = (int x) => { Debug.Log(x); };

// 省略类型（编译器自动推断）
Action<int> f2 = (x) => { Debug.Log(x); };

// 单参数省略括号
Action<int> f3 = x => Debug.Log(x);

// 有返回值 — 单表达式省略 return 和大括号
Func<int, int, int> add = (a, b) => a + b;
```

### 闭包 — Lambda 捕获外部变量

```csharp
int counter = 0;
Action increment = () => counter++;  // Lambda 捕获了 counter 变量

increment();
increment();
Debug.Log(counter);  // → 2 — 变量被"包"进了委托
```

> ⚠️ 闭包会延长被捕获变量的生命周期，注意 Unity 中 `MonoBehaviour` 字段被捕获后可能引发意外行为。

---

## 事件

### event 关键字

事件本质是委托 + 访问限制 — 对外只暴露 `+=` 和 `-=`：

```csharp
public class Player
{
    private int hp;

    // 公开事件：外部可以订阅/取消，但不能触发
    public event Action<int> OnHpChanged;

    // 属性封装修改，修改时自动触发事件
    public int Hp
    {
        get => hp;
        set
        {
            hp = value;
            OnHpChanged?.Invoke(hp);  // 只有 Player 自己能触发
        }
    }
}

// 使用
Player p = new Player();
p.OnHpChanged += hp => Debug.Log($"HP changed to {hp}");
// p.OnHpChanged.Invoke(50);  // ❌ 编译错误：外部不能触发事件
```

### EventHandler 模式

.NET 标准事件模式，WinForm / WPF 常用：

```csharp
public class PlayerEventArgs : EventArgs
{
    public int CurrentHp { get; set; }
    public int MaxHp { get; set; }
}

public class Player
{
    // EventHandler<T> → void(object sender, T args)
    public event EventHandler<PlayerEventArgs> OnHpChanged;

    protected virtual void OnHpChangedEvent(PlayerEventArgs args)
    {
        OnHpChanged?.Invoke(this, args);  // 约定：sender = this
    }
}
```

Unity 开发中更倾向用 `Action<T>` — 比 `EventHandler` 少写一个 `EventArgs` 子类（除非需要遵循 .NET 标准库规范）。

> **`?.Invoke()` 是线程安全的吗？** 不完全是 — `?.` 保证了 null 检查不抛异常，但如果在 `?.` 之后另一个线程取消了订阅，仍可能触发已取消的方法。但 Unity 大部分代码在主线程执行，这个问题很少遇到。

---

## Unity 实战案例

### 1. UnityEvent — 编辑器可视化事件

`UnityEvent` 是 Unity 对事件的封装，**可以在 Inspector 中拖拽绑定**：

```csharp
using UnityEngine;
using UnityEngine.Events;

public class HealthBarUI : MonoBehaviour
{
    [SerializeField] private UnityEvent<float> onHealthChanged;
    // 在 Inspector 中可以直接拖 Slider 的 SetValue 方法进来
    // 策划/美术也能绑定，不依赖代码

    public void UpdateHealth(float percentage)
    {
        onHealthChanged.Invoke(percentage);
    }
}
```

| | `UnityEvent` | C# `event` |
|------|------|------|
| **Inspector 绑定** | ✅ | ❌ |
| **性能** | 较慢（有序列化开销） | 快 |
| **适用场景** | 编辑器配置、策划调整 | 纯代码逻辑 |

> **选择建议**：需要策划/美术在 Inspector 中配置时用 `UnityEvent`；纯代码内部逻辑用 C# `event`（更快更轻量）。

### 2. 自定义游戏事件 — 解耦模块

没有事件时，所有模块互相持有引用 → 强耦合；用事件后，各模块只关心"发生了什么"，不关心"谁处理"：

```csharp
// ❌ 没有事件 — UI 需要持有玩家的引用才能更新
public class PlayerUI : MonoBehaviour
{
    public Player player;  // 拖拽绑定，强耦合

    void Update()
    {
        hpText.text = player.Hp.ToString();  // 每帧轮询
    }
}

// ✅ 用事件 — UI 只订阅事件，不依赖 Player 类型
public class PlayerUI : MonoBehaviour
{
    void Start()
    {
        // 订阅 — 玩家血量变化时自动更新
        EventBus.Subscribe<PlayerHpChangedEvent>(OnPlayerHpChanged);
    }

    void OnDestroy()
    {
        EventBus.Unsubscribe<PlayerHpChangedEvent>(OnPlayerHpChanged);
    }

    void OnPlayerHpChanged(PlayerHpChangedEvent e)
    {
        hpText.text = e.currentHp.ToString();
    }
}
```

### 3. 典型游戏事件示例

```csharp
// 事件数据类型 — 用 struct 避免堆分配
public struct EnemyDiedEvent
{
    public int enemyId;
    public Vector3 position;
    public int expReward;
}

public struct ScoreChangedEvent
{
    public int newScore;
    public int delta;
}

public struct GameStateEvent
{
    public GameState from;
    public GameState to;  // Playing → Paused / GameOver / Victory
}
public enum GameState { Playing, Paused, GameOver, Victory }

// 发布事件
public class Enemy : MonoBehaviour
{
    private void OnDestroy()
    {
        EventBus.Publish(new EnemyDiedEvent
        {
            enemyId = GetInstanceID(),
            position = transform.position,
            expReward = 10
        });
    }
}

// 不同模块各自订阅自己关心的
public class QuestManager : MonoBehaviour
{
    void Start() => EventBus.Subscribe<EnemyDiedEvent>(OnEnemyDied);
    void OnDestroy() => EventBus.Unsubscribe<EnemyDiedEvent>(OnEnemyDied);

    void OnEnemyDied(EnemyDiedEvent e)
    {
        // 检查击杀任务进度...
    }
}

public class ScoreManager : MonoBehaviour
{
    void Start() => EventBus.Subscribe<EnemyDiedEvent>(OnEnemyDied);
    void OnDestroy() => EventBus.Unsubscribe<EnemyDiedEvent>(OnEnemyDied);

    void OnEnemyDied(EnemyDiedEvent e)
    {
        EventBus.Publish(new ScoreChangedEvent
        {
            newScore = currentScore + e.expReward,
            delta = e.expReward
        });
    }
}
```

### 4. 回调委托 — 动画结束、异步加载完成

```csharp
// 异步加载场景，完成后回调
public void LoadSceneAsync(string sceneName, Action onComplete = null)
{
    StartCoroutine(LoadRoutine());

    IEnumerator LoadRoutine()
    {
        AsyncOperation op = SceneManager.LoadSceneAsync(sceneName);
        while (!op.isDone)
            yield return null;

        onComplete?.Invoke();  // 场景加载完成，执行回调
    }
}

// 调用
LoadSceneAsync("Battle", () =>
{
    Debug.Log("战场场景加载完成");
    UIManager.Instance.ShowPanel("battle_ui");
});


// DoTween 风格 — 动画完成回调
transform.DOMove(target, 1f).OnComplete(() =>
{
    Debug.Log("移动完成");
    // 可以链式触发下一个动画
});
```

### 5. 链式条件判断 — 委托组合

```csharp
// 成就系统 — 用 Func<bool> 组合多个条件
public class AchievementSystem : MonoBehaviour
{
    // 多个解锁条件用委托表示
    public static Func<bool> Level3Unlocked;
    public static Func<bool> HasKey;
    public static Func<bool> SecretBossDefeated;

    public bool CanEnterSecretLevel()
    {
        // 三个条件都满足才开门
        return Level3Unlocked?.Invoke() == true
            && HasKey?.Invoke() == true
            && SecretBossDefeated?.Invoke() == true;
    }
}
```

### 6. 项目案例：Health 发布事件，EnemyAI 订阅死亡

[Backpack Survivor 的伤害管线](../../projects/backpack-survivor/damage-pipeline-and-hazard-zone.md)中，`Health` 只维护生命值并发布状态变化：

```csharp
public event Action<DamageInfo> OnDamaged;
public event Action OnDeath;

OnDamaged?.Invoke(info);

if (currentHp <= 0f)
{
    OnDeath?.Invoke();
}
```

这让血条、受击表现、掉落和任务系统不必由 `Health` 直接持有引用。

[敌人追击、近战与死亡流程](../../projects/backpack-survivor/enemy-ai-and-melee.md)随后加入了实际订阅者：`EnemyAI` 订阅自身 `Health.OnDeath`，死亡时退订并销毁对象。对于“一次创建、死亡后销毁”的对象，这形成了最小闭环。

第 3 课把死亡改成 `SetActive(false)` 后验证了一个更重要的边界：如果只在 `Start` 订阅、在 `Die` 退订，那么对象再次启用时 `Start` 不会重跑，死亡处理不会恢复。第 5 课已将死亡订阅迁移到 `OnEnable` / `OnDisable`，并在池化取出时重置 `Health`，让订阅生命周期与激活期匹配。第 7 课进一步把掉落接到 `Die()`，并明确掉落只属于死亡事件，不属于 `OnReturnPool()`；否则一次死亡可能触发两次掉落。详见[目标注册表、自动武器与投射物](../../projects/backpack-survivor/target-registry-and-auto-weapon.md)、[刷怪器与对象池](../../projects/backpack-survivor/spawner-and-object-pooling.md)、[掉落系统与保底机制](../../projects/backpack-survivor/loot-drop-and-pity.md)和[Unity 生命周期](../../unity/lifecycle.md)。

---

## 委托 vs 事件 vs 接口 vs UnityEvent

| | 委托 (Delegate) | 事件 (Event) | 接口 (Interface) | UnityEvent |
|------|------|------|------|------|
| **核心作用** | 传递方法（回调） | 发布-订阅广播 | 定义行为契约 | Inspector 绑定 |
| **谁触发** | 任何持有者 | 仅发布者 | 调用方 | 任意代码或 UI |
| **多播** | ✅ `+=` | ✅ `+=` | ❌ 单实现 | ✅ `AddListener` |
| **解耦程度** | 中等 | 高 | 中高 | 中 |
| **Inspector 可见** | ❌ | ❌ | ❌ | ✅ |
| **性能** | 最快 | 快 | 快 | 慢（序列化） |
| **典型场景** | 回调、LINQ、排序 | 状态变化广播 | 策略/插件模式 | 编辑器事件配置 |

> **选择建议**：
> - 一个回调，一对一 → **委托**（`Action` / `Func`）
> - 一对多广播，状态变化通知 → **C# `event` 或事件总线**
> - 需要在 Inspector 中绑定 → **UnityEvent**
> - 多态行为，多种实现 → **接口**

---

## ⚠️ 常见坑

### 1. 忘记取消订阅 → 内存泄漏（头号杀手）

```csharp
public class EnemyUI : MonoBehaviour
{
    void Start()
    {
        // ❌ 订阅了事件，但 OnDestroy 时忘记取消
        Player.Instance.OnHpChanged += UpdateHpBar;
    }

    // EnemyUI 销毁后，Player 的事件链仍持有 UpdateHpBar 引用
    // → EnemyUI 对象无法被 GC → 内存泄漏
}

// ✅ 正确做法
public class EnemyUI : MonoBehaviour
{
    void OnEnable()  => Player.Instance.OnHpChanged += UpdateHpBar;
    void OnDisable() => Player.Instance.OnHpChanged -= UpdateHpBar;
    // 或用 Start + OnDestroy，但要保证配对
}
```

> **原则**：`+=` 和 `-=` 必须成对出现。推荐在 `OnEnable`/`OnDisable` 中订阅/取消（对象禁用时也能正确解绑）。

### 2. Null 检查的细微差别

```csharp
// ✅ 推荐 — C# 6+ 的 ?. 是原子操作，不会抛 NullReferenceException
OnHpChanged?.Invoke(hp);

// ⚠️ 有隐患 — 在检查后、调用前，事件可能被另一线程设为 null
if (OnHpChanged != null)
    OnHpChanged(hp);

// ✅ 传统线程安全写法（极少需要）
var handler = OnHpChanged;
if (handler != null)
    handler(hp);
```

Unity 主线程场景下直接用 `?.Invoke()` 即可。

### 3. UnityEvent 比 C# event 慢

```csharp
// ❌ 热路径上用 UnityEvent（每帧调用的 Update 等）
public UnityEvent onUpdate;  // 每帧触发有序列化开销

// ✅ 热路径用 C# event
public event Action onUpdate;  // 纯托管代码，开销极低
```

### 4. Lambda 取消订阅失效

```csharp
// ❌ Lambda 每次都是新对象 — 取消订阅无效！
button.onClick.AddListener(() => Debug.Log("clicked"));
button.onClick.RemoveListener(() => Debug.Log("clicked"));  // 移除的是另一个对象！

// ✅ 先保存引用
UnityAction handler = () => Debug.Log("clicked");
button.onClick.AddListener(handler);
button.onClick.RemoveListener(handler);
```

### 5. 事件引起的循环依赖

```csharp
// A 订阅 B 的事件，B 的处理又触发 A 的事件 → 死循环
public class A
{
    void OnBChanged() { EventBus.Publish(new AChangedEvent()); }
}
public class B
{
    void OnAChanged() { EventBus.Publish(new BChangedEvent()); }
}
// A ⇄ B 无限循环 → 栈溢出
```

> **解决方案**：加 `isProcessing` 标记防止重入，或在设计上避免双向事件触发。

---

## 何时用 / 何时不用

| ✅ 适合用委托/事件 | ❌ 不适合用委托/事件 |
|------|------|
| 状态变化广播（HP、分数、状态机） | 简单的父子组件通信（直接引用更清晰） |
| 模块间解耦（任务系统、成就系统） | 每帧调用的逻辑（直接调用，避免委托开销） |
| 回调通知（加载完成、动画结束） | 严格的调用顺序要求（事件无法保证订阅者执行顺序） |
| 可配置的逻辑（排序规则、筛选条件） | 需要返回值的广播（考虑用 `Func` 或迭代） |
| Inspector 可配置的响应（`UnityEvent`） | 一个发布者 + 一个订阅者（过度设计，直接引用即可） |

---

## 核心技巧

- **委托 = 把方法当变量传递**。`Action`（无返回值）、`Func`（有返回值）、`Predicate`（bool）覆盖绝大多数场景
- **事件 = 安全的委托广播**。`event` 关键字禁止外部触发，强制发布者掌控触发权
- **`?.Invoke()` 代替 null 检查** — 安全、简洁，Unity 主线程场景够用
- **`+=` 和 `-=` 必须配对** — 在 `OnEnable`/`OnDisable` 或 `Start`/`OnDestroy` 中成对出现
- **Lambda 取消订阅时注意** — 匿名 Lambda 每次创建新对象，无法移除（先保存为变量）
- **热路径上避免 UnityEvent** — 用 C# `event` 或 `Action` 替代
- **事件数据类型优先用 struct** — 避免每次 `Publish` 产生堆分配

---

> 📎 标签：`委托` `事件` `delegate` `event` `Action` `Func` `UnityEvent` `解耦` `观察者模式`

> 📖 通用事件总线实现见 [泛型 — 泛型事件总线](generics.md)
