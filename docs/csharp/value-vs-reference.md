# 值类型 vs 引用类型

> Unity C# 中最基础但也最容易踩坑的概念之一

---

## 一句话区分

| | 值类型 (Value Type) | 引用类型 (Reference Type) |
|------|------|------|
| **存在哪** | 栈 (stack) | 堆 (heap) |
| **赋值时** | 复制整个数据 | 复制引用（指针） |
| **传递时** | 传副本 | 传引用 |
| **常见类型** | `int`, `float`, `bool`, `struct`, `enum` | `class`, `string`, `array`, `delegate` |
| **Unity 例子** | `Vector3`, `Quaternion`, `Color` | `GameObject`, `Transform`, `MonoBehaviour` |

---

## 一个让你头疼的 Bug

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
// struct —— 适合小而频繁使用的数据
public struct DamageInfo
{
    public float amount;
    public DamageType type;
    public Vector3 hitPoint;
}

// class —— 适合有行为、需要继承的对象
public class Enemy
{
    public int hp;
    public virtual void TakeDamage(DamageInfo info) { ... }
}
```

**Unity 中什么时候用 struct：**

- 数据容器，大小 < 16 字节
- 不需要继承
- 频繁创建和销毁（不会产生 GC 压力）
- 例子：`AttackData`、`MovementInput`、`FrameSnapshot`

**什么时候用 class：**

- 需要继承 `MonoBehaviour` / `ScriptableObject`
- 数据较大或需要引用语义
- 例子：角色类、武器类、技能类

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

// ✅ 用字符串插值避免
Debug.Log($"HP: {currentHp}");
```

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
