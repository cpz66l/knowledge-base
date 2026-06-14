# 运算符重载

> 让自定义类型用 `+` `-` `==` 等运算符操作 — 代码更自然、更可读

---

## 一句话理解

```csharp
// 没有运算符重载 — 方法调用，啰嗦
Vector3 result = a.Add(b);

// 有运算符重载 — 像原生类型一样写
Vector3 result = a + b;
```

运算符重载本质是**语法糖** — 编译后还是方法调用。但好的重载能让代码意图一目了然。

---

## 可重载的运算符

| 类别 | 运算符 | 备注 |
|------|--------|------|
| 算术 | `+` `-` `*` `/` `%` | 最常用 |
| 一元 | `-` `+` `!` `~` | |
| 自增自减 | `++` `--` | |
| 关系 | `==` `!=` `<` `>` `<=` `>=` | `==` 和 `!=` 必须成对重载 |
| 位运算 | `&` `\|` `^` `<<` `>>` | |
| 类型转换 | `implicit` `explicit` | 隐式/显式转换 |
| true/false | `true` `false` | 极少用，必须成对 |

**不可重载**：`&&` `\|\|`（短路逻辑）、`=` `?.` `.` `new` `typeof` `sizeof`

---

## 基本语法

```csharp
public class Vector2Int
{
    public int x;
    public int y;

    public Vector2Int(int x, int y)
    {
        this.x = x;
        this.y = y;
    }

    // 语法：public static 返回值 operator 运算符(参数)
    public static Vector2Int operator +(Vector2Int a, Vector2Int b)
    {
        return new Vector2Int(a.x + b.x, a.y + b.y);
    }

    public static Vector2Int operator -(Vector2Int a, Vector2Int b)
    {
        return new Vector2Int(a.x - b.x, a.y - b.y);
    }
}

// 使用
Vector2Int pos = new Vector2Int(1, 2);
Vector2Int offset = new Vector2Int(3, 4);
Vector2Int result = pos + offset;  // (4, 6)
```

**关键点**：
- 必须是 `public static`
- 参数至少有一个是当前类型
- 返回类型可以不是当前类型（但通常是）

---

## 常用重载示例

### 算术运算符

```csharp
public class Damage
{
    public float physical;
    public float magical;

    public Damage(float physical, float magical)
    {
        this.physical = physical;
        this.magical = magical;
    }

    // 伤害相加
    public static Damage operator +(Damage a, Damage b)
    {
        return new Damage(a.physical + b.physical, a.magical + b.magical);
    }

    // 伤害翻倍
    public static Damage operator *(Damage d, float multiplier)
    {
        return new Damage(d.physical * multiplier, d.magical * multiplier);
    }

    // 支持 float * Damage（参数顺序反过来）
    public static Damage operator *(float multiplier, Damage d)
    {
        return d * multiplier;  // 复用上面的重载
    }
}

// 使用
Damage sword = new Damage(30, 0);
Damage fire = new Damage(0, 15);
Damage total = sword + fire;         // (30, 15)
Damage crit = total * 1.5f;          // (45, 22.5)
Damage buffed = 2f * total;          // (60, 30) — 反过来也可以
```

### 相等比较

```csharp
public class Item
{
    public int id;
    public string name;

    // == 和 != 必须成对重载
    public static bool operator ==(Item a, Item b)
    {
        // 处理 null 情况
        if (a is null && b is null) return true;
        if (a is null || b is null) return false;
        return a.id == b.id;
    }

    public static bool operator !=(Item a, Item b)
    {
        return !(a == b);
    }

    // ⚠️ 重载 == 后必须同时重写 Equals 和 GetHashCode
    public override bool Equals(object obj)
    {
        if (obj is Item other)
            return id == other.id;
        return false;
    }

    public override int GetHashCode()
    {
        return id.GetHashCode();
    }
}

// 使用
Item potion1 = new Item { id = 1, name = "红药" };
Item potion2 = new Item { id = 1, name = "Red Potion" };  // 名字不同但 id 相同
bool same = potion1 == potion2;  // true — 按 id 判断
```

### 大小比较

```csharp
public class Power
{
    public int value;

    public static bool operator <(Power a, Power b)
    {
        return a.value < b.value;
    }

    public static bool operator >(Power a, Power b)
    {
        return a.value > b.value;
    }
}
```

---


## Unity 实战示例

### 1. 自定义网格坐标

