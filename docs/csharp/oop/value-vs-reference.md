# 值类型 vs 引用类型

> Unity C# 中最基础但也最容易踩坑的概念之一

---

## 一句话区分

| | 值类型 (Value Type) | 引用类型 (Reference Type) |
|------|------|------|
| **存储方式** | 数据通常内联存放在变量、字段或数组元素中；具体位置取决于上下文和运行时 | 变量保存对象引用，对象通常位于托管堆 |
| **赋值时** | 复制整个数据 | 复制引用（指针） |
| **默认传参** | 传递值的副本 | 传递“引用值”的副本；仍然是按值传参 |
| **常见类型** | `int`, `float`, `bool`, `struct`, `enum` | `class`, `string`, `array`, `delegate` |
| **Unity 例子** | `Vector3`, `Quaternion`, `Color` | `GameObject`, `Transform`, `MonoBehaviour` |

---

## 一个让初学者头疼的 Bug

```csharp
Vector3 pos = transform.position;  // Vector3 是 struct（值类型）
pos.y = 10f;
// ❌ transform.position.y 还是原来的值！pos 是副本，改它不影响原对象
```

**正确做法：**

```csharp
Vector3 pos = transform.position;
pos.y = 10f;
transform.position = pos;   // 把整个 struct 赋值回去
```

---

## struct vs class 的选择

```csharp
// struct —— 适合以数据为主、具有值语义的数据包
public readonly struct DamageInfo
{
    public float Damage { get; }
    public GameObject Attacker { get; }
    public Vector3 HitPoint { get; }

    public DamageInfo(float damage, GameObject attacker, Vector3 hitPoint)
    {
        Damage = damage;
        Attacker = attacker;
        HitPoint = hitPoint;
    }
}

// class —— 适合有行为、需要继承的对象
public class Enemy
{
    public int hp;
    public virtual void TakeDamage(DamageInfo info) { ... }
}
```

**Unity 中什么时候考虑 struct：**

- 类型表达一个完整的数据值，而不是具有身份和共享生命周期的对象
- 数据规模较小，复制成本可以接受；不存在适用于所有项目的固定 16 字节分界线
- 不需要继承
- 希望数据直接存储在字段或数组中；仍需注意装箱、闭包和接口调用可能产生分配
- 例子：`AttackData`、`MovementInput`、`FrameSnapshot`

**什么时候用 class：**

- 需要继承 `MonoBehaviour` / `ScriptableObject`
- 数据较大或需要引用语义
- 例子：角色类、武器类、技能类

项目应用：[Backpack Survivor 的 DamageInfo](../../projects/backpack-survivor/damage-pipeline-and-hazard-zone.md)使用 struct 传递伤害上下文。`readonly struct` 能阻止字段被重新赋值，但其中的 `GameObject` 仍然是指向可变对象的引用，因此不是深层不可变。

[Backpack Survivor 的背包纯数据网格](../../projects/backpack-survivor/inventory-data-grid.md)使用 `class Item` 表达具有身份的物品实例。两个 `new Item("gun", 1, 2)` 可以代表同一种物品的两份实例；默认引用相等能让 `InventoryGrid.Contains(item)` 拦住“同一个实例占两块地”，同时允许“同 Id 的两把枪共存”。第 14 课的[合并升级与邻接联动](../../projects/backpack-survivor/merge-upgrade-and-adjacency.md)继续依赖这个语义：合并规则要求同 `Id`、同 `Level`，但必须是不同实例；多格物品扫描邻接时也用引用相等跳过自己。第 21 课的[构筑最小兑现](../../projects/backpack-survivor/build-payoff-dual-wield.md)也依赖 `HashSet<Item>` 的实例身份来防止同一把手枪参与两组 `DualWield`。如果未来重写 `Equals` / `GetHashCode` 改成按 `Id` 比较，`HashSet<Item>`、`Dictionary<Item, ...>`、合并、邻接去重和有效效果解析的语义都必须重新审视。

---

## 装箱 (Boxing) — 性能杀手

```csharp
int hp = 100;
object obj = hp;      // ❌ 装箱：值类型 → object，堆分配
int hp2 = (int)obj;   // ❌ 拆箱：object → 值类型
```

**Unity 中的常见装箱陷阱：**

```csharp
// ❌ string.Format 会导致装箱
Debug.Log(string.Format("HP: {0}", currentHp));

// 字符串插值通常更易读，但日志字符串仍可能产生分配
Debug.Log($"HP: {currentHp}");
```

不同 Unity / .NET 版本对插值字符串的实现不同，不应仅凭语法判断是否装箱或分配；热路径日志需要关闭、采样或用 Profiler 验证。

---

## ref / in / out — 值类型按引用传递

```csharp
// 默认：传副本
void Modify(Vector3 v) { v.x = 100; }        // 不影响外部

// ref：可读写传引用
void Modify(ref Vector3 v) { v.x = 100; }    // 影响外部

// in：只读传引用，避免复制大 struct
void Print(in Vector3 v) { ... }              // 零拷贝，只读

// out：输出参数
void GetPosition(out Vector3 v) { v = ...; }  // 必须在方法内赋值
```

---

## 面试常问

- `Vector3` 是 struct 还是 class？为什么 Unity 这么设计？
- 装箱是什么？怎么在 Unity 中避免？
- `string` 是值类型还是引用类型？它有什么特殊行为？

---

## 延伸阅读

- C# 官方文档：[Value Types](https://learn.microsoft.com/en-us/dotnet/csharp/language-reference/builtin-types/value-types)
- Unity 博客：[Understanding Automatic Memory Management](https://unity.com/how-to/understanding-automatic-memory-management)