```csharp
[System.Serializable]
public struct GridPos
{
    public int row;
    public int col;

    public GridPos(int row, int col)
    {
        this.row = row;
        this.col = col;
    }

    public static GridPos operator +(GridPos a, GridPos b)
        => new GridPos(a.row + b.row, a.col + b.col);

    public static GridPos operator -(GridPos a, GridPos b)
        => new GridPos(a.row - b.row, a.col - b.col);

    public static bool operator ==(GridPos a, GridPos b)
        => a.row == b.row && a.col == b.col;

    public static bool operator !=(GridPos a, GridPos b)
        => !(a == b);

    public override bool Equals(object obj)
        => obj is GridPos other && this == other;

    public override int GetHashCode()
        => (row, col).GetHashCode();

    public override string ToString()
        => $"({row}, {col})";
}

// 使用 — 像 Unity 内置的 Vector2Int 一样自然
GridPos center = new GridPos(5, 5);
GridPos offset = new GridPos(1, -2);
GridPos neighbor = center + offset;  // (6, 3)
if (neighbor == new GridPos(6, 3))
{
    Debug.Log("命中了相邻格");
}
```

### 2. 属性值叠加

```csharp
[System.Serializable]
public struct StatBonus
{
    public float attack;
    public float defense;
    public float speed;

    public static StatBonus operator +(StatBonus a, StatBonus b)
        => new StatBonus
        {
            attack = a.attack + b.attack,
            defense = a.defense + b.defense,
            speed = a.speed + b.speed
        };

    // 方便与 int 混用
    public static StatBonus operator *(StatBonus s, float multiplier)
        => new StatBonus
        {
            attack = s.attack * multiplier,
            defense = s.defense * multiplier,
            speed = s.speed * multiplier
        };
}

// 装备系统中的应用
public class Equipment
{
    public StatBonus baseStats;
    public StatBonus enchantStats;

    public StatBonus TotalStats => baseStats + enchantStats;
}

StatBonus sword = new StatBonus { attack = 10, defense = 2, speed = 5 };
StatBonus gem = new StatBonus { attack = 5, defense = 0, speed = -1 };
StatBonus final = sword + gem;  // attack=15, defense=2, speed=4
```

### 3. 资源类型防止误用

```csharp
// 类型化 ID — 防止把金币 ID 误传给钻石 ID
public struct GoldAmount
{
    public int amount;

    public static implicit operator GoldAmount(int amount)
        => new GoldAmount { amount = amount };

    public static GoldAmount operator +(GoldAmount a, GoldAmount b)
        => new GoldAmount { amount = a.amount + b.amount };

    public static GoldAmount operator -(GoldAmount a, GoldAmount b)
        => new GoldAmount { amount = a.amount - b.amount };

    public static bool operator >=(GoldAmount a, int cost)
        => a.amount >= cost;

    public static bool operator <=(GoldAmount a, int cost)
        => a.amount <= cost;
}

// 使用 — 语义清晰，不会传错
GoldAmount gold = 100;           // 隐式转换
gold += 50;                      // gold = 150
gold -= 30;                      // gold = 120
if (gold >= 100)
{
    Debug.Log("买得起！");
}
```

---

## ⚠️ 常见坑

### 1. 重载 `==` 后忘记重写 Equals/GetHashCode

```csharp
// ❌ 只重载了 ==，字典/HashSet 行为会不一致
public struct BadExample
{
    public int id;
    public static bool operator ==(BadExample a, BadExample b) => a.id == b.id;
    public static bool operator !=(BadExample a, BadExample b) => !(a == b);
    // 缺少 Equals 和 GetHashCode → 放 HashSet 里有 bug
}

// ✅ 正确：==、!=、Equals、GetHashCode 一起实现
```

### 2. 滥用 — 让代码更难懂

```csharp
// ❌ 过分重载：谁知道 >> 对 Inventory 做什么？
public static Inventory operator >>(Inventory inv, Item item) { ... }

// ✅ 用命名清晰的方法
public void TransferItem(Item item, Inventory target) { ... }
```

**原则**：只有运算含义**直观、不意外**时才重载。`Damage + Damage` 是直观的，`Player >> Enemy` 不是。

---

## 何时用 / 何时不用

| ✅ 适合重载 | ❌ 不适合重载 |
|-------------|---------------|
| 数值/向量运算（`+` `-` `*`） | 语义不明确的运算符 |
| 值比较（`==` `!=` `<` `>`） | 会产生副作用的操作 |
| 类型安全转换（`implicit` 简单类型） | 可能抛异常的操作 |
| 结构体/不可变类型的运算 | 重载只是为了少打几个字 |
| 符合直觉的数学/逻辑运算 | 这个运算符在框架中已经有约定含义 |

---

## 核心技巧

- 运算符重载 = 语法糖，编译后还是静态方法调用
- `==` 和 `!=` 必须成对重载；`<` 和 `>` 也是
- 重载 `==` 后必须同时 `override Equals` 和 `GetHashCode`
- `implicit` = 不会丢数据的转换（如 `int → Rarity`），`explicit` = 可能丢数据（如 `float → int`）
- 只重载直觉上"就是这个意思"的运算符，不要炫技

---

> 📎 标签：`运算符重载` `operator` `隐式转换` `Unity`
